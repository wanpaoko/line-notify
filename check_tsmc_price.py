import re
import requests
import sys # Import sys to access command-line arguments

# --- Configuration ---
# The URL for TSMC stock information on Yahoo Finance Taiwan
STOCK_URL = "https://tw.stock.yahoo.com/quote/2330.TW"
# The price threshold to trigger a notification
PRICE_THRESHOLD = 1700
# --- End Configuration ---

def get_tsmc_price():
    """
    Fetches the current TSMC stock price from Yahoo Finance Taiwan.
    Returns the price as an integer, or None if an error occurs.
    """
    try:
        # Make a GET request to the Yahoo Finance URL
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(STOCK_URL, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        html_content = response.text

        # Parse the HTML to find the stock price using regex
        # We look for "成交" (traded price) followed by numbers and commas.
        # Example from previous fetch: "成交1,775"
        match = re.search(r'成交([0-9,]+)', html_content)
        
        if match:
            price_str = match.group(1).replace(',', '') # Remove commas
            current_price = int(price_str)
            return current_price
        else:
            # Fallback: try to find "最低" (lowest price) if "成交" is not found
            # This might happen if the page structure changes slightly or during off-hours.
            match_min = re.search(r'最低([0-9,]+)', html_content)
            if match_min:
                price_str = match_min.group(1).replace(',', '') # Remove commas
                current_price = int(price_str)
                print(f"Note: '成交' price not found, using '最低' price: {current_price}")
                return current_price
            else:
                print(f"Error: Could not find stock price on the page {STOCK_URL}.")
                return None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {STOCK_URL}: {e}")
        return None
    except ValueError:
        print("Error: Could not parse stock price as an integer.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def check_and_notify(price_threshold, url_link):
    """
    Checks the TSMC stock price and prints a notification message if it's below the threshold.
    """
    current_price = get_tsmc_price()

    if current_price is not None:
        if current_price < price_threshold:
            print(f"🚨🚨🚨 老哥！台積電股價 (2330.TW) 已跌破 {price_threshold}！目前股價：{current_price}。")
            print(f"連結：{url_link}")
            # To actually send a message, you would need to integrate with Clawdbot's message tool
            # or another notification service here. For this script, we just print.
            # Example: You could use a library to send emails, or a webhook.
        else:
            # Optional: print status even if not triggered
            print(f"台積電股價 (2330.TW) 目前為 {current_price}，低於 {price_threshold} 的門檻。")
    else:
        print("無法獲取台積電股價。請檢查網路連線或網址。")

if __name__ == "__main__":
    # Check if a threshold is provided as a command-line argument
    if len(sys.argv) > 1:
        try:
            threshold_arg = int(sys.argv[1])
            if threshold_arg > 0:
                PRICE_THRESHOLD = threshold_arg
        except ValueError:
            print(f"Warning: Invalid threshold argument '{sys.argv[1]}'. Using default threshold {PRICE_THRESHOLD}.")

    check_and_notify(PRICE_THRESHOLD, STOCK_URL)
