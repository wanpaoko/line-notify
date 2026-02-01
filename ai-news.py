import os
import re
from datetime import datetime
from dotenv import load_dotenv
import tomli
from google import genai
from google.genai import types
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
channel_access_token = os.environ.get("CHANNEL_ACCESS_TOKEN")
gemini_api_key = os.environ.get("GEMINI_API_KEY")

# 優先從 config.toml 讀取 USER_ID (可能是 list 或 str)
user_ids = config_data.get("news", {}).get("USER_ID") or os.environ.get("USER_ID")
# 確保轉為 list
if isinstance(user_ids, str):
    user_ids = [user_ids]
elif user_ids is None:
    user_ids = []

def get_ai_news():
    """
    從 Gemini 2.5 + Google Search 獲取最新 AI 新聞摘要
    """

    today = datetime.now().strftime("%Y-%m-%d")

    if not gemini_api_key:
        return "錯誤：尚未設定 GEMINI_API_KEY 環境變數。"

    try:
        # 設定 Gemini API Client
        client = genai.Client(api_key=gemini_api_key)

        prompt_text = (
            f"今天是 {today}，請搜尋最近 5 則與 AI 或 LLM 相關的技術新聞。\n\n"
            "請遵守以下格式規定：\n"
            "每則新聞格式範例：\n"
            "** [新聞標題] **\n"
            "[簡短摘要, 約20-30字]\n"
        )

        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt_text)],
            )
        ]

        # 啟用 Google Search 工具
        tools = [types.Tool(googleSearch=types.GoogleSearch())]

        config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=-1),
            tools=tools
        )

        # 使用 generate_content_stream 取得新聞摘要
        news_summary = ""
        for chunk in client.models.generate_content_stream(
            model="gemini-2.5-flash",
            contents=contents,
            config=config
        ):
            news_summary += chunk.text

        # 移除行首的 Markdown 清單符號 (例如 "* ", "- ")
        news_summary = re.sub(r"^[ \t]*[*+-][ \t]+", "", news_summary, flags=re.MULTILINE)
        # 清理多餘的空白行或開頭結尾空白
        news_summary = news_summary.strip()

        if news_summary:
            return f"每日 AI 新聞摘要 🤖 ({today})\n\n{news_summary}"
        else:
            return "目前找不到最新的 AI 新聞。"

    except Exception as e:
        return f"處理新聞時發生未知錯誤: {e}"


def main():
    """
    主程式：檢查設定並發送 LINE 訊息
    """
    if not channel_access_token:
        print("錯誤：請設定 CHANNEL_ACCESS_TOKEN 環境變數。")
        return
    
    if not user_ids:
        print("錯誤：請在 config.toml 或環境變數中設定 USER_ID。")
        return

    configuration = Configuration(access_token=channel_access_token)
    message_text = get_ai_news()

    print(f"準備發送訊息至 {len(user_ids)} 位使用者...")
    print(f"內容摘要:\n---\n{message_text[:100]}...\n---")

    try:
        with ApiClient(configuration) as api_client:
            api_instance = MessagingApi(api_client)
            for uid in user_ids:
                push_message_request = PushMessageRequest(
                    to=uid,
                    messages=[TextMessage(text=message_text)]
                )
                api_instance.push_message(push_message_request)
                print(f"✓ 訊息成功發送至 {uid}")

    except ApiException as e:
        print(f"發送訊息時發生錯誤 (LINE API): {e.status}")
        print(f"原因: {e.reason}")
        print(f"內容: {e.body}")
    except Exception as e:
        print(f"發生未預期的錯誤: {e}")

if __name__ == "__main__":
    main()
