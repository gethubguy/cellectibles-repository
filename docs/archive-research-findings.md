# Archive Research Findings

## Heritage Auctions (ha.com)

### Access Requirements
- **Public Access**: Limited, returns 403 errors for automated requests
- **CloudFlare Protection**: Active anti-bot measures
- **Authenticated Access**: Full access when logged in with user account
- **robots.txt**: Requires 15-second crawl delay

### Data Structure Analysis
Based on saved HTML sample (George Gibson PSA VG-3 card):

#### Key Data Points Available
```javascript
{
  "isLoggedIn": 1,
  "isClosedLot": 1,
  "showLotPriceLogin": false,  // Price visible when logged in!
  "saleNo": 50078,
  "lotNo": 81828
}
```

#### Extractable Information
1. **Lot Identification**
   - Sale Number (e.g., 50078)
   - Lot Number (e.g., 81828)
   - URL pattern: `/itm/category/subcategory/title/a/[saleNo]-[lotNo].s`

2. **Item Details**
   - Title: Clean, descriptive (e.g., "1910 Novelty Cutlery George Gibson PSA VG 3")
   - Full description: 500+ words with historical context
   - Grading info: Embedded in title and description
   - Population data: "Only five PSA graded examples"
   - Provenance: "From the John Esch collection"

3. **Pricing Data** (when logged in)
   - Sold price: Encoded but readable (e.g., `&#36;&#49;&#44;&#48;&#51;&#55;&#46;&#48;&#48;` = $1,037.00)
   - Includes Buyer's Premium
   - Bid source (Internet bidder, floor, etc.)

4. **Images**
   - Multiple high-res images in carousel
   - Direct URLs to image server
   - Structured image data array

### Authentication Strategy
```python
# Proven approach for session-based auth
class HeritageAuthScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0...',
            'Accept': 'text/html,application/xhtml+xml...'
        })
    
    def login(self, username, password):
        # 1. GET login page for CSRF token
        # 2. POST credentials
        # 3. Maintain session cookies
```

### Time Estimates
- **Per lot page**: 15-18 seconds (mostly due to required delay)
- **Data extraction**: <100ms (very fast with BeautifulSoup)
- **Full auction (5,000 lots)**: ~21 hours
- **Optimized (using list pages)**: 2-4 hours for 500-1000 baseball lots

### Optimization Opportunities
1. **List Pages First**: Catalog pages show many items at once
2. **Selective Fetching**: Only get detailed pages for baseball items
3. **Parallel Sessions**: Use 2-3 authenticated sessions from different IPs
4. **Category Filtering**: Focus on specific departments/categories

### Technical Considerations
- Clean JSON data embedded in HTML
- Consistent URL structure
- Well-organized auction/lot numbering
- Price data requires login but no special permissions

## REA (Robert Edward Auctions)

### Site Structure
REA operates across multiple domains:
- **bid.collectrea.com** - Live auctions and marketplace
- **collectrea.com** - Archives and search functionality
- **robertedwardauctions.com** - Redirects to collectrea.com

### Access Requirements
- **robots.txt**: Complete block (`Disallow: /`) - very restrictive
- **Public Access**: Archives fully browsable without login
- **Authentication**: Required only for bidding, not browsing
- **Anti-bot**: Unknown, but robots.txt suggests strong protection

### Archive Structure (collectrea.com/archives)
- **Volume**: 1,000+ archived lots publicly searchable
- **Time Range**: 2004-2025 (20+ years of auctions)
- **Categories**: 40+ including baseball, basketball, hockey, memorabilia

#### Data Available per Lot:
- Lot number and title
- High-resolution images
- Sale price (publicly visible!)
- Category and subcategory
- Grading information (PSA, SGC, etc.)
- Year sold
- Item year/era

#### URL Pattern:
```
/archives/[YEAR]/[SEASON]/[LOT-NUMBER]/[ITEM-DESCRIPTION]
Example: /archives/2023/Fall/1/extremely-rare-1914-baltimore-news-babe-ruth-rookie-sgc-vg-3
```

### Marketplace (bid.collectrea.com/marketplace)
- **Format**: Buy It Now fixed prices
- **Volume**: 945+ items (79 pages)
- **Identifier**: MP# (Marketplace number)
- **URL Pattern**: `/marketplace/{MP#}`

### Search Capabilities
- Filter by category (40+ options)
- Filter by year sold
- Filter by item year
- Sort by price, date, relevance
- Pagination (12/25/50/100 per page)

### Auction Schedule
- Major seasonal auctions (Spring, Summer, Fall, Winter)
- Monthly "Encore" auctions
- Countdown timers for upcoming auctions

### Technical Implementation
- **Framework**: Laravel/Livewire (dynamic content)
- **Analytics**: Google Tag Manager
- **UI**: Swiper.js for catalog browsing
- **No visible API**: All server-rendered

### Scraping Considerations
1. **Strict robots.txt**: Complete disallow requires careful approach
2. **Public archive**: Prices visible without login (major advantage!)
3. **Clean URLs**: Semantic, descriptive paths
4. **Structured data**: Consistent layout across lots
5. **Rate limiting**: Unknown, but assume conservative (10-20 seconds)

### Optimization Strategy
1. Start with archive search pages (12-100 items per page)
2. Extract lot URLs and basic info
3. Only fetch detailed pages for specific categories
4. No authentication needed for historical data
5. Respect robots.txt with long delays

### Time Estimates (Full Archive)
- **Per lot**: 25-30 seconds (includes 20-30s delay for strict robots.txt)
- **Per auction**: 1,000-3,000 lots = ~17-21 hours
- **Full archive**: ~260,000 lots over 20 years = ~75 days continuous

#### Realistic Approach:
1. **Index Phase**: 2-3 days to scrape all list pages
2. **Selective Detail**: 1-2 weeks for high-value items only
3. **Complete Archive**: 2-3 months with breaks and respectful pacing

### Scraping Ethics Considerations
- **robots.txt = "Disallow: /"**: Strongest possible "no scraping" signal
- **Options**:
  1. Contact REA directly for permission/API access (recommended)
  2. Manual browser automation (mimics human clicking)
  3. Proceed with extreme caution (30+ second delays, breaks)
  4. Skip REA entirely (respect their wishes)
- **If proceeding**: Use random delays (25-35s), session breaks, single connection

## Brockelman Auctions

### Access Requirements
- **Public Access**: Complete block - 403 errors on all requests
- **robots.txt**: Also returns 403 (extremely restrictive)
- **Anti-bot Protection**: Stronger than Heritage or REA
- **Alternative Access**: Data available through WorthPoint partnership

### Site Structure
- **Base URL**: brockelmanauctions.com
- **Technology**: ASP.NET (.aspx pages, circa 2015)
- **Current Auction**: /catalog.aspx
- **Archive/Results**: /auctionresults.aspx
- **Auction Format**: Periodic auctions with set end dates

### Company Background
- "An auction company by collectors, for collectors"
- Founded by Scott Brockelman (collector since 1990s)
- Handles rare and expensive cards
- Contributor to major hobby publications

### Data Partnership Model
- **WorthPoint Integration**: 10,460+ sales results available
- **Commercial Strategy**: Monetizes data through partnerships
- **Implication**: Direct scraping likely discouraged in favor of API access

### Scraping Considerations
1. **Extreme Protection**: Even stronger than REA's complete disallow
2. **No Direct Access**: All requests return 403 immediately
3. **Partnership Required**: Likely need commercial agreement
4. **Alternative Sources**: 
   - WorthPoint API (if available)
   - Direct contact for data access
   - Manual collection only

### Recommended Approach
1. **Contact Directly**: Explain value proposition
2. **Explore WorthPoint**: May have API for partners
3. **Skip if Necessary**: Most restrictive site encountered
4. **Monitor Changes**: Small auction houses may update policies

## PrewarCards.com

### Access Requirements
- **Public Access**: Completely open - no restrictions
- **robots.txt**: Explicitly allows all crawlers
- **Authentication**: None required
- **Anti-bot Protection**: None detected

### Site Structure
- **Platform**: WordPress blog
- **URL Pattern**: /YYYY/MM/DD/[article-slug]/
- **Content Type**: Long-form articles (2000-5000 words)
- **API Access**: WordPress REST API likely at /wp-json/

### Technical Details
```
robots.txt:
User-agent: *
Disallow:
Sitemap: https://prewarcards.com/sitemap.xml
```

### Content Value
- **Article Count**: Estimated 500-1000 posts
- **Focus**: Pre-1948 sports cards (baseball, basketball, etc.)
- **Unique Data**:
  - Detailed variation documentation
  - Print error analysis
  - Market valuations and trends
  - Discovery narratives
  - Cross-set comparisons

### Example Content Structure
From T205 article analysis:
- 25-point listicle format
- Embedded historical context
- Specific variation details
- Population data
- Market insights

### Scraping Approach
1. **WordPress API Method**:
   ```python
   base_url = "https://prewarcards.com/wp-json/wp/v2/"
   endpoints = ["posts", "categories", "tags", "media"]
   ```

2. **Traditional Scraping**:
   - Parse sitemap.xml
   - Extract article URLs
   - BeautifulSoup for content parsing

### Time Estimates
- **Full site**: 1-2 days (no delays required)
- **Baseball content only**: 8-12 hours
- **High-value articles**: 2-4 hours

### Technical Advantages
- No rate limiting needed (but 1-2s courtesy delay recommended)
- Well-structured HTML
- SEO-optimized content
- Standard WordPress patterns

### Strategic Value
- **Complements checklists**: Adds context to raw data
- **Variation expertise**: Documents errors/variants in detail
- **Market intelligence**: Historical pricing and trends
- **Content enrichment**: Perfect for AI-generated descriptions

## PWCC Marketplace
*Research pending*

## PSA Forums (collectors.com)
*Research pending*

## General Findings

### Anti-Bot Protection Patterns
1. **CloudFlare**: Common on commercial sites
2. **Solution**: Authenticated sessions bypass most protection
3. **Headers**: Proper browser headers essential
4. **Delays**: Respect robots.txt requirements

### Data Availability
1. **Public**: Basic information, images, descriptions
2. **Authenticated**: Prices, bid history, complete data
3. **API Access**: Generally not public, need partnerships

### Scaling Considerations
1. **Rate Limits**: 15-30 seconds typical for auction sites
2. **Data Volume**: Auction sites have less content than forums
3. **Structure**: More consistent than forums, easier to parse
4. **Storage**: Images can be large, consider selective downloading