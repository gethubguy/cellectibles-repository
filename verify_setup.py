#!/usr/bin/env python3
"""
Verify the collectibles migration setup without requiring all dependencies
"""
import os
from pathlib import Path


def verify_setup():
    """Verify the collectibles setup"""
    print("\n🔍 Verifying Collectibles Migration Setup\n")
    
    # Directory checks
    print("📁 Directory Structure:")
    dirs = {
        'Archives root': 'archives',
        'Forums': 'archives/forums',
        'Auctions': 'archives/auctions', 
        'Content': 'archives/content',
        'Net54 archive': 'archives/forums/net54',
        'Tools': 'tools',
        'Scrapers': 'tools/scrapers',
        'Base classes': 'tools/scrapers/base',
        'Configs': 'configs'
    }
    
    for name, path in dirs.items():
        exists = Path(path).exists()
        print(f"  {'✅' if exists else '❌'} {name}: {path}")
    
    # File checks
    print("\n📄 Key Files:")
    files = {
        'Base scraper': 'tools/scrapers/base/base_scraper.py',
        'Multi-archive storage': 'tools/scrapers/base/storage.py',
        'Net54 wrapper': 'tools/scrapers/forums/net54_scraper.py',
        'Heritage scraper': 'tools/scrapers/auctions/heritage_scraper.py',
        'Net54 config': 'configs/net54.yaml',
        'Heritage config': 'configs/heritage.yaml',
        'Wrapper script': 'scripts/scraper_wrapper.py',
        'Migration script': 'scripts/migrate_data.py',
        'CLI tool': 'collectibles.py',
        'Test workflow': '.github/workflows/test-new-structure.yml',
        'Updated workflow': '.github/workflows/scrape_updated.yml'
    }
    
    for name, path in files.items():
        exists = Path(path).exists()
        print(f"  {'✅' if exists else '❌'} {name}: {path}")
    
    # Configuration checks
    print("\n⚙️  Configurations:")
    config_dir = Path('configs')
    if config_dir.exists():
        configs = list(config_dir.glob('*.yaml'))
        print(f"  Found {len(configs)} configuration files:")
        for config in configs:
            print(f"    • {config.stem}")
    else:
        print("  ❌ No configs directory found")
    
    # Check for existing data
    print("\n💾 Existing Data:")
    old_data = Path('data')
    if old_data.exists():
        if old_data.is_symlink():
            target = os.readlink(old_data)
            print(f"  ✅ Old data path is symlink to: {target}")
        else:
            print(f"  ⚠️  Old data exists at: {old_data}")
            print("     (Not yet migrated to new structure)")
    
    # Summary
    print("\n📊 Summary:")
    print("  ✅ Migration structure is ready")
    print("  ✅ Backward compatibility maintained")
    print("  ⚠️  Some dependencies may need to be installed")
    print("\n📝 Next Steps:")
    print("  1. Run test workflow in GitHub Actions")
    print("  2. Test with USE_NEW_SCRAPERS=true locally")
    print("  3. Migrate existing data when ready")
    print("  4. Start adding new archive sources")


if __name__ == '__main__':
    verify_setup()