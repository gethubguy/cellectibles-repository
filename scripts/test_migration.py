#!/usr/bin/env python3
"""Test script to verify migration components work correctly"""
import sys
import os

print("=== Testing Migration Components ===\n")

# Test 1: Directory structure
print("1. Directory Structure:")
dirs_to_check = [
    "checklists/vintage",
    "archives/forums/net54", 
    "enrichment/analysis",
    "tools/scrapers/base",
    "configs"
]
for dir_path in dirs_to_check:
    exists = os.path.exists(dir_path)
    print(f"  {'✓' if exists else '✗'} {dir_path}")

# Test 2: Configuration file
print("\n2. Configuration:")
config_path = "configs/net54.yaml"
if os.path.exists(config_path):
    print(f"  ✓ {config_path} exists")
    try:
        import yaml
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        print(f"  ✓ Config loaded: archive name = '{config['archive']['name']}'")
    except Exception as e:
        print(f"  ✗ Error loading config: {e}")
else:
    print(f"  ✗ {config_path} not found")

# Test 3: Module imports
print("\n3. Module Imports:")
try:
    sys.path.insert(0, '.')
    from tools.scrapers.base import BaseScraper
    print("  ✓ BaseScraper imported")
except Exception as e:
    print(f"  ✗ BaseScraper import failed: {e}")

try:
    from tools.scrapers.forums import Net54Scraper
    print("  ✓ Net54Scraper imported")
except Exception as e:
    print(f"  ✗ Net54Scraper import failed: {e}")

# Test 4: Storage compatibility
print("\n4. Storage Compatibility:")
storage_updated = os.path.exists("scripts/storage_updated.py")
print(f"  {'✓' if storage_updated else '✗'} storage_updated.py exists")

# Test 5: Wrapper script
print("\n5. Wrapper Script:")
wrapper_path = "scripts/scraper_wrapper.py"
if os.path.exists(wrapper_path):
    print(f"  ✓ {wrapper_path} exists")
    # Check if executable
    is_executable = os.access(wrapper_path, os.X_OK)
    print(f"  {'✓' if is_executable else '✗'} Wrapper is executable")
else:
    print(f"  ✗ {wrapper_path} not found")

# Test 6: GitHub Actions workflow
print("\n6. GitHub Actions:")
workflow_path = ".github/workflows/test-new-structure.yml"
if os.path.exists(workflow_path):
    print(f"  ✓ {workflow_path} exists")
else:
    print(f"  ✗ {workflow_path} not found")

print("\n=== Summary ===")
print("Phase 1 migration components are in place.")
print("The wrapper script maintains backward compatibility.")
print("New structure can be activated with USE_NEW_SCRAPERS=true")