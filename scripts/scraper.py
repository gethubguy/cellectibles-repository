#!/usr/bin/env python3
import os
import sys
import requests
from tqdm import tqdm
from utils import setup_logging, rate_limit, fetch_page
from storage import DataStorage
from parser import Net54Parser

logger = setup_logging('scraper')

class Net54Scraper:
    def __init__(self):
        self.base_url = os.getenv('BASE_URL', 'https://www.net54baseball.com')
        self.session = requests.Session()
        self.parser = Net54Parser()
        self.storage = DataStorage()
        
    def scrape_forums(self):
        """Scrape the main forum list."""
        logger.info("Starting forum list scrape...")
        
        try:
            response = fetch_page(self.base_url, self.session)
            forums = self.parser.parse_forum_list(response.text)
            
            for forum in forums:
                self.storage.save_forum(forum)
                
            logger.info(f"Successfully scraped {len(forums)} forums")
            return forums
            
        except Exception as e:
            logger.error(f"Error scraping forum list: {e}")
            raise
    
    def scrape_forum_threads(self, forum_id, limit=None):
        """Scrape all threads from a specific forum."""
        # Don't skip forums - continue where we left off
        # if self.storage.is_forum_scraped(forum_id):
        #     logger.info(f"Forum {forum_id} already scraped, skipping...")
        #     return
        
        logger.info(f"Scraping threads from forum {forum_id}...")
        all_threads = []
        page_url = f"{self.base_url}/forumdisplay.php?f={forum_id}"
        page_count = 0
        
        while page_url:
            page_count += 1
            logger.info(f"Scraping forum {forum_id} page {page_count}")
            
            rate_limit()
            response = fetch_page(page_url, self.session)
            threads, next_page = self.parser.parse_forum_page(response.text, forum_id)
            
            # Save threads (skip already scraped ones)
            new_threads = []
            for thread in threads:
                if not self.storage.is_thread_scraped(forum_id, thread['id']):
                    self.storage.save_thread(thread)
                    new_threads.append(thread)
                    all_threads.append(thread)  # Only add NEW threads to all_threads
                else:
                    logger.debug(f"Thread {thread['id']} already scraped, skipping...")
            
            # If we found no new threads on this page, we're done
            if not new_threads and threads:
                logger.info(f"No new threads found on page {page_count}, stopping...")
                break
            
            page_url = next_page
            
            # Check limit (only count NEW threads)
            if limit and len(all_threads) >= limit:
                logger.info(f"Reached thread limit of {limit}")
                break
        
        logger.info(f"Scraped {len(all_threads)} threads from forum {forum_id}")
        return all_threads
    
    def scrape_thread_posts(self, thread_id, forum_id):
        """Scrape all posts from a specific thread."""
        if self.storage.is_thread_scraped(forum_id, thread_id):
            logger.info(f"Thread {thread_id} already scraped, skipping...")
            return
        
        logger.info(f"Scraping posts from thread {thread_id}...")
        all_posts = []
        page_url = f"{self.base_url}/showthread.php?t={thread_id}"
        page_count = 0
        
        while page_url:
            page_count += 1
            logger.debug(f"Scraping thread {thread_id} page {page_count}")
            
            rate_limit()
            response = fetch_page(page_url, self.session)
            posts, next_page = self.parser.parse_thread_page(response.text, thread_id)
            
            all_posts.extend(posts)
            page_url = next_page
        
        # Save all posts for this thread
        self.storage.save_posts(thread_id, all_posts, forum_id)
        
        logger.info(f"Scraped {len(all_posts)} posts from thread {thread_id}")
        return all_posts
    
    def scrape_entire_forum(self, forum_id=None, thread_limit=None):
        """Scrape an entire forum or all forums."""
        try:
            # Get forums
            forums = self.scrape_forums()
            
            # Filter if specific forum requested
            if forum_id:
                forums = [f for f in forums if f['id'] == str(forum_id)]
                if not forums:
                    logger.error(f"Forum {forum_id} not found")
                    return
            
            # Process each forum
            for forum in forums:
                logger.info(f"\n{'='*60}")
                logger.info(f"Processing forum: {forum['name']} (ID: {forum['id']})")
                logger.info(f"Expected threads: {forum['thread_count']}")
                logger.info(f"{'='*60}\n")
                
                # Get threads
                threads = self.scrape_forum_threads(forum['id'], limit=thread_limit)
                
                if threads:
                    # Process each thread
                    for i, thread in enumerate(tqdm(threads, desc="Scraping threads")):
                        try:
                            self.scrape_thread_posts(thread['id'], forum['id'])
                        except Exception as e:
                            logger.error(f"Error scraping thread {thread['id']}: {e}")
                            continue
                
                # Show progress
                stats = self.storage.get_stats()
                logger.info(f"\nProgress: {stats['threads_scraped']} threads scraped")
        
        except KeyboardInterrupt:
            logger.info("\nScraping interrupted by user")
            stats = self.storage.get_stats()
            logger.info(f"Final stats: {stats}")
        
        except Exception as e:
            logger.error(f"Fatal error during scraping: {e}")
            raise

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Scrape Net54 Baseball forum')
    parser.add_argument('--forum', type=int, help='Specific forum ID to scrape')
    parser.add_argument('--thread-limit', type=int, help='Limit number of threads per forum')
    parser.add_argument('--stats', action='store_true', help='Show scraping statistics')
    
    args = parser.parse_args()
    
    scraper = Net54Scraper()
    
    if args.stats:
        stats = scraper.storage.get_stats()
        print(f"\nScraping Statistics:")
        print(f"Forums scraped: {stats['forums_scraped']}")
        print(f"Threads scraped: {stats['threads_scraped']}")
        print(f"Last update: {stats['last_update']}")
    else:
        scraper.scrape_entire_forum(
            forum_id=args.forum,
            thread_limit=args.thread_limit
        )

if __name__ == '__main__':
    main()