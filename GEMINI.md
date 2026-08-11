# Project: Line Notify & AI News Automation

This project contains a collection of Python scripts managed with `uv` for automating news fetching (using Google Gemini) and sending notifications via LINE (Messaging API & LINE Notify).

## 📂 Key Files & Scripts

### 1. `ai-news.py` (AI News via LINE Bot)
- **Purpose:** Fetches daily AI/LLM news using **Gemini 2.5 Flash** (with Google Search grounding) and sends a summary via **LINE Messaging API**.
- **Key Dependencies:** `line-bot-sdk`, `google-genai`, `python-dotenv`, `tomli`.
- **Env Vars Required:** `CHANNEL_ACCESS_TOKEN`, `GEMINI_API_KEY`.
- **Config File:** `config/config.toml` under `[news] USER_ID`.

### 2. `stock-news.py` (Taiwan Stock News via LINE Bot)
- **Purpose:** Fetches daily Taiwan stock headlines & market forecast using **Gemini 2.5 Flash** (with Google Search grounding) and sends a summary via **LINE Messaging API**.
- **Key Dependencies:** `line-bot-sdk`, `google-genai`, `python-dotenv`, `tomli`.
- **Env Vars Required:** `CHANNEL_ACCESS_TOKEN`, `GEMINI_API_KEY`.
- **Config File:** `config/config.toml` under `[stock] USER_ID`.

### 3. `ispo-shopback.py` (ShopBack Cashback Monitor)
- **Purpose:** Scrapes the ShopBack ISPO page for cashback rates. If rate exceeds threshold (default 10.0%), sends notifications via **LINE Notify** and/or **LINE Messaging API**.
- **Key Dependencies:** `requests`, `beautifulsoup4`, `line-bot-sdk`, `tomli`.
- **Env Vars Required:** `LINE_NOTIFY_TOKEN` (optional), `CHANNEL_ACCESS_TOKEN` (optional), `CASHBACK_THRESHOLD` (optional).
- **Config File:** `config/config.toml` under `[ispo] USER_ID`.

### 4. `birthday-notify.py` (Birthday Greetings Generator)
- **Purpose:** Checks `config/birthday-config.json` for birthdays matching today's date, generates AI birthday wishes using Gemini, and sends push notifications via **LINE Messaging API**.
- **Key Dependencies:** `line-bot-sdk`, `google-genai`, `python-dotenv`.
- **Env Vars Required:** `CHANNEL_ACCESS_TOKEN`, `GEMINI_API_KEY`.
- **Config File:** `config/birthday-config.json`.

### 5. `garmin-run.py` (Garmin Run Registration Alert)
- **Purpose:** Sends Garmin Run registration notifications via **LINE Notify** and/or **LINE Messaging API**.
- **Config File:** `config/config.toml` under `[garmin-run] USER_ID`.

### 6. `check_tsmc_price.py` (TSMC Stock Monitor)
- **Purpose:** Scrapes Yahoo Finance Taiwan for TSMC stock price (2330.TW) and alerts when price falls below threshold.

## 🚀 Building and Running

This project uses `uv` for package management.

### Setup
1. **Install uv** (if not already installed).
2. **Install dependencies:**
   ```bash
   uv sync
   ```
3. **Configure Environment:**
   ```bash
   cp .env.example .env
   cp config/config.toml.example config/config.toml
   cp config/birthday-config.json.example config/birthday-config.json
   ```

### Running Scripts
Use `uv run` to execute scripts:

```bash
uv run ai-news.py
uv run stock-news.py
uv run ispo-shopback.py
uv run birthday-notify.py
uv run garmin-run.py
uv run check_tsmc_price.py
```

## 🛠 Development Conventions

- **Package Management:** Strictly use `uv` (`uv add <package>`, `uv remove <package>`).
- **Environment Variables:** All secrets and configuration (API Keys, Tokens) are loaded from `.env` using `python-dotenv`.
- **Code Style:** Standard Python PEP 8 conventions.
- **AI Integration:** Uses Google's `google-genai` SDK with Search Grounding tools.
