# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains two Python automation scripts:
1. **ai-news.py**: Uses Google's Gemini 3 Flash API with Google Search grounding to fetch the latest 5 AI/LLM technology news articles and automatically creates child pages in Confluence with the summarized content.
2. **check-ispo-shopback.py**: Monitors ShopBack's ISPO cashback rate and sends LINE Notify alerts when the cashback exceeds a specified threshold (default: 9%).

## Development Setup

### Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows

# Install dependencies
pip install -r requirements.txt
```

### Configuration
The project requires a `.env` file (copy from `.env.example`):

**For ai-news.py:**
- `GEMINI_API_KEY`: Google Gemini API key from https://aistudio.google.com/app/apikey
- `CONFLUENCE_URL`: Confluence instance URL (default: https://trendmicro.atlassian.net)
- `CONFLUENCE_USERNAME`: Email address for Atlassian account
- `CONFLUENCE_API_TOKEN`: API token from https://id.atlassian.com/manage-profile/security/api-tokens
- `CONFLUENCE_PARENT_PAGE_ID`: Parent page ID where new pages will be created (extract from Confluence page URL)

**For check-ispo-shopback.py:**
- `LINE_NOTIFY_TOKEN`: LINE Notify token from https://notify-bot.line.me/
- `CASHBACK_THRESHOLD`: Threshold percentage for alerts (default: 9.0)

### Running the Scripts
```bash
# Run AI news to Confluence updater
python ai-news.py

# Run ShopBack ISPO cashback checker
python check-ispo-shopback.py
```

## Architecture

### ai-news.py Components

1. **News Fetching (`get_ai_news()`)** (ai-news.py:20-71)
   - Uses Gemini 3 Flash Preview model (`gemini-3-flash-preview`) with Google Search grounding
   - Generates Chinese language news summaries in Markdown format
   - Configured with temperature=0.7 and max_output_tokens=2000
   - Returns 5 recent AI/LLM news items with titles (### format) and bullet-point summaries

2. **Markdown to Confluence Conversion** (ai-news.py:74-167)
   - `markdown_to_confluence_storage()`: Converts Markdown to Confluence Storage Format (XHTML)
   - `process_inline_formatting()`: Handles inline formatting (bold, italic, links, code)
   - `escape_html()`: Escapes HTML special characters
   - Supports: headings (h1-h3), bulleted/numbered lists, horizontal rules, inline formatting

3. **Confluence Integration (`create_confluence_child_page()`)** (ai-news.py:170-232)
   - Creates child pages under specified parent page using Confluence REST API
   - Uses Space key "TrendLifeRD"
   - Page title format: "AI 新聞摘要 - YYYY-MM-DD"
   - Uses HTTP Basic Auth (email + API token)
   - Endpoint: `{CONFLUENCE_URL}/wiki/rest/api/content`

### check-ispo-shopback.py Components

1. **Cashback Rate Extraction (`get_shopback_cashback()`)** (check-ispo-shopback.py:15-65)
   - Fetches HTML from https://www.shopback.com.tw/ispo
   - Uses BeautifulSoup for HTML parsing
   - Employs multiple regex patterns to extract cashback percentage
   - Patterns include: "X% 現金回饋", "全館商品 X%", "高達 X%"
   - Returns cashback percentage as float or error message

2. **LINE Notification (`send_line_notify()`)** (check-ispo-shopback.py:68-89)
   - Sends alerts via LINE Notify API (https://notify-api.line.me/api/notify)
   - Uses Bearer token authentication
   - Formats message with cashback rate, threshold, timestamp, and URL

3. **Main Logic (`main()`)** (check-ispo-shopback.py:92-128)
   - Fetches current cashback rate
   - Compares against configured threshold (default: 9%)
   - Sends LINE notification only if threshold is exceeded

### Key Technical Details

**ai-news.py:**

- **API Model**: Uses `gemini-3-flash-preview` with Google Search grounding tool
- **Encoding**: All content is explicitly encoded/decoded as UTF-8 with error handling (`errors='ignore'`)
- **Confluence Format**: Uses "storage" representation (XHTML) for Confluence Cloud
- **Page Structure**: Includes update timestamp, news content, and auto-generated footer with attribution

**check-ispo-shopback.py:**
- **Web Scraping**: Uses User-Agent header to avoid blocking, 10-second timeout for requests
- **Pattern Matching**: Multiple regex patterns to handle various cashback display formats
- **Threshold-based Alerts**: Only sends notifications when cashback exceeds threshold (avoids spam)
- **LINE Notify API**: Simple HTTP POST with Bearer authentication

## Dependencies

- `python-dotenv`: Environment variable management
- `requests`: HTTP client for API calls (Confluence, LINE Notify, web scraping)
- `google-genai`: Google Generative AI SDK for Gemini API access
- `beautifulsoup4`: HTML parsing for web scraping (ShopBack)

## Error Handling

**ai-news.py** validates:
- Presence of required environment variables (GEMINI_API_KEY, CONFLUENCE_USERNAME, CONFLUENCE_API_TOKEN)
- API response validity
- HTTP status codes for Confluence API calls
- UTF-8 encoding for all text content

**check-ispo-shopback.py** validates:
- Presence of LINE_NOTIFY_TOKEN
- Network request success (with timeout)
- Cashback percentage extraction (multiple fallback patterns)
- LINE Notify API response status
