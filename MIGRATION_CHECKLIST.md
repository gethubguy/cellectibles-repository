# Migration Readiness Checklist

## Pre-Migration Verification ✓

### Current State Assessment
- [ ] Current GitHub Actions workflow is functioning
- [ ] No active scraping jobs running
- [ ] Latest data has been committed
- [ ] Review `git status` - no uncommitted changes

### Backup Verification
- [ ] Create backup branch: `git checkout -b backup-before-migration-$(date +%Y%m%d)`
- [ ] Push backup branch to GitHub
- [ ] Download current data artifact from GitHub Actions
- [ ] Create local backup of data directory

## Phase 4: GitHub Actions Testing 🚀

### Test Workflow Preparation
- [x] Test workflow created: `.github/workflows/test-new-structure.yml`
- [x] Wrapper script is executable
- [x] PyYAML added to requirements.txt
- [ ] Verify all imports work in GitHub environment

### Test Execution Steps
1. **Run Stats Test**
   - [ ] Go to Actions → "Test New Structure"
   - [ ] Run with test_type: "stats"
   - [ ] Verify no import errors
   - [ ] Check that stats display correctly

2. **Run Small Scrape Test**
   - [ ] Run with test_type: "scrape-small"
   - [ ] Verify data saves to new structure
   - [ ] Check logs for any errors
   - [ ] Confirm rate limiting works

3. **Compare Structures Test**
   - [ ] Run with test_type: "compare-structures"
   - [ ] Verify directory creation
   - [ ] Check symlink compatibility

### Verification Points
- [ ] No Python import errors
- [ ] Configuration loads correctly
- [ ] Storage paths are created
- [ ] Wrapper script executes without error
- [ ] Data saves to correct locations

## Phase 5: Production Migration 🔄

### Before Switching
- [ ] All tests pass in GitHub Actions
- [ ] Document current data statistics
- [ ] Notify team of migration window
- [ ] Review rollback procedure

### Migration Steps
1. **Update Main Workflow**
   - [ ] Replace `scrape.yml` with `scrape_updated.yml`
   - [ ] Or update existing workflow with new options
   - [ ] Test manual trigger with old structure
   - [ ] Test manual trigger with new structure

2. **Data Migration** (if needed)
   - [ ] Stop current scraping
   - [ ] Run data migration script
   - [ ] Verify data integrity
   - [ ] Update progress tracking

3. **Switch Default**
   - [ ] Change default to `use_new_structure: true`
   - [ ] Run full test cycle
   - [ ] Monitor for 24 hours

### Post-Migration Verification
- [ ] Scheduled scraping works
- [ ] Manual triggers work
- [ ] Data commits properly
- [ ] Artifacts upload correctly
- [ ] Stats reporting accurate

## Rollback Procedure 🔙

If issues occur at any stage:

### Quick Rollback (No data movement)
```bash
# In GitHub Actions inputs
use_new_structure: false
```

### Full Rollback
```bash
# Restore original workflow
git checkout main -- .github/workflows/scrape.yml
git commit -m "Rollback to original workflow"
git push
```

### Emergency Rollback
```bash
# From backup branch
git checkout backup-before-migration-YYYYMMDD
git branch -D main
git checkout -b main
git push --force origin main
```

## Success Criteria ✅

Migration is successful when:
- [ ] New structure processes same data as old
- [ ] No data loss or corruption
- [ ] Performance is same or better
- [ ] All automated processes work
- [ ] Can add new archive sources

## Communication Plan 📢

- [ ] Create GitHub issue for migration tracking
- [ ] Update README with new structure info
- [ ] Document any breaking changes
- [ ] Notify on completion

## Next Archive Addition

Once migration is stable:
- [ ] Choose first new archive (Heritage recommended)
- [ ] Create scraper using base classes
- [ ] Test thoroughly before adding to workflow
- [ ] Document lessons learned

---
*Use this checklist to ensure safe migration. Check off items as completed.*