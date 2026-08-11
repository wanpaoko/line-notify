import json
import os
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    PushMessageRequest, TextMessage
)
from linebot.v3.messaging.exceptions import ApiException

load_dotenv()

channel_access_token = os.environ.get("CHANNEL_ACCESS_TOKEN")
gemini_api_key = os.environ.get("GEMINI_API_KEY")

BIRTHDAY_CONFIG_PATH = "config/birthday-config.json"


def load_birthday_config():
    with open(BIRTHDAY_CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_todays_birthdays(config):
    today = datetime.now()
    return [
        friend for friend in config["birthdayFriends"]
        if friend["month"] == today.month and friend["day"] == today.day
    ]


def generate_birthday_message(friend_name):
    if not gemini_api_key:
        return f"🎂 生日快樂，{friend_name}！祝你今天過得開心！"

    client = genai.Client(api_key=gemini_api_key)
    prompt = f"請為 {friend_name} 生成一句簡短的生日快樂祝福語，約 15-20 字，並包含 {friend_name}"

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=[types.Content(role="user", parts=[types.Part.from_text(text=prompt)])],
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0)
        )
    )
    return response.text.strip()


def main():
    if not channel_access_token:
        print("錯誤：請設定 CHANNEL_ACCESS_TOKEN 環境變數。")
        return

    config = load_birthday_config()
    line_ids = config["lineIds"]
    todays_birthdays = get_todays_birthdays(config)

    if not todays_birthdays:
        print("今天沒有生日。")
        return

    configuration = Configuration(access_token=channel_access_token)

    with ApiClient(configuration) as api_client:
        api_instance = MessagingApi(api_client)

        for friend in todays_birthdays:
            name = friend["name"]
            group_key = friend["id"]
            line_id = line_ids.get(group_key)

            if not line_id:
                print(f"警告：找不到 '{group_key}' 的 LINE ID，跳過 {name}。")
                continue

            print(f"正在為 {name} 生成生日祝福...")
            message = generate_birthday_message(name)
            print(f"訊息：{message}")

            try:
                api_instance.push_message(PushMessageRequest(
                    to=line_id,
                    messages=[TextMessage(text=message)]
                ))
                print(f"✓ 已發送至 {group_key}（{line_id}）")
            except ApiException as e:
                print(f"發送失敗 ({name}): {e.status} {e.reason} {e.body}")


if __name__ == "__main__":
    main()
