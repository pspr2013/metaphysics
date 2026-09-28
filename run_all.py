import threading
import uvicorn
import time
from config import HOST, PORT, TELEGRAM_BOT_TOKEN
import bot

def run_api():
    uvicorn.run("main:app", host=HOST, port=PORT, log_level="info")

def run_bot():
    if TELEGRAM_BOT_TOKEN:
        bot.start_polling()
    else:
        print("[Notice] TELEGRAM_BOT_TOKEN not set in .env. Bot polling skipped.")

if __name__ == "__main__":
    print(f"[*] Starting Metaphysics Suite on http://{HOST}:{PORT}...")
    if TELEGRAM_BOT_TOKEN:
        print("[*] Telegram Bot token detected; bot will start via FastAPI background poller.")
    else:
        print("[Notice] TELEGRAM_BOT_TOKEN not set. Running in Web/API-only mode.")

    uvicorn.run("main:app", host=HOST, port=PORT, log_level="info")
