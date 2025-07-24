# Archive Sources Summary

## Quick Reference Table

| Archive | Type | Access | Auth | Delay | robots.txt | Data Value | Priority |
|---------|------|--------|------|-------|------------|------------|----------|
| **Net54** | Forum | Open | No | 5s | Allowed | Forum wisdom | HIGH (active) |
| **Heritage** | Auction | CloudFlare | Yes | 15s | Restricted | Prices w/login | HIGH |
| **REA** | Auction | Open Archive | No | 20-30s | Disallow all | Public prices! | MEDIUM |
| **Brockelman** | Auction | Blocked | N/A | N/A | 403 all | Via WorthPoint | SKIP |
| **PrewarCards** | Content | Open | No | 0-2s | Allow all | Variations/context | HIGH |
| **OldCardboard** | Reference | Open | No | 0s | None | Basic checklists | LOW |
| **PWCC** | Market | Unknown | TBD | TBD | TBD | Current prices | TBD |
| **PSA Forums** | Forum | Unknown | TBD | TBD | TBD | Grading wisdom | TBD |

## Scraping Order Recommendation

### Phase 1: Low-Hanging Fruit
1. **PrewarCards.com** - Completely open, high value content (1-2 days)
2. **Net54** - Already running, continue via GitHub Actions

### Phase 2: Authentication Required
3. **Heritage** - Login for prices, good data structure (2-4 weeks)
4. **REA Archives** - Public prices but strict robots.txt (1-2 months)

### Phase 3: Evaluate
5. **PWCC/PSA** - Need more research
6. **OldCardboard** - Low priority, basic data

### Skip
- **Brockelman** - Too restrictive, use WorthPoint instead

## Key Technical Patterns

### Open Sites (PrewarCards, OldCardboard)
- Direct scraping OK
- Minimal delays
- Focus on content quality

### Protected Auctions (Heritage, REA)
- Session management crucial
- Respect delays strictly
- Consider official contact

### Blocked Sites (Brockelman)
- Partner APIs only
- Manual collection
- Alternative sources

## Resource Allocation

- **GitHub Actions**: Net54 (continuous)
- **Local Fast**: PrewarCards, OldCardboard
- **Local Careful**: Heritage, REA
- **Manual/API**: Brockelman via WorthPoint