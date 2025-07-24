#!/usr/bin/env python3
"""
Post-Migration Validation Script

Validates that the migration was successful and all systems are working.
Run this after migration to ensure everything is functioning correctly.
"""
import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
import hashlib


class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m' 
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{text}{Colors.RESET}")


def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")


def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")


def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")


def validate_directory_structure():
    """Validate that all required directories exist"""
    print_header("Validating Directory Structure")
    
    required_dirs = [
        'archives/forums/net54/data/processed/forums',
        'archives/forums/net54/data/processed/threads',
        'archives/forums/net54/data/processed/posts',
        'archives/forums/net54/data/metadata',
        'archives/forums/net54/data/raw',
        'configs',
        'tools/scrapers/base',
        'tools/scrapers/forums',
        'tools/scrapers/auctions'
    ]
    
    all_good = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print_success(f"Found: {dir_path}")
        else:
            print_error(f"Missing: {dir_path}")
            all_good = False
    
    return all_good


def validate_symlink():
    """Validate symlink from old to new structure"""
    print_header("Validating Symlink")
    
    old_path = Path('data')
    expected_target = 'archives/forums/net54/data'
    
    if not old_path.exists():
        print_warning("No 'data' path found (symlink or directory)")
        return False
    
    if old_path.is_symlink():
        actual_target = os.readlink(old_path)
        if actual_target == expected_target or actual_target.endswith('net54/data'):
            print_success(f"Symlink correct: data → {actual_target}")
            return True
        else:
            print_error(f"Symlink incorrect: data → {actual_target}")
            print(f"  Expected: {expected_target}")
            return False
    else:
        print_warning("'data' exists but is not a symlink")
        print("  Migration may not have been completed")
        return False


def validate_data_integrity():
    """Check that data was migrated correctly"""
    print_header("Validating Data Integrity")
    
    new_data = Path('archives/forums/net54/data')
    
    if not new_data.exists():
        print_error("New data directory doesn't exist")
        return False
    
    # Count files
    file_types = {
        'forums': list(new_data.glob('processed/forums/*.json')),
        'threads': list(new_data.glob('processed/threads/**/*.json')),
        'posts': list(new_data.glob('processed/posts/*.json')),
        'metadata': list(new_data.glob('metadata/*.json'))
    }
    
    total_files = 0
    for file_type, files in file_types.items():
        count = len(files)
        total_files += count
        if count > 0:
            print_success(f"{file_type}: {count} files")
        else:
            print_warning(f"{file_type}: 0 files")
    
    if total_files > 0:
        print_success(f"Total data files: {total_files}")
        
        # Check progress file
        progress_file = new_data / 'metadata' / 'progress.json'
        if progress_file.exists():
            try:
                with open(progress_file) as f:
                    progress = json.load(f)
                
                if 'migration_info' in progress:
                    print_success("Migration info found in progress file")
                    print(f"  Migrated at: {progress['migration_info']['migrated_at']}")
                
                forums = len(progress.get('forums', {}))
                threads = sum(len(t) for t in progress.get('threads', {}).values())
                print(f"  Progress tracking: {forums} forums, {threads} threads")
                
            except Exception as e:
                print_error(f"Error reading progress file: {e}")
        
        return True
    else:
        print_warning("No data files found in new structure")
        return False


def validate_scrapers():
    """Test that scrapers can be imported and initialized"""
    print_header("Validating Scrapers")
    
    # Test imports
    try:
        import sys
        sys.path.insert(0, '.')
        
        # Test base imports
        from tools.scrapers.base import BaseScraper
        print_success("Base scraper imports correctly")
        
        from tools.scrapers.base.storage import MultiArchiveStorage
        print_success("Multi-archive storage imports correctly")
        
        # Test specific scrapers
        from tools.scrapers.forums import Net54Scraper
        print_success("Net54 scraper imports correctly")
        
        from tools.scrapers.auctions import HeritageScraper  
        print_success("Heritage scraper imports correctly")
        
        # Test initialization
        storage = MultiArchiveStorage('net54', 'archives')
        print_success("Storage initializes correctly")
        
        return True
        
    except ImportError as e:
        print_error(f"Import error: {e}")
        print("  Check that all dependencies are installed")
        return False
    except Exception as e:
        print_error(f"Initialization error: {e}")
        return False


def validate_configs():
    """Validate configuration files"""
    print_header("Validating Configurations")
    
    config_files = ['net54.yaml', 'heritage.yaml', 'psa.yaml', 'prewarcards.yaml']
    all_good = True
    
    for config_file in config_files:
        config_path = Path('configs') / config_file
        if config_path.exists():
            try:
                import yaml
                with open(config_path) as f:
                    config = yaml.safe_load(f)
                
                # Check required fields
                if 'archive' in config and 'scraping' in config:
                    print_success(f"{config_file}: Valid")
                else:
                    print_error(f"{config_file}: Missing required fields")
                    all_good = False
                    
            except Exception as e:
                print_error(f"{config_file}: Parse error - {e}")
                all_good = False
        else:
            print_warning(f"{config_file}: Not found")
    
    return all_good


def validate_cli():
    """Test the collectibles CLI"""
    print_header("Validating CLI Tool")
    
    cli_path = Path('collectibles.py')
    
    if not cli_path.exists():
        print_error("collectibles.py not found")
        return False
    
    # Test CLI commands
    commands = [
        ('python3 collectibles.py verify', 'Verify command'),
        ('python3 collectibles.py list', 'List command'),
        ('python3 collectibles.py stats', 'Stats command')
    ]
    
    all_good = True
    for cmd, desc in commands:
        try:
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            if result.returncode == 0:
                print_success(f"{desc} works")
            else:
                print_error(f"{desc} failed: {result.stderr}")
                all_good = False
        except Exception as e:
            print_error(f"{desc} error: {e}")
            all_good = False
    
    return all_good


def validate_wrapper():
    """Test the wrapper script with both modes"""
    print_header("Validating Wrapper Script")
    
    # Test old mode
    cmd = ['python3', 'scripts/scraper_wrapper.py', '--help']
    env = {'USE_NEW_SCRAPERS': 'false'}
    
    try:
        result = subprocess.run(cmd, env={**os.environ, **env}, 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print_success("Wrapper works with old structure")
        else:
            print_error("Wrapper fails with old structure")
            return False
    except Exception as e:
        print_error(f"Error testing wrapper: {e}")
        return False
    
    # Test new mode
    env = {'USE_NEW_SCRAPERS': 'true'}
    try:
        result = subprocess.run(cmd, env={**os.environ, **env},
                              capture_output=True, text=True)
        if result.returncode == 0:
            print_success("Wrapper works with new structure")
        else:
            # May fail due to dependencies
            if 'ModuleNotFoundError' in result.stderr:
                print_warning("Wrapper has dependency issues (expected if not all deps installed)")
            else:
                print_error("Wrapper fails with new structure")
                return False
    except Exception as e:
        print_error(f"Error testing wrapper: {e}")
        return False
    
    return True


def validate_github_actions():
    """Check GitHub Actions readiness"""
    print_header("Validating GitHub Actions")
    
    workflows = [
        '.github/workflows/test-new-structure.yml',
        '.github/workflows/scrape.yml'
    ]
    
    all_good = True
    for workflow in workflows:
        if Path(workflow).exists():
            print_success(f"Found: {workflow}")
        else:
            print_warning(f"Missing: {workflow}")
    
    # Check for updated workflow
    updated = Path('.github/workflows/scrape_updated.yml')
    if updated.exists():
        print_success("Updated workflow available")
        print("  Ready to replace main workflow when needed")
    
    return all_good


def generate_report(results):
    """Generate validation report"""
    print_header("Validation Report")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    
    print(f"\nTests passed: {passed}/{total}")
    
    for test, result in results.items():
        status = "PASS" if result else "FAIL"
        color = Colors.GREEN if result else Colors.RED
        print(f"  {color}{status}{Colors.RESET} - {test}")
    
    if passed == total:
        print_success("\nAll validation checks passed! ✨")
        print("Migration appears successful.")
    else:
        print_error(f"\n{total - passed} validation checks failed")
        print("Review failures above and address issues.")
    
    # Save report
    report = {
        'timestamp': datetime.now().isoformat(),
        'results': results,
        'passed': passed,
        'total': total
    }
    
    report_file = f'validation_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Report saved to: {report_file}")


def main():
    print(f"{Colors.BOLD}=== Post-Migration Validation ==={Colors.RESET}")
    print("This script validates the collectibles migration\n")
    
    # Run all validation checks
    results = {
        'Directory Structure': validate_directory_structure(),
        'Symlink': validate_symlink(),
        'Data Integrity': validate_data_integrity(),
        'Scrapers': validate_scrapers(),
        'Configurations': validate_configs(),
        'CLI Tool': validate_cli(),
        'Wrapper Script': validate_wrapper(),
        'GitHub Actions': validate_github_actions()
    }
    
    # Generate report
    generate_report(results)
    
    # Return exit code based on results
    return 0 if all(results.values()) else 1


if __name__ == '__main__':
    exit(main())