from bs4 import BeautifulSoup
import re
from datetime import datetime
from utils import setup_logging

logger = setup_logging('parser')

class Net54Parser:
    def __init__(self):
        self.base_url = "https://www.net54baseball.com"
    
    def parse_forum_list(self, html):
        """Parse the main forum list page."""
        soup = BeautifulSoup(html, 'lxml')
        forums = []
        
        # Find all forum rows
        forum_tables = soup.find_all('table', class_='tborder')
        
        for table in forum_tables:
            forum_rows = table.find_all('tr')
            
            for row in forum_rows:
                # Look for forum links
                forum_link = row.find('a', href=re.compile(r'forumdisplay\.php\?f=\d+'))
                if forum_link:
                    forum_id = re.search(r'f=(\d+)', forum_link['href']).group(1)
                    forum_name = forum_link.text.strip()
                    
                    # Get description
                    desc_td = row.find('td', class_='alt1Active')
                    description = ''
                    if desc_td:
                        desc_text = desc_td.find_all(text=True)
                        description = ' '.join(text.strip() for text in desc_text if text.strip())
                    
                    # Get thread/post counts
                    stats = row.find_all('td', class_='alt2')
                    thread_count = 0
                    post_count = 0
                    
                    if len(stats) >= 2:
                        try:
                            thread_count = int(stats[0].text.strip().replace(',', ''))
                            post_count = int(stats[1].text.strip().replace(',', ''))
                        except:
                            pass
                    
                    forums.append({
                        'id': forum_id,
                        'name': forum_name,
                        'description': description,
                        'url': f"{self.base_url}/forumdisplay.php?f={forum_id}",
                        'thread_count': thread_count,
                        'post_count': post_count
                    })
        
        logger.info(f"Parsed {len(forums)} forums from main page")
        return forums
    
    def parse_forum_page(self, html, forum_id):
        """Parse a forum page to get thread list."""
        soup = BeautifulSoup(html, 'lxml')
        threads = []
        
        # Find thread table
        thread_table = soup.find('table', id='threadslist')
        if not thread_table:
            logger.warning(f"No thread table found for forum {forum_id}")
            return threads, None
        
        # Find all thread rows
        thread_rows = thread_table.find_all('tr')
        
        for row in thread_rows:
            # Skip header/footer rows
            if not row.find('td', class_='alt1'):
                continue
            
            # Get thread link
            thread_link = row.find('a', id=re.compile(r'thread_title_\d+'))
            if not thread_link:
                continue
            
            thread_id = re.search(r'thread_title_(\d+)', thread_link['id']).group(1)
            thread_title = thread_link.text.strip()
            thread_url = thread_link['href']
            if not thread_url.startswith('http'):
                thread_url = f"{self.base_url}/{thread_url}"
            
            # Get author
            author = 'Unknown'
            author_cell = row.find('td', class_='alt2')
            if author_cell:
                author_link = author_cell.find('a')
                if author_link:
                    author = author_link.text.strip()
            
            # Get stats
            reply_count = 0
            view_count = 0
            stats_cells = row.find_all('td', class_='alt1')
            if len(stats_cells) >= 2:
                try:
                    reply_count = int(stats_cells[-2].text.strip().replace(',', ''))
                    view_count = int(stats_cells[-1].text.strip().replace(',', ''))
                except:
                    pass
            
            threads.append({
                'id': thread_id,
                'forum_id': forum_id,
                'title': thread_title,
                'url': thread_url,
                'author': author,
                'reply_count': reply_count,
                'view_count': view_count
            })
        
        # Check for next page
        next_page = None
        page_nav = soup.find('div', class_='pagenav')
        if page_nav:
            next_link = page_nav.find('a', rel='next')
            if next_link:
                next_page = next_link['href']
                if not next_page.startswith('http'):
                    next_page = f"{self.base_url}/{next_page}"
        
        logger.info(f"Parsed {len(threads)} threads from forum {forum_id}")
        return threads, next_page
    
    def parse_thread_page(self, html, thread_id):
        """Parse a thread page to get all posts."""
        soup = BeautifulSoup(html, 'lxml')
        posts = []
        
        # Find all post containers
        post_divs = soup.find_all('div', id=re.compile(r'post_\d+'))
        
        for post_div in post_divs:
            post_id = re.search(r'post_(\d+)', post_div['id']).group(1)
            
            # Get author
            author = 'Unknown'
            author_div = post_div.find('div', class_='username_container')
            if author_div:
                author_link = author_div.find('a')
                if author_link:
                    author = author_link.text.strip()
            
            # Get timestamp
            timestamp = None
            date_div = post_div.find('div', class_='date')
            if date_div:
                timestamp = date_div.text.strip()
            
            # Get post content
            content = ''
            content_div = post_div.find('div', class_='postcontent')
            if content_div:
                # Remove quote blocks to avoid duplication
                for quote in content_div.find_all('div', class_='quote'):
                    quote.decompose()
                
                content = content_div.get_text(separator='\n', strip=True)
            
            # Get attachments/images
            attachments = []
            img_tags = post_div.find_all('img', src=True)
            for img in img_tags:
                if 'attachment.php' in img['src'] or 'images/attach' in img['src']:
                    attachments.append(img['src'])
            
            posts.append({
                'id': post_id,
                'thread_id': thread_id,
                'author': author,
                'timestamp': timestamp,
                'content': content,
                'attachments': attachments
            })
        
        # Check for next page
        next_page = None
        page_nav = soup.find('div', class_='pagenav')
        if page_nav:
            next_link = page_nav.find('a', rel='next')
            if next_link:
                next_page = next_link['href']
                if not next_page.startswith('http'):
                    next_page = f"{self.base_url}/{next_page}"
        
        logger.info(f"Parsed {len(posts)} posts from thread {thread_id}")
        return posts, next_page