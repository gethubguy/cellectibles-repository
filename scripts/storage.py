import json
import os
from datetime import datetime
from pathlib import Path
from utils import setup_logging, get_safe_filename

logger = setup_logging('storage')

class DataStorage:
    def __init__(self, base_dir='./data/forums/net54baseball.com'):
        self.base_dir = Path(base_dir)
        self.processed_dir = self.base_dir / 'processed'
        self.metadata_dir = self.base_dir / 'metadata'
        
        # Create base directories
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        
        # Forum-specific directories created on demand
        
        # Load or create progress tracking
        self.progress_file = self.metadata_dir / 'progress.json'
        self.progress = self.load_progress()
    
    def load_progress(self):
        """Load scraping progress from file."""
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        return {
            'forums': {},
            'threads': {},
            'last_update': None
        }
    
    def save_progress(self):
        """Save current progress to file."""
        self.progress['last_update'] = datetime.now().isoformat()
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)
        logger.debug(f"Progress saved at {self.progress['last_update']}")
    
    def save_forum(self, forum_data):
        """Save forum metadata."""
        forum_id = str(forum_data['id'])
        # Save forum metadata in the forum directory
        forum_dir = self.processed_dir / f'forum_{forum_id}'
        forum_dir.mkdir(parents=True, exist_ok=True)
        filename = forum_dir / 'metadata.json'
        
        with open(filename, 'w') as f:
            json.dump(forum_data, f, indent=2)
        
        # Update progress
        self.progress['forums'][forum_id] = {
            'name': forum_data['name'],
            'scraped_at': datetime.now().isoformat(),
            'thread_count': forum_data.get('thread_count', 0)
        }
        self.save_progress()
        
        logger.info(f"Saved forum: {forum_data['name']} (ID: {forum_id})")
    
    def save_thread(self, thread_data):
        """Save thread metadata only - posts will be added later."""
        thread_id = str(thread_data['id'])
        forum_id = str(thread_data['forum_id'])
        
        # Save directly in forum directory
        forum_dir = self.processed_dir / f'forum_{forum_id}'
        forum_dir.mkdir(parents=True, exist_ok=True)
        
        filename = forum_dir / f'thread_{thread_id}.json'
        
        # Initialize with thread metadata and empty posts array
        thread_data['posts'] = []
        
        with open(filename, 'w') as f:
            json.dump(thread_data, f, indent=2)
        
        # Update progress
        if forum_id not in self.progress['threads']:
            self.progress['threads'][forum_id] = {}
        
        self.progress['threads'][forum_id][thread_id] = {
            'title': thread_data['title'],
            'scraped_at': datetime.now().isoformat(),
            'post_count': thread_data.get('post_count', 0)
        }
        self.save_progress()
        
        logger.info(f"Saved thread: {thread_data['title'][:50]}... (ID: {thread_id})")
    
    def save_posts(self, thread_id, posts, forum_id):
        """Add posts to existing thread file."""
        thread_id = str(thread_id)
        forum_id = str(forum_id)
        
        # Load existing thread file
        forum_dir = self.processed_dir / f'forum_{forum_id}'
        filename = forum_dir / f'thread_{thread_id}.json'
        
        if filename.exists():
            with open(filename, 'r') as f:
                thread_data = json.load(f)
            
            # Add posts to thread data
            thread_data['posts'] = posts
            
            with open(filename, 'w') as f:
                json.dump(thread_data, f, indent=2)
            
            logger.info(f"Added {len(posts)} posts to thread {thread_id}")
        else:
            logger.error(f"Thread file not found for {thread_id} - save thread first!")
    
    def is_forum_scraped(self, forum_id):
        """Check if forum has already been scraped."""
        return str(forum_id) in self.progress['forums']
    
    def is_thread_scraped(self, forum_id, thread_id):
        """Check if thread has already been scraped."""
        forum_id = str(forum_id)
        thread_id = str(thread_id)
        return (forum_id in self.progress['threads'] and 
                thread_id in self.progress['threads'][forum_id])
    
    def get_stats(self):
        """Get scraping statistics."""
        total_forums = len(self.progress['forums'])
        total_threads = sum(len(threads) for threads in self.progress['threads'].values())
        
        return {
            'forums_scraped': total_forums,
            'threads_scraped': total_threads,
            'last_update': self.progress['last_update']
        }