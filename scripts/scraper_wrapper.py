#!/usr/bin/env python3
"""Wrapper to maintain backward compatibility during migration"""
import sys
import os

# Check if we should use new or old implementation
USE_NEW_STRUCTURE = os.getenv('USE_NEW_SCRAPERS', 'false').lower() == 'true'

if USE_NEW_STRUCTURE:
    # Add parent directory to path for new structure imports
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from tools.scrapers.forums.net54_scraper import Net54Scraper
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Net54 Forum Scraper (New Structure)')
    parser.add_argument('--forum', type=int, help='Specific forum ID to scrape')
    parser.add_argument('--thread-limit', type=int, help='Limit number of threads to scrape')
    parser.add_argument('--stats', action='store_true', help='Show scraping statistics')
    args = parser.parse_args()
    
    # Instantiate new scraper
    scraper = Net54Scraper()
    
    if args.stats:
        # Show statistics using legacy storage
        stats = scraper.legacy_scraper.storage.get_stats()
        print(f"\nScraping Statistics:")
        print(f"Forums scraped: {stats['forums_scraped']}")
        print(f"Threads scraped: {stats['threads_scraped']}")
        print(f"Last update: {stats['last_update']}")
    else:
        # Run scraping
        try:
            scraper.scrape(args.forum, args.thread_limit)
        except KeyboardInterrupt:
            print("\nScraping interrupted by user")
        except Exception as e:
            print(f"Error during scraping: {e}")
            import traceback
            traceback.print_exc()
else:
    # Use existing implementation directly
    from scraper import main
    main()