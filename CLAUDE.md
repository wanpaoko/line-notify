# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains several Python automation scripts for monitoring and notifications:

1. **ai-news.py**: Fetches latest AI/LLM news using Google Gemini 2.5 Flash with Google Search grounding and sends formatted summaries via LINE Messaging API to configured users.

2. **stock-news.py**: Fetches daily Taiwan stock headlines and market forecasts using Gemini 2.5 Flash with Google Search grounding, pushing via LINE Messaging API.

3. **ispo-shopback.py**: Monitors ShopBack's ISPO cashback rate via web scraping and sends LINE notifications (via both LINE Notify and LINE Messaging API) when cashback exceeds a threshold.

4. **birthday-notify.py**: Checks a configured list of birthdays for today's date, generates AI birthday wishes using Gemini, and sends push notifications via LINE Messaging API.

5. **garmin-run.py**: Sends Garmin Run registration notifications via LINE Notify and/or LINE Messaging API.

## Development Setup

### Environment Setup
We recommend using [`uv`](https://github.com/astral-sh/uv) for package management:
```bash
# Using uv (Recommended)
uv sync

# Or manually using pip
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
pip install .
```

### Configuration Files

The project uses two configuration methods:

1. **Environment variables (.env file)**:
   - Copy `.env.example` to `.env` and fill in values
   - Required for API keys and tokens

2. **TOML configuration (config/config.toml)**:
   - Used for USER_ID lists (supports multiple recipients)
   - Structure:
     ```toml
     [news]
     USER_ID = ["user_id_1", "user_id_2"]

     [ispo]
     USER_ID = ["user_id_1", "user_id_2"]
     ```

### Required Environment Variables

**For ai-news.py:**
- `GEMINI_API_KEY`: Google Gemini API key from https://aistudio.google.com/app/apikey
- `CHANNEL_ACCESS_TOKEN`: LINE Messaging API channel access token
- Optional: `USER_ID` (can be set in config.toml under `[news]` section)

**For ispo-shopback.py:**
- `CHANNEL_ACCESS_TOKEN`: LINE Messaging API channel access token
- `LINE_NOTIFY_TOKEN`: LINE Notify token from https://notify-bot.line.me/
- `CASHBACK_THRESHOLD`: Threshold percentage for alerts (default: 10.0)
- User IDs configured in config.toml under `[ispo]` section

### Running the Scripts
```bash
# Run AI news fetcher and send to LINE
uv run ai-news.py

# Run Taiwan stock news fetcher
uv run stock-news.py

# Run ShopBack ISPO cashback checker
uv run ispo-shopback.py

# Run birthday notifications
uv run birthday-notify.py

# Run Garmin Run notification
uv run garmin-run.py
```

## Architecture

### ai-news.py Components

1. **Configuration Loading** (ai-news.py:14-34)
   - Loads environment variables from .env
   - Reads config.toml for USER_ID lists
   - Supports both string and list formats for USER_ID
   - Falls back to environment variable if TOML config not present

2. **News Fetching (`get_ai_news()`)** (ai-news.py:36-93)
   - Uses Gemini 2.5 Flash model (`gemini-2.5-flash`)
   - Configures Google Search grounding tool for real-time search
   - Uses `thinking_config` with budget=-1 for extended thinking
   - Streams response chunks and concatenates them
   - Removes Markdown list symbols (`*`, `-`, `+`) from line starts
   - Returns formatted message: "每日 AI 新聞摘要 🤖 (YYYY-MM-DD)\n\n[news content]"

3. **LINE Message Sending (`main()`)** (ai-news.py:96-133)
   - Uses LINE Messaging API v3 SDK
   - Validates CHANNEL_ACCESS_TOKEN and USER_ID presence
   - Sends push messages to multiple users in loop
   - Handles ApiException with detailed error reporting

### ispo-shopback.py Components

1. **Configuration Loading** (ispo-shopback.py:14-34)
   - Loads both LINE Notify token and Messaging API token
   - Reads ISPO user IDs from config.toml `[ispo]` section
   - Converts string USER_ID to list if needed
   - Sets cashback threshold from environment (default: 10.0)

2. **Cashback Rate Extraction (`get_shopback_cashback()`)** (ispo-shopback.py:37-93)
   - Fetches HTML from https://www.shopback.com.tw/ispo
   - Uses BeautifulSoup for HTML parsing
   - Employs multiple regex patterns to extract cashback percentage:
     - `(\d+(?:\.\d+)?)\s*%\s*現金回饋`
     - `全館商品\s*(\d+(?:\.\d+)?)\s*%`
     - `(\d+(?:\.\d+)?)\s*%\s*回饋`
     - `高達\s*(\d+(?:\.\d+)?)\s*%`
   - Falls back to searching span/div/p elements for percentage
   - Returns tuple: (cashback_percentage, error_message)

3. **Dual Notification System**
   - **LINE Notify (`send_line_notify()`)** (ispo-shopback.py:96-119): Simple notification API using Bearer token
   - **LINE Messaging API (`send_line_message()`)** (ispo-shopback.py:122-142): Sends to specific user IDs with better formatting

4. **Main Logic (`main()`)** (ispo-shopback.py:145-205)
   - Fetches current cashback rate
   - Compares against threshold
   - If exceeded, sends notifications via BOTH:
     - LINE Notify (if token configured)
     - LINE Messaging API to all users in ispo USER_ID list
   - Message format includes: emoji, cashback rate, threshold, timestamp, URL

### Key Technical Details

**Common Patterns:**
- All scripts use `python-dotenv` for environment variable management
- All scripts use TOML configuration via `tomli` library
- Web scraping scripts use User-Agent headers to avoid blocking
- Error handling with try/except and detailed error messages

**ai-news.py specific:**
- Uses streaming API (`generate_content_stream`) for Gemini responses
- Thinking budget set to -1 (unlimited)
- Removes Markdown list symbols with regex: `re.sub(r"^[ \t]*[*+-][ \t]+", "", text, flags=re.MULTILINE)`

**ispo-shopback.py specific:**
- Supports dual notification channels (Notify + Messaging API)
- Only sends when threshold exceeded (avoids spam)
- Multiple regex patterns for robustness against HTML changes

## Dependencies

Key dependencies from pyproject.toml:
- `python-dotenv>=1.2.1`: Environment variable management
- `requests>=2.32.5`: HTTP client for API calls and web scraping
- `google-genai>=1.60.0`: Google Generative AI SDK for Gemini API
- `beautifulsoup4>=4.14.3`: HTML parsing for web scraping
- `line-bot-sdk>=3.22.0`: LINE Messaging API v3 SDK
- `tomli>=2.4.0`: TOML configuration file parsing

Requires Python >=3.10

## Error Handling

**ai-news.py:**
- Validates GEMINI_API_KEY presence
- Validates CHANNEL_ACCESS_TOKEN and USER_ID configuration
- Catches ApiException from LINE SDK with detailed logging
- Generic Exception handler for unexpected errors

**ispo-shopback.py:**
- Validates LINE_NOTIFY_TOKEN and CHANNEL_ACCESS_TOKEN
- Returns error tuples from scraping function
- Handles RequestException for network errors
- Separate error handling for Notify vs Messaging API
