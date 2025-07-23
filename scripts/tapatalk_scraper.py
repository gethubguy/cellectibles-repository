#!/usr/bin/env python3
"""
Tapatalk API scraper for Net54 Baseball forum
Uses XML-RPC protocol to fetch forum data
"""
import os
import sys
import time
import base64
import xmlrpc.client
import requests
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET
from utils import setup_logging, rate_limit, get_safe_filename
from storage import DataStorage

logger = setup_logging('tapatalk_scraper')

class TapatalkTransport(xmlrpc.client.Transport):
    """Custom transport to handle Tapatalk responses"""
    def __init__(self, use_datetime=False, use_builtin_types=False):
        super().__init__(use_datetime, use_builtin_types)
        self._use_builtin_types = use_builtin_types
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
            'Accept': 'text/xml',
            'Content-Type': 'text/xml'
        })
    
    def request(self, host, handler, request_body, verbose=False):
        """Make request using requests library to handle redirects"""
        url = f"https://{host}{handler}"
        
        try:
            response = self.session.post(
                url, 
                data=request_body,
                allow_redirects=True,
                timeout=30
            )
            response.raise_for_status()
            
            # Parse the XML response
            p, u = self.getparser()
            p.feed(response.text)
            p.close()
            return u.close()
            
        except Exception as e:
            raise xmlrpc.client.ProtocolError(
                host + handler,
                500,
                str(e),
                {}
            )

class TapatalkScraper:
    def __init__(self):
        self.base_url = os.getenv('BASE_URL', 'https://www.net54baseball.com')
        self.api_url = f"{self.base_url}/mobiquo/mobiquo.php"
        self.storage = DataStorage()
        
        # Setup XML-RPC client
        transport = TapatalkTransport()
        self.proxy = xmlrpc.client.ServerProxy(self.api_url, transport=transport)
        
        # Rate limiting
        self.delay = float(os.getenv('DELAY_SECONDS', 5.0))  # Conservative 5 seconds
        
    def decode_base64_field(self, value):
        """Decode base64 encoded fields from Tapatalk"""
        if isinstance(value, xmlrpc.client.Binary):
            # Handle XML-RPC Binary objects
            return value.data.decode('utf-8', errors='ignore')
        elif isinstance(value, dict) and 'base64' in str(value):
            # Handle base64 encoded values
            return base64.b64decode(value).decode('utf-8', errors='ignore')
        elif isinstance(value, bytes):
            return value.decode('utf-8', errors='ignore')
        return value
    
    def parse_topic_list(self, response):
        """Parse topic list from get_topic response"""
        topics = []
        
        if isinstance(response, dict) and 'topics' in response:
            topic_list = response['topics']
        elif isinstance(response, list):
            topic_list = response
        else:
            logger.warning(f"Unexpected response format: {type(response)}")
            return topics
        
        for topic in topic_list:
            parsed_topic = {
                'topic_id': str(topic.get('topic_id', '')),
                'forum_id': str(topic.get('forum_id', '')),
                'topic_title': self.decode_base64_field(topic.get('topic_title', '')),
                'topic_author_name': self.decode_base64_field(topic.get('topic_author_name', '')),
                'reply_number': int(topic.get('reply_number', 0)) if topic.get('reply_number') else 0,
                'view_number': int(topic.get('view_number', 0)) if topic.get('view_number') else 0,
                'post_time': topic.get('post_time', ''),
                'last_reply_time': topic.get('last_reply_time', '')
            }
            topics.append(parsed_topic)
        
        return topics
    
    def parse_posts(self, response):
        """Parse posts from get_thread response"""
        posts = []
        
        if isinstance(response, dict) and 'posts' in response:
            post_list = response['posts']
        elif isinstance(response, list):
            post_list = response
        else:
            logger.warning(f"Unexpected post response format: {type(response)}")
            return posts
        
        for post in post_list:
            parsed_post = {
                'post_id': str(post.get('post_id', '')),
                'post_title': self.decode_base64_field(post.get('post_title', '')),
                'post_author_name': self.decode_base64_field(post.get('post_author_name', '')),
                'post_content': self.decode_base64_field(post.get('post_content', '')),
                'post_time': str(post.get('post_time', '')) if post.get('post_time') else '',
                'timestamp': str(post.get('timestamp', '')) if post.get('timestamp') else ''
            }
            posts.append(parsed_post)
        
        return posts
    
    def get_forum_topics(self, forum_id, start=0, limit=20):
        """Get topics from a specific forum"""
        logger.info(f"Fetching topics from forum {forum_id} (start: {start}, limit: {limit})")
        
        try:
            time.sleep(self.delay)  # Rate limiting
            
            # Call get_topic method
            response = self.proxy.get_topic(str(forum_id), start, start + limit - 1)
            
            # Check for error response
            if isinstance(response, dict) and response.get('result') == False:
                error_msg = self.decode_base64_field(response.get('result_text', ''))
                logger.error(f"API error: {error_msg}")
                return []
            
            topics = self.parse_topic_list(response)
            logger.info(f"Found {len(topics)} topics")
            return topics
            
        except Exception as e:
            logger.error(f"Error fetching topics: {e}")
            return []
    
    def get_thread_posts(self, topic_id, start=0, limit=20):
        """Get posts from a specific thread"""
        logger.info(f"Fetching posts from thread {topic_id}")
        
        try:
            time.sleep(self.delay)  # Rate limiting
            
            # Call get_thread method
            response = self.proxy.get_thread(str(topic_id), start, start + limit - 1)
            
            # Check for error response
            if isinstance(response, dict) and response.get('result') == False:
                error_msg = self.decode_base64_field(response.get('result_text', ''))
                logger.error(f"API error: {error_msg}")
                return []
            
            posts = self.parse_posts(response)
            logger.info(f"Found {len(posts)} posts")
            return posts
            
        except Exception as e:
            logger.error(f"Error fetching posts: {e}")
            return []
    
    def scrape_forum(self, forum_id, topic_limit=None, post_limit_per_topic=50):
        """Scrape a complete forum"""
        logger.info(f"Starting scrape of forum {forum_id}")
        
        # Save forum metadata
        forum_data = {
            'id': str(forum_id),
            'name': f'Forum {forum_id}',  # We'll update this from topic data
            'scraped_at': datetime.now().isoformat()
        }
        self.storage.save_forum(forum_data)
        
        # Get topics in batches
        all_topics = []
        batch_size = 50
        start = 0
        
        while True:
            topics = self.get_forum_topics(forum_id, start, batch_size)
            if not topics:
                break
                
            all_topics.extend(topics)
            
            # Check if we've hit the limit
            if topic_limit and len(all_topics) >= topic_limit:
                all_topics = all_topics[:topic_limit]
                break
            
            # If we got less than batch_size, we're at the end
            if len(topics) < batch_size:
                break
                
            start += batch_size
            logger.info(f"Fetched {len(all_topics)} topics so far...")
        
        logger.info(f"Total topics to process: {len(all_topics)}")
        
        # Process each topic
        for i, topic in enumerate(all_topics):
            topic_title = topic.get('topic_title', 'Unknown')
            if len(topic_title) > 50:
                topic_title = topic_title[:50] + "..."
            logger.info(f"Processing topic {i+1}/{len(all_topics)}: {topic_title}")
            
            # Save thread metadata
            thread_data = {
                'id': str(topic['topic_id']),
                'forum_id': str(forum_id),
                'title': topic['topic_title'],
                'author': topic['topic_author_name'],
                'reply_count': topic['reply_number'],
                'view_count': topic['view_number'],
                'created_date': str(topic['post_time']) if topic['post_time'] else None,
                'last_reply': str(topic['last_reply_time']) if topic['last_reply_time'] else None
            }
            self.storage.save_thread(thread_data)
            
            # Get posts for this thread
            posts = []
            post_start = 0
            
            while True:
                batch_posts = self.get_thread_posts(topic['topic_id'], post_start, 20)
                if not batch_posts:
                    break
                    
                posts.extend(batch_posts)
                
                # Limit posts per topic
                if len(posts) >= post_limit_per_topic:
                    posts = posts[:post_limit_per_topic]
                    break
                
                if len(batch_posts) < 20:  # Got all posts
                    break
                    
                post_start += 20
            
            # Save posts
            if posts:
                self.storage.save_posts(topic['topic_id'], posts)
        
        stats = self.storage.get_stats()
        logger.info(f"Scraping complete. Total threads: {stats['threads_scraped']}")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Scrape Net54 forum using Tapatalk API')
    parser.add_argument('--forum', type=int, required=True, help='Forum ID to scrape')
    parser.add_argument('--topic-limit', type=int, help='Maximum topics to scrape')
    parser.add_argument('--post-limit', type=int, default=50, help='Maximum posts per topic')
    
    args = parser.parse_args()
    
    scraper = TapatalkScraper()
    scraper.scrape_forum(
        forum_id=args.forum,
        topic_limit=args.topic_limit,
        post_limit_per_topic=args.post_limit
    )

if __name__ == '__main__':
    main()