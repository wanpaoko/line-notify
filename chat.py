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

# --- 讀取 .env ---
load_dotenv()

# --- 從環境變數讀取設定 ---
channel_access_token = os.environ.get("CHANNEL_ACCESS_TOKEN")
user_id = os.environ.get("USER_ID")
gemini_api_key = os.environ.get("GEMINI_API_KEY")

from datetime import datetime
import os
from google import genai
from google.genai import types

def get_ai_news():
    """
    從 Gemini 2.5 + Google Search 獲取最新 AI 新聞摘要
    """

    today = datetime.now().strftime("%Y-%m-%d")
    gemini_api_key = os.environ.get("GEMINI_API_KEY")

    if not gemini_api_key:
        return "錯誤：尚未設定 GEMINI_API_KEY 環境變數。"

    try:
        # 設定 Gemini API Client
        client = genai.Client(api_key=gemini_api_key)

        prompt_text = (
            f"今天是 {today}，請搜尋最近的3則AI/LLM的技術新聞，以中文純文字格式並以條列式摘要標題。"
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
            model="gemini-2.5-pro",
            contents=contents,
            config=config
        ):
            news_summary += chunk.text

        if news_summary.strip():
            return f"每日 AI 新聞摘要 🤖 ({today})\n\n{news_summary}"
        else:
            return "目前找不到最新的 AI 新聞。"

    except Exception as e:
        return f"處理新聞時發生未知錯誤: {e}"


def main():
    """
    主程式：檢查設定並發送 LINE 訊息
    """
    if not all([channel_access_token, user_id]):
        print("錯誤：請設定 CHANNEL_ACCESS_TOKEN 和 USER_ID 環境變數。")
        return

    configuration = Configuration(access_token=channel_access_token)

    message_text = get_ai_news()

    print(f"準備發送訊息:\n---\n{message_text}\n---")

    try:
        with ApiClient(configuration) as api_client:
            api_instance = MessagingApi(api_client)
            push_message_request = PushMessageRequest(
                to=user_id,
                messages=[TextMessage(text=message_text)]
            )
            api_instance.push_message(push_message_request)

        print(f"訊息成功發送至 {user_id}")

    except ApiException as e:
        print(f"發送訊息時發生錯誤 (LINE API): {e.status}")
        print(f"原因: {e.reason}")
        print(f"內容: {e.body}")
    except Exception as e:
        print(f"發生未預期的錯誤: {e}")

if __name__ == "__main__":
    main()
