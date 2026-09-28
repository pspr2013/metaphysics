import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROMPTS_DIR = BASE_DIR / "prompts"

# Simple .env file loader if python-dotenv is not installed
env_file = BASE_DIR / ".env"
if env_file.exists():
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip().strip("\"'"))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

def load_prompt(filename: str) -> str:
    path = PROMPTS_DIR / filename
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

SKILLS = {
    "bazi": {
        "id": "bazi",
        "title": "BaZi Reading & Destiny Analysis (PSPR)",
        "title_km": "ការទស្សន៍ទាយជោគជាតា ប៉ាហ្ស៉ី (BaZi PSPR)",
        "command": "bazi",
        "description": "Four Pillars of Destiny, Day Master, 10 Gods quality, and life strategy (Phann Sophearith PSPR framework).",
        "prompt_file": "bazi_reading.md",
        "icon": "🔮"
    },
    "fengshui": {
        "id": "fengshui",
        "title": "Feng Shui Homebuyer & Property Audit",
        "title_km": "ការពិនិត្យហុងស៊ុយផ្ទះ និងអចលនទ្រព្យ",
        "command": "fengshui",
        "description": "External landforms, building architecture, 9 Palaces blueprint audit, door/stove/bed positioning.",
        "prompt_file": "fengshui_audit.md",
        "icon": "🏡"
    },
    "qimen_fs": {
        "id": "qimen_fs",
        "title": "Qi Men Dun Jia Feng Shui (Zhi Run Fa)",
        "title_km": "ជីមិនហុងស៊ុយ (ក្បួន Zhi Run Fa)",
        "command": "qimen_fs",
        "description": "Qi Men Feng Shui audit and forecasting for 13 household sectors using Zhi Run Fa (置閏法) engine.",
        "prompt_file": "qimen_fengshui.md",
        "icon": "🧭"
    },
    "qimen_date": {
        "id": "qimen_date",
        "title": "Qi Men Date Selection & Directional Activation (Zhi Run Fa)",
        "title_km": "ការជ្រើសរើសថ្ងៃល្អ ជីមិន (ក្បួន Zhi Run Fa)",
        "command": "qimen_date",
        "description": "Auspicious timing and spatial activations (Back/Moving Towards direction) using Zhi Run Fa (置閏法).",
        "prompt_file": "qimen_date_selection.md",
        "icon": "📅"
    },
    "calendar": {
        "id": "calendar",
        "title": "Ten Thousand Year Calendar Ephemeris",
        "title_km": "ប្រតិទិនម៉ឺនឆ្នាំ និងរូបមន្តគណនា",
        "command": "calendar",
        "description": "Solar terms (Jie Qi), 60 Jia Zi, 24 Mountains, Five Tigers/Rats, Ba Zhai, and Flying Stars.",
        "prompt_file": "ten_thousand_calendar.md",
        "icon": "📜"
    }
}

# Cache loaded prompts
SYSTEM_PROMPTS = {key: load_prompt(val["prompt_file"]) for key, val in SKILLS.items()}

# Master Router Prompt for General Consultation
ROUTER_SYSTEM_PROMPT = """You are an elite Master Chinese Metaphysics AI Assistant specializing in Phann Sophearith classical frameworks:
1. BaZi Reading & PSPR: Four Pillars calculation, 10 Gods quality hierarchy, Day Master strength.
2. Classical Feng Shui: Exterior landforms, interior 9 Palaces layout, main door, kitchen/stove, bed.
3. Qi Men Dun Jia Feng Shui (Zhi Run Fa): Property audits and dynamic remote forecasting across 13 sectors.
4. Qi Men Date Selection (Zhi Run Fa): Precision date selection, personal BaZi clash filtering, hourly Qi Men activations.
5. Ten Thousand Year Calendar: Solar terms, 60 Jia Zi, ephemeris conversions.

STRICT INSTRUCTION:
- All Qi Men Dun Jia charts (Dun and Ju determination) must strictly use Zhi Run Fa (置閏法 - Intercalation Method) as the default engine.
- Respond in the language used by the user (fluent Khmer or English).
- Be analytical, practical, and non-superstitious (reject trinkets, talismans, and crystals).
"""
