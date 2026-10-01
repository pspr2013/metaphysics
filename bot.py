import json
import logging
import time
import urllib.request
import urllib.error
from config import TELEGRAM_BOT_TOKEN, SKILLS
from gemini_engine import call_gemini
from bazi_engine import build_grounded_bazi_prompt

logger = logging.getLogger("telegram_bot")
logging.basicConfig(level=logging.INFO)

API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# User state storage for conversational step-by-step guidance
USER_MODES = {}

def send_telegram_request(method: str, payload: dict) -> dict:
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is missing.")
        return {}
    url = f"{API_URL}/{method}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            err_data = json.loads(e.read().decode("utf-8"))
            logger.error(f"Telegram API HTTP {e.code} ({method}): {err_data.get('description', err_data)}")
            return err_data
        except Exception:
            logger.error(f"Telegram API HTTP error {e.code} ({method})")
            return {"ok": False, "error_code": e.code}
    except Exception as e:
        logger.error(f"Telegram API request error ({method}): {e}")
        return {}

def send_message(chat_id: int, text: str, reply_markup: dict = None):
    # Telegram message character limit is 4096. Split if longer.
    max_len = 4000
    chunks = [text[i:i+max_len] for i in range(0, len(text), max_len)]
    for idx, chunk in enumerate(chunks):
        payload = {
            "chat_id": chat_id,
            "text": chunk,
            "parse_mode": "Markdown"
        }
        if reply_markup and idx == len(chunks) - 1:
            payload["reply_markup"] = reply_markup
        res = send_telegram_request("sendMessage", payload)
        # If markdown parsing fails due to unmatched asterisks/underscores, fallback to plain text
        if not res.get("ok"):
            payload.pop("parse_mode", None)
            send_telegram_request("sendMessage", payload)

def build_main_menu() -> dict:
    keyboard = [
        [
            {"text": "📅 Qi Men Date Selection (Zhi Run)", "callback_data": "skill_qimen_date"},
            {"text": "🧭 Qi Men Feng Shui (Zhi Run)", "callback_data": "skill_qimen_fs"}
        ],
        [
            {"text": "🔮 BaZi Reading (PSPR)", "callback_data": "skill_bazi"},
            {"text": "🏡 Feng Shui Audit", "callback_data": "skill_fengshui"}
        ],
        [
            {"text": "💬 Free Consultation", "callback_data": "skill_free"}
        ]
    ]
    return {"inline_keyboard": keyboard}

def handle_update(update: dict):
    if "message" in update:
        msg = update["message"]
        chat_id = msg.get("chat", {}).get("id")
        text = msg.get("text", "").strip()
        if not chat_id or not text:
            return

        user_id = msg.get("from", {}).get("id", chat_id)

        # Handle Commands
        if text.startswith("/start"):
            welcome = (
                "🌟 *Phann Sophearith Classical Chinese Metaphysics Suite*\n"
                "សូមស្វាគមន៍មកកាន់ប្រព័ន្ធវិភាគចិនសែបុរាណ និងជីមិន遁甲\n\n"
                "⚡ *Qi Men Engine*: Configured to *Zhi Run Fa (置閏法)* as default.\n\n"
                "Please choose a specialized service from the menu below or type your inquiry directly:"
            )
            send_message(chat_id, welcome, reply_markup=build_main_menu())
            return

        elif text.startswith("/help"):
            help_text = (
                "📚 *Available Commands:*\n\n"
                "• `/qimen_date <event> <dates> [bazi]` - Auspicious date selection & spatial activations (Zhi Run Fa)\n"
                "• `/qimen_fs <inquiry>` - Qi Men Feng Shui audit & dynamic forecasting (Zhi Run Fa)\n"
                "• `/bazi <YYYY-MM-DD> <time> <gender> [question]` - Four Pillars & 10 Gods PSPR\n"
                "• `/fengshui <period> <facing> <door>` - Classical landform & 9 Palaces audit\n"
                "• `/menu` - Show interactive service menu"
            )
            send_message(chat_id, help_text)
            return

        elif text.startswith("/menu"):
            send_message(chat_id, "Choose a service:", reply_markup=build_main_menu())
            return

        # Direct command processing
        active_skill = USER_MODES.get(user_id)
        if text.startswith("/bazi"):
            active_skill = "bazi"
            text = text.replace("/bazi", "").strip() or "Please perform a BaZi analysis."
        elif text.startswith("/fengshui"):
            active_skill = "fengshui"
            text = text.replace("/fengshui", "").strip() or "Please audit this property layout."
        elif text.startswith("/qimen_fs"):
            active_skill = "qimen_fs"
            text = text.replace("/qimen_fs", "").strip() or "Please perform a Qi Men Feng Shui analysis."
        elif text.startswith("/qimen_date"):
            active_skill = "qimen_date"
            text = text.replace("/qimen_date", "").strip() or "Please select an auspicious date."
        # Send typing action
        send_telegram_request("sendChatAction", {"chat_id": chat_id, "action": "typing"})

        # Ground BaZi queries with exact four pillars if applicable
        prompt_to_send = text
        if active_skill == "bazi":
            prompt_to_send, _ = build_grounded_bazi_prompt(text, text, "Unspecified", text)
        else:
            from bazi_engine import parse_date_and_time
            y, m, d, _, _ = parse_date_and_time(text)
            if y and m and d:
                prompt_to_send, _ = build_grounded_bazi_prompt(text, text, "Unspecified", text)
                active_skill = "bazi"

        # Call Gemini with specialized skill prompt
        response = call_gemini(prompt=prompt_to_send, skill_key=active_skill)
        send_message(chat_id, response, reply_markup=build_main_menu())

    elif "callback_query" in update:
        cq = update["callback_query"]
        chat_id = cq.get("message", {}).get("chat", {}).get("id")
        user_id = cq.get("from", {}).get("id", chat_id)
        data = cq.get("data", "")

        # Acknowledge callback
        send_telegram_request("answerCallbackQuery", {"callback_query_id": cq.get("id")})

        if data.startswith("skill_"):
            skill_id = data.replace("skill_", "")
            if skill_id == "free":
                USER_MODES[user_id] = None
                send_message(chat_id, "💬 *General Consultation Mode*\nType any Chinese Metaphysics question directly.")
            else:
                USER_MODES[user_id] = skill_id
                info = SKILLS.get(skill_id, {})
                title = info.get("title", skill_id)
                desc = info.get("description", "")
                icon = info.get("icon", "✨")
                msg = (
                    f"{icon} *Selected: {title}*\n\n"
                    f"{desc}\n\n"
                    f"👉 Please type your input or query now. Example:\n"
                )
                if skill_id == "qimen_date":
                    msg += "`Launch product between Oct 10 - Oct 25, 2026. Born 1990 Horse, Day Master Ding Fire.`"
                elif skill_id == "qimen_fs":
                    msg += "`Period 8 house facing South (Li), Door at Northwest 1 (Xu). Evaluate master bedroom in SW.`"
                elif skill_id == "bazi":
                    msg += "`Born 1988-08-08 at 09:30 AM (Solar Time), Male. Analyze career & wealth potential.`"
                elif skill_id == "fengshui":
                    msg += "`Period 8 apartment, Balcony facing East, main door at SE. Road curve on the north side.`"

                send_message(chat_id, msg)

is_polling = False

def start_polling():
    """Runs long polling for local development or standalone server."""
    global is_polling
    if is_polling:
        logger.info("Telegram Bot polling is already active.")
        return
    is_polling = True
    logger.info("Starting Telegram Bot long-polling...")
    last_update_id = 0
    while is_polling:
        try:
            updates = send_telegram_request("getUpdates", {"offset": last_update_id + 1, "timeout": 20})
            if not updates.get("ok"):
                desc = updates.get("description", "")
                if "webhook is active" in desc.lower():
                    logger.warning("Telegram webhook is active. Stopping long-polling loop (updates are served via webhook).")
                    is_polling = False
                    break
                time.sleep(3)
                continue
            for item in updates.get("result", []):
                last_update_id = item.get("update_id", last_update_id)
                handle_update(item)
        except Exception as e:
            logger.error(f"Polling loop error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    start_polling()
