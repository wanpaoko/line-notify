# LINE AI 新聞摘要通知機器人

這是一個 Python 腳本，它會自動使用 Google 最新的 Gemini 2.5 Pro 模型結合 Google 搜尋，取得最新的 AI/LLM 技術新聞，並將摘要整理後，透過 LINE Messaging API 發送給你。

## ✨ 功能

-   **自動化新聞摘要**：每日自動抓取最新的 AI 技術新聞。
-   **先進的 AI 模型**：使用 Gemini 2.5 Pro 產生高品質、條列式的摘要。
-   **即時 LINE 通知**：將整理好的新聞摘要直接推送到你的 LINE。
-   **簡易設定**：只需要幾個環境變數即可完成設定。

## ⚙️ 設定步驟

### 1. 取得必要的金鑰

在開始之前，請先準備好以下三項資訊：

-   **LINE Channel Access Token**: 前往 [LINE Developers Console](https://developers.line.biz/console/) 建立一個 Messaging API channel，並從 "Channel access token" 頁籤取得。
-   **LINE User ID**: 這是你的個人 LINE ID，用來接收訊息。你可以透過加入 LINE 官方的「LINE Developers」帳號，它會自動回傳你的 User ID。
-   **Gemini API Key**: 前往 [Google AI Studio](https://aistudio.google.com/app/apikey) 取得你的 API 金鑰。

### 2. 安裝專案

```bash
# 1. 複製���個專案
git clone <your-repository-url>
cd line-news-notify

# 2. 建立並啟用虛擬環境
python3 -m venv venv
source venv/bin/activate

# 3. 安裝必要的套件
pip install -r requirements.txt
```

### 3. 設定環境變數

將專案中的 `.env.example` 檔案（如果有的話，若沒有請手動建立）複製為 `.env`，並填入你第一步取得的金鑰：

```
CHANNEL_ACCESS_TOKEN="你的 LINE Channel Access Token"
USER_ID="你的 LINE User ID"
GEMINI_API_KEY="你的 Gemini API Key"
```

## 🚀 如何執行

完成設定後，直接執行主程式即可：

```bash
python ai-news.py
```

腳本會執行一次，發送新聞摘要後即結束。

## 🕒 設定定時任務 (選用)

若希望每日自動執行，可以將此腳本設定為 `cron` 定時任務。例如，設定每天早上 9 點執行：

```bash
# 輸入 crontab -e，並加入以下這行
0 9 * * * /path/to/your/project/venv/bin/python /path/to/your/project/ai-news.py
```
