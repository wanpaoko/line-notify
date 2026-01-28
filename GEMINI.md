# Project: Line Notify & AI News Automation

This project contains a collection of Python scripts managed with `uv` for automating news fetching (using Google Gemini) and sending notifications via LINE (Messaging API & Notify) and Confluence.

## 📂 Key Files & Scripts

### 1. `my-news.py` (LINE Bot News)
-   **Purpose:** Fetches daily AI/LLM news using **Gemini 2.5 Pro** (with Google Search grounding) and sends a summary to a specific user via the **LINE Messaging API**.
-   **Key Dependencies:** `line-bot-sdk`, `google-genai`, `python-dotenv`.
-   **Env Vars Required:** `CHANNEL_ACCESS_TOKEN`, `USER_ID`, `GEMINI_API_KEY`.

### 2. `ai-news.py` (Confluence News)
-   **Purpose:** Fetches AI news using **Gemini 3 Flash** (preview) and automatically creates a new child page in **Confluence** with the summary.
-   **Key Dependencies:** `requests`, `google-genai`.
-   **Env Vars Required:** `GEMINI_API_KEY`, `CONFLUENCE_URL`, `CONFLUENCE_USERNAME`, `CONFLUENCE_API_TOKEN`, `CONFLUENCE_PARENT_PAGE_ID`.

### 3. `check-ispo-shopback.py` (ShopBack Monitor)
-   **Purpose:** Scrapes the ShopBack ISPO page to check for cashback rates. If the rate exceeds a configured threshold (default 9%), it sends a notification via **LINE Notify**.
-   **Key Dependencies:** `requests`, `beautifulsoup4`.
-   **Env Vars Required:** `LINE_NOTIFY_TOKEN`, `CASHBACK_THRESHOLD` (optional).

### 4. `SHOPBACK_SETUP.md`
-   **Purpose:** Documentation for setting up the ShopBack monitoring script.

## 🚀 Building and Running

This project uses `uv` for package management.

### Setup
1.  **Install uv** (if not already installed).
2.  **Install dependencies:**
    ```bash
    uv sync
    ```
3.  **Configure Environment:**
    Create a `.env` file based on `.env.example` (if available) or manual setup:
    ```bash
    cp .env.example .env
    # Edit .env with your API keys and tokens
    ```

### Running Scripts
Use `uv run` to execute the scripts within the managed environment:

```bash
# Run the LINE Bot AI News fetcher
uv run my-news.py

# Run the Confluence AI News publisher
uv run ai-news.py

# Run the ShopBack Cashback checker
uv run check-ispo-shopback.py
```

## 🛠 Development Conventions

-   **Package Management:** Strictly use `uv` for adding/removing packages (`uv add <package>`, `uv remove <package>`).
-   **Environment Variables:** All secrets and configuration (API Keys, Tokens, URLs) must be loaded from `.env` using `python-dotenv`.
-   **Code Style:** Standard Python PEP 8 conventions.
-   **AI Integration:** Uses Google's `google-genai` SDK (v1+) targeting Gemini models with Search Grounding tools.

## ⚠️ Notes
-   `my-news.py` uses `gemini-2.5-pro` while `ai-news.py` uses `gemini-3-flash-preview`. Ensure your API key has access to these models.
-   The Confluence script expects a specific page structure (Parent ID).
