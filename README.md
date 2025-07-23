# Net54 Baseball Forum Archive

This project archives the Net54 Baseball forum (https://www.net54baseball.com/) for historical preservation and future AI analysis.

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy environment variables:
```bash
cp .env.example .env
```

3. Run the scraper:
```bash
# Scrape all forums
python scripts/scraper.py

# Scrape specific forum
python scripts/scraper.py --forum 123

# Limit threads per forum
python scripts/scraper.py --thread-limit 50

# Show statistics
python scripts/scraper.py --stats
```

## GitHub Actions

The scraper can run on GitHub's infrastructure to protect your IP:

1. Go to Actions tab
2. Select "Scrape Net54 Forum" workflow
3. Click "Run workflow"
4. Optionally specify forum ID and thread limit
5. Download artifacts when complete

The workflow also runs automatically every Sunday at 2 AM UTC.

## Data Structure

Scraped data is organized as:
- `data/processed/forums/` - Forum metadata
- `data/processed/threads/` - Thread information by forum
- `data/processed/posts/` - Post content by thread
- `data/metadata/progress.json` - Scraping progress tracker

## Features

- Respectful rate limiting (2 seconds between requests)
- Resume capability for interrupted scrapes
- Progress tracking to avoid re-scraping
- Structured JSON output for easy analysis
- Comprehensive logging