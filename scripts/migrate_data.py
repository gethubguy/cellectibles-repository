#!/usr/bin/env python3
"""
Data Migration Script

Migrates existing Net54 data from old structure to new archive structure.
Safe to run multiple times - checks for existing data.
"""
import os
import shutil
import json
from pathlib import Path
from datetime import datetime
import argparse


def create_backup(source_dir: Path, backup_dir: Path):
    """Create a backup of the source directory
    
    Args:
        source_dir: Directory to backup
        backup_dir: Where to store backup
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = backup_dir / f'backup_{timestamp}'
    
    print(f"Creating backup at: {backup_path}")
    shutil.copytree(source_dir, backup_path)
    
    # Create backup manifest
    manifest = {
        'created_at': datetime.now().isoformat(),
        'source_path': str(source_dir),
        'backup_path': str(backup_path),
        'file_count': sum(1 for _ in backup_path.rglob('*') if _.is_file())
    }
    
    with open(backup_path / 'backup_manifest.json', 'w') as f:
        json.dump(manifest, f, indent=2)
    
    return backup_path


def migrate_data(dry_run: bool = True, create_symlink: bool = True):
    """Migrate data from old structure to new structure
    
    Args:
        dry_run: If True, only show what would be done
        create_symlink: If True, create symlink for backward compatibility
    """
    old_data_dir = Path('./data')
    new_data_dir = Path('./archives/forums/net54/data')
    backup_dir = Path('./backups')
    
    print("=== Net54 Data Migration ===\n")
    
    # Check if old data exists
    if not old_data_dir.exists():
        print("❌ No data directory found at ./data")
        print("   Nothing to migrate.")
        return
    
    # Check if new structure exists
    if new_data_dir.exists() and any(new_data_dir.iterdir()):
        print("⚠️  New data directory already exists and contains files:")
        print(f"   {new_data_dir}")
        response = input("\nContinue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Migration cancelled.")
            return
    
    # Count files to migrate
    file_count = sum(1 for _ in old_data_dir.rglob('*') if _.is_file())
    dir_size_mb = sum(f.stat().st_size for f in old_data_dir.rglob('*') if f.is_file()) / (1024 * 1024)
    
    print(f"📊 Migration Summary:")
    print(f"   Files to migrate: {file_count}")
    print(f"   Total size: {dir_size_mb:.2f} MB")
    print(f"   Source: {old_data_dir}")
    print(f"   Destination: {new_data_dir}")
    
    if dry_run:
        print("\n🔍 DRY RUN MODE - No changes will be made")
    
    if not dry_run:
        response = input("\nProceed with migration? (y/N): ")
        if response.lower() != 'y':
            print("Migration cancelled.")
            return
        
        # Create backup
        print("\n📦 Creating backup...")
        backup_dir.mkdir(exist_ok=True)
        backup_path = create_backup(old_data_dir, backup_dir)
        print(f"✅ Backup created: {backup_path}")
        
        # Create new directory structure
        print("\n📁 Creating new directory structure...")
        new_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Migrate data
        print("\n🚀 Migrating data...")
        
        # Option 1: Move (faster but removes original)
        # shutil.move(str(old_data_dir), str(new_data_dir))
        
        # Option 2: Copy (safer but uses more disk space temporarily)
        for item in old_data_dir.iterdir():
            dest = new_data_dir / item.name
            if item.is_dir():
                print(f"   Copying directory: {item.name}")
                shutil.copytree(item, dest, dirs_exist_ok=True)
            else:
                print(f"   Copying file: {item.name}")
                shutil.copy2(item, dest)
        
        print("✅ Data copied successfully")
        
        # Remove old data directory
        print("\n🗑️  Removing old data directory...")
        shutil.rmtree(old_data_dir)
        print("✅ Old directory removed")
        
        # Create symlink for backward compatibility
        if create_symlink:
            print("\n🔗 Creating symlink for backward compatibility...")
            try:
                os.symlink(new_data_dir, old_data_dir)
                print(f"✅ Symlink created: {old_data_dir} -> {new_data_dir}")
            except OSError as e:
                print(f"⚠️  Could not create symlink: {e}")
                print("   You may need to update paths in your scripts.")
        
        # Update progress file paths in metadata
        print("\n📝 Updating metadata paths...")
        progress_file = new_data_dir / 'metadata' / 'progress.json'
        if progress_file.exists():
            with open(progress_file, 'r') as f:
                progress = json.load(f)
            
            # Add migration info
            progress['migration_info'] = {
                'migrated_at': datetime.now().isoformat(),
                'from_path': str(old_data_dir),
                'to_path': str(new_data_dir),
                'backup_path': str(backup_path)
            }
            
            with open(progress_file, 'w') as f:
                json.dump(progress, f, indent=2)
        
        print("\n✅ Migration completed successfully!")
        
        # Show summary
        print("\n📊 Final Summary:")
        print(f"   Files migrated: {file_count}")
        print(f"   New location: {new_data_dir}")
        print(f"   Backup saved: {backup_path}")
        if create_symlink and old_data_dir.is_symlink():
            print(f"   Symlink created: {old_data_dir} -> {new_data_dir}")
    
    else:
        print("\n📋 Migration Plan:")
        print("   1. Create backup of current data")
        print("   2. Create new directory structure")
        print("   3. Copy all data to new location")
        print("   4. Remove old data directory")
        if create_symlink:
            print("   5. Create symlink for compatibility")
        print("\nRun without --dry-run to execute migration")


def verify_migration():
    """Verify that migration was successful"""
    old_data_dir = Path('./data')
    new_data_dir = Path('./archives/forums/net54/data')
    
    print("\n=== Verifying Migration ===\n")
    
    # Check new structure
    if new_data_dir.exists():
        file_count = sum(1 for _ in new_data_dir.rglob('*') if _.is_file())
        print(f"✅ New data directory exists: {new_data_dir}")
        print(f"   Contains {file_count} files")
    else:
        print(f"❌ New data directory not found: {new_data_dir}")
    
    # Check symlink
    if old_data_dir.exists():
        if old_data_dir.is_symlink():
            target = os.readlink(old_data_dir)
            print(f"✅ Symlink exists: {old_data_dir} -> {target}")
        else:
            print(f"⚠️  Old data directory exists but is not a symlink")
    else:
        print(f"❌ No symlink found at: {old_data_dir}")
    
    # Check key directories
    for subdir in ['processed/forums', 'processed/threads', 'processed/posts', 'metadata']:
        path = new_data_dir / subdir
        if path.exists():
            print(f"✅ {subdir} exists")
        else:
            print(f"❌ {subdir} missing")


def main():
    parser = argparse.ArgumentParser(description='Migrate Net54 data to new structure')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be done without making changes')
    parser.add_argument('--no-symlink', action='store_true',
                       help='Do not create backward compatibility symlink')
    parser.add_argument('--verify', action='store_true',
                       help='Verify migration status')
    
    args = parser.parse_args()
    
    if args.verify:
        verify_migration()
    else:
        migrate_data(dry_run=args.dry_run, create_symlink=not args.no_symlink)


if __name__ == '__main__':
    main()