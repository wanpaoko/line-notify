import os
import re
import requests
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types

# --- 讀取 .env ---
load_dotenv()

# --- 從環境變數讀取設定 ---
gemini_api_key = os.environ.get("GEMINI_API_KEY")
confluence_url = os.environ.get("CONFLUENCE_URL", "https://trendmicro.atlassian.net")
confluence_email = os.environ.get("CONFLUENCE_USERNAME")
confluence_api_token = os.environ.get("CONFLUENCE_API_TOKEN")
confluence_parent_page_id = os.environ.get("CONFLUENCE_PARENT_PAGE_ID", "1969488035")  # AI 頁面 ID


def get_ai_news():
    """
    從 Gemini API 獲取最新 AI 新聞摘要（使用 Google Search grounding）
    """
    today = datetime.now().strftime("%Y-%m-%d")

    if not gemini_api_key:
        return None, "錯誤：尚未設定 GEMINI_API_KEY 環境變數。"

    try:
        prompt_text = (
            f"今天是 {today}，請搜尋並提供最近的5則AI/LLM的重要技術新聞或發展趨勢，"
            f"以中文 Markdown 格式撰寫，包含：\n"
            f"1. 每則新聞的標題（使用 ### 格式）\n"
            f"2. 重點摘要（使用條列式）\n"
            f"3. 如果有來源或參考資料請附上\n"
            f"請確保格式清晰易讀。"
        )

        # 初始化 Gemini 客戶端
        client = genai.Client(api_key=gemini_api_key)

        # 配置 Google Search grounding
        grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )

        config = types.GenerateContentConfig(
            tools=[grounding_tool],
            temperature=0.7,
            max_output_tokens=2000
        )

        # 呼叫 Gemini API (使用穩定的 3 Flash)
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt_text,
            config=config
        )

        # 提取回應內容
        if response.text:
            # 確保回應是有效的 UTF-8 編碼
            content = response.text.strip()
            # 移除可能的非 UTF-8 字元
            content = content.encode('utf-8', errors='ignore').decode('utf-8')
            return content, None
        else:
            return None, "目前找不到最新的 AI 新聞。"

    except Exception as e:
        return None, f"處理新聞時發生錯誤: {e}"


def markdown_to_confluence_storage(markdown_text):
    """
    將 Markdown 格式轉換為 Confluence storage 格式 (簡化版)
    """
    lines = markdown_text.split('\n')
    result_lines = []
    in_list = False

    for i, line in enumerate(lines):
        # 處理標題
        if line.startswith('### '):
            if in_list:
                result_lines.append('</ul>')
                in_list = False
            result_lines.append(f'<h3>{line[4:]}</h3>')
        elif line.startswith('## '):
            if in_list:
                result_lines.append('</ul>')
                in_list = False
            result_lines.append(f'<h2>{line[3:]}</h2>')
        elif line.startswith('# '):
            if in_list:
                result_lines.append('</ul>')
                in_list = False
            result_lines.append(f'<h1>{line[2:]}</h1>')
        # 處理列表
        elif line.strip().startswith('- ') or line.strip().startswith('* '):
            if not in_list:
                result_lines.append('<ul>')
                in_list = True
            content = line.strip()[2:]
            # 處理內嵌的粗體和斜體
            content = content.replace('**', '<strong>').replace('**', '</strong>')
            content = content.replace('*', '<em>').replace('*', '</em>')
            result_lines.append(f'<li>{content}</li>')
        # 處理水平線
        elif line.strip() == '---':
            if in_list:
                result_lines.append('</ul>')
                in_list = False
            result_lines.append('<hr />')
        # 處理空行
        elif line.strip() == '':
            if in_list:
                result_lines.append('</ul>')
                in_list = False
            result_lines.append('<p></p>')
        # 一般文字（可能包含格式）
        else:
            if in_list:
                result_lines.append('</ul>')
                in_list = False
            # 處理行內格式
            formatted_line = line
            # 處理粗體
            while '**' in formatted_line:
                formatted_line = formatted_line.replace('**', '<strong>', 1)
                formatted_line = formatted_line.replace('**', '</strong>', 1)
            # 處理斜體 (單 *)
            formatted_line = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', formatted_line)

            result_lines.append(f'<p>{formatted_line}</p>')

    # 關閉未結束的列表
    if in_list:
        result_lines.append('</ul>')

    return '\n'.join(result_lines)


def create_confluence_child_page(parent_page_id, title, content):
    """
    在指定的父頁面下建立新的子頁面
    """
    try:
        auth = (confluence_email, confluence_api_token)
        url = f"{confluence_url}/wiki/rest/api/content"

        today = datetime.now().strftime("%Y-%m-%d")

        # 組合完整的頁面內容 (Markdown)
        markdown_content = f"""## 更新時間：{today}

{content}

---

*本頁面由自動化程式建立*
*資料來源：Google Gemini 3 Flash API (with Google Search)*
"""
        # 確保內容是有效的 UTF-8 編碼
        markdown_content = markdown_content.encode('utf-8', errors='ignore').decode('utf-8')

        # 轉換為 Confluence storage 格式
        storage_content = markdown_to_confluence_storage(markdown_content)

        # 準備建立新頁面的資料
        data = {
            "type": "page",
            "title": title,
            "space": {
                "key": "TrendLifeRD"  # 從 URL 可以看出 space key
            },
            "ancestors": [
                {
                    "id": parent_page_id  # 指定父頁面
                }
            ],
            "body": {
                "storage": {
                    "value": storage_content,
                    "representation": "storage"  # 使用 storage 格式
                }
            }
        }

        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=data, auth=auth, headers=headers)
        response.raise_for_status()

        # 取得新建立頁面的資訊
        new_page = response.json()
        new_page_id = new_page.get('id')

        return True, f"成功建立新頁面！頁面 ID：{new_page_id}", new_page_id

    except requests.exceptions.HTTPError as e:
        return False, f"HTTP 錯誤：{e.response.status_code} - {e.response.text}", None
    except Exception as e:
        return False, f"建立頁面時發生錯誤：{e}", None


def main():
    """
    主程式：獲取 AI 新聞並在 Confluence 建立新的子頁面
    """
    # 檢查必要的環境變數
    if not all([confluence_email, confluence_api_token]):
        print("錯誤：請設定 CONFLUENCE_USERNAME 和 CONFLUENCE_API_TOKEN 環境變數。")
        print("\n請在 .env 檔案中設定：")
        print("CONFLUENCE_USERNAME=your-email@trendmicro.com")
        print("CONFLUENCE_API_TOKEN=your-api-token")
        print("\nAPI Token 可以在這裡生成：https://id.atlassian.com/manage-profile/security/api-tokens")
        return

    print("正在獲取最新 AI 新聞...")
    news_content, error = get_ai_news()

    if error:
        print(f"錯誤：{error}")
        return

    print(f"\n成功獲取新聞內容：\n{'-'*60}\n{news_content}\n{'-'*60}\n")

    # 使用日期作為頁面標題
    today = datetime.now().strftime("%Y-%m-%d")
    page_title = f"AI 新聞摘要 - {today}"

    print(f"正在建立新的 Confluence 子頁面（父頁面 ID: {confluence_parent_page_id}）...")
    success, message, new_page_id = create_confluence_child_page(
        confluence_parent_page_id,
        page_title,
        news_content
    )

    if success:
        print(f"✓ {message}")
        print(f"✓ 頁面連結：{confluence_url}/wiki/spaces/TrendLifeRD/pages/{new_page_id}")
    else:
        print(f"✗ {message}")


if __name__ == "__main__":
    main()
