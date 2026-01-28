import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv

# --- 讀取 .env ---
load_dotenv()

# --- 從環境變數讀取設定 ---
line_notify_token = os.environ.get("LINE_NOTIFY_TOKEN")
threshold_percentage = float(os.environ.get("CASHBACK_THRESHOLD", "9.0"))
shopback_url = "https://www.shopback.com.tw/ispo"


def get_shopback_cashback():
    """
    從 ShopBack ISPO 頁面取得現金回饋百分比
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(shopback_url, headers=headers, timeout=10)
        response.raise_for_status()

        # 解析 HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # 嘗試多種方式找到回饋百分比
        cashback_percentage = None

        # 方法 1: 尋找包含 "%" 和 "回饋" 的文字
        text_content = soup.get_text()

        # 尋找類似 "3% 現金回饋" 或 "全館商品 3%" 的模式
        patterns = [
            r'(\d+(?:\.\d+)?)\s*%\s*現金回饋',
            r'全館商品\s*(\d+(?:\.\d+)?)\s*%',
            r'(\d+(?:\.\d+)?)\s*%\s*回饋',
            r'高達\s*(\d+(?:\.\d+)?)\s*%',
        ]

        for pattern in patterns:
            match = re.search(pattern, text_content)
            if match:
                cashback_percentage = float(match.group(1))
                break

        # 方法 2: 尋找特定的 class 或 data attributes (根據實際網頁結構調整)
        if cashback_percentage is None:
            # 尋找可能包含回饋率的元素
            cashback_elements = soup.find_all(['span', 'div', 'p'],
                                             text=re.compile(r'\d+(?:\.\d+)?%'))

            for element in cashback_elements:
                text = element.get_text()
                match = re.search(r'(\d+(?:\.\d+)?)\s*%', text)
                if match:
                    cashback_percentage = float(match.group(1))
                    break

        if cashback_percentage is None:
            return None, "無法從頁面中找到回饋百分比資訊"

        return cashback_percentage, None

    except requests.exceptions.RequestException as e:
        return None, f"網路請求錯誤：{e}"
    except Exception as e:
        return None, f"處理資料時發生錯誤：{e}"


def send_line_notify(message):
    """
    發送訊息到 LINE Notify
    """
    if not line_notify_token:
        return False, "錯誤：尚未設定 LINE_NOTIFY_TOKEN 環境變數"

    try:
        url = "https://notify-api.line.me/api/notify"
        headers = {
            "Authorization": f"Bearer {line_notify_token}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "message": message
        }

        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()

        return True, "LINE 通知發送成功"

    except requests.exceptions.RequestException as e:
        return False, f"發送 LINE 通知失敗：{e}"


def main():
    """
    主程式：檢查 ShopBack ISPO 回饋並在超過門檻時發送 LINE 通知
    """
    print(f"正在檢查 ShopBack ISPO 回饋率...")
    print(f"目標網址：{shopback_url}")
    print(f"門檻值：{threshold_percentage}%\n")

    # 取得回饋百分比
    cashback, error = get_shopback_cashback()

    if error:
        print(f"✗ {error}")
        return

    print(f"✓ 目前回饋率：{cashback}%")

    # 檢查是否超過門檻
    if cashback > threshold_percentage:
        print(f"✓ 回饋率 {cashback}% 超過門檻 {threshold_percentage}%！")

        # 準備 LINE 訊息
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"""
🎉 ShopBack ISPO 高回饋通知

目前回饋率：{cashback}%
門檻值：{threshold_percentage}%
檢查時間：{now}

立即前往：{shopback_url}
"""

        print("\n正在發送 LINE 通知...")
        success, result_msg = send_line_notify(message)

        if success:
            print(f"✓ {result_msg}")
        else:
            print(f"✗ {result_msg}")
    else:
        print(f"✓ 回饋率 {cashback}% 未超過門檻 {threshold_percentage}%，不發送通知")


if __name__ == "__main__":
    main()
