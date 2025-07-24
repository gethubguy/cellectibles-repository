import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import logging


class MultiArchiveStorage:
    """Storage that supports multiple archives with isolated data spaces"""
    
    def __init__(self, archive_name: str, base_dir: str = 'archives'):
        """Initialize storage for a specific archive
        
        Args:
            archive_name: Name of the archive (e.g., 'net54', 'heritage')
            base_dir: Base directory for all archives
        """
        self.archive_name = archive_name
        self.base_dir = Path(base_dir)
        
        # Determine archive type from path structure
        archive_path = None
        for archive_type in ['forums', 'auctions', 'content']:
            potential_path = self.base_dir / archive_type / archive_name
            if potential_path.exists() or archive_type in str(base_dir):
                archive_path = potential_path
                self.archive_type = archive_type
                break
        
        if not archive_path:
            # Default to forums if type cannot be determined
            self.archive_type = 'forums'
            archive_path = self.base_dir / self.archive_type / archive_name
        
        self.archive_dir = archive_path / 'data'
        self.processed_dir = self.archive_dir / 'processed'
        self.metadata_dir = self.archive_dir / 'metadata'
        self.raw_dir = self.archive_dir / 'raw'
        
        # Create directories
        for dir_path in [self.processed_dir, self.metadata_dir, self.raw_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Set up logging
        self.logger = logging.getLogger(f"{archive_name}_storage")
        
        # Load or create progress tracking
        self.progress_file = self.metadata_dir / 'progress.json'
        self.progress = self.load_progress()
    
    def load_progress(self) -> Dict[str, Any]:
        """Load scraping progress from file"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        return {
            'archive_name': self.archive_name,
            'archive_type': self.archive_type,
            'items': {},
            'last_update': None,
            'statistics': {
                'total_items': 0,
                'total_size_bytes': 0
            }
        }
    
    def save_progress(self):
        """Save current progress to file"""
        self.progress['last_update'] = datetime.now().isoformat()
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)
        self.logger.debug(f"Progress saved for {self.archive_name}")
    
    def save_item(self, item_type: str, item_id: str, data: Dict[str, Any]) -> Path:
        """Save an item to the archive
        
        Args:
            item_type: Type of item (e.g., 'thread', 'auction_lot', 'article')
            item_id: Unique identifier for the item
            data: Item data to save
            
        Returns:
            Path to saved file
        """
        # Create type-specific directory
        type_dir = self.processed_dir / item_type
        type_dir.mkdir(exist_ok=True)
        
        # Save item
        filename = type_dir / f"{item_id}.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Update progress
        if item_type not in self.progress['items']:
            self.progress['items'][item_type] = {}
        
        self.progress['items'][item_type][item_id] = {
            'saved_at': datetime.now().isoformat(),
            'size_bytes': filename.stat().st_size
        }
        
        # Update statistics
        self.progress['statistics']['total_items'] += 1
        self.progress['statistics']['total_size_bytes'] += filename.stat().st_size
        
        self.save_progress()
        self.logger.info(f"Saved {item_type} {item_id} to {filename}")
        
        return filename
    
    def save_raw(self, item_type: str, item_id: str, content: str, extension: str = 'html') -> Path:
        """Save raw content (HTML, JSON, etc.)
        
        Args:
            item_type: Type of item
            item_id: Unique identifier
            content: Raw content to save
            extension: File extension
            
        Returns:
            Path to saved file
        """
        type_dir = self.raw_dir / item_type
        type_dir.mkdir(exist_ok=True)
        
        filename = type_dir / f"{item_id}.{extension}"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.logger.debug(f"Saved raw {item_type} {item_id}")
        return filename
    
    def is_item_scraped(self, item_type: str, item_id: str) -> bool:
        """Check if an item has already been scraped
        
        Args:
            item_type: Type of item
            item_id: Unique identifier
            
        Returns:
            True if item exists in progress tracking
        """
        return (item_type in self.progress['items'] and 
                str(item_id) in self.progress['items'][item_type])
    
    def get_item(self, item_type: str, item_id: str) -> Optional[Dict[str, Any]]:
        """Load a previously saved item
        
        Args:
            item_type: Type of item
            item_id: Unique identifier
            
        Returns:
            Item data or None if not found
        """
        filename = self.processed_dir / item_type / f"{item_id}.json"
        if filename.exists():
            with open(filename, 'r') as f:
                return json.load(f)
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get archive statistics
        
        Returns:
            Dictionary with archive statistics
        """
        stats = {
            'archive_name': self.archive_name,
            'archive_type': self.archive_type,
            'last_update': self.progress['last_update'],
            'total_items': self.progress['statistics']['total_items'],
            'total_size_mb': round(self.progress['statistics']['total_size_bytes'] / (1024 * 1024), 2)
        }
        
        # Add item type breakdown
        stats['items_by_type'] = {}
        for item_type, items in self.progress['items'].items():
            stats['items_by_type'][item_type] = len(items)
        
        return stats
    
    def list_items(self, item_type: str, limit: Optional[int] = None) -> list:
        """List items of a specific type
        
        Args:
            item_type: Type of items to list
            limit: Maximum number of items to return
            
        Returns:
            List of item IDs
        """
        if item_type in self.progress['items']:
            items = list(self.progress['items'][item_type].keys())
            if limit:
                return items[:limit]
            return items
        return []
    
    def export_metadata(self, output_file: Optional[Path] = None) -> Path:
        """Export archive metadata for analysis
        
        Args:
            output_file: Optional output path
            
        Returns:
            Path to exported file
        """
        if not output_file:
            output_file = self.metadata_dir / f'{self.archive_name}_metadata_{datetime.now().strftime("%Y%m%d")}.json'
        
        metadata = {
            'archive_info': {
                'name': self.archive_name,
                'type': self.archive_type,
                'exported_at': datetime.now().isoformat()
            },
            'statistics': self.get_stats(),
            'progress': self.progress
        }
        
        with open(output_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        self.logger.info(f"Exported metadata to {output_file}")
        return output_file