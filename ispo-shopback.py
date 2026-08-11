import os
import re
import requests
import tomli
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    PushMessageRequest, TextMessage
)
from linebot.v3.messaging.exceptions import ApiException

# --- 讀取 .env ---
load_dotenv()

# --- 讀取 TOML 設定 ---
config_data = {}
config_path = "config/config.toml"
if os.path.exists(config_path):
    with open(config_path, "rb") as f:
        config_data = tomli.load(f)

# --- 從環境變數或 TOML 讀取設定 ---
line_notify_token = os.environ.get("LINE_NOTIFY_TOKEN")
channel_access_token = os.environ.get("CHANNEL_ACCESS_TOKEN")
# 從 config.toml 讀取 ispo user ids (清單)
ispo_user_ids = config_data.get("ispo", {}).get("USER_ID", [])
# 如果不是 list，轉成 list
if isinstance(ispo_user_ids, str):
    ispo_user_ids = [ispo_user_ids]

threshold_percentage = float(os.environ.get("CASHBACK_THRESHOLD", "10.0"))
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


def send_line_message(user_id, message):
    """
    發送訊息到指定的 LINE User ID (使用 Messaging API)
    """
    if not channel_access_token:
        return False, "錯誤：尚未設定 CHANNEL_ACCESS_TOKEN 環境變數"

    configuration = Configuration(access_token=channel_access_token)
    try:
        with ApiClient(configuration) as api_client:
            api_instance = MessagingApi(api_client)
            push_message_request = PushMessageRequest(
                to=user_id,
                messages=[TextMessage(text=message)]
            )
            api_instance.push_message(push_message_request)
        return True, f"訊息成功發送至 {user_id}"
    except ApiException as e:
        return False, f"發送訊息至 {user_id} 失敗 (LINE API): {e.reason}"
    except Exception as e:
        return False, f"發生未預期的錯誤: {e}"


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

        # 1. 發送 LINE Notify
        if line_notify_token:
            print("\n正在發送 LINE Notify 通知...")
            success, result_msg = send_line_notify(message)
            if success:
                print(f"✓ {result_msg}")
            else:
                print(f"✗ {result_msg}")

        # 2. 發送 LINE Messaging API (to multiple users)
        if ispo_user_ids:
            if not channel_access_token:
                print("\n✗ 錯誤：設定了 USER_ID 但未提供 CHANNEL_ACCESS_TOKEN，無法發送 Messaging API 訊息。")
            else:
                print(f"\n正在發送 Messaging API 訊息至 {len(ispo_user_ids)} 位使用者...")
                for uid in ispo_user_ids:
                    success, result_msg = send_line_message(uid, message)
                    if success:
                        print(f"✓ {result_msg}")
                    else:
                        print(f"✗ {result_msg}")

    else:
        print(f"✓ 回饋率 {cashback}% 未超過門檻 {threshold_percentage}%，不發送通知")


if __name__ == "__main__":
    main()
