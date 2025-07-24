# Scraping Strategies for Different Archive Types

## Authentication Strategies

### 1. Session-Based Authentication (Heritage, REA)
```python
class AuthenticatedScraper:
    def __init__(self):
        self.session = requests.Session()
        # Mimic real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def login(self, username, password):
        # Get login page (usually has CSRF token)
        login_page = self.session.get(f'{self.base_url}/login')
        csrf_token = self.extract_csrf_token(login_page.text)
        
        # Submit credentials
        login_data = {
            'username': username,
            'password': password,
            'csrf_token': csrf_token
        }
        response = self.session.post(f'{self.base_url}/login', data=login_data)
        
        # Verify login succeeded
        return self.verify_login(response)
    
    def save_session(self):
        # Save cookies for resuming
        with open('session_cookies.json', 'w') as f:
            json.dump(self.session.cookies.get_dict(), f)
```

### 2. API Key Authentication (If Available)
```python
class APIBasedScraper:
    def __init__(self, api_key):
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/json'
        }
```

### 3. No Authentication (Public Forums)
```python
class PublicScraper:
    def __init__(self):
        self.session = requests.Session()
        # Basic headers sufficient
```

## Anti-Bot Protection Handling

### CloudFlare/WAF Detection
```python
def handle_cloudflare(response):
    if response.status_code == 403:
        if 'cloudflare' in response.text.lower():
            # Options:
            # 1. Use authenticated session
            # 2. Use cloudscraper library
            # 3. Use Selenium for JavaScript challenges
            # 4. Route through proxy
            return use_authenticated_session()
```

### Rate Limiting Best Practices
```python
class RateLimiter:
    def __init__(self, delay_seconds):
        self.delay = delay_seconds
        self.last_request = 0
    
    def wait(self):
        elapsed = time.time() - self.last_request
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self.last_request = time.time()
```

## Data Extraction Patterns

### Forums (Net54, PSA Forums)
```python
def extract_forum_data(html):
    soup = BeautifulSoup(html, 'lxml')
    
    # Forums typically have:
    # - Nested structure (Forum > Thread > Post)
    # - Pagination on multiple levels
    # - User-generated content (varied formatting)
    # - Attachments and embedded images
    
    return {
        'threads': extract_thread_list(soup),
        'posts': extract_posts(soup),
        'users': extract_user_info(soup),
        'attachments': extract_attachments(soup)
    }
```

### Auction Houses (Heritage, REA)
```python
def extract_auction_data(html):
    soup = BeautifulSoup(html, 'lxml')
    
    # Auctions typically have:
    # - Structured data (JSON-LD often embedded)
    # - Consistent lot numbering
    # - High-quality images
    # - Price/bid information
    
    # Look for structured data first
    json_ld = soup.find('script', type='application/ld+json')
    if json_ld:
        data = json.loads(json_ld.string)
    
    return {
        'lot_number': extract_lot_number(soup),
        'title': extract_title(soup),
        'description': extract_description(soup),
        'estimate': extract_estimate(soup),
        'realized_price': extract_price(soup),  # May require auth
        'images': extract_image_urls(soup),
        'provenance': extract_provenance(soup)
    }
```

### Marketplaces (PWCC, COMC)
```python
def extract_marketplace_data(html):
    # Marketplaces typically have:
    # - Dynamic pricing
    # - Inventory status
    # - Multiple sellers
    # - Search/filter capabilities
    
    return {
        'item_id': extract_item_id(soup),
        'price': extract_current_price(soup),
        'seller': extract_seller_info(soup),
        'condition': extract_condition(soup),
        'availability': extract_stock_status(soup)
    }
```

## Optimization Strategies

### 1. Use List/Search Pages First
```python
def optimized_scraping():
    # Get list pages with many items
    list_pages = scrape_all_list_pages()
    
    # Extract basic info and URLs
    all_items = parse_list_pages(list_pages)
    
    # Filter to items of interest
    target_items = filter_items(all_items, criteria)
    
    # Only fetch detail pages for targets
    for item in target_items:
        detail_page = fetch_with_delay(item['url'])
        full_data = extract_full_details(detail_page)
```

### 2. Parallel Processing (Carefully)
```python
from concurrent.futures import ThreadPoolExecutor
import threading

class ParallelScraper:
    def __init__(self, max_workers=3, delay_seconds=15):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.rate_limiter = threading.Lock()
        self.delay = delay_seconds
    
    def fetch_many(self, urls):
        # Ensure rate limiting across threads
        def fetch_one(url):
            with self.rate_limiter:
                time.sleep(self.delay)
                return fetch_page(url)
        
        futures = [self.executor.submit(fetch_one, url) for url in urls]
        return [f.result() for f in futures]
```

### 3. Incremental/Resume Capability
```python
class ResumableScraper:
    def __init__(self):
        self.progress_file = 'scraping_progress.json'
        self.completed = self.load_progress()
    
    def scrape_with_resume(self, items):
        for item in items:
            if item['id'] in self.completed:
                continue
            
            try:
                data = self.scrape_item(item)
                self.save_item(data)
                self.mark_complete(item['id'])
            except Exception as e:
                logger.error(f"Failed on {item['id']}: {e}")
                # Can resume from here later
```

## Storage Strategies

### 1. Hierarchical JSON (Current Approach)
```
data/
├── [archive_name]/
│   ├── metadata/
│   │   └── progress.json
│   ├── listings/        # List pages, search results
│   ├── items/          # Individual items/lots/threads
│   └── media/          # Images, attachments
```

### 2. Database for Relationships
```python
# Consider SQLite for complex relationships
import sqlite3

def init_database():
    conn = sqlite3.connect('archive.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id TEXT PRIMARY KEY,
            archive_name TEXT,
            category TEXT,
            title TEXT,
            description TEXT,
            price REAL,
            date TEXT,
            raw_data JSON
        )
    ''')
```

### 3. Compressed Storage for Old Data
```python
import gzip
import json

def compress_old_data(filepath, days_old=30):
    if is_older_than(filepath, days_old):
        with open(filepath, 'rb') as f_in:
            with gzip.open(f'{filepath}.gz', 'wb') as f_out:
                f_out.writelines(f_in)
        os.remove(filepath)
```

## Error Handling

### Robust Retry Logic
```python
def fetch_with_retry(url, max_retries=3, backoff_factor=2):
    for attempt in range(max_retries):
        try:
            response = session.get(url, timeout=30)
            if response.status_code == 200:
                return response
            elif response.status_code == 429:  # Rate limited
                wait_time = int(response.headers.get('Retry-After', 60))
                time.sleep(wait_time)
            else:
                response.raise_for_status()
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            wait_time = backoff_factor ** attempt
            logger.warning(f"Retry {attempt + 1} after {wait_time}s: {e}")
            time.sleep(wait_time)
```

## Testing Strategies

### 1. Start Small
- Test auth with single login
- Scrape 5-10 items first
- Verify data quality
- Check rate limiting

### 2. Monitor Performance
```python
class ScraperMetrics:
    def __init__(self):
        self.start_time = time.time()
        self.items_scraped = 0
        self.errors = 0
    
    def report(self):
        elapsed = time.time() - self.start_time
        rate = self.items_scraped / elapsed
        logger.info(f"Scraped {self.items_scraped} items in {elapsed:.1f}s")
        logger.info(f"Rate: {rate:.2f} items/second")
        logger.info(f"Errors: {self.errors}")
```

### 3. Data Validation
```python
def validate_scraped_data(data):
    required_fields = ['id', 'title', 'description']
    for field in required_fields:
        if field not in data or not data[field]:
            raise ValueError(f"Missing required field: {field}")
    
    # Type checking
    if 'price' in data and data['price']:
        try:
            float(data['price'])
        except ValueError:
            raise ValueError(f"Invalid price format: {data['price']}")
```

## Large-Scale Archive Planning

### Phase 1: Discovery and Indexing (1-2 months)
```python
class ArchiveIndexer:
    """Build comprehensive index before detailed scraping"""
    
    def __init__(self, archive_config):
        self.config = archive_config
        self.index_db = sqlite3.connect('archive_index.db')
        
    def index_archive(self):
        # 1. Scrape all list/search/catalog pages
        catalog_urls = self.discover_catalog_pages()
        
        # 2. Extract basic item info
        for url in catalog_urls:
            items = self.parse_catalog_page(url)
            self.save_to_index(items)
            
        # 3. Analyze and prioritize
        stats = self.analyze_index()
        return stats
```

### Phase 2: Prioritized Deep Scraping (2-6 months)
```python
class PrioritizedScraper:
    """Scrape high-value content first"""
    
    def __init__(self, index_db):
        self.index = index_db
        self.priority_queue = self.build_priority_queue()
        
    def build_priority_queue(self):
        # Prioritize by multiple factors
        query = """
        SELECT url, 
               CASE 
                   WHEN price > 1000 THEN 3
                   WHEN grade = 'PSA 10' THEN 3
                   WHEN player IN ('Ruth', 'Mantle', 'Wagner') THEN 3
                   WHEN year < 1950 THEN 2
                   ELSE 1
               END as priority
        FROM indexed_items
        ORDER BY priority DESC, price DESC
        """
        return self.index.execute(query).fetchall()
```

### Phase 3: Backfill and Maintenance (Ongoing)
```python
class MaintenanceScraper:
    """Keep archive updated with new content"""
    
    def __init__(self, archive_name):
        self.archive = archive_name
        self.last_update = self.get_last_update()
        
    def update_archive(self):
        # 1. Check for new auctions/posts
        new_content = self.find_new_content(since=self.last_update)
        
        # 2. Update existing items (price changes, etc)
        updated_items = self.find_updated_items()
        
        # 3. Scrape incrementally
        self.scrape_items(new_content + updated_items)
        
        # 4. Update timestamp
        self.last_update = datetime.now()
```

### Multi-Archive Orchestration
```python
class MultiArchiveManager:
    """Manage multiple archives efficiently"""
    
    def __init__(self, config_dir='configs/'):
        self.archives = self.load_all_configs(config_dir)
        self.scheduler = self.create_schedule()
        
    def create_schedule(self):
        # Balance scraping across archives
        schedule = []
        
        for archive in self.archives:
            if archive['type'] == 'auction':
                # Check daily for new auctions
                schedule.append({
                    'archive': archive['name'],
                    'frequency': 'daily',
                    'action': 'check_new_auctions'
                })
            elif archive['type'] == 'forum':
                # Check hourly for active forums
                schedule.append({
                    'archive': archive['name'],
                    'frequency': 'hourly',
                    'action': 'check_new_posts'
                })
                
        return schedule
    
    def run(self):
        while True:
            for task in self.scheduler.get_due_tasks():
                self.execute_task(task)
            time.sleep(300)  # Check every 5 minutes
```

### Distributed Scraping Architecture
```python
class DistributedScraper:
    """Scale across multiple machines/IPs"""
    
    def __init__(self, redis_url):
        self.redis = redis.from_url(redis_url)
        self.worker_id = uuid.uuid4()
        
    def get_next_job(self):
        # Pop from shared queue
        job = self.redis.lpop('scrape_queue')
        if job:
            return json.loads(job)
        return None
        
    def process_job(self, job):
        try:
            # Mark as processing
            self.redis.hset('processing', job['id'], self.worker_id)
            
            # Scrape with appropriate delays
            result = self.scrape_item(job['url'], job['config'])
            
            # Save result
            self.save_result(result)
            
            # Mark complete
            self.redis.hset('completed', job['id'], datetime.now())
            
        except Exception as e:
            # Return to queue for retry
            self.redis.rpush('scrape_queue', json.dumps(job))
            raise
```

### Archive Health Monitoring
```python
class ArchiveMonitor:
    """Track scraping health and progress"""
    
    def __init__(self):
        self.metrics = {
            'items_per_hour': [],
            'error_rate': 0,
            'blocked_requests': 0,
            'storage_used': 0
        }
        
    def report_dashboard(self):
        return f"""
        Archive Status Dashboard
        ========================
        Total Items: {self.total_items:,}
        Last 24h: {self.items_24h:,}
        Success Rate: {self.success_rate:.1%}
        Storage Used: {self.storage_gb:.1f} GB
        
        Per Archive:
        {self.per_archive_stats()}
        
        Alerts:
        {self.check_alerts()}
        """
```

### Resource Planning
```python
def estimate_resources(archives):
    """Calculate infrastructure needs"""
    
    estimates = {
        'storage_gb': 0,
        'bandwidth_gb_month': 0,
        'compute_hours': 0,
        'time_months': 0
    }
    
    for archive in archives:
        if archive['type'] == 'forum':
            estimates['storage_gb'] += archive['post_count'] * 0.00001  # 10KB per post
            estimates['bandwidth_gb_month'] += archive['post_count'] * 0.00002
            estimates['compute_hours'] += archive['post_count'] * 0.001  # 3.6s per post
            
        elif archive['type'] == 'auction':
            estimates['storage_gb'] += archive['lot_count'] * 0.001  # 1MB per lot with images
            estimates['bandwidth_gb_month'] += archive['lot_count'] * 0.002  
            estimates['compute_hours'] += archive['lot_count'] * 0.005  # 18s per lot
            
    estimates['time_months'] = estimates['compute_hours'] / (24 * 30)  # Sequential
    
    return estimates
```