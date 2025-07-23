#!/usr/bin/env python3
"""
Helper script to commit data periodically during long-running scrapes
"""
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def run_command(cmd):
    """Run a shell command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def commit_data():
    """Commit any new scraped data"""
    # Configure git
    run_command("git config --global user.name 'GitHub Action'")
    run_command("git config --global user.email 'action@github.com'")
    
    # Add data files
    success, _, _ = run_command("git add data/processed/")
    if not success:
        print("No data/processed directory to add")
        
    success, _, _ = run_command("git add data/metadata/")
    if not success:
        print("No data/metadata directory to add")
    
    # Check if there are changes to commit
    success, output, _ = run_command("git diff --staged --quiet")
    if success:
        print("No changes to commit")
        return True
    
    # Get stats for commit message
    thread_count = len(list(Path("data/processed/threads").rglob("*.json"))) if Path("data/processed/threads").exists() else 0
    post_count = len(list(Path("data/processed/posts").rglob("*.json"))) if Path("data/processed/posts").exists() else 0
    
    # Commit with descriptive message
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    commit_msg = f"Add scraped data: {thread_count} threads, {post_count} posts ({timestamp}) [skip ci]"
    
    success, output, error = run_command(f'git commit -m "{commit_msg}"')
    if success:
        print(f"Committed: {commit_msg}")
        
        # Push to remote
        success, output, error = run_command("git push")
        if success:
            print("Successfully pushed to remote")
            return True
        else:
            print(f"Failed to push: {error}")
            return False
    else:
        print(f"Failed to commit: {error}")
        return False

if __name__ == "__main__":
    # This can be called periodically during scraping
    success = commit_data()
    sys.exit(0 if success else 1)