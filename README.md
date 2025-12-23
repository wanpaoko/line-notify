# AI 新聞自動更新到 Confluence

這是一個 Python 腳本，它會自動使用 Google 最新的 Gemini 2.5 Flash 模型結合 Google 搜尋，取得最新的 5 則 AI/LLM 技術新聞，並將摘要整理後，自動在指定的 Confluence 頁面下建立新的子頁面。

## ✨ 功能

-   **自動化新聞摘要**：自動抓取最新的 5 則 AI 技術新聞。
-   **先進的 AI 模型**：使用 Gemini 2.5 Flash 搭配 Google Search grounding 產生高品質、Markdown 格式的摘要。
-   **自動建立 Confluence 子頁面**：每次執行會在指定的父頁面下建立新的子頁面，標題包含日期（例如：AI 新聞摘要 - 2025-12-23）。
-   **簡易設定**：只需要幾個環境變數即可完成設定。

## ⚙️ 設定步驟

### 1. 取得必要的金鑰

在開始之前，請先準備好以下資訊：

#### Gemini API Key
前往 [Google AI Studio](https://aistudio.google.com/app/apikey) 取得你的 API 金鑰。

#### Confluence API Token
1. 前往 [Atlassian API Tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. 點擊「Create API token」
3. 為 token 命名（例如：AI-News-Updater）
4. 複製生成的 token（只會顯示一次）

#### Confluence 父頁面 ID
從 Confluence 頁面 URL 中取得父頁面 ID（新頁面會建立在此頁面之下）。例如：
```
https://trendmicro.atlassian.net/wiki/spaces/TrendLifeRD/pages/1969488035/AI
                                                                    ^^^^^^^^^^ 這是父頁面 ID
```

### 2. 安裝專案

```bash
# 1. 複製這個專案
git clone <your-repository-url>
cd ai-news-update

# 2. 建立並啟用虛擬環境
python3 -m venv venv
source venv/bin/activate

# 3. 安裝必要的套件
pip install -r requirements.txt
```

### 3. 設定環境變數

將 `.env.example` 檔案複製為 `.env`，並填入你的設定：

```bash
cp .env.example .env
```

編輯 `.env` 檔案：

```
GEMINI_API_KEY=你的 Gemini API Key
CONFLUENCE_URL=https://trendmicro.atlassian.net
CONFLUENCE_USERNAME=你的 Email（Atlassian 帳號）
CONFLUENCE_API_TOKEN=你的 Confluence API Token
CONFLUENCE_PARENT_PAGE_ID=1969488035
```

## 🚀 如何執行

完成設定後，直接執行主程式即可：

```bash
python ai-news.py
```

程式會：
1. 使用 Gemini 2.5 Flash 搭配 Google Search 搜尋最新的 5 則 AI 新聞
2. 將新聞整理成 Markdown 格式
3. 在指定的父頁面下自動建立新的子頁面（標題包含當天日期）

執行結果範例：
```
正在獲取最新 AI 新聞...

成功獲取新聞內容：
------------------------------------------------------------
### 1. OpenAI 發布 GPT-5
...
------------------------------------------------------------

正在建立新的 Confluence 子頁面（父頁面 ID: 1969488035）...
✓ 成功建立新頁面！頁面 ID：1970123456
✓ 頁面連結：https://trendmicro.atlassian.net/wiki/spaces/TrendLifeRD/pages/1970123456
```

## 🕒 設定定時任務 (選用)

若希望每日自動執行，可以將此腳本設定為 `cron` 定時任務。例如，設定每天早上 9 點執行：

```bash
# 輸入 crontab -e，並加入以下這行
0 9 * * * /path/to/your/project/venv/bin/python /path/to/your/project/ai-news.py
```

或者使用 GitHub Actions 定時執行（需要額外設定）。

## 🔧 故障排除

### API Token 錯誤
確認你的 Confluence API Token 是否正確，且 Email 必須是你的 Atlassian 帳號。

### 頁面建立失敗
確認：
1. 父頁面 ID 是否正確
2. 你的帳號是否有在該父頁面下建立子頁面的權限
3. Confluence URL 是否正確（不需要包含 /wiki 後綴）
4. Space key 是否正確（預設為 TrendLifeRD）

### 找不到新聞
可能是 Google Search 暫時無法取得結果，稍後再試。

## 📝 授權

MIT License
