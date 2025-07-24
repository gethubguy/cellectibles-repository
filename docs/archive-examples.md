# Archive Source Configuration Examples

## Forum Archives

### Net54 Baseball (Current)
```yaml
# configs/net54.yaml
archive:
  name: net54
  type: forum
  display_name: "Net54 Baseball Forum"
  base_url: https://www.net54baseball.com
  description: "Vintage baseball card collecting community"
  
scraping:
  delay_seconds: 5
  max_retries: 3
  timeout_seconds: 30
  user_agent: "Net54Archive/1.0"
  
api:
  use_tapatalk: true
  tapatalk_key: "${TAPATALK_API_KEY}"
  
storage:
  structure:
    forums: processed/forums
    threads: processed/threads  
    posts: processed/posts
    
features:
  scrape_attachments: true
  preserve_formatting: true
  track_edits: false
```

### PSA Card Forums
```yaml
# configs/psacard.yaml
archive:
  name: psacard
  type: forum
  display_name: "PSA Card Forums"
  base_url: https://forums.collectors.com
  
scraping:
  delay_seconds: 8
  categories:
    - vintage-baseball
    - grading-questions
    - registry-talk
    
authentication:
  required: false
  
storage:
  compress_old_data: true
  retention_days: 0  # Keep forever
```

### Blowout Cards Forums
```yaml
# configs/blowout.yaml
archive:
  name: blowout
  type: forum
  display_name: "Blowout Cards Forums"
  base_url: https://www.blowoutforums.com
  
scraping:
  delay_seconds: 10
  respect_robots_txt: true
  categories:
    - baseball
    - vintage-trading
```

## Auction House Archives

### Heritage Auctions
```yaml
# configs/heritage.yaml
archive:
  name: heritage
  type: auction
  display_name: "Heritage Auctions"
  base_url: https://www.ha.com
  
scraping:
  delay_seconds: 15  # Required by robots.txt
  max_retries: 3
  timeout_seconds: 30
  departments:
    - sports-collectibles
    - trading-cards/baseball
  
authentication:
  required: true  # For price data
  method: session  # Form-based login
  login_url: /login
  credentials_env: 
    username: HERITAGE_USERNAME
    password: HERITAGE_PASSWORD
  
anti_bot:
  protection: cloudflare
  solution: authenticated_session
  
data_extraction:
  fields:
    - lot_number      # e.g., 81828
    - sale_number     # e.g., 50078
    - title           # Clean, includes grade
    - description     # 500+ words typically
    - estimate        # May be hidden
    - realized_price  # Requires login
    - auction_date    # From sale info
    - images          # Multiple high-res
    - condition_notes # PSA/BGS grades
    - provenance      # "From X collection"
    - population      # PSA pop data
    
features:
  download_images: true
  image_quality: medium  # low, medium, high
  track_bidders: false  # Privacy
  use_list_pages: true  # Optimize with catalog pages
  
optimization:
  start_with_list_pages: true
  items_per_list_page: 50
  parallel_sessions: 2  # Different IPs recommended
  
api:
  available: false  # No public API found
  requires_key: false
  mobile_app_api: possible  # Could reverse engineer
```

### Robert Edward Auctions (REA)
```yaml
# configs/rea.yaml
archive:
  name: rea
  type: auction
  display_name: "Robert Edward Auctions"
  base_urls:
    main: https://robertedwardauctions.com  # Redirects to collectrea
    archives: https://collectrea.com
    bidding: https://bid.collectrea.com
  
scraping:
  delay_seconds: 20  # Conservative due to strict robots.txt
  respect_robots_txt: true  # Complete disallow, be careful
  auction_types:
    - spring
    - summer
    - fall
    - winter
    - encore  # Monthly auctions
    
authentication:
  required: false  # Archives are public!
  bidding_only: true
  
anti_bot:
  robots_txt: "Disallow: /"  # Very restrictive
  solution: respect_delays
    
data_extraction:
  archives:  # collectrea.com/archives
    - lot_number
    - title
    - sale_price      # Publicly visible!
    - category
    - subcategory
    - grading_info    # PSA, SGC, etc.
    - year_sold
    - item_year
    - images
  marketplace:  # bid.collectrea.com/marketplace
    - mp_number       # Marketplace ID
    - buy_now_price
    - status          # SOLD, available, etc.
    
url_patterns:
  archive_lot: "/archives/{year}/{season}/{lot_number}/{slug}"
  marketplace: "/marketplace/{mp_number}"
  
search:
  max_per_page: 100
  categories: 40+   # Baseball, basketball, etc.
  sort_options:
    - price
    - sale_date
    - relevance
    
optimization:
  use_search_pages: true  # 12-100 items per page
  public_prices: true     # Major advantage!
  
storage:
  group_by: auction_season
  archive_completed: true
```

### PWCC Marketplace
```yaml
# configs/pwcc.yaml
archive:
  name: pwcc
  type: marketplace
  display_name: "PWCC Marketplace"
  base_url: https://www.pwccmarketplace.com
  
scraping:
  delay_seconds: 10
  sections:
    - fixed-price
    - auctions
    - vault
    
data_extraction:
  fixed_price:
    - item_id
    - title
    - price
    - make_offer_available
    - seller_info
  auctions:
    - lot_number
    - current_bid
    - bid_count
    - time_remaining
    
features:
  track_price_history: true
  monitor_vault_items: true
```

## Specialized Archives

### Vintage Card Prices Database
```yaml
# configs/vintagecardprices.yaml
archive:
  name: vcp
  type: price_guide
  display_name: "VintageCardPrices"
  base_url: https://www.vintagecardprices.com
  
scraping:
  delay_seconds: 20  # Very respectful
  rate_limit: 100_per_hour
  
data_extraction:
  - card_id
  - year
  - brand
  - player
  - card_number
  - variations
  - price_history
  - recent_sales
  - population_data
  
features:
  build_price_index: true
  track_trends: true
```

### Baseball Card Exchange (BBCE)
```yaml
# configs/bbce.yaml
archive:
  name: bbce
  type: dealer
  display_name: "Baseball Card Exchange"
  base_url: https://www.bbcexchange.com
  
scraping:
  delay_seconds: 15
  categories:
    - unopened
    - graded-cards
    - authenticated-packs
    
data_extraction:
  - product_id
  - title
  - price
  - quantity_available
  - description
  - authentication_details
  
features:
  monitor_inventory: true
  alert_new_items: false
```

## Configuration Schema Reference

### Common Fields (All Types)
```yaml
archive:
  name: string          # Unique identifier
  type: enum           # forum, auction, marketplace, price_guide, dealer
  display_name: string  # Human-readable name
  base_url: string     # Starting URL
  description: string  # Optional description

scraping:
  delay_seconds: number     # Delay between requests
  max_retries: number      # Retry failed requests
  timeout_seconds: number  # Request timeout
  user_agent: string      # Custom user agent
  rate_limit: string     # e.g., "100_per_hour"
  respect_robots_txt: boolean

storage:
  base_path: string        # Override default path
  compress_old_data: boolean
  retention_days: number   # 0 = forever
  
authentication:
  required: boolean
  method: string          # basic, oauth, api_key
  credentials_env: string # Environment variable name
```

### Forum-Specific Fields
```yaml
features:
  scrape_attachments: boolean
  preserve_formatting: boolean
  track_edits: boolean
  follow_redirects: boolean
  scrape_private_messages: boolean  # If authenticated

api:
  use_tapatalk: boolean
  tapatalk_key: string
```

### Auction-Specific Fields
```yaml
data_extraction:
  track_bidding_history: boolean
  download_condition_reports: boolean
  extract_provenance: boolean
  
features:
  monitor_live_auctions: boolean
  archive_completed: boolean
  alert_keywords: array  # ["T206", "Mantle", "PSA 10"]
```

### Marketplace-Specific Fields
```yaml
monitoring:
  check_frequency: string  # "hourly", "daily"
  track_price_changes: boolean
  inventory_snapshots: boolean
```

## Content Sites

### PrewarCards
```yaml
# configs/prewarcards.yaml
archive:
  name: prewarcards
  type: content
  display_name: "Pre-War Cards"
  base_url: https://prewarcards.com
  description: "Expert analysis of pre-1948 sports cards"
  
scraping:
  delay_seconds: 2  # Courtesy only - no restrictions
  respect_robots_txt: true  # They allow everything
  
api:
  wordpress_rest: true
  base_path: /wp-json/wp/v2/
  endpoints:
    - posts
    - categories
    - tags
    - media
    
data_extraction:
  article_fields:
    - title
    - content  # Full HTML
    - excerpt
    - date
    - categories
    - tags
    - featured_media
  parsing_targets:
    - variations  # Extract variation descriptions
    - errors      # Document known errors
    - prices      # Historical price mentions
    - population  # PSA/SGC pop data
    
features:
  download_images: true
  parse_structured_data: true
  extract_checklists: true  # From article content
  
optimization:
  use_api_first: true
  batch_size: 100  # WP API pagination
  no_delays_needed: true
  
storage:
  group_by: category  # baseball, basketball, etc.
  format: markdown  # Convert HTML for analysis
```

## Environment Variables

Create `.env` file for sensitive data:
```bash
# API Keys
TAPATALK_API_KEY=your_key_here
HERITAGE_API_KEY=your_key_here
PWCC_API_KEY=your_key_here

# Authentication
PSA_FORUM_USERNAME=username
PSA_FORUM_PASSWORD=password

# Notifications
DISCORD_WEBHOOK=https://discord.com/api/webhooks/...
EMAIL_ALERTS=admin@example.com

# Storage
ARCHIVE_BASE_PATH=/data/archives
USE_S3_BACKUP=true
AWS_BUCKET_NAME=card-archives
```

## Adding a New Archive Source

1. **Create Configuration**:
```bash
cp configs/template.yaml configs/newsource.yaml
# Edit with your specific settings
```

2. **Test Configuration**:
```python
# scripts/test_config.py
import yaml

with open('configs/newsource.yaml') as f:
    config = yaml.safe_load(f)
    print(f"Archive: {config['archive']['name']}")
    print(f"Type: {config['archive']['type']}")
```

3. **Create Scraper**:
```python
# scrapers/[type]/newsource_scraper.py
from scrapers.base.base_scraper import BaseScraper

class NewSourceScraper(BaseScraper):
    def __init__(self):
        super().__init__('configs/newsource.yaml')
```

4. **Register in Main Script**:
```python
# scrapers/registry.py
SCRAPERS = {
    'net54': 'scrapers.forums.net54_scraper.Net54Scraper',
    'heritage': 'scrapers.auctions.heritage_scraper.HeritageScraper',
    'newsource': 'scrapers.[type].newsource_scraper.NewSourceScraper',
}
```