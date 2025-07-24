# Testing Guide for Collectibles Migration

## Overview
This guide walks through testing the new collectibles structure before fully migrating. All tests are non-destructive and maintain backward compatibility.

## Phase 1: Local Testing 🖥️

### Prerequisites
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Current data is backed up or committed
- No active scraping jobs running

### Test 1: Verify Setup
```bash
# Check all components are in place
python3 verify_setup.py
```

Expected output: All green checkmarks ✅

### Test 2: Import Tests
```bash
# Test new imports work
python3 -c "from tools.scrapers.base import BaseScraper; print('✅ Base imports work')"
python3 -c "import yaml; print('✅ PyYAML available')"
```

### Test 3: Configuration Loading
```bash
# Test configuration system
python3 -c "
import yaml
with open('configs/net54.yaml') as f:
    config = yaml.safe_load(f)
    print(f'✅ Config loaded: {config[\"archive\"][\"name\"]}')
"
```

### Test 4: Storage System
```bash
# Test multi-archive storage
python3 -c "
from tools.scrapers.base.storage import MultiArchiveStorage
storage = MultiArchiveStorage('net54', 'archives')
print('✅ Storage initialized')
print(f'   Archive: {storage.archive_name}')
print(f'   Path: {storage.archive_dir}')
"
```

### Test 5: Wrapper Script (Dry Run)
```bash
# Test wrapper with old structure (should work normally)
USE_NEW_SCRAPERS=false python3 scripts/scraper_wrapper.py --stats

# Test wrapper with new structure (may show no data initially)
USE_NEW_SCRAPERS=true python3 scripts/scraper_wrapper.py --stats
```

### Test 6: Data Migration (Dry Run)
```bash
# See what would be migrated without making changes
python3 scripts/migrate_data.py --dry-run
```

## Phase 2: GitHub Actions Testing 🚀

### Step 1: Run Stats Test
1. Go to your repository on GitHub
2. Navigate to Actions → "Test New Structure"
3. Click "Run workflow"
4. Select:
   - Branch: `main` (or your current branch)
   - Test type: `stats`
5. Click "Run workflow"

**What to check:**
- ✅ Workflow completes without errors
- ✅ No import errors in logs
- ✅ Stats display (may show 0 if no data migrated yet)

### Step 2: Run Small Scrape Test
1. Run workflow again with:
   - Test type: `scrape-small`
2. This will attempt to scrape 1 thread with new structure

**What to check:**
- ✅ Scraping starts successfully
- ✅ Rate limiting works (5 second delays)
- ✅ Data saves to new location
- ✅ No permission errors

### Step 3: Compare Structures
1. Run workflow with:
   - Test type: `compare-structures`
2. This shows directory creation and structure

**What to check:**
- ✅ New directories created properly
- ✅ Old data directory still intact
- ✅ Archive structure matches design

## Phase 3: Production Testing 🏭

### Test 1: Manual Trigger with Toggle
1. Go to Actions → "Scrape Net54 Forum" (main workflow)
2. If using `scrape_updated.yml`:
   - Set `use_new_structure: false` (test old)
   - Run and verify normal operation
   - Set `use_new_structure: true` (test new)
   - Run and verify new structure works

### Test 2: Data Integrity Check
After any test scrape:
```bash
# Check old structure (if not migrated)
ls -la data/processed/forums/
ls -la data/metadata/

# Check new structure
ls -la archives/forums/net54/data/processed/
ls -la archives/forums/net54/data/metadata/
```

### Test 3: CLI Tool Test
```bash
# List archives
python3 collectibles.py list

# Show stats
python3 collectibles.py stats

# Verify setup
python3 collectibles.py verify
```

## Common Issues & Solutions 🔧

### Issue: Import Errors
```
ModuleNotFoundError: No module named 'tqdm'
```
**Solution:** Install dependencies in GitHub Actions or locally:
```bash
pip install -r requirements.txt
```

### Issue: Permission Denied
```
Permission denied: './data'
```
**Solution:** Ensure directories are created with proper permissions:
```bash
chmod -R 755 archives/
chmod +x scripts/*.py
```

### Issue: Config Not Found
```
FileNotFoundError: configs/net54.yaml
```
**Solution:** Ensure you're running from project root:
```bash
cd /path/to/net54
python3 scripts/scraper_wrapper.py
```

### Issue: Symlink Errors (Windows)
```
OSError: symbolic link privilege not held
```
**Solution:** Run migration without symlinks:
```bash
python3 scripts/migrate_data.py --no-symlink
```

## Test Checklist ✓

### Local Tests
- [ ] Setup verification passes
- [ ] All imports work
- [ ] Config files load
- [ ] Storage initializes
- [ ] Wrapper script runs with both modes
- [ ] Migration dry run shows correct plan

### GitHub Actions Tests
- [ ] Stats test passes
- [ ] Small scrape test passes
- [ ] Directory structure correct
- [ ] No permission errors
- [ ] Logs show expected behavior

### Integration Tests
- [ ] Old structure still works
- [ ] New structure creates data
- [ ] Can switch between modes
- [ ] CLI tool functions properly

## Success Criteria 🎯

Testing is successful when:
1. **No Breaking Changes**: Old scraper works exactly as before
2. **New Structure Works**: Can scrape to new archive paths
3. **Toggle Functions**: USE_NEW_SCRAPERS switches behavior
4. **No Data Loss**: All existing data remains accessible
5. **Clean Logs**: No unexpected errors or warnings

## Emergency Rollback 🚨

If anything goes wrong:

### Quick Fix (GitHub Actions)
```yaml
# In workflow inputs
use_new_structure: false
```

### Full Rollback (Local)
```bash
# Restore original workflow
git checkout main -- .github/workflows/scrape.yml
git commit -m "Rollback to original workflow"
git push

# Remove new files (optional)
rm -rf tools/ configs/ archives/
```

### Data Recovery
If data was migrated and needs recovery:
```bash
# Check backups directory
ls -la backups/

# Restore from backup
cp -r backups/backup_[timestamp]/* data/
```

## Next Steps After Testing ➡️

Once all tests pass:
1. **Document Results**: Note any issues or adjustments needed
2. **Plan Migration Window**: Choose low-activity time
3. **Notify Team**: If applicable
4. **Execute Migration**: Follow MIGRATION_CHECKLIST.md
5. **Monitor**: Watch first few automated runs closely

---
*Remember: Take it slow, test thoroughly, and always have a rollback plan!*