# Net54 Baseball Forum Archive Project

## Communication Preferences
- **ALWAYS respond with yes/no when appropriate & possible. If you need to supplement with context, a Maximum 1-2 sentences is acceptable.**
- User will ask for more detail when needed
- Explain in "enthusiast" terminology, not developer jargon
- Work slowly and carefully unless told otherwise
- Don't answer questions user didn't ask (unless user says "explain fully", "give me details", "why?", etc.)

## Debugging & Problem-Solving Approach
- **ALWAYS check actual data first before theorizing**
- When something's wrong:
  1. **Check the log files** - logs/YYYY-MM-DD/ contains scraping logs and errors
  2. Check the scraped data to see what's ACTUALLY there
  3. Compare actual output to expected output
  4. Find the specific code that's failing
- **NO speculation or analysis until facts are verified**
- Binary questions are good - answer yes/no when possible

## Project Overview
This project archives the Net54 Baseball forum (https://www.net54baseball.com/), a massive repository of vintage sports card history and knowledge. The goal is to preserve ~300,000 threads and 2.2 million posts locally for future AI analysis and historical preservation.

## Technical Stack
- **Language**: Python 3.x
- **Scraping**: BeautifulSoup4, requests
- **Storage**: JSON files with hierarchical structure
- **Automation**: GitHub Actions (to protect user IP)
- **Rate Limiting**: 1-2 seconds between requests

## Directory Structure
```
net54-archive/
├── scripts/
│   ├── scraper.py         # Main scraping orchestration
│   ├── parser.py          # HTML parsing and data extraction
│   ├── storage.py         # Data persistence handlers
│   └── utils.py           # Shared utilities
├── data/
│   ├── raw/               # Raw HTML pages (if needed)
│   ├── processed/         # Structured JSON data
│   │   ├── forums/        # Forum metadata
│   │   ├── threads/       # Thread data by ID
│   │   └── posts/         # Individual posts
│   └── metadata/          # Site structure, progress tracking
├── logs/                  # Scraping logs by date
├── .github/
│   └── workflows/
│       └── scrape.yml     # GitHub Actions workflow
├── requirements.txt       # Python dependencies
├── .env.example          # Environment configuration
├── .gitignore            # Excludes data/ and logs/
└── CLAUDE.md             # This file
```

## Data Structure
The scraped data follows this JSON hierarchy:
- **Forum**: id, name, description, thread_count
- **Thread**: id, forum_id, title, author, created_date, post_count, views
- **Post**: id, thread_id, author, timestamp, content, attachments

## Scraping Guidelines
1. **Respectful Crawling**: 1-2 second delays between requests
2. **Resume Capability**: Track progress to handle interruptions
3. **Error Handling**: Log failures, retry with exponential backoff
4. **Data Integrity**: Verify content before marking as complete
5. **Storage Efficiency**: Compress old data, organize by date/forum

## GitHub Actions Configuration
- Runs on schedule (e.g., weekly) to capture new content
- Uses GitHub's infrastructure (not user's IP)
- Stores results in artifacts or separate data repository
- Includes progress reporting and error notifications

## Future AI Analysis Goals
The archived data will enable:
- Historical trend analysis of card values and discussions
- Expert knowledge extraction from veteran collectors
- Pattern recognition in authentication discussions
- Building a comprehensive knowledge base for card identification

## CLAUDE.md Update Protocol
- **Always inform the user** before updating CLAUDE.md
- **Describe the proposed change** and explain why it's needed
- **Wait for approval** before proceeding with edits

## Code References
When referencing specific functions or pieces of code include the pattern `file_path:line_number` to allow the user to easily navigate to the source code location.

---
*Project Start Date: July 2025*