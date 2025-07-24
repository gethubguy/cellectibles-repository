# Collectibles Repository Migration Guide

## Overview
This guide walks through transforming the Net54 scraper into the comprehensive `collectibles` repository that supports multiple data sources (checklists, forums, auction houses, content sites) without breaking the existing GitHub Actions workflow.

## Pre-Migration Checklist

### 1. Wait for Current Scraping to Complete
- [ ] Current GitHub Actions run has finished
- [ ] No uncommitted data in the repository
- [ ] Latest data has been pushed to GitHub

### 2. Backup Current Data
```bash
# Create a backup branch
git checkout -b backup-before-migration
git push origin backup-before-migration

# Create local backup
cp -r data/ data_backup_$(date +%Y%m%d)/
```

### 3. Document Current State
```bash
# Record current stats
python scripts/scraper.py --stats > migration_baseline.txt

# Note current GitHub Actions run ID
echo "Last successful run: $(date)" >> migration_baseline.txt
```

## Phase 1: Repository Rename and Structure

### Step 1.1: Rename Repository on GitHub
1. Go to Settings → Rename repository to `collectibles`
2. GitHub will handle redirects automatically
3. Update local git remote if needed

### Step 1.2: Create Comprehensive Directory Structure
```bash
# Create the unified structure for all collectibles data
mkdir -p checklists/{vintage,modern,custom}
mkdir -p archives/{forums/net54,auctions,content}
mkdir -p enrichment/{analysis,ml_outputs,market_data}
mkdir -p tools/{scrapers,processors,analyzers}
mkdir -p configs
mkdir -p tests

# Move existing Net54 data to new location (after scraping completes)
# mv data/* archives/forums/net54/
```

### Directory Structure Explanation:
```
collectibles/
├── checklists/        # Structured set data (your existing work)
│   ├── vintage/       # T206, N172, etc.
│   ├── modern/        # Post-1980 sets
│   └── custom/        # User-created lists
├── archives/          # All scraped content
│   ├── forums/        # Discussion forums
│   │   ├── net54/     # Current scraping target
│   │   └── psa/       # Future target
│   ├── auctions/      # Auction houses
│   │   ├── heritage/
│   │   ├── rea/
│   │   └── pwcc/
│   └── content/       # Article sites
│       ├── prewarcards/
│       └── oldcardboard/
├── enrichment/        # Derived insights
│   ├── analysis/      # Statistical analysis
│   ├── ml_outputs/    # AI-generated content
│   └── market_data/   # Price trends
└── tools/            # All code
    ├── scrapers/     # Data collection
    ├── processors/   # Data transformation
    └── analyzers/    # Data analysis
```

### Step 1.3: Update Paths for Current Operations
Update `scripts/storage.py` to use new paths:
```python
# Temporary compatibility - point to new location
self.base_dir = Path('./archives/forums/net54')
```

### Step 1.4: Create Base Scraper Classes
Create `tools/scrapers/base/base_scraper.py`:
```python
from abc import ABC, abstractmethod
import requests
from pathlib import Path

class BaseScraper(ABC):
    """Abstract base class for all scrapers"""
    
    def __init__(self, config_path):
        self.config = self.load_config(config_path)
        self.session = requests.Session()
        self.archive_name = self.config['archive']['name']
        
    @abstractmethod
    def scrape(self):
        """Main scraping method to be implemented by subclasses"""
        pass
        
    @abstractmethod
    def parse_item(self, html):
        """Parse a single item (thread, auction lot, etc.)"""
        pass
```

### Step 1.3: Create Configuration System
Create `configs/net54.yaml`:
```yaml
archive:
  name: net54
  type: forum
  base_url: https://www.net54baseball.com
  
scraping:
  delay_seconds: 5
  max_retries: 3
  timeout_seconds: 30
  
storage:
  base_path: archives/forums/net54
  structure:
    forums: processed/forums
    threads: processed/threads
    posts: processed/posts
    
features:
  use_tapatalk: true
  respect_robots_txt: true
```

## Phase 2: Create Compatibility Layer

### Step 2.1: Create Net54 Scraper Adapter
Create `scrapers/forums/net54_scraper.py`:
```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../scripts'))

from base.base_scraper import BaseScraper
from scraper import Net54Scraper as LegacyScraper
from parser import Net54Parser
from storage import DataStorage

class Net54Scraper(BaseScraper):
    """New Net54 scraper that wraps the legacy implementation"""
    
    def __init__(self, config_path='configs/net54.yaml'):
        super().__init__(config_path)
        # Use existing implementation
        self.legacy_scraper = LegacyScraper()
        
    def scrape(self, forum_id=None, thread_limit=None):
        """Maintain compatibility with existing interface"""
        return self.legacy_scraper.scrape_entire_forum(forum_id, thread_limit)
```

### Step 2.2: Create Wrapper Scripts
Create `scripts/scraper_wrapper.py`:
```python
#!/usr/bin/env python3
"""Wrapper to maintain backward compatibility during migration"""
import sys
import os

# Check if we should use new or old implementation
USE_NEW_STRUCTURE = os.getenv('USE_NEW_SCRAPERS', 'false').lower() == 'true'

if USE_NEW_STRUCTURE:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from scrapers.forums.net54_scraper import Net54Scraper
    
    # Instantiate and run with same interface
    scraper = Net54Scraper()
    # Pass through command line args
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--forum', type=int)
    parser.add_argument('--thread-limit', type=int)
    parser.add_argument('--stats', action='store_true')
    args = parser.parse_args()
    
    if args.stats:
        scraper.legacy_scraper.storage.show_stats()
    else:
        scraper.scrape(args.forum, args.thread_limit)
else:
    # Use existing implementation
    from scraper import main
    main()
```

## Phase 3: Data Migration Strategy

### Step 3.1: Create Archive-Specific Data Directories
```bash
# Don't move data yet, just prepare structure
mkdir -p archives/net54/data/{raw,processed,metadata}
mkdir -p archives/heritage/data/{raw,processed,metadata}
mkdir -p archives/robertedwards/data/{raw,processed,metadata}

# Create symlinks for backward compatibility (after scraping stops)
# ln -s $(pwd)/archives/net54/data $(pwd)/data
```

### Step 3.2: Update Storage Class for Multi-Archive
Create `scrapers/base/storage.py`:
```python
class MultiArchiveStorage:
    """Storage that supports multiple archives"""
    
    def __init__(self, archive_name, base_dir='archives'):
        self.archive_name = archive_name
        self.base_dir = Path(base_dir) / archive_name / 'data'
        # Rest similar to existing DataStorage
```

## Phase 4: GitHub Actions Migration

### Step 4.1: Create Test Workflow
Create `.github/workflows/test-new-structure.yml`:
```yaml
name: Test New Structure
on:
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Test new structure
      env:
        USE_NEW_SCRAPERS: true
      run: |
        pip install -r requirements.txt
        python scripts/scraper_wrapper.py --stats
```

### Step 4.2: Update Main Workflow (After Testing)
Modify `.github/workflows/scrape.yml` gradually:
```yaml
# Add environment variable to control which implementation
env:
  USE_NEW_SCRAPERS: ${{ github.event.inputs.use_new_structure || 'false' }}
```

## Phase 5: Add New Archive Sources

### Step 5.1: Create Heritage Auctions Scraper
Create `scrapers/auctions/heritage_scraper.py`:
```python
from scrapers.base.base_scraper import BaseScraper

class HeritageScraper(BaseScraper):
    """Scraper for Heritage Auctions"""
    
    def parse_item(self, html):
        # Parse auction lot
        pass
```

### Step 5.2: Create Configuration
Create `configs/heritage.yaml`:
```yaml
archive:
  name: heritage
  type: auction
  base_url: https://www.ha.com
  
scraping:
  delay_seconds: 10  # Be respectful
  categories:
    - sports-collectibles
    - trading-cards
```

## Implementation Timeline

### Week 1: Safe Preparations
1. **Day 1-2**: Create new directory structure and base classes
2. **Day 3-4**: Implement configuration system
3. **Day 5-7**: Create and test wrapper scripts locally

### Week 2: Compatibility Testing  
1. **Day 1-2**: Test wrapper scripts with existing data
2. **Day 3-4**: Create test GitHub Action workflow
3. **Day 5-7**: Run parallel tests (old vs new structure)

### Week 3: Migration
1. **Day 1**: Stop current scraping temporarily
2. **Day 2**: Move data to new structure with symlinks
3. **Day 3**: Update GitHub Actions to use new structure
4. **Day 4-5**: Monitor and fix any issues
5. **Day 6-7**: Remove compatibility layers

### Week 4: Expansion
1. **Day 1-3**: Add first new archive source
2. **Day 4-5**: Test multi-archive scraping
3. **Day 6-7**: Documentation and cleanup

## Rollback Procedures

### Quick Rollback (Phase 1-2)
```bash
# Just remove new directories
rm -rf scrapers/ configs/ archives/

# Continue using existing scripts/
```

### Full Rollback (Phase 3+)
```bash
# Restore from backup branch
git checkout backup-before-migration
git branch -D main
git checkout -b main
git push --force origin main

# Restore GitHub Actions
git checkout backup-before-migration -- .github/workflows/
```

## Testing Checklist

### Local Testing
- [ ] Wrapper scripts work with USE_NEW_SCRAPERS=false
- [ ] Wrapper scripts work with USE_NEW_SCRAPERS=true  
- [ ] Data saves to correct directories
- [ ] Progress tracking works across archives

### GitHub Actions Testing
- [ ] Test workflow runs successfully
- [ ] No data loss during migration
- [ ] Scheduled runs continue working
- [ ] Manual runs work with both structures

### Data Integrity
- [ ] All existing data accessible
- [ ] New data saves correctly
- [ ] Stats reporting works
- [ ] No duplicate scraping

## Common Issues & Solutions

### Issue: Import errors after migration
**Solution**: Check Python path in wrapper scripts
```python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
```

### Issue: GitHub Actions can't find data
**Solution**: Ensure symlinks are relative, not absolute
```bash
cd /path/to/repo
ln -s ../archives/net54/data data
```

### Issue: Permission errors in GitHub Actions  
**Solution**: Ensure directories are created before use
```yaml
- name: Create directories
  run: mkdir -p archives/net54/data/{raw,processed,metadata}
```

## Archive-Specific Considerations

### Authentication Testing
Before migrating, test authentication for each archive:
```bash
# Test Heritage login
python scripts/test_auth.py --archive heritage --username $HERITAGE_USER

# Test session persistence
python scripts/test_auth.py --archive heritage --resume-session
```

### Rate Limit Planning
Different archives have different limits:
- **Net54**: 1-2 seconds (forums are lenient)
- **Heritage**: 15 seconds (strict robots.txt)
- **REA**: Unknown (test carefully)
- **PWCC**: Unknown (likely 10-20 seconds)

### Storage Estimates
Based on our research:
- **Forum post**: ~5-10 KB each
- **Auction lot**: ~20-50 KB each (without images)
- **Images**: 100-500 KB each (auction houses have high-res)

Example storage needs:
- Net54 (2M posts): ~10-20 GB
- Heritage (100K lots/year): ~5-10 GB + 50-100 GB images
- Total for 5 archives: ~200-500 GB over time

### Testing Approach
1. **Start Small**: 10 items from each source
2. **Verify Data**: Check extraction quality
3. **Test Resume**: Interrupt and resume
4. **Monitor Rate**: Ensure compliance
5. **Scale Gradually**: 100, 1000, then full

## Post-Migration Checklist

- [ ] Remove old scripts/ directory (keep wrappers temporarily)
- [ ] Update README.md with new structure
- [ ] Update CLAUDE.md with multi-archive information
- [ ] Create documentation for adding new sources
- [ ] Set up monitoring for all archive sources
- [ ] Plan regular data backups

## Adding New Archive Sources

### Template for New Sources
1. Create scraper in `scrapers/[type]/[name]_scraper.py`
2. Create config in `configs/[name].yaml`
3. Add to GitHub Actions workflow
4. Test locally first
5. Add documentation

### Example: Adding PSA Forums
```bash
# 1. Create scraper
touch scrapers/forums/psa_scraper.py

# 2. Create config  
touch configs/psa.yaml

# 3. Test locally
USE_NEW_SCRAPERS=true python scripts/scraper_wrapper.py --archive psa

# 4. Add to workflow
# Update .github/workflows/scrape.yml
```

---

**Remember**: The key to successful migration is maintaining backward compatibility until you're confident in the new structure. Take it slow, test thoroughly, and always have a rollback plan.