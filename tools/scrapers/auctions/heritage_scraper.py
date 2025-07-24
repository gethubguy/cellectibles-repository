"""
Heritage Auctions Scraper

Scrapes auction lots and results from Heritage Auctions (ha.com)
Focuses on sports collectibles and trading cards
"""
import re
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from bs4 import BeautifulSoup

from ..base.base_scraper import BaseScraper
from ..base.storage import MultiArchiveStorage


class HeritageScraper(BaseScraper):
    """Scraper for Heritage Auctions"""
    
    def __init__(self, config_path='configs/heritage.yaml'):
        """Initialize Heritage scraper
        
        Args:
            config_path: Path to YAML configuration file
        """
        super().__init__(config_path)
        self.storage = MultiArchiveStorage('heritage', 'archives')
        
        # Heritage-specific settings
        self.categories = self.config.get('categories', [])
        self.download_images = self.config['features'].get('download_images', False)
        self.track_prices = self.config['features'].get('track_prices', True)
        
    def scrape(self, auction_id: Optional[str] = None, lot_limit: Optional[int] = None):
        """Main scraping method
        
        Args:
            auction_id: Specific auction to scrape (optional)
            lot_limit: Maximum number of lots to scrape (optional)
        """
        self.logger.info(f"Starting Heritage scraper...")
        
        if auction_id:
            # Scrape specific auction
            self.scrape_auction(auction_id, lot_limit)
        else:
            # Scrape recent auctions from categories
            for category in self.categories:
                self.logger.info(f"Scraping category: {category}")
                self.scrape_category(category, lot_limit)
    
    def scrape_category(self, category: str, lot_limit: Optional[int] = None):
        """Scrape auctions from a specific category
        
        Args:
            category: Category path (e.g., 'sports-collectibles/trading-cards')
            lot_limit: Maximum lots per auction
        """
        # Build category URL
        url = f"{self.base_url}/{category}"
        
        response = self.make_request(url)
        if not response:
            self.logger.error(f"Failed to fetch category: {category}")
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find auction listings
        auctions = self.parse_auction_list(soup)
        
        for auction in auctions:
            if not self.storage.is_item_scraped('auctions', auction['id']):
                self.logger.info(f"Scraping auction: {auction['title']}")
                self.scrape_auction(auction['id'], lot_limit)
    
    def scrape_auction(self, auction_id: str, lot_limit: Optional[int] = None):
        """Scrape lots from a specific auction
        
        Args:
            auction_id: Heritage auction ID
            lot_limit: Maximum number of lots to scrape
        """
        # Get auction details
        auction_url = f"{self.base_url}/c/auction-home.zx?saleNo={auction_id}"
        response = self.make_request(auction_url)
        
        if not response:
            self.logger.error(f"Failed to fetch auction: {auction_id}")
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')
        auction_data = self.parse_auction_details(soup, auction_id)
        
        # Save auction metadata
        self.storage.save_item('auctions', auction_id, auction_data)
        
        # Get lot listings
        lots_scraped = 0
        page = 1
        
        while True:
            if lot_limit and lots_scraped >= lot_limit:
                break
                
            lots_url = f"{self.base_url}/c/search.zx?saleNo={auction_id}&pg={page}"
            response = self.make_request(lots_url)
            
            if not response:
                break
                
            soup = BeautifulSoup(response.text, 'html.parser')
            lots = self.parse_lot_list(soup)
            
            if not lots:
                break
            
            for lot in lots:
                if lot_limit and lots_scraped >= lot_limit:
                    break
                    
                if not self.storage.is_item_scraped('lots', lot['id']):
                    self.scrape_lot(lot['id'], auction_id)
                    lots_scraped += 1
            
            page += 1
        
        self.logger.info(f"Scraped {lots_scraped} lots from auction {auction_id}")
    
    def scrape_lot(self, lot_id: str, auction_id: str):
        """Scrape individual lot details
        
        Args:
            lot_id: Heritage lot ID
            auction_id: Parent auction ID
        """
        lot_url = f"{self.base_url}/c/item.zx?saleNo={auction_id}&lotNo={lot_id}"
        response = self.make_request(lot_url)
        
        if not response:
            self.logger.error(f"Failed to fetch lot: {lot_id}")
            return
        
        # Save raw HTML if configured
        if self.config['features'].get('save_raw_html', True):
            self.storage.save_raw('lots', lot_id, response.text)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        lot_data = self.parse_lot_details(soup, lot_id, auction_id)
        
        # Download images if configured
        if self.download_images and lot_data.get('images'):
            lot_data['local_images'] = self.download_lot_images(lot_id, lot_data['images'])
        
        # Save lot data
        self.storage.save_item('lots', lot_id, lot_data)
    
    def parse_item(self, html: str) -> Dict[str, Any]:
        """Parse HTML content (implements abstract method)
        
        Args:
            html: HTML content to parse
            
        Returns:
            Parsed data dictionary
        """
        soup = BeautifulSoup(html, 'html.parser')
        # This is a generic parser - specific parsing is done in specialized methods
        return self.parse_lot_details(soup, 'unknown', 'unknown')
    
    def parse_auction_list(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parse list of auctions from category page
        
        Args:
            soup: BeautifulSoup object of category page
            
        Returns:
            List of auction dictionaries
        """
        auctions = []
        
        # Find auction listings (adjust selectors based on actual HTML structure)
        auction_elements = soup.find_all('div', class_='auction-listing')
        
        for element in auction_elements:
            auction = {
                'id': self.extract_auction_id(element),
                'title': element.find('h3').text.strip() if element.find('h3') else '',
                'date': element.find('span', class_='date').text.strip() if element.find('span', class_='date') else '',
                'lot_count': self.extract_number(element.find('span', class_='lot-count').text) if element.find('span', class_='lot-count') else 0
            }
            if auction['id']:
                auctions.append(auction)
        
        return auctions
    
    def parse_auction_details(self, soup: BeautifulSoup, auction_id: str) -> Dict[str, Any]:
        """Parse auction details page
        
        Args:
            soup: BeautifulSoup object of auction page
            auction_id: Auction ID
            
        Returns:
            Auction data dictionary
        """
        return {
            'id': auction_id,
            'title': soup.find('h1').text.strip() if soup.find('h1') else '',
            'description': soup.find('div', class_='auction-description').text.strip() if soup.find('div', class_='auction-description') else '',
            'start_date': self.extract_date(soup, 'start-date'),
            'end_date': self.extract_date(soup, 'end-date'),
            'lot_count': self.extract_number(soup.find('span', class_='total-lots').text) if soup.find('span', class_='total-lots') else 0,
            'scraped_at': datetime.now().isoformat()
        }
    
    def parse_lot_list(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Parse list of lots from search results
        
        Args:
            soup: BeautifulSoup object of search page
            
        Returns:
            List of lot dictionaries
        """
        lots = []
        
        # Find lot listings
        lot_elements = soup.find_all('div', class_='lot-item')
        
        for element in lot_elements:
            lot = {
                'id': self.extract_lot_id(element),
                'title': element.find('h4').text.strip() if element.find('h4') else '',
                'current_bid': self.extract_price(element.find('span', class_='current-bid')) if element.find('span', class_='current-bid') else None
            }
            if lot['id']:
                lots.append(lot)
        
        return lots
    
    def parse_lot_details(self, soup: BeautifulSoup, lot_id: str, auction_id: str) -> Dict[str, Any]:
        """Parse individual lot details
        
        Args:
            soup: BeautifulSoup object of lot page
            lot_id: Lot ID
            auction_id: Parent auction ID
            
        Returns:
            Lot data dictionary
        """
        lot_data = {
            'id': lot_id,
            'auction_id': auction_id,
            'title': soup.find('h1').text.strip() if soup.find('h1') else '',
            'description': soup.find('div', class_='lot-description').text.strip() if soup.find('div', class_='lot-description') else '',
            'scraped_at': datetime.now().isoformat()
        }
        
        # Extract price information
        if self.track_prices:
            lot_data.update({
                'estimate_low': self.extract_price(soup.find('span', class_='estimate-low')),
                'estimate_high': self.extract_price(soup.find('span', class_='estimate-high')),
                'current_bid': self.extract_price(soup.find('span', class_='current-bid')),
                'starting_bid': self.extract_price(soup.find('span', class_='starting-bid')),
                'realized_price': self.extract_price(soup.find('span', class_='realized-price'))
            })
        
        # Extract images
        images = []
        image_elements = soup.find_all('img', class_='lot-image')
        for img in image_elements:
            if img.get('src'):
                images.append({
                    'url': img['src'],
                    'alt': img.get('alt', '')
                })
        lot_data['images'] = images
        
        # Extract lot details/specifications
        details = {}
        detail_elements = soup.find_all('div', class_='lot-detail')
        for detail in detail_elements:
            label = detail.find('span', class_='label')
            value = detail.find('span', class_='value')
            if label and value:
                details[label.text.strip()] = value.text.strip()
        lot_data['details'] = details
        
        return lot_data
    
    def extract_auction_id(self, element) -> Optional[str]:
        """Extract auction ID from element"""
        # Implementation depends on actual HTML structure
        link = element.find('a')
        if link and link.get('href'):
            match = re.search(r'saleNo=(\d+)', link['href'])
            if match:
                return match.group(1)
        return None
    
    def extract_lot_id(self, element) -> Optional[str]:
        """Extract lot ID from element"""
        # Implementation depends on actual HTML structure
        link = element.find('a')
        if link and link.get('href'):
            match = re.search(r'lotNo=(\d+)', link['href'])
            if match:
                return match.group(1)
        return None
    
    def extract_price(self, element) -> Optional[float]:
        """Extract price from element"""
        if not element:
            return None
        text = element.text.strip()
        # Remove currency symbols and commas
        price_text = re.sub(r'[^0-9.]', '', text)
        try:
            return float(price_text)
        except ValueError:
            return None
    
    def extract_number(self, text: str) -> int:
        """Extract number from text"""
        if not text:
            return 0
        match = re.search(r'\d+', text)
        return int(match.group()) if match else 0
    
    def extract_date(self, soup: BeautifulSoup, class_name: str) -> Optional[str]:
        """Extract date from soup"""
        element = soup.find('span', class_=class_name)
        if element:
            # Parse date and return ISO format
            return element.text.strip()
        return None
    
    def download_lot_images(self, lot_id: str, images: List[Dict[str, str]]) -> List[str]:
        """Download images for a lot
        
        Args:
            lot_id: Lot ID for naming
            images: List of image dictionaries with URLs
            
        Returns:
            List of local file paths
        """
        local_paths = []
        
        for i, image in enumerate(images):
            url = image['url']
            extension = url.split('.')[-1].split('?')[0]  # Get extension, remove query params
            
            if extension not in self.config['image_settings']['formats']:
                continue
            
            filename = f"lot_{lot_id}_img_{i}.{extension}"
            # Implementation would download and save image
            # local_paths.append(saved_path)
            
        return local_paths