import traceback
import sys
import requests
import numpy as np
from telegram import Bot

# ----------------------------
# CONFIGURATION
# ----------------------------
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"
TELEGRAM_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID_HERE"

RSI_PERIOD = 14               # typical RSI period
RSI_LOWER_THRESHOLD = 30      # buy signal
RSI_UPPER_THRESHOLD = 70      # sell signal
COIN_SYMBOL = "XRP"           # example, change as needed

bot = Bot(token=TELEGRAM_BOT_TOKEN)

# ----------------------------
# HELPER FUNCTIONS
# ----------------------------
def calculate_rsi(prices, period=14):
    """Calculates RSI from a list of prices"""
    deltas = np.diff(prices)
    seed = deltas[:period]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down if down != 0 else 0
    rsi = np.zeros_like(prices)
    rsi[:period] = 50  # initial neutral
    for i in range(period, len(prices)):
        delta = deltas[i - 1]
        if delta > 0:
            upval = delta
            downval = 0
        else:
            upval = 0
            downval = -delta
        up = (up * (period - 1) + upval) / period
        down = (down * (period - 1) + downval) / period
        rs = up / down if down != 0 else 0
        rsi[i] = 100 - (100 / (1 + rs))
    return rsi[-1]  # return latest RSI

# ----------------------------
# MAIN MONITOR LOGIC
# ----------------------------
try:
    print(f"Running XRPL monitor for {COIN_SYMBOL}...")

    # Fetch price data from XRPL API (example)
    response = requests.get(f"https://data.ripple.com/v2/exchanges/XRP/USD/close")
    if response.status_code != 200:
        print("Error fetching XRPL prices:", response.status_code)
        sys.exit(0)
    
    data = response.json()
    # assume API returns a list of closing prices, adjust according to real API
    prices = [float(item['close']) for item in data.get('rows', [])]
    if len(prices) < RSI_PERIOD:
        print("Not enough data to calculate RSI")
        sys.exit(0)

    # Calculate RSI
    rsi_value = calculate_rsi(prices, RSI_PERIOD)
    print(f"Latest RSI: {rsi_value}")

    # Check RSI thresholds
    if rsi_value < RSI_LOWER_THRESHOLD:
        msg = f"{COIN_SYMBOL} RSI alert: RSI={rsi_value:.2f} (Buy Signal)"
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)
        print("Sent Buy alert")
    elif rsi_value > RSI_UPPER_THRESHOLD:
        msg = f"{COIN_SYMBOL} RSI alert: RSI={rsi_value:.2f} (Sell Signal)"
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)
        print("Sent Sell alert")
    else:
        print("RSI within neutral range, no alert sent.")

except Exception as e:
    print("Error occurred:", e)
    traceback.print_exc()
    sys.exit(0)
