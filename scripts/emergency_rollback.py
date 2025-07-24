#!/usr/bin/env python3
"""
Emergency Rollback Script

Use this if the migration causes issues and you need to quickly revert.
This script can rollback at various levels depending on the situation.
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
import argparse


class Colors:
    """Terminal colors"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.RESET}")


def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")


def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")


def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.RESET}")


def rollback_github_actions():
    """Rollback GitHub Actions to use old workflow"""
    print(f"\n{Colors.BOLD}Rolling back GitHub Actions...{Colors.RESET}")
    
    # Check if original workflow exists
    original = Path('.github/workflows/scrape.yml')
    updated = Path('.github/workflows/scrape_updated.yml')
    
    if not original.exists():
        print_error("Original workflow not found!")
        print_info("You may need to restore from git history")
        return False
    
    # If we're using the updated workflow, offer to switch back
    if updated.exists():
        print_warning("Found updated workflow. Switching back to original.")
        
        # Create backup of current state
        backup_name = f'scrape_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.yml'
        shutil.copy2(original, f'.github/workflows/{backup_name}')
        print_success(f"Backed up current workflow to {backup_name}")
    
    print_success("GitHub Actions using original workflow")
    print_info("Remember to commit and push changes!")
    
    return True


def rollback_file_structure():
    """Remove new directories and files"""
    print(f"\n{Colors.BOLD}Rolling back file structure...{Colors.RESET}")
    
    response = input("Remove new directories (tools/, configs/, archives/)? [y/N]: ")
    if response.lower() != 'y':
        print("Skipping file removal")
        return True
    
    # Items to remove
    to_remove = [
        'tools',
        'configs', 
        'archives',
        'collectibles.py',
        'MIGRATION_GUIDE.md',
        'MIGRATION_PROGRESS.md',
        'MIGRATION_CHECKLIST.md',
        'TESTING_GUIDE.md',
        'verify_setup.py'
    ]
    
    for item in to_remove:
        path = Path(item)
        if path.exists():
            try:
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                print_success(f"Removed {item}")
            except Exception as e:
                print_error(f"Failed to remove {item}: {e}")
        else:
            print_info(f"Not found: {item}")
    
    return True


def rollback_data_migration():
    """Rollback data migration if it was performed"""
    print(f"\n{Colors.BOLD}Checking data migration...{Colors.RESET}")
    
    # Check if data was migrated
    old_data = Path('data')
    new_data = Path('archives/forums/net54/data')
    
    if old_data.exists() and old_data.is_symlink():
        print_warning("Data directory is a symlink (migration was performed)")
        
        # Check for backups
        backup_dir = Path('backups')
        if backup_dir.exists():
            backups = sorted(backup_dir.glob('backup_*'))
            if backups:
                print_info(f"Found {len(backups)} backup(s):")
                for i, backup in enumerate(backups[-5:]):  # Show last 5
                    print(f"  {i+1}. {backup.name}")
                
                response = input("\nRestore from backup? [y/N]: ")
                if response.lower() == 'y':
                    if len(backups) == 1:
                        backup_choice = backups[0]
                    else:
                        choice = input("Enter backup number (or full path): ")
                        try:
                            if choice.isdigit():
                                backup_choice = backups[int(choice) - 1]
                            else:
                                backup_choice = Path(choice)
                        except:
                            print_error("Invalid choice")
                            return False
                    
                    # Restore from backup
                    print_info(f"Restoring from {backup_choice}...")
                    
                    # Remove symlink
                    old_data.unlink()
                    
                    # Copy backup
                    shutil.copytree(backup_choice, old_data)
                    print_success("Data restored from backup")
                    
                    # Remove new data location
                    if new_data.exists():
                        response = input("Remove migrated data? [y/N]: ")
                        if response.lower() == 'y':
                            shutil.rmtree(new_data)
                            print_success("Removed migrated data")
                    
                    return True
    
    elif old_data.exists() and not old_data.is_symlink():
        print_success("Data directory is original (no migration performed)")
        return True
    
    else:
        print_warning("No data directory found")
        return True
    
    return False


def rollback_git_changes():
    """Offer to rollback git changes"""
    print(f"\n{Colors.BOLD}Git rollback options...{Colors.RESET}")
    
    # Check git status
    result = subprocess.run(['git', 'status', '--porcelain'], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        if result.stdout:
            print_warning("You have uncommitted changes")
            print_info("Consider committing or stashing before rollback")
        
        print("\nGit rollback options:")
        print("1. Discard all uncommitted changes")
        print("2. Revert to specific commit") 
        print("3. Create rollback branch")
        print("4. Skip git rollback")
        
        choice = input("\nChoice [1-4]: ")
        
        if choice == '1':
            confirm = input("⚠️  Discard ALL uncommitted changes? [y/N]: ")
            if confirm.lower() == 'y':
                subprocess.run(['git', 'reset', '--hard'])
                subprocess.run(['git', 'clean', '-fd'])
                print_success("Discarded all changes")
        
        elif choice == '2':
            # Show recent commits
            print("\nRecent commits:")
            subprocess.run(['git', 'log', '--oneline', '-10'])
            commit = input("\nEnter commit hash to revert to: ")
            if commit:
                subprocess.run(['git', 'reset', '--hard', commit])
                print_success(f"Reverted to {commit}")
        
        elif choice == '3':
            branch_name = f'rollback-{datetime.now().strftime("%Y%m%d-%H%M%S")}'
            subprocess.run(['git', 'checkout', '-b', branch_name])
            print_success(f"Created rollback branch: {branch_name}")
    
    return True


def create_rollback_record():
    """Create a record of the rollback"""
    print(f"\n{Colors.BOLD}Creating rollback record...{Colors.RESET}")
    
    record = {
        'timestamp': datetime.now().isoformat(),
        'reason': input("Reason for rollback (optional): "),
        'actions_taken': []
    }
    
    record_file = Path(f'rollback_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    
    with open(record_file, 'w') as f:
        f.write(f"Rollback performed at {record['timestamp']}\n")
        f.write(f"Reason: {record['reason']}\n\n")
        f.write("Actions taken:\n")
        f.write("- See terminal output above\n")
    
    print_success(f"Rollback record saved to {record_file}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Emergency rollback for collectibles migration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Rollback levels:
  --actions    Rollback GitHub Actions only (safest)
  --files      Remove new files and directories
  --data       Restore data from backup
  --full       Complete rollback (all of the above)
  
Examples:
  # Just rollback GitHub Actions
  python emergency_rollback.py --actions
  
  # Full rollback
  python emergency_rollback.py --full
        """
    )
    
    parser.add_argument('--actions', action='store_true',
                       help='Rollback GitHub Actions workflow')
    parser.add_argument('--files', action='store_true',
                       help='Remove new files and directories')
    parser.add_argument('--data', action='store_true',
                       help='Restore data from backup')
    parser.add_argument('--full', action='store_true',
                       help='Complete rollback')
    parser.add_argument('--git', action='store_true',
                       help='Include git rollback options')
    
    args = parser.parse_args()
    
    # If no specific options, ask what to do
    if not any([args.actions, args.files, args.data, args.full]):
        print(f"{Colors.BOLD}Emergency Rollback Script{Colors.RESET}")
        print("\nWhat would you like to rollback?")
        print("1. GitHub Actions only (safest)")
        print("2. Files and directories") 
        print("3. Data migration")
        print("4. Everything (full rollback)")
        print("5. Exit")
        
        choice = input("\nChoice [1-5]: ")
        
        if choice == '1':
            args.actions = True
        elif choice == '2':
            args.files = True
        elif choice == '3':
            args.data = True
        elif choice == '4':
            args.full = True
        else:
            print("Exiting...")
            return
    
    # Perform rollback
    print(f"\n{Colors.RED}{Colors.BOLD}EMERGENCY ROLLBACK INITIATED{Colors.RESET}")
    print_warning("This will revert migration changes")
    
    confirm = input("\nContinue? [y/N]: ")
    if confirm.lower() != 'y':
        print("Rollback cancelled")
        return
    
    success = True
    
    if args.full or args.actions:
        success &= rollback_github_actions()
    
    if args.full or args.files:
        success &= rollback_file_structure()
    
    if args.full or args.data:
        success &= rollback_data_migration()
    
    if args.git:
        success &= rollback_git_changes()
    
    # Create record
    create_rollback_record()
    
    # Summary
    print(f"\n{Colors.BOLD}Rollback Summary{Colors.RESET}")
    if success:
        print_success("Rollback completed successfully")
        print("\nNext steps:")
        print("1. Test that old scraper works: python scripts/scraper.py --stats")
        print("2. Commit rollback changes if needed")
        print("3. Document what went wrong for future reference")
    else:
        print_error("Some rollback steps failed")
        print("Manual intervention may be required")


if __name__ == '__main__':
    main()