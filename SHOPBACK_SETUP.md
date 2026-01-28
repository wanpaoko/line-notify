# ShopBack ISPO 回饋監控設定指南

## 功能說明

`check-ispo-shopback.py` 會自動監控 ShopBack ISPO 的現金回饋率，當回饋率超過設定的門檻（預設 9%）時，自動發送 LINE 通知到你的群組或個人。

## 設定步驟

### 1. 取得 LINE Notify Token

1. 前往 [LINE Notify](https://notify-bot.line.me/)
2. 登入你的 LINE 帳號
3. 點選右上角的「個人頁面」
4. 點選「發行權杖」
5. 選擇要接收通知的聊天室（可以選擇個人或群組）
6. 輸入權杖名稱（例如：ShopBack ISPO 監控）
7. 複製生成的 Token（只會顯示一次，請妥善保存）

### 2. 設定環境變數

在 `.env` 檔案中加入以下設定：

```bash
# LINE Notify 設定
LINE_NOTIFY_TOKEN=你的LINE Notify Token

# 回饋百分比門檻（可選，預設為 9.0）
CASHBACK_THRESHOLD=9.0
```

### 3. 安裝相依套件

如果尚未安裝，請執行：

```bash
pip install -r requirements.txt
```

這會安裝 `beautifulsoup4`（用於網頁解析）。

### 4. 測試執行

```bash
python check-ispo-shopback.py
```

執行結果範例：

```
正在檢查 ShopBack ISPO 回饋率...
目標網址：https://www.shopback.com.tw/ispo
門檻值：9.0%

✓ 目前回饋率：3.0%
✓ 回饋率 3.0% 未超過門檻 9.0%，不發送通知
```

當回饋率超過門檻時：

```
正在檢查 ShopBack ISPO 回饋率...
目標網址：https://www.shopback.com.tw/ispo
門檻值：9.0%

✓ 目前回饋率：12.0%
✓ 回饋率 12.0% 超過門檻 9.0%！

正在發送 LINE 通知...
✓ LINE 通知發送成功
```

## 設定定時執行

### 使用 cron（Linux/macOS）

編輯 crontab：

```bash
crontab -e
```

加入以下內容（每小時執行一次）：

```bash
0 * * * * cd /path/to/line-notify && /path/to/venv/bin/python check-ispo-shopback.py
```

或每 30 分鐘執行一次：

```bash
*/30 * * * * cd /path/to/line-notify && /path/to/venv/bin/python check-ispo-shopback.py
```

### 使用 Windows 工作排程器

1. 開啟「工作排程器」
2. 建立基本工作
3. 設定觸發程序（例如：每小時）
4. 動作：啟動程式
   - 程式：`C:\path\to\venv\Scripts\python.exe`
   - 引數：`check-ispo-shopback.py`
   - 起始於：`C:\path\to\line-notify`

## 自訂設定

### 調整門檻值

在 `.env` 檔案中修改：

```bash
CASHBACK_THRESHOLD=8.5  # 改為 8.5%
```

### 停用通知測試

如果只想查看目前回饋率而不發送通知，可以設定一個非常高的門檻值：

```bash
CASHBACK_THRESHOLD=99.9
```

## 故障排除

### 無法取得回饋率

如果顯示「無法從頁面中找到回饋百分比資訊」：
1. ShopBack 網站可能改版，調整了 HTML 結構
2. 網路連線問題
3. 網站暫時無法存取

可以手動訪問 https://www.shopback.com.tw/ispo 確認網站狀態。

### LINE 通知發送失敗

檢查：
1. LINE_NOTIFY_TOKEN 是否正確
2. Token 是否已過期或被撤銷
3. 網路連線是否正常

### 收到太多通知

如果回饋率長時間維持在門檻以上，每次執行都會發送通知。建議：
1. 調高門檻值
2. 減少執行頻率
3. 可以修改腳本加入「冷卻時間」機制（需要額外開發）
