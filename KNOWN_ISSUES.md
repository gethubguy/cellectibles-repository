# Known Issues and Solutions

## Common Issues During Migration

### 1. Import Errors (ModuleNotFoundError)

**Issue:**
```
ModuleNotFoundError: No module named 'tqdm'
ModuleNotFoundError: No module named 'yaml'
```

**Solution:**
```bash
# Install all dependencies
pip install -r requirements.txt

# Or for specific modules
pip install tqdm PyYAML beautifulsoup4 requests
```

**GitHub Actions Fix:**
The workflow already installs requirements.txt, so this shouldn't happen in CI/CD.

### 2. Permission Errors

**Issue:**
```
Permission denied: './data'
OSError: [Errno 13] Permission denied: 'archives/forums/net54'
```

**Solution:**
```bash
# Fix permissions
chmod -R 755 data/ archives/
chmod +x scripts/*.py

# On Windows, run as administrator or skip symlinks
python scripts/migrate_data.py --no-symlink
```

### 3. Symlink Issues (Windows)

**Issue:**
```
OSError: symbolic link privilege not held
```

**Solution:**
1. Run as administrator, OR
2. Use without symlinks:
   ```bash
   python scripts/migrate_data.py --no-symlink
   ```
3. Update paths in scripts manually

### 4. Configuration Not Found

**Issue:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'configs/net54.yaml'
```

**Solution:**
Always run from project root:
```bash
cd /path/to/net54
python scripts/scraper_wrapper.py  # Correct
# NOT: cd scripts && python scraper_wrapper.py
```

### 5. Old Structure Still Being Used

**Issue:**
New structure isn't activated despite setting environment variable.

**Solution:**
```bash
# Make sure to export the variable
export USE_NEW_SCRAPERS=true
python scripts/scraper_wrapper.py

# Or inline
USE_NEW_SCRAPERS=true python scripts/scraper_wrapper.py
```

### 6. GitHub Actions Using Wrong Workflow

**Issue:**
GitHub Actions not showing new options or using old behavior.

**Solution:**
1. Ensure you're using the updated workflow file
2. Check workflow file name in `.github/workflows/`
3. You may need to update the default workflow:
   ```bash
   cp .github/workflows/scrape_updated.yml .github/workflows/scrape.yml
   ```

### 7. Data Not Found After Migration

**Issue:**
Scripts can't find data after migration.

**Solution:**
1. Check if symlink was created:
   ```bash
   ls -la data
   ```
2. If no symlink, create manually:
   ```bash
   ln -s archives/forums/net54/data data
   ```
3. Or update paths in scripts

### 8. Memory Issues with Large Forums

**Issue:**
```
MemoryError: Unable to allocate array
```

**Solution:**
Use thread limits:
```bash
# Limit threads per forum
python scripts/scraper.py --thread-limit 100

# In GitHub Actions
forum_id: 39
thread_limit: 100
```

### 9. Rate Limiting Errors

**Issue:**
```
HTTPError: 429 Too Many Requests
```

**Solution:**
1. Increase delay in config:
   ```yaml
   scraping:
     delay_seconds: 10  # Increase from 5
   ```
2. Use exponential backoff
3. Run during off-peak hours

### 10. Incomplete Migration

**Issue:**
Migration partially completed and system is in inconsistent state.

**Solution:**
```bash
# Run emergency rollback
python scripts/emergency_rollback.py --full

# Or manually restore from backup
cp -r backups/backup_[timestamp]/* data/
```

## Platform-Specific Issues

### macOS
- File system case sensitivity may cause issues
- Use consistent casing for all paths

### Windows
- Symlinks require admin privileges
- Path separators: use forward slashes or Path objects
- Long path names may cause issues (enable long path support)

### Linux
- Usually works without issues
- Ensure Python 3.6+ is used

## Testing Issues

### Local Tests Pass but GitHub Actions Fail
1. Check Python version matches (3.11)
2. Ensure all files are committed
3. Check for hardcoded paths
4. Verify environment variables are set correctly

### Can't Run Tests Locally
1. Install test dependencies
2. Use virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

## Prevention Tips

1. **Always backup before migration:**
   ```bash
   cp -r data/ data_backup_$(date +%Y%m%d)/
   ```

2. **Test in stages:**
   - Test imports first
   - Test configuration loading
   - Test with small data set
   - Then full migration

3. **Use dry run options:**
   ```bash
   python scripts/migrate_data.py --dry-run
   ```

4. **Monitor first runs:**
   - Watch GitHub Actions logs
   - Check data is saved correctly
   - Verify no data loss

## Getting Help

If you encounter issues not listed here:

1. Check existing GitHub issues
2. Run diagnostic script:
   ```bash
   python verify_setup.py
   ```
3. Include full error message and environment details
4. Check MIGRATION_PROGRESS.md for current state

## Emergency Contacts

- Rollback script: `scripts/emergency_rollback.py`
- Original files in git history
- Backup branch: `backup-before-migration-[date]`

---
*Last updated: July 2025*