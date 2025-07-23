# Forum 2 Scraping Options

Forum 2 is the "motherload" - Net54baseball Vintage (WWII & Older) Baseball Cards & New Member Introductions. It requires authentication to access.

**Stats:** 59,000 threads, 1.1 million posts

## Option 1: Direct Authentication with Tapatalk API

**How it works:**
- Add login credentials to the Tapatalk scraper
- Use GitHub Secrets to store username/password
- Login via API, then scrape normally

**Implementation:**
```python
# Simple addition to existing scraper
response = proxy.login(username, password)
# Then scrape Forum 2 exactly like Forum 39
```

**Pros:**
- Very fast (2-3 hours for entire forum)
- Uses existing code with minimal changes
- 95%+ likely to work technically

**Cons:**
- **HIGH RISK** - Directly tied to your account
- Easy for admins to see "User X downloaded 1.1M posts via API"
- Could result in account ban
- Legal exposure (authenticated = traceable to you)

## Option 2: Browser Automation (Human-Like)

**How it works:**
- Use Selenium/Playwright to control a real browser
- Login through web interface normally
- Click each thread, wait, save, repeat
- Runs from your home server (Unraid Docker)

**Time estimate:**
- 10 seconds per thread = 163 hours = 6.8 days running 24/7
- More realistic (12 hours/day): 2-3 weeks

**Implementation:**
```python
# Selenium example
driver.get("https://www.net54baseball.com/login.php")
driver.find_element_by_name("username").send_keys("your_username")
driver.find_element_by_name("password").send_keys("your_password")
# Click threads, wait, save...
```

**Pros:**
- Very safe - looks exactly like human browsing
- From your normal home IP
- Natural delays and patterns
- Can handle JavaScript, dynamic content

**Cons:**
- SLOW - weeks to complete
- Requires monitoring for errors
- Session timeouts need handling

## Option 3: Hybrid Approach (Best of Both)

**How it works:**
1. Use browser automation ONLY for login (from home server)
2. Extract session cookies after login
3. Feed cookies to fast scraper (GitHub Actions or local)
4. Bulk download using the authenticated session

**Implementation:**
```python
# Step 1: Home server gets cookies
cookies = selenium_login_and_get_cookies()
upload_to_github_secret(cookies)

# Step 2: GitHub Actions uses cookies
scraper.session.cookies = load_cookies_from_secret()
# Now scrape at full API speed
```

**Pros:**
- Login from home IP (safe)
- Bulk download from GitHub IP (anonymous-ish)
- Fast like Option 1, safer like Option 2
- Looks like: "User logged in at home, then browsed from work"

**Cons:**
- More complex to implement
- Still some risk (your session = your account)
- Cookies expire, need refresh

## Option 4: Alternative Approaches

### RSS Feed
- Only gets recent posts, not historical
- But very safe and ongoing

### Archive.org
- Check if historical snapshots exist
- No authentication needed

### Community Help
- Ask if someone has an archive to share
- Many collectors care about preservation

## Recommended Approach

1. **Start with public forums** (4, 13, 14, 20, 39) using Tapatalk
2. **Evaluate the risk** after seeing how much data you get
3. **If you must have Forum 2:**
   - Try browser automation first (safest)
   - If too slow, consider hybrid approach
   - Direct auth only as last resort

## Technical Tools

### Browser Automation Options:
- **Selenium**: Most popular, lots of docs
- **Playwright**: Modern, faster, better API
- **Puppeteer**: Chrome-specific, lightweight

### Pre-built Archive Tools:
- **ArchiveBox**: Self-hosted web archiver
- **Browsertrix Crawler**: Docker-based crawler
- **HTTrack**: Classic website copier

### Docker Setup for Unraid:
```bash
# Selenium container
docker run -d \
  --name=selenium \
  -p 4444:4444 \
  -v /mnt/user/appdata/selenium:/config \
  selenium/standalone-chrome
```

## Risk Assessment

**Low Risk**: RSS feeds, public forums
**Medium Risk**: Browser automation from home
**High Risk**: Direct API auth, hybrid approach
**Nuclear Risk**: Using your main account for bulk API downloads

Remember: The site owner seems hostile to archiving. Any authenticated approach carries risk of account suspension.