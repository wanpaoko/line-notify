# LINE Notify & AI 新聞自動化推播腳本集

本專案是一套基於 Python 與 `uv` 套件管理的自動化腳本集合。結合 **Google Gemini API** (具備 Google Search 實時搜尋能力)、**LINE Messaging API** 與 **LINE Notify**，實現每日 AI/股市新聞摘要、特惠回饋監控、生日祝福發送及股價警示等自動化功能。

---

## ✨ 功能腳本一覽

| 腳本名稱 | 功能說明 | 主要技術 / API | 推播管道 |
| :--- | :--- | :--- | :--- |
| 🤖 **`ai-news.py`** | 自動抓取最新 AI / LLM 技術新聞並生成簡短摘要 | Gemini 2.5 Flash + Google Search Grounding | LINE Messaging API (`[news]`) |
| 📈 **`stock-news.py`** | 自動抓取今日台股頭條與大盤/個股趨勢預測 | Gemini 2.5 Flash + Google Search Grounding | LINE Messaging API (`[stock]`) |
| 🛍️ **`ispo-shopback.py`** | 監控 ShopBack ISPO 現金回饋率，超過設定門檻即發送推播 | Web Scraping (BeautifulSoup4) | LINE Notify & LINE Messaging API (`[ispo]`) |
| 🎂 **`birthday-notify.py`** | 比對當天生日好友，使用 AI 產生個性化祝福語並發送通知 | Gemini API + `birthday-config.json` | LINE Messaging API |
| 🏃 **`garmin-run.py`** | 發送 Garmin Run 賽事報名開跑通知 | LINE SDK & Requests | LINE Notify & LINE Messaging API (`[garmin-run]`) |
| 💻 **`check_tsmc_price.py`** | 監控台積電 (2330.TW) 股價，跌破設定門檻時輸出警示 | Yahoo 奇摩股市爬蟲 | Console 輸出 (可搭配主控端整合) |

---

## ⚙️ 環境準備與套件安裝

本專案建議使用 [`uv`](https://github.com/astral-sh/uv) 進行快速高效的 Python 虛擬環境與依賴管理。

### 1. 安裝套件

```bash
# 複製專案
git clone <your-repository-url>
cd line-notify

# 使用 uv 自動同步並建立虛擬環境
uv sync
```

*(若使用傳統 `pip`，可執行 `python3 -m venv .venv && source .venv/bin/activate && pip install .`)*

---

## 🛠️ 設定檔說明與範例

專案提供完整的範例設定檔，使用前請先複製並填入對應的 API Key 與 USER ID。

### 1. `.env` (環境變數設定)
複製 `.env.example` 為 `.env`：
```bash
cp .env.example .env
```

`.env` 內容說明：
```env
# Google Gemini API 金鑰 (用於 ai-news.py, stock-news.py, birthday-notify.py)
GEMINI_API_KEY=your-gemini-api-key-here

# LINE Messaging API Channel Access Token (用於多數腳本發送 LINE Push Message)
CHANNEL_ACCESS_TOKEN=your-channel-access-token-here
USER_ID=your-default-line-user-id-here

# LINE Notify Token (用於 ispo-shopback.py, garmin-run.py)
LINE_NOTIFY_TOKEN=your-line-notify-token-here

# ShopBack ISPO 回饋百分比門檻（預設 10.0%）
CASHBACK_THRESHOLD=10.0
```

### 2. `config/config.toml` (群組/使用者 LINE ID 設定)
複製 `config/config.toml.example` 為 `config/config.toml`：
```bash
cp config/config.toml.example config/config.toml
```

`config/config.toml` 內容說明：
```toml
[news]
# 用於 ai-news.py：接收每日 AI 新聞摘要的 LINE User ID 清單
USER_ID = ["C1234567890abcdef1234567890abcdef"]

[stock]
# 用於 stock-news.py：接收每日台股頭條的 LINE User ID 清單
USER_ID = ["U1234567890abcdef1234567890abcdef"]

[ispo]
# 用於 ispo-shopback.py：接收 ShopBack 高回饋通知的 LINE User ID 清單
USER_ID = ["U1234567890abcdef1234567890abcdef", "C1234567890abcdef1234567890abcdef"]

[garmin-run]
# 用於 garmin-run.py：接收 Garmin Run 報名通知的 LINE User ID 清單
USER_ID = ["C1234567890abcdef1234567890abcdef"]

[trend]
# 專屬群組或備用 ID 設定
USER_ID = ["C9876543210abcdef9876543210abcdef"]
```

### 3. `config/birthday-config.json` (生日通知設定)
複製 `config/birthday-config.json.example` 為 `config/birthday-config.json`：
```bash
cp config/birthday-config.json.example config/birthday-config.json
```

`config/birthday-config.json` 內容說明：
```json
{
  "lineIds": {
    "長榮馬": "C1234567890abcdef1234567890abcdef",
    "忍太郎": "U1234567890abcdef1234567890abcdef",
    "小資": "C9876543210abcdef9876543210abcdef"
  },
  "birthdayFriends": [
    { "month": 2, "day": 26, "name": "Darren", "id": "小資" },
    { "month": 8, "day": 8,  "name": "忍太郎", "id": "個人ID" }
  ]
}
```

---

## 🚀 執行方式

使用 `uv run` 可以直接在專案環境下執行指定的腳本：

```bash
# 1. 執行 AI 新聞摘要推播
uv run ai-news.py

# 2. 執行台股頭條與預測推播
uv run stock-news.py

# 3. 檢查 ShopBack ISPO 現金回饋率
uv run ispo-shopback.py

# 4. 執行每日生日祝福檢查與推播
uv run birthday-notify.py

# 5. 發送 Garmin Run 報名通知
uv run garmin-run.py

# 6. 檢查台積電股價 (預設門檻 1700，可自訂門檻參數)
uv run check_tsmc_price.py
uv run check_tsmc_price.py 1650
```

---

## 🕒 設定 Crontab 排程自動化

若需每日定期自動執行推播，可在伺服器上設定 `crontab`：

```bash
# 輸入 crontab -e 加入以下排程範例

# 每日 08:30 發送 AI 新聞
30 8 * * * cd /path/to/line-notify && /usr/local/bin/uv run ai-news.py >> logs/ai-news.log 2>&1

# 每日 08:45 發送股市新聞
45 8 * * * cd /path/to/line-notify && /usr/local/bin/uv run stock-news.py >> logs/stock-news.log 2>&1

# 每日 09:00 檢查生日並發送祝福
0 9 * * * cd /path/to/line-notify && /usr/local/bin/uv run birthday-notify.py >> logs/birthday-notify.log 2>&1

# 每小時檢查 ShopBack 回饋
0 * * * * cd /path/to/line-notify && /usr/local/bin/uv run ispo-shopback.py >> logs/ispo.log 2>&1
```

---

## 🔧 故障排除

1. **LINE Messaging API (401 / 403 錯誤)**：
   - 請檢查 `.env` 中的 `CHANNEL_ACCESS_TOKEN` 是否正確且未過期。
   - 確認 `config/config.toml` 或 `.env` 中的 `USER_ID` (User ID / Group ID / Room ID) 格式是否正確。
2. **Gemini API 錯誤**：
   - 請確認 `GEMINI_API_KEY` 已設定且配額充裕。
3. **ShopBack 抓取失敗**：
   - 可能是目標網頁 HTML 結構有變更，請檢視 `ispo-shopback.py` 中的 Regex 匹配邏輯。

---

## 📝 授權

MIT License
