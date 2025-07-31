#!/usr/bin/env python3
"""Test which Net54 forums are accessible via Tapatalk API"""

import xmlrpc.client
import logging
from tapatalk_scraper import TapatalkScraper

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def test_forum_access():
    """Test access to various Net54 forums"""
    scraper = TapatalkScraper()
    
    # Common forum IDs to test (based on Net54 structure)
    forum_ids = [
        4,   # Postwar Baseball Cards (1948-1980ish) B/S/T
        13,  # T3-T207 B/S/T
        14,  # 1920 to 1949 Baseball cards- B/S/T
        39,  # WTB Pre-War Cards
        56,  # Everything Else B/S/T, Non-Sports, etc.
        71,  # Net54 Vintage (PWCC Marquee) Auction
    ]
    
    results = {}
    
    for forum_id in forum_ids:
        logger.info(f"\nTesting forum {forum_id}...")
        try:
            # Try to get just 1 topic to test access
            topics = scraper.get_forum_topics(forum_id, 0, 1)
            if topics:
                results[forum_id] = "ACCESSIBLE"
                logger.info(f"✓ Forum {forum_id} is accessible via Tapatalk")
            else:
                results[forum_id] = "EMPTY or RESTRICTED"
                logger.warning(f"✗ Forum {forum_id} returned no topics")
        except Exception as e:
            results[forum_id] = f"ERROR: {str(e)}"
            logger.error(f"✗ Forum {forum_id} error: {e}")
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("SUMMARY:")
    logger.info("="*50)
    for forum_id, status in results.items():
        logger.info(f"Forum {forum_id}: {status}")
    
    accessible = [f for f, s in results.items() if s == "ACCESSIBLE"]
    logger.info(f"\nAccessible forums: {accessible}")

if __name__ == '__main__':
    test_forum_access()