# Web Scraping Ethics and Compliance Guide

## Understanding robots.txt

The `robots.txt` file is a website's way of communicating with automated systems. Respecting it is both ethical and practical.

### Levels of Restriction

#### 1. Permissive with Delays
```
User-agent: *
Crawl-delay: 5
```
**Example**: Net54 (5 seconds)
**Approach**: Follow stated delays exactly

#### 2. Restrictive with Specific Rules
```
User-agent: *
Crawl-delay: 15
Disallow: /private/
Disallow: /admin/
```
**Example**: Heritage Auctions (15 seconds, many blocked paths)
**Approach**: Respect delays, avoid blocked paths, consider authentication

#### 3. Complete Disallow
```
User-agent: *
Disallow: /
```
**Example**: REA (Robert Edward Auctions)
**Approach**: This is the strongest "no" signal - see ethics section below

## Ethical Approaches by Restriction Level

### For Permissive Sites
- Follow stated delays precisely
- Use reasonable request headers
- Don't overwhelm the server
- Cache responses to avoid duplicate requests

### For Restrictive Sites
- Add buffer to stated delays (e.g., 15s → 18-20s)
- Authenticate if it provides better access
- Focus on allowed paths only
- Consider reaching out for clarification

### For Complete Disallow Sites
**Options in order of preference:**

1. **Contact First** (Recommended)
   ```
   Subject: Data Access Request for Research/Archive Project
   
   Hello [Company],
   
   I'm working on a historical archive project to preserve [specific content].
   I noticed your robots.txt disallows automated access. 
   
   Would you be open to:
   - Providing API access?
   - Allowing limited scraping with specific conditions?
   - Sharing historical data directly?
   
   I'm happy to discuss rate limits, attribution, or any concerns.
   ```

2. **Manual Collection**
   - Use browser automation that mimics human behavior
   - Selenium/Playwright with realistic delays
   - Random mouse movements and scrolling
   - Take breaks between sessions

3. **Extreme Caution Approach**
   If you must proceed:
   - 30-60 second delays (2-3x normal)
   - Random delay ranges (e.g., 30-45 seconds)
   - Single connection only
   - Session breaks every 50-100 requests
   - Stop immediately if blocked

4. **Respect Their Wishes**
   - Sometimes the ethical choice is not to scrape
   - Look for alternative data sources
   - Consider purchasing data if available

## Legal vs Ethical Considerations

### Legal
- robots.txt is not legally binding in most jurisdictions
- Public data is generally legal to access
- Terms of Service may have legal weight
- CFAA (in US) criminalizes "unauthorized access"

### Ethical
- robots.txt represents the site owner's wishes
- Excessive scraping can impact server costs
- Some sites rely on ad revenue you're bypassing
- Consider the purpose and sustainability of the site

## Best Practices

### Before Scraping
1. **Check robots.txt**: `https://site.com/robots.txt`
2. **Read Terms of Service**: Look for data use policies
3. **Search for APIs**: Many sites offer official data access
4. **Consider alternatives**: 
   - Common Crawl
   - Internet Archive
   - Official data dumps
   - Partner programs

### During Scraping
1. **Identify yourself**:
   ```python
   headers = {
       'User-Agent': 'ArchiveBot/1.0 (+https://myproject.com/bot)'
   }
   ```

2. **Implement exponential backoff**:
   ```python
   def fetch_with_backoff(url, max_retries=3):
       for attempt in range(max_retries):
           try:
               response = session.get(url)
               if response.status_code == 429:  # Rate limited
                   wait_time = (2 ** attempt) * 30  # 30, 60, 120 seconds
                   time.sleep(wait_time)
                   continue
               return response
           except Exception as e:
               if attempt == max_retries - 1:
                   raise
   ```

3. **Respect rate limits**:
   - 429 status = slow down
   - 403/401 = stop and reconsider
   - Server errors = back off exponentially

### After Scraping
1. **Attribute properly**: Credit the source
2. **Don't republish**: Respect copyright
3. **Update periodically**: Don't hammer for updates
4. **Share findings**: Contribute back when possible

## Template: Requesting Official Access

```
Subject: Academic/Research Data Access Request

Dear [Website] Data Team,

I am [your role] working on [project description]. Our goal is to [specific purpose].

We're interested in accessing historical data from your platform, specifically:
- [Type of data needed]
- [Time period]
- [Estimated volume]

We've reviewed your robots.txt file and want to respect your policies. Would you consider:

1. Providing API access with appropriate rate limits?
2. Sharing historical data dumps?
3. Allowing scraping under specific conditions?

We're happy to:
- Sign data use agreements
- Provide attribution
- Share our research findings
- Comply with any rate limits
- Pay reasonable fees if applicable

Thank you for considering this request. We value your platform and want to ensure our research respects your operations.

Best regards,
[Your name]
```

## Red Flags to Stop Immediately

- Repeated 403/401 errors
- CAPTCHA challenges
- IP blocks
- Legal notices
- Degraded site performance
- Changes to robots.txt targeting you

## Alternative Data Sources

Before scraping, always check:

1. **Official APIs**: Many sites offer them (sometimes paid)
2. **Data dumps**: Wikipedia, Reddit, others provide archives
3. **Common Crawl**: Free web crawl data
4. **Internet Archive**: Historical snapshots
5. **Academic datasets**: Many researchers share data
6. **Commercial providers**: Sometimes worth the cost

Remember: The goal is to preserve and analyze data, not to harm the platforms that host it. When in doubt, err on the side of caution and communication.