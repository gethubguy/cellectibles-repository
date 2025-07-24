#!/usr/bin/env python3
"""
Migration Monitoring Script

Monitors the migration process and provides real-time status updates.
Use this during migration to track progress and catch issues early.
"""
import os
import time
import json
from pathlib import Path
from datetime import datetime
import subprocess


class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def format_size(bytes):
    """Format bytes to human readable size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} TB"


def check_directory_status():
    """Check status of key directories"""
    dirs = {
        'Old Data': Path('data'),
        'New Data': Path('archives/forums/net54/data'),
        'Backups': Path('backups'),
        'Logs': Path('logs')
    }
    
    status = {}
    for name, path in dirs.items():
        if path.exists():
            if path.is_symlink():
                target = os.readlink(path)
                status[name] = f"Symlink → {target}"
            else:
                file_count = sum(1 for _ in path.rglob('*') if _.is_file())
                size = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
                status[name] = f"{file_count} files, {format_size(size)}"
        else:
            status[name] = "Not found"
    
    return status


def check_process_status():
    """Check if scraper processes are running"""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        processes = result.stdout.lower()
        
        running = []
        if 'scraper.py' in processes:
            running.append('scraper.py')
        if 'scraper_wrapper.py' in processes:
            running.append('scraper_wrapper.py')
        if 'migrate_data.py' in processes:
            running.append('migrate_data.py')
        
        return running
    except:
        return []


def check_github_actions():
    """Check latest GitHub Actions status"""
    try:
        # Check if gh CLI is available
        result = subprocess.run(['gh', 'run', 'list', '--limit', '5'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            runs = []
            for line in lines[:3]:  # Show last 3 runs
                parts = line.split('\t')
                if len(parts) >= 3:
                    status = parts[0]
                    name = parts[2]
                    runs.append(f"{status}: {name}")
            return runs
        return ["GitHub CLI not available"]
    except:
        return ["Unable to check GitHub Actions"]


def get_migration_progress():
    """Check migration progress if running"""
    progress = {
        'status': 'Not started',
        'files_migrated': 0,
        'current_operation': None
    }
    
    # Check for migration lock file or progress indicator
    migration_log = Path('migration.log')
    if migration_log.exists():
        try:
            # Read last line of migration log
            with open(migration_log, 'r') as f:
                lines = f.readlines()
                if lines:
                    last_line = lines[-1].strip()
                    progress['current_operation'] = last_line
        except:
            pass
    
    # Check if new data directory has content
    new_data = Path('archives/forums/net54/data')
    if new_data.exists():
        file_count = sum(1 for _ in new_data.rglob('*') if _.is_file())
        if file_count > 0:
            progress['status'] = 'In progress' if check_process_status() else 'Completed'
            progress['files_migrated'] = file_count
    
    return progress


def display_dashboard():
    """Display monitoring dashboard"""
    clear_screen()
    
    print(f"{Colors.BOLD}=== Migration Monitor ==={Colors.RESET}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Directory Status
    print(f"{Colors.BLUE}📁 Directory Status:{Colors.RESET}")
    dir_status = check_directory_status()
    for name, status in dir_status.items():
        color = Colors.GREEN if status != "Not found" else Colors.RED
        print(f"  {name}: {color}{status}{Colors.RESET}")
    
    # Process Status
    print(f"\n{Colors.BLUE}⚙️  Process Status:{Colors.RESET}")
    processes = check_process_status()
    if processes:
        for proc in processes:
            print(f"  🟢 {proc} is running")
    else:
        print(f"  {Colors.YELLOW}No migration processes running{Colors.RESET}")
    
    # Migration Progress
    print(f"\n{Colors.BLUE}📊 Migration Progress:{Colors.RESET}")
    progress = get_migration_progress()
    print(f"  Status: {progress['status']}")
    print(f"  Files migrated: {progress['files_migrated']}")
    if progress['current_operation']:
        print(f"  Current: {progress['current_operation']}")
    
    # GitHub Actions
    print(f"\n{Colors.BLUE}🚀 Recent GitHub Actions:{Colors.RESET}")
    actions = check_github_actions()
    for action in actions:
        if action.startswith('✓'):
            color = Colors.GREEN
        elif action.startswith('✗'):
            color = Colors.RED
        else:
            color = Colors.YELLOW
        print(f"  {color}{action}{Colors.RESET}")
    
    # Recommendations
    print(f"\n{Colors.BLUE}💡 Recommendations:{Colors.RESET}")
    
    old_data = Path('data')
    new_data = Path('archives/forums/net54/data')
    
    if old_data.exists() and not old_data.is_symlink():
        print(f"  {Colors.YELLOW}• Old data structure still exists{Colors.RESET}")
        print(f"    Run: python scripts/migrate_data.py")
    elif old_data.is_symlink():
        print(f"  {Colors.GREEN}• Data successfully migrated (symlink active){Colors.RESET}")
    
    if processes:
        print(f"  {Colors.YELLOW}• Migration in progress - do not interrupt{Colors.RESET}")
    
    if not new_data.exists():
        print(f"  {Colors.RED}• New data directory not found{Colors.RESET}")
        print(f"    Create with: mkdir -p {new_data}")


def monitor_loop(interval=5):
    """Run monitoring loop"""
    print("Starting migration monitor...")
    print(f"Refreshing every {interval} seconds. Press Ctrl+C to exit.\n")
    
    try:
        while True:
            display_dashboard()
            time.sleep(interval)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Monitor stopped by user{Colors.RESET}")


def quick_check():
    """Do a quick one-time check"""
    display_dashboard()
    
    print(f"\n{Colors.BOLD}=== Quick Checks ==={Colors.RESET}")
    
    # Check if ready for migration
    old_data = Path('data')
    new_data = Path('archives/forums/net54/data')
    
    ready = True
    
    if not old_data.exists():
        print(f"{Colors.YELLOW}⚠️  No existing data to migrate{Colors.RESET}")
        ready = False
    
    if check_process_status():
        print(f"{Colors.RED}❌ Active processes detected - stop before migrating{Colors.RESET}")
        ready = False
    
    backup_dir = Path('backups')
    if not backup_dir.exists() or not list(backup_dir.glob('*')):
        print(f"{Colors.YELLOW}⚠️  No backups found - create before migrating{Colors.RESET}")
        ready = False
    
    if ready:
        print(f"{Colors.GREEN}✅ System appears ready for migration{Colors.RESET}")
    else:
        print(f"{Colors.RED}❌ Address issues before migrating{Colors.RESET}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor collectibles migration')
    parser.add_argument('--once', action='store_true',
                       help='Run once and exit')
    parser.add_argument('--interval', type=int, default=5,
                       help='Refresh interval in seconds (default: 5)')
    
    args = parser.parse_args()
    
    if args.once:
        quick_check()
    else:
        monitor_loop(args.interval)


if __name__ == '__main__':
    main()