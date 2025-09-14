import requests
import time
from datetime import datetime
import numpy as np

# === Telegram Bot Config ===
TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

# === Helper: Send Telegram Message ===
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Telegram error:", e)

# === Get XRP Prices (Binance API) ===
def get_prices(symbol="XRPUSDT", limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit={limit}"
    data = requests.get(url).json()
    closes = [float(c[4]) for c in data]  # closing prices
    return closes

# === RSI Calculation ===
def calculate_rsi(prices, period=14):
    deltas = np.diff(prices)
    seed = deltas[:period]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down if down != 0 else 0
    rsi = np.zeros_like(prices)
    rsi[:period] = 100. - 100. / (1. + rs)

    for i in range(period, len(prices)):
        delta = deltas[i - 1]
        upval = max(delta, 0)
        downval = -min(delta, 0)
        up = (up * (period - 1) + upval) / period
        down = (down * (period - 1) + downval) / period
        rs = up / down if down != 0 else 0
        rsi[i] = 100. - 100. / (1. + rs)
    return rsi[-1]

# === Moving Average Calculation ===
def moving_average(prices, period):
    return np.mean(prices[-period:])

# === News Checker (dummy for now) ===
def check_news():
    # placeholder: you can later connect this to XRPL RSS feeds or APIs
    return None

# === Main Monitor ===
def main():
    prices = get_prices()
    rsi = calculate_rsi(prices)
    ma_short = moving_average(prices, 9)
    ma_long = moving_average(prices, 21)
    current_price = prices[-1]

    # RSI Alerts
    if rsi < 30:
        send_telegram(f"🟢 XRP RSI={rsi:.2f} (Oversold). Possible BUY zone. Current price: ${current_price:.4f}")
    elif rsi > 70:
        send_telegram(f"🔴 XRP RSI={rsi:.2f} (Overbought). Possible SELL zone. Current price: ${current_price:.4f}")

    # Moving Average Cross Alerts
    if ma_short > ma_long:
        send_telegram(f"🟢 Bullish crossover! 9MA={ma_short:.4f} > 21MA={ma_long:.4f}. Current price: ${current_price:.4f}")
    elif ma_short < ma_long:
        send_telegram(f"🔴 Bearish crossover! 9MA={ma_short:.4f} < 21MA={ma_long:.4f}. Current price: ${current_price:.4f}")

    # News Alerts (if any)
    news = check_news()
    if news:
        send_telegram(f"📰 XRP News: {news}")

# === Daily Heartbeat ===
if __name__ == "__main__":
    now = datetime.utcnow()
    if now.hour == 0 and now.minute < 10:
        send_telegram("✅ XRPL Monitor is alive and checking every 10 minutes.")
    main()
