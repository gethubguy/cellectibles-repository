import os
import sys
import re
import requests
import cloudscraper
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime
import time
import random
import socket

# Add utilities directory to path for ncc_logger
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'utilities'))
from ncc_logger import get_logger, log_dry_mode, log_start, log_complete, log_found_records, log_progress, log_summary

# ─────────────────────────────
# SCRIPT CONFIG
# ─────────────────────────────

#GENERAL CONFIG
DRY_RUN    = False         # True = Dry run: no writes
SCRIPT_MODE = "batch"       # "single" or "batch"
SUB_THEME_ID = "spt_base"   # used for position enrichment

#BATCHING CONFIG
BATCH_ONE   = False          # True to run only batch
BATCH_SIZE  = 150            # Records per batch

# DELAY CONFIG
USE_DELAY   = True          # Toggle delay on/off
DELAY_MIN   = 2             # Minimum delay in seconds
DELAY_MAX   = 5             # Maximum delay in seconds

# ─────────────────────────────
# LOGGING SETUP
# ─────────────────────────────
logger = get_logger("enrich_br")

def log_regex_input(name: str, text: str):
    logger.debug(f"[Regex Input: {name}] {text}")

if DRY_RUN:
    log_dry_mode(logger)

# ─────────────────────────────
# ENV & DB SETUP
# ─────────────────────────────
load_dotenv()
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# ─────────────────────────────
# Prompt & Fetch Pending Rows
# ─────────────────────────────
TARGET_BR_ID = None    # Will hold a manually entered BR ID in single mode

def load_position_lookup():
    """
    Load position_name and alt_form from the positions table
    and build a lookup to position_abbrev.
    """
    resp = (
        supabase
        .table("positions")
        .select("position_name, alt_form, position_abbrev")
        .execute()
    )
    rows = resp.data or []

    lookup = {}
    for row in rows:
        name = row["position_name"]
        alt = row.get("alt_form")
        abbrev = row["position_abbrev"]

        if name:
            lookup[name.strip().lower()] = abbrev
        if alt:
            lookup[alt.strip().lower()] = abbrev

    return lookup

def split_position_string(pos_string: str) -> list:
    """
    Split a position string on commas and 'and', then strip whitespace.
    """
    parts = re.split(r",|\band\b", pos_string)
    return [part.strip() for part in parts if part.strip()]

def prompt_for_br_id():
    """
    Ask the user to enter a BR ID when running in single mode.
    """
    global TARGET_BR_ID
    TARGET_BR_ID = input("Enter the BR ID to enrich (e.g. 'jeterde01'): ").strip()
    logger.info(f"User provided TARGET_BR_ID={TARGET_BR_ID}")

def fetch_pending_rows():
    # SINGLE-MODE OVERRIDE
    if SCRIPT_MODE == "single":
        prompt_for_br_id()
        resp = (
            supabase
            .table("subjects_staging")
            .select("subject_id, br_id")
            .eq("br_id", TARGET_BR_ID)
            .execute()
        )
        rows = resp.data or []
        logger.info(f"Fetched {len(rows)} row(s) for TARGET_BR_ID={TARGET_BR_ID}")
        return rows

    # BATCH MODE
    resp = (
        supabase
        .table("subjects_staging")
        .select("subject_id, br_id")
        .neq("br_id", None).eq("br_enriched", False)
        .limit(BATCH_SIZE)
        .execute()
    )
    rows = resp.data or []
    logger.info(f"Fetched {len(rows)} rows ready for BR enrichment")
    return rows

# ─────────────────────────────
# Build BR URL helper
# ─────────────────────────────

def build_br_url(br_id: str) -> str:
    """
    Given a Baseball-Reference ID (e.g. 'jeterde01'),
    return the full player page URL.
    """
    prefix = br_id[0].lower()
    return f"https://www.baseball-reference.com/players/{prefix}/{br_id}.shtml"

# ─────────────────────────────
# Fetch & Parse All Bio Fields
# ─────────────────────────────

def fetch_bio_html(br_id: str) -> str:
    """
    Given a BR ID, fetch the player’s Baseball-Reference page HTML.
    """
    url = build_br_url(br_id)
    scraper = cloudscraper.create_scraper()
    resp = scraper.get(url)
    resp.raise_for_status()
    return resp.text

# --------- FIXED FUNCTION DEFINITION (now takes subject_id) ---------
def extract_bio_fields(html: str, subject_id: str) -> dict:
    """
    Parse the HTML meta block using your Google-Sheets regex.
    """
    soup = BeautifulSoup(html, "html.parser")
    meta = soup.find("div", id="meta")
    if not meta:
        logger.warning("No meta block found")
        return {}

    # flatten the meta text to one line
    text = " ".join(meta.get_text(separator=" ", strip=True).split())
    log_regex_input("BR bio meta", text)

    pattern = re.compile(
        r"""(?i)
        #(.*?)\s*positions?:\s*(?P<pos>.*?)\s*          # positions required
        (.*?)\s*(?:positions?:\s*(?P<pos>.*?))?\s*      # positions optional
        bats:\s*(?P<bats>left|right|both|unknown)
        (?:\s+[^\w\s]\s+)?
        throws:\s*(?P<throws>left|right|both|unknown)(?:\s*(?P<height_feet_inch>\d+-\d+)\s*,\s*(?P<weight_lb>\d+))?.*?
        (?:born:\s*(?P<born>.*?\d{4}).*?)?
        (?:died:\s*(?P<died>.*?\d{4}).*?)?
        (?:hall of fame:.*?(?P<hall_of_fame>\d{4}).*?)?
        (?:full name:\s*(?P<full_name>.*?))?
        (?:nicknames?:\s*(?P<nicknames>.*?))?
        \s+View\s+Player\s+Info
        """,
        re.IGNORECASE | re.VERBOSE | re.MULTILINE,
    )

    match = pattern.search(text)
    if not match:
        logger.warning(f"[Regex Fail] subject_id={subject_id} | input={text}")
        return {}

    bio_data = match.groupdict()

    # ────────────────────────────────────────
    # Clean up dates, aliases, & names
    # ────────────────────────────────────────
    if bio_data.get("born"):
        born_clean = bio_data["born"].replace(" ,", ",").strip()
        try:
            # Try full format first
            bio_data["born"] = datetime.strptime(born_clean, "%B %d, %Y").date().isoformat()
        except Exception:
            if re.fullmatch(r"\d{4}", born_clean):
                bio_data["born"] = f"{born_clean}-00-00"
            else:
                logger.warning(f"Failed to parse born date: {born_clean}")
                bio_data["born"] = None

    if bio_data.get("died"):
        died_clean = bio_data["died"].replace(" ,", ",").strip()
        try:
            # Try full format first
            bio_data["died"] = datetime.strptime(died_clean, "%B %d, %Y").date().isoformat()
        except Exception:
            if re.fullmatch(r"\d{4}", died_clean):
                bio_data["died"] = f"{died_clean}-00-00"
            else:
                logger.warning(f"Failed to parse died date: {died_clean}")
                bio_data["died"] = None

    if match.group(1):
        bio_data["primary_subject"] = re.sub(r"\s*Name Note.*$", "", match.group(1)).strip()

    if bio_data.get("nicknames"):
        aliases = bio_data["nicknames"]
        aliases = re.sub(r"\s*Pronunciation.*$", "", aliases).strip()
        aliases = re.sub(r"\s*Instagram.*$", "", aliases).strip()
        bio_data["nicknames"] = aliases

    if bio_data.get("weight_lb"):
        bio_data["weight_lb"] = re.sub(r"\D", "", bio_data["weight_lb"])

    return {
        "primary_subject":    bio_data.get("primary_subject"),
        "positions":          bio_data.get("pos"),
        "bats":               bio_data.get("bats"),
        "throws":             bio_data.get("throws"),
        "height":             bio_data.get("height_feet_inch"),
        "weight":             bio_data.get("weight_lb"),
        "born":               bio_data.get("born"),
        "died":               bio_data.get("died"),
        "hof_year":           bio_data.get("hall_of_fame"),
        "subject_full_name":  bio_data.get("full_name"),
        "aliases":            bio_data.get("nicknames"),
    }

# ─────────────────────────────
# Update Bio
# ─────────────────────────────

def update_bio_fields(subject_id: str, bio: dict) -> None:
    existing = (
        supabase
        .table("subjects_staging")
        .select("primary_subject")
        .eq("subject_id", subject_id)
        .single()
        .execute()
    )
    current = existing.data or {}

    if current.get("primary_subject"):
        bio["primary_subject"] = None

    full_row = (
        supabase
        .table("subjects_staging")
        .select("*")
        .eq("subject_id", subject_id)
        .single()
        .execute()
    )
    latest = full_row.data or {}

    if all(bio.get(k) == latest.get(k) for k in bio if bio.get(k) is not None):
        logger.info(f"No changes detected for {subject_id}. Skipping update.")
        return

    if DRY_RUN:
        filtered = {k: v for k, v in bio.items() if v is not None}
        logger.info(f"[DRY RUN] Would update {subject_id} with {filtered}")
        return   

    data = {k: v for k, v in bio.items() if v is not None}
    if not data:
        logger.warning(f"No new bio data to update for subject {subject_id}")
        return

    resp = (
        supabase
        .table("subjects_staging")
        .update(data)
        .eq("subject_id", subject_id)
        .execute()
    )

    if hasattr(resp, "error") and resp.error:
        logger.error(f"Failed to update {subject_id}: {resp.error}")
    elif isinstance(resp, dict) and "error" in resp:
        logger.error(f"Failed to update {subject_id}: {resp['error']}")
    else:
        logger.info(f"Updated {subject_id} with fields: {list(data.keys())}")

# ─────────────────────────────
# Summary & Exit
# ─────────────────────────────

def exit_with_summary(total_processed: int, total_success: int, total_failed: int):
    """
    Print a final summary and exit with 0 if no failures, 1 otherwise.
    """
    summary = (
        f"BR enrichment complete: "
        f"Processed={total_processed}, "
        f"Succeeded={total_success}, "
        f"Failed={total_failed}"
    )
    logger.info(summary)
    print(summary)
    sys.exit(0)

def run_enrichment_loop():
    total_processed = 0
    total_success   = 0
    total_failed    = 0

    position_lookup = load_position_lookup()

    while True:
        pending = fetch_pending_rows()
        if not pending:
            logger.info("No more rows to process. Exiting loop.")
            break

        for row in pending:
            subject_id = row["subject_id"]
            br_id      = row["br_id"]
            try:
                try:
                    html = fetch_bio_html(br_id)
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 429:
                        logger.info("Received 429 Too Many Requests from Baseball Reference — exiting early.")
                        exit_with_summary(total_processed, total_success, total_failed)
                    else:
                        raise
                except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                    logger.info(f"Network error during fetch ({type(e).__name__}) — exiting early.")
                    exit_with_summary(total_processed, total_success, total_failed)
                bio = extract_bio_fields(html, subject_id)
                raw_positions = bio.get("positions") or ""
                split_positions = split_position_string(raw_positions)
                normalized_positions = [pos.lower() for pos in split_positions]
                mapped_positions = [position_lookup[pos] for pos in normalized_positions if pos in position_lookup]
                final_positions = ", ".join(mapped_positions)
                position_ids = [f"{abbr}_{SUB_THEME_ID}" for abbr in mapped_positions]

                bio["position_id"]     = position_ids[0] if len(position_ids) > 0 else None
                bio["position2_id"]    = position_ids[1] if len(position_ids) > 1 else None
                bio["position3_id"]    = position_ids[2] if len(position_ids) > 2 else None

                if any(v is not None for v in bio.values()):
                    bio["positions"] = final_positions
                    bio["br_enriched"] = True
                    update_bio_fields(subject_id, bio)
                    total_success += 1
                else:
                    logger.warning(f"No bio fields extracted for subject {subject_id}")
                    total_failed += 1

                total_processed += 1

                if USE_DELAY:
                    time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

            except Exception as e:
                logger.error(f"Error processing subject {subject_id}: {e}")
                total_failed += 1

        if SCRIPT_MODE == "single" or BATCH_ONE:
            logger.info("Single mode or one-batch flag set; exiting after this batch.")
            break

    exit_with_summary(total_processed, total_success, total_failed)

if __name__ == "__main__":
    log_start(logger, "Baseball Reference subject")
    run_enrichment_loop()