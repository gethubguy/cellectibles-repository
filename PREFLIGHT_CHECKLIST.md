# Pre-Flight Checklist for Migration Testing

## Before Running GitHub Actions Tests

### 1. Current State Check ✓
- [ ] No active scraping jobs running
- [ ] All current data is committed to git
- [ ] You have recorded current statistics:
  ```bash
  python scripts/scraper.py --stats > current_stats.txt
  ```

### 2. Local Verification ✓
- [ ] Run local test suite:
  ```bash
  python scripts/test_migration_local.py
  ```
- [ ] Verify setup:
  ```bash
  python verify_setup.py
  ```
- [ ] Test wrapper works:
  ```bash
  USE_NEW_SCRAPERS=false python scripts/scraper_wrapper.py --stats
  ```

### 3. GitHub Repository Check ✓
- [ ] All new files are committed and pushed:
  ```bash
  git add -A
  git commit -m "Add migration infrastructure"
  git push
  ```
- [ ] Verify workflows are visible in GitHub Actions tab
- [ ] Check you have workflow dispatch permissions

### 4. Backup Preparation ✓
- [ ] Create a backup branch:
  ```bash
  git checkout -b pre-migration-backup
  git push origin pre-migration-backup
  git checkout main
  ```
- [ ] Document current data location and size
- [ ] Note last successful scrape date/time

## GitHub Actions Test Sequence

### Phase 1: Basic Test (5 minutes)
1. **Go to GitHub Actions**
   - Navigate to your repository
   - Click "Actions" tab
   - Find "Test New Structure" workflow

2. **Run Stats Test**
   - Click "Run workflow"
   - Branch: `main`
   - Test type: `stats`
   - Click green "Run workflow" button

3. **Monitor Progress**
   - Click on the running workflow
   - Watch live logs
   - Check for:
     - ✅ No import errors
     - ✅ Configuration loads
     - ✅ Stats display (may show 0)

### Phase 2: Scrape Test (10-15 minutes)
1. **Run Small Scrape**
   - Run workflow again
   - Test type: `scrape-small`
   - This scrapes only 1 thread

2. **Check Results**
   - ✅ Scraping starts
   - ✅ Rate limiting active (5 sec delays)
   - ✅ No permission errors
   - ✅ Data saves to archives/forums/net54

3. **Verify Data**
   - Check artifacts if uploaded
   - Look for success messages in logs

### Phase 3: Structure Comparison (5 minutes)
1. **Run Structure Test**
   - Test type: `compare-structures`
   
2. **Verify Output Shows**
   - Old structure (if exists)
   - New structure created
   - Proper directory hierarchy

## Decision Points

### If All Tests Pass ✅
1. **Update Main Workflow**
   - Option A: Replace scrape.yml with scrape_updated.yml
   - Option B: Add toggle to existing workflow
   
2. **Test Main Workflow**
   - Run with `use_new_structure: false` (verify old works)
   - Run with `use_new_structure: true` (verify new works)

### If Tests Fail ❌
1. **Check Logs**
   - Download full logs from Actions
   - Look for specific error messages
   - Check KNOWN_ISSUES.md

2. **Common Fixes**
   - Missing dependencies → Update requirements.txt
   - Import errors → Check Python paths
   - Permission errors → Check directory creation

3. **Rollback if Needed**
   ```bash
   python scripts/emergency_rollback.py --actions
   ```

## Production Migration Checklist

Once tests pass, before full migration:

### 1. Communication
- [ ] Notify team (if applicable)
- [ ] Set maintenance window
- [ ] Document migration time

### 2. Final Backup
- [ ] Download current data artifact from GitHub
- [ ] Create local backup:
  ```bash
  tar -czf net54_backup_$(date +%Y%m%d).tar.gz data/
  ```

### 3. Migration Execution
- [ ] Stop scheduled workflows temporarily
- [ ] Run data migration:
  ```bash
  python scripts/migrate_data.py
  ```
- [ ] Verify data in new location
- [ ] Test scraper with new structure
- [ ] Re-enable scheduled workflows

### 4. Post-Migration
- [ ] Monitor first automated run
- [ ] Verify data integrity
- [ ] Check performance metrics
- [ ] Document any issues

## Emergency Procedures

### Quick Rollback
```bash
# In GitHub UI: set use_new_structure: false
# Or locally:
python scripts/emergency_rollback.py --actions
```

### Full Rollback
```bash
python scripts/emergency_rollback.py --full
```

### Data Recovery
```bash
# List backups
ls -la backups/

# Restore specific backup
python scripts/migrate_data.py --restore backups/backup_[timestamp]
```

## Success Criteria

Migration is successful when:
- [ ] All tests pass in GitHub Actions
- [ ] Data migrates without loss
- [ ] Old structure still accessible (via symlink or direct)
- [ ] New scraper runs successfully
- [ ] No performance degradation
- [ ] Scheduled runs work automatically

## Go/No-Go Decision

**GO** if:
- All GitHub Actions tests pass
- Local tests show no issues  
- You have verified backups
- Rollback procedures tested

**NO-GO** if:
- Any critical test fails
- Import or dependency issues
- Uncertain about data integrity
- No backup available

---
*Use this checklist step-by-step. Don't skip steps or rush the process.*