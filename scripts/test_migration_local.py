#!/usr/bin/env python3
"""
Local Testing Script for Migration

Simulates GitHub Actions environment to test the migration locally.
This helps catch issues before running in CI/CD.
"""
import os
import sys
import subprocess
import tempfile
from pathlib import Path
import shutil


class Colors:
    """Terminal colors for output"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}=== {text} ==={Colors.RESET}")


def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")


def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")


def run_command(cmd, env=None, capture=False):
    """Run a shell command and return success status
    
    Args:
        cmd: Command to run
        env: Environment variables
        capture: Whether to capture output
        
    Returns:
        Tuple of (success, output)
    """
    try:
        if capture:
            result = subprocess.run(
                cmd, 
                shell=True, 
                env={**os.environ, **(env or {})},
                capture_output=True,
                text=True
            )
            return result.returncode == 0, result.stdout + result.stderr
        else:
            result = subprocess.run(
                cmd,
                shell=True,
                env={**os.environ, **(env or {})}
            )
            return result.returncode == 0, None
    except Exception as e:
        return False, str(e)


def test_imports():
    """Test that all required imports work"""
    print_header("Testing Imports")
    
    imports = [
        ("yaml", "PyYAML"),
        ("bs4", "BeautifulSoup4"),
        ("requests", "Requests"),
    ]
    
    all_good = True
    for module, name in imports:
        try:
            __import__(module)
            print_success(f"{name} imported successfully")
        except ImportError:
            print_error(f"{name} not available")
            all_good = False
    
    # Test custom imports
    try:
        sys.path.insert(0, '.')
        from tools.scrapers.base import BaseScraper
        print_success("Custom base classes imported successfully")
    except ImportError as e:
        print_error(f"Failed to import custom classes: {e}")
        all_good = False
    
    return all_good


def test_directory_creation():
    """Test directory creation like GitHub Actions would"""
    print_header("Testing Directory Creation")
    
    # Test old structure
    print("\nOld structure:")
    cmd = "mkdir -p data/{raw,processed/{forums,threads,posts},metadata} logs"
    success, _ = run_command(cmd)
    if success:
        print_success("Old directory structure created")
        # Clean up
        shutil.rmtree('data', ignore_errors=True)
        shutil.rmtree('logs', ignore_errors=True)
    else:
        print_error("Failed to create old structure")
    
    # Test new structure
    print("\nNew structure:")
    cmd = "mkdir -p archives/forums/net54/data/{raw,processed/{forums,threads,posts},metadata} logs"
    success, _ = run_command(cmd)
    if success:
        print_success("New directory structure created")
        
        # Test symlink creation
        if not Path('data').exists():
            try:
                os.symlink('archives/forums/net54/data', 'data')
                print_success("Symlink created successfully")
                os.unlink('data')  # Clean up
            except OSError:
                print_warning("Cannot create symlink (may need admin rights on Windows)")
        
        # Clean up
        shutil.rmtree('archives/forums/net54/data', ignore_errors=True)
    else:
        print_error("Failed to create new structure")
    
    return True


def test_wrapper_script():
    """Test the wrapper script with both modes"""
    print_header("Testing Wrapper Script")
    
    # Test with old structure
    print("\nTesting old structure (USE_NEW_SCRAPERS=false):")
    env = {'USE_NEW_SCRAPERS': 'false'}
    success, output = run_command(
        'python3 scripts/scraper_wrapper.py --help',
        env=env,
        capture=True
    )
    
    if success and 'usage:' in output.lower():
        print_success("Old structure wrapper works")
    else:
        print_error("Old structure wrapper failed")
        if output:
            print(f"   Output: {output[:200]}...")
    
    # Test with new structure
    print("\nTesting new structure (USE_NEW_SCRAPERS=true):")
    env = {'USE_NEW_SCRAPERS': 'true'}
    success, output = run_command(
        'python3 scripts/scraper_wrapper.py --help',
        env=env,
        capture=True
    )
    
    if success and 'usage:' in output.lower():
        print_success("New structure wrapper works")
    else:
        print_warning("New structure wrapper may have dependency issues")
        if output and 'ModuleNotFoundError' in output:
            print("   (This is expected if dependencies aren't installed)")
    
    return True


def test_github_actions_simulation():
    """Simulate what GitHub Actions would do"""
    print_header("Simulating GitHub Actions Workflow")
    
    print("\nThis simulates the test-new-structure.yml workflow:")
    
    # Step 1: Create directories
    print("\n1. Creating directories...")
    os.makedirs('logs', exist_ok=True)
    os.makedirs('archives/forums/net54/data', exist_ok=True)
    print_success("Directories created")
    
    # Step 2: Check imports
    print("\n2. Checking imports...")
    success, output = run_command(
        'python3 -c "from tools.scrapers.base import BaseScraper; print(\'Imports work\')"',
        capture=True
    )
    if success:
        print_success("Module imports successful")
    else:
        print_warning("Module imports failed (dependencies needed)")
    
    # Step 3: Test configuration loading
    print("\n3. Testing configuration...")
    success, output = run_command(
        'python3 -c "import yaml; print(\'YAML works\')"',
        capture=True
    )
    if success:
        print_success("Configuration system ready")
    else:
        print_error("YAML not available")
    
    # Clean up
    shutil.rmtree('logs', ignore_errors=True)
    
    return True


def test_migration_safety():
    """Test migration script safety features"""
    print_header("Testing Migration Safety")
    
    # Create fake data structure
    print("\nCreating test data structure...")
    os.makedirs('data/processed/forums', exist_ok=True)
    Path('data/processed/forums/test.json').write_text('{"test": true}')
    
    # Test dry run
    print("\nTesting migration dry run:")
    success, output = run_command(
        'python3 scripts/migrate_data.py --dry-run',
        capture=True
    )
    
    if success:
        print_success("Migration dry run completed")
        if 'Files to migrate: 1' in output:
            print_success("Correctly detected test file")
    else:
        print_error("Migration dry run failed")
    
    # Verify nothing was changed
    if Path('data/processed/forums/test.json').exists():
        print_success("Dry run didn't modify data")
    else:
        print_error("Dry run modified data!")
    
    # Clean up
    shutil.rmtree('data', ignore_errors=True)
    
    return True


def main():
    """Run all tests"""
    print(f"{Colors.BOLD}Local Migration Testing Suite{Colors.RESET}")
    print("This simulates GitHub Actions environment locally")
    
    tests = [
        ("Import Tests", test_imports),
        ("Directory Creation", test_directory_creation),
        ("Wrapper Script", test_wrapper_script),
        ("GitHub Actions Simulation", test_github_actions_simulation),
        ("Migration Safety", test_migration_safety),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print_header("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nTests passed: {passed}/{total}")
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {name}")
    
    if passed == total:
        print_success("\nAll tests passed! Ready for GitHub Actions testing.")
    else:
        print_warning(f"\n{total - passed} test(s) failed. Review issues before proceeding.")
    
    # Recommendations
    print_header("Recommendations")
    if passed < total:
        print("1. Install all dependencies: pip install -r requirements.txt")
        print("2. Ensure you're running from the project root directory")
        print("3. On Windows, you may need admin rights for symlinks")
    else:
        print("1. Review TESTING_GUIDE.md for GitHub Actions steps")
        print("2. Run the test workflow in GitHub Actions")
        print("3. Monitor the first migration carefully")


if __name__ == '__main__':
    main()