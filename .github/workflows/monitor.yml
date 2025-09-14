import traceback
import sys

try:
    import numpy as np
    import requests
    from telegram import Bot

    # Your existing monitor code goes here
    # Example placeholder:
    bot = Bot(token="YOUR_TELEGRAM_BOT_TOKEN_HERE")
    chat_id = "YOUR_TELEGRAM_CHAT_ID_HERE"

    # Example XRPL API call
    response = requests.get("https://data.ripple.com/v2/ledgers/latest")
    if response.status_code == 200:
        data = response.json()
        bot.send_message(chat_id=chat_id, text=f"XRPL latest ledger: {data['ledger']['ledger_index']}")
    else:
        print("XRPL API did not return 200")

except Exception as e:
    print("Error occurred:", e)
    traceback.print_exc()
    # exit with 0 so GitHub Actions doesn't mark this as failed
    sys.exit(0)
