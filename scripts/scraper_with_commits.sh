#!/bin/bash
# Wrapper script to run scraper with periodic commits

# Start time tracking
START_TIME=$(date +%s)
COMMIT_INTERVAL=3600  # Commit every hour (3600 seconds)
LAST_COMMIT_TIME=$START_TIME

# Function to check if it's time to commit
should_commit() {
    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - LAST_COMMIT_TIME))
    if [ $ELAPSED -ge $COMMIT_INTERVAL ]; then
        return 0  # True, should commit
    else
        return 1  # False, not time yet
    fi
}

# Function to commit data
commit_data() {
    echo "=== Committing data at $(date) ==="
    python scripts/commit_helper.py
    if [ $? -eq 0 ]; then
        LAST_COMMIT_TIME=$(date +%s)
        echo "=== Commit successful ==="
    else
        echo "=== Commit failed, continuing scrape ==="
    fi
}

# Trap to ensure we commit on exit
cleanup() {
    echo "=== Scraper interrupted, committing final data ==="
    commit_data
    exit 0
}
trap cleanup EXIT INT TERM

# Start the scraper in background
echo "=== Starting scraper at $(date) ==="
python scripts/tapatalk_scraper.py "$@" &
SCRAPER_PID=$!

# Monitor scraper and commit periodically
while kill -0 $SCRAPER_PID 2>/dev/null; do
    if should_commit; then
        commit_data
    fi
    sleep 60  # Check every minute
done

# Wait for scraper to finish
wait $SCRAPER_PID
SCRAPER_EXIT_CODE=$?

echo "=== Scraper finished with exit code $SCRAPER_EXIT_CODE ==="
exit $SCRAPER_EXIT_CODE