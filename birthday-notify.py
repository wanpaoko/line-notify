import argparse
import json
import logging
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from google import genai
from google.genai import types
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    PushMessageRequest, TextMessage, StickerMessage
)
from linebot.v3.messaging.exceptions import ApiException

load_dotenv()

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

channel_access_token = os.environ.get("CHANNEL_ACCESS_TOKEN")
gemini_api_key = os.environ.get("GEMINI_API_KEY")

BIRTHDAY_CONFIG_PATH = "config/birthday-config.json"
TAIPEI_TZ = ZoneInfo("Asia/Taipei")

# 生日貼圖設定 (LINE 官方貼圖: Package 446, Sticker 1989)
STICKER_PACKAGE_ID = "446"
STICKER_ID = "1989"


def load_birthday_config():
    with open(BIRTHDAY_CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_todays_birthdays(config):
    today = datetime.now(TAIPEI_TZ)
    logger.info(f"今天日期（台北時間）：{today.month}月{today.day}日")
    return [
        friend for friend in config.get("birthdayFriends", [])
        if friend["month"] == today.month and friend["day"] == today.day
    ]


def generate_birthday_message(friend_name):
    if not gemini_api_key:
        logger.warning("未設定 GEMINI_API_KEY，使用預設祝福語。")
        return f"🎂 生日快樂，{friend_name}！祝你今天過得開心！"

    client = genai.Client(api_key=gemini_api_key)
    prompt = f"請為 {friend_name} 生成一句簡短的生日快樂祝福語，約 20-30 字，並包含 {friend_name}"

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=[types.Content(role="user", parts=[types.Part.from_text(text=prompt)])],
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=-1)
            )
        )
        return response.text.strip()
    except Exception as e:
        logger.error(f"Gemini 生成失敗 ({e})，使用預設祝福語。")
        return f"🎂 生日快樂，{friend_name}！祝你今天過得開心！"


def send_push_notification(api_instance, target_line_id, message_text, recipient_desc=""):
    """
    發送包含文字與生日貼圖的推播訊息
    """
    messages = [
        TextMessage(text=message_text),
        StickerMessage(package_id=STICKER_PACKAGE_ID, sticker_id=STICKER_ID)
    ]
    try:
        api_instance.push_message(PushMessageRequest(
            to=target_line_id,
            messages=messages
        ))
        logger.info(f"✓ 已發送至 {recipient_desc}（{target_line_id}）")
        return True
    except ApiException as e:
        logger.error(f"發送失敗 ({recipient_desc}): {e.status} {e.reason} {e.body}")
        return False


def main():
    parser = argparse.ArgumentParser(description="LINE 生日祝福機器人")
    parser.add_argument(
        "--test",
        action="store_true",
        help="測試模式：不檢查生日，直接發送測試訊息與貼圖到「個人ID」",
    )
    args = parser.parse_args()

    if not channel_access_token:
        logger.error("錯誤：請設定 CHANNEL_ACCESS_TOKEN 環境變數。")
        return

    try:
        config = load_birthday_config()
    except Exception as e:
        logger.error(f"讀取生日設定檔失敗 ({BIRTHDAY_CONFIG_PATH}): {e}")
        return

    line_ids = config.get("lineIds", {})
    configuration = Configuration(access_token=channel_access_token)

    with ApiClient(configuration) as api_client:
        api_instance = MessagingApi(api_client)

        if args.test:
            target_key = (
                "個人ID" if "個人ID" in line_ids
                else ("個人" if "個人" in line_ids else (next(iter(line_ids.keys())) if line_ids else None))
            )
            target_line_id = line_ids.get(target_key) if target_key else None

            if not target_line_id:
                logger.error("錯誤：LINE_IDS 對照表中找不到測試目標（例如「個人ID」或「個人」），無法發送測試訊息。")
                return

            logger.info(f"測試模式：準備發送測試訊息至 [{target_key}] ({target_line_id})")
            test_message = generate_birthday_message("測試")
            logger.info(f"測試訊息：{test_message}")
            send_push_notification(api_instance, target_line_id, test_message, recipient_desc=f"測試: {target_key}")
            return

        todays_birthdays = get_todays_birthdays(config)
        if not todays_birthdays:
            logger.info("今天沒有朋友過生日。")
            return

        for friend in todays_birthdays:
            name = friend.get("name", "朋友")
            group_key = friend.get("id")
            line_id = line_ids.get(group_key)

            if not line_id:
                logger.warning(f"警告：找不到 '{group_key}' 的 LINE ID，跳過 {name}。")
                continue

            logger.info(f"偵測到壽星：{name}，正在為其生成生日祝福...")
            message = generate_birthday_message(name)
            logger.info(f"訊息：{message}")
            send_push_notification(api_instance, line_id, message, recipient_desc=f"{name} ({group_key})")


if __name__ == "__main__":
    main()
