# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains three Python automation scripts for monitoring and notifications:

1. **ai-news.py**: Fetches latest AI/LLM news using Google Gemini 2.5 Flash with Google Search grounding and sends formatted summaries via LINE Messaging API to configured users.

2. **ispo-shopback.py**: Monitors ShopBack's ISPO cashback rate via web scraping and sends LINE notifications (via both LINE Notify and LINE Messaging API) when cashback exceeds a threshold.

3. **check_tsmc_price.py**: Monitors TSMC stock price (2330.TW) from Yahoo Finance Taiwan and alerts when price drops below a threshold.

## Development Setup

### Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows

# Install dependencies
pip install -e .
# Or manually install from pyproject.toml dependencies
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

**For check_tsmc_price.py:**
- No environment variables required
- Threshold can be passed as command-line argument

### Running the Scripts
```bash
# Run AI news fetcher and send to LINE
python ai-news.py

# Run ShopBack ISPO cashback checker
python ispo-shopback.py

# Run TSMC stock price checker
python check_tsmc_price.py           # Uses default threshold (1700)
python check_tsmc_price.py 1650      # Custom threshold
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

### check_tsmc_price.py Components

1. **Price Fetching (`get_tsmc_price()`)** (check_tsmc_price.py:12-56)
   - Scrapes Yahoo Finance Taiwan: https://tw.stock.yahoo.com/quote/2330.TW
   - Uses regex to find "成交" (traded price) pattern
   - Falls back to "最低" (lowest price) if "成交" not found
   - Returns integer price or None on error

2. **Check and Notify (`check_and_notify()`)** (check_tsmc_price.py:58-75)
   - Compares current price against threshold
   - Prints notification message if below threshold
   - Currently prints to stdout (no LINE integration)

3. **Command-line Interface** (check_tsmc_price.py:77-87)
   - Accepts optional threshold as first argument
   - Default threshold: 1700
   - Usage: `python check_tsmc_price.py [threshold]`

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

**check_tsmc_price.py specific:**
- Simple stdout notification (no LINE integration yet)
- Command-line configurable threshold
- Fallback price detection patterns

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

**check_tsmc_price.py:**
- Handles RequestException for network errors
- Validates integer parsing with ValueError
- Generic Exception handler with logging
- Returns None on any error in price fetching
