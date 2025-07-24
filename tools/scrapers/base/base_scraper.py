from abc import ABC, abstractmethod
import requests
from pathlib import Path
import yaml
import time
import logging
from typing import Dict, Any, Optional


class BaseScraper(ABC):
    """Abstract base class for all scrapers"""
    
    def __init__(self, config_path: str):
        """Initialize the base scraper with configuration
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.config = self.load_config(config_path)
        self.session = requests.Session()
        self.archive_name = self.config['archive']['name']
        self.archive_type = self.config['archive']['type']
        self.base_url = self.config['archive']['base_url']
        
        # Set up session headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Configure logging
        self.logger = logging.getLogger(f"{self.archive_name}_scraper")
        
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file
        
        Args:
            config_path: Path to YAML configuration file
            
        Returns:
            Dictionary containing configuration
        """
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def rate_limit(self):
        """Apply rate limiting based on configuration"""
        delay = self.config['scraping'].get('delay_seconds', 2)
        time.sleep(delay)
    
    def make_request(self, url: str, **kwargs) -> Optional[requests.Response]:
        """Make HTTP request with retry logic
        
        Args:
            url: URL to request
            **kwargs: Additional arguments for requests.get()
            
        Returns:
            Response object or None if failed
        """
        max_retries = self.config['scraping'].get('max_retries', 3)
        timeout = self.config['scraping'].get('timeout_seconds', 30)
        
        for attempt in range(max_retries):
            try:
                self.rate_limit()
                response = self.session.get(url, timeout=timeout, **kwargs)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
        
        return None
    
    @abstractmethod
    def scrape(self):
        """Main scraping method to be implemented by subclasses"""
        pass
        
    @abstractmethod
    def parse_item(self, html: str) -> Dict[str, Any]:
        """Parse a single item (thread, auction lot, etc.)
        
        Args:
            html: HTML content to parse
            
        Returns:
            Dictionary containing parsed data
        """
        pass
    
    def get_storage_path(self, item_type: str) -> Path:
        """Get storage path for a specific item type
        
        Args:
            item_type: Type of item (e.g., 'forums', 'threads', 'posts')
            
        Returns:
            Path object for storage location
        """
        base_path = Path(self.config['storage']['base_path'])
        structure = self.config['storage']['structure']
        return base_path / structure.get(item_type, item_type)