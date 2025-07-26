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
    success, _, _ = run_command("git add data/forums/net54baseball.com/")
    if not success:
        print("No data/forums/net54baseball.com directory to add")
    
    # Check if there are changes to commit
    success, output, _ = run_command("git diff --staged --quiet")
    if success:
        print("No changes to commit")
        return True
    
    # Get stats for commit message (count thread files, excluding metadata.json)
    all_files = list(Path("data/forums/net54baseball.com").rglob("*.json")) if Path("data/forums/net54baseball.com").exists() else []
    thread_files = [f for f in all_files if f.name.startswith("thread_")]
    thread_count = len(thread_files)
    
    # Commit with descriptive message
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    commit_msg = f"Add scraped data: {thread_count} threads ({timestamp}) [skip ci]"
    
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