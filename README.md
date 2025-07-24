# Net54 Baseball Forum Archive → Collectibles Archive (Migration in Progress)

This project started as a Net54 Baseball forum archiver and is expanding to become a comprehensive collectibles data archive, including forums, auction houses, and content sites.

## 🚀 Migration Status

We're currently migrating to a new structure that supports multiple data sources. The existing Net54 scraper continues to work normally during this transition.

- **Current**: Net54 forum scraping (fully operational)
- **Coming Soon**: Heritage Auctions, PSA Forums, PrewarCards, and more
- **Migration Guide**: See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for details

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

## New Collectibles CLI (Beta)

A unified CLI for managing multiple archives is now available:

```bash
# List all configured archives
python collectibles.py list

# Scrape specific archives
python collectibles.py scrape net54 --forum 39
python collectibles.py scrape heritage  # Coming soon

# View statistics
python collectibles.py stats

# Verify setup
python collectibles.py verify
```

## Testing the Migration

Before migrating, test the new structure:

```bash
# Run local tests
python scripts/test_migration_local.py

# Test with new structure (non-destructive)
USE_NEW_SCRAPERS=true python scripts/scraper_wrapper.py --stats

# Dry run data migration
python scripts/migrate_data.py --dry-run
```

See [TESTING_GUIDE.md](TESTING_GUIDE.md) for comprehensive testing instructions.

## Documentation

- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - Full migration plan and timeline
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - How to test the new structure
- [MIGRATION_CHECKLIST.md](MIGRATION_CHECKLIST.md) - Step-by-step migration checklist
- [MIGRATION_PROGRESS.md](MIGRATION_PROGRESS.md) - Current migration status