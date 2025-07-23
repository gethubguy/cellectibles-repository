import os
import logging
import colorlog
from datetime import datetime
import time
from retrying import retry
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_logging(name):
    """Set up colored logging with both file and console output."""
    log_dir = os.getenv('LOG_DIR', './logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # File handler for detailed logs
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = os.path.join(log_dir, f'{today}-{name}.log')
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # Console handler with colors
    console_handler = colorlog.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(levelname)-8s%(reset)s %(message)s',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler.setFormatter(console_formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def rate_limit():
    """Apply rate limiting between requests."""
    delay = float(os.getenv('DELAY_SECONDS', 1.5))
    time.sleep(delay)

@retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000)
def fetch_page(url, session=None):
    """Fetch a page with retry logic."""
    if session is None:
        session = requests.Session()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    timeout = int(os.getenv('TIMEOUT_SECONDS', 30))
    response = session.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    
    return response

def get_safe_filename(text, max_length=50):
    """Convert text to safe filename."""
    # Remove/replace unsafe characters
    safe_text = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in text)
    safe_text = safe_text.strip()[:max_length]
    return safe_text or 'unnamed'