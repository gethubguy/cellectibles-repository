import sys
import os
# Add scripts directory to path for legacy imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../scripts'))

from ..base.base_scraper import BaseScraper
from scraper import Net54Scraper as LegacyScraper
from storage import DataStorage

class Net54Scraper(BaseScraper):
    """New Net54 scraper that wraps the legacy implementation"""
    
    def __init__(self, config_path='configs/net54.yaml'):
        """Initialize the scraper with configuration
        
        Args:
            config_path: Path to YAML configuration file
        """
        super().__init__(config_path)
        
        # Initialize legacy scraper with new storage path
        self.legacy_scraper = LegacyScraper()
        
        # Override storage to use new path structure if enabled
        if os.getenv('USE_NEW_STRUCTURE', 'false').lower() == 'true':
            archive_path = self.config['storage']['base_path']
            self.legacy_scraper.storage = DataStorage(archive_path=archive_path)
            
    def scrape(self, forum_id=None, thread_limit=None):
        """Maintain compatibility with existing interface
        
        Args:
            forum_id: Optional specific forum to scrape
            thread_limit: Optional limit on number of threads
            
        Returns:
            Scraping results
        """
        # Update delay in legacy scraper based on config
        self.legacy_scraper.delay = self.config['scraping']['delay_seconds']
        
        # Run legacy scraper
        if forum_id:
            return self.legacy_scraper.scrape_forum_threads(forum_id, thread_limit)
        else:
            return self.legacy_scraper.scrape_entire_forum(thread_limit)
    
    def parse_item(self, html):
        """Parse a single item using legacy parser
        
        Args:
            html: HTML content to parse
            
        Returns:
            Parsed data dictionary
        """
        # This method satisfies the abstract requirement
        # but delegates to legacy parser when needed
        return self.legacy_scraper.parser.parse_thread_content(html)