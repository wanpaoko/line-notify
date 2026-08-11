import os
import requests
import tomli
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

# 從 config.toml 讀取 user ids (優先使用 [garmin-run]，次之使用 [jimko])
user_ids = config_data.get("garmin-run", {}).get("USER_ID")
# 如果不是 list，轉成 list
if isinstance(user_ids, str):
    user_ids = [user_ids]


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
    主程式：單純發送 Garmin Run 報名通知訊息
    """
    message = "Garmin Run 2026即將開始報名，https://bao-ming.com/eb/content/7032#32972"
    print(f"準備發送通知訊息：\n{message}\n")

    # 1. 發送 LINE Notify
    if line_notify_token:
        print("正在發送 LINE Notify 通知...")
        success, result_msg = send_line_notify(message)
        if success:
            print(f"✓ {result_msg}")
        else:
            print(f"✗ {result_msg}")
    else:
        print("⚠️ 未設定 LINE_NOTIFY_TOKEN，跳過 LINE Notify 通知。")

    # 2. 發送 LINE Messaging API (to multiple users)
    if user_ids:
        if not channel_access_token:
            print("✗ 錯誤：設定了 USER_ID 但未提供 CHANNEL_ACCESS_TOKEN，無法發送 Messaging API 訊息。")
        else:
            print(f"正在發送 Messaging API 訊息至 {len(user_ids)} 位使用者...")
            for uid in user_ids:
                success, result_msg = send_line_message(uid, message)
                if success:
                    print(f"✓ {result_msg}")
                else:
                    print(f"✗ {result_msg}")
    else:
        print("ℹ️ 未在 config/config.toml 中設定 [garmin-run].USER_ID 或 [jimko].USER_ID，跳過 Messaging API 通知。")


if __name__ == "__main__":
    main()
