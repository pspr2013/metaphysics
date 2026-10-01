# Classical Chinese Metaphysics & QiMen Suite (Zhi Run Fa Engine)

A unified, production-ready Web Application (FastAPI + HTML Dashboard) and interactive Telegram Bot that integrates all 4 classical Chinese Metaphysics frameworks based on Phann Sophearith's authentic reference curriculum:

1. **BaZi Reading & Destiny Analysis (PSPR)** (`/api/bazi`, `/bazi`)
2. **Classical Feng Shui Homebuyer & Property Audit** (`/api/fengshui`, `/fengshui`)
3. **Qi Men Dun Jia Feng Shui (Zhi Run Fa)** (`/api/qimen-fengshui`, `/qimen_fs`)
4. **Qi Men Date Selection & Directional Activation (Zhi Run Fa)** (`/api/qimen-date`, `/qimen_date`)

---

## ⚡ Core Engine Configuration
All Qi Men Dun Jia modules are strictly configured to use **Zhi Run Fa (置閏法 - Intercalation Method)** as the mandatory default system:
- **5-Day Yuan Segmentation**: Shang Yuan (Zi/Wu/Mao/You), Zhong Yuan (Yin/Shen/Si/Hai), Xia Yuan (Chen/Xu/Chou/Wei) tied to Jia/Ji leader stems.
- **Intercalation Mechanics**: Automatically monitors Chao Shen (>9 days lead) prior to Solstices to intercalate at Mang Zhong (Summer Solstice) or Da Xue (Winter Solstice) before switching Dun polarity.
- **Dun Polarity**: Ascending Ju (1 to 9) for Yang Dun, descending Ju (9 to 1) for Yin Dun.

---

## 📁 Project Structure

```
metaphysics_app/
├── prompts/                         # Complete reference curriculum prompts
│   ├── bazi_reading.md              # Phann Sophearith BaZi PSPR framework
│   ├── fengshui_audit.md            # Feng Shui for Homebuyers (Exterior & Interior)
│   ├── qimen_fengshui.md            # 13 household sectors & Zhi Run Fa Hour Chart
│   └── qimen_date_selection.md      # Date selection, BaZi clash filters & Qi Men
├── config.py                        # Environment & prompt loader
├── gemini_engine.py                 # Direct Gemini API integration (urllib / zero-dependency)
├── main.py                          # FastAPI REST API + HTML Dashboard + Webhook
├── bot.py                           # Telegram Bot (polling & webhook handler)
├── run_all.py                       # Unified launcher (Runs Web App + Telegram Bot)
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables template
└── metaphysics_suite.service        # Systemd service for 24/7 background run on Linux
```

---

## 🚀 Quick Start (Local or Linux VPS)

### 1. Install Dependencies
```bash
git clone <your-repo> metaphysics_app
cd metaphysics_app
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Fill in your keys:
- `GEMINI_API_KEY`: Get a free key from [Google AI Studio](https://aistudio.google.com/)
- `TELEGRAM_BOT_TOKEN`: Get a bot token from [@BotFather](https://t.me/BotFather) on Telegram
- `GEMINI_MODEL`: `gemini-3.6-flash`
- `PORT`: `8000`

### 3. Run the Unified Application
```bash
python3 run_all.py
```
- **Web App Dashboard**: Open `http://localhost:8000` in your browser.
- **API Docs (Swagger)**: Open `http://localhost:8000/docs`.
- **Telegram Bot**: Open your Telegram bot and type `/start`.

---

## ☁️ Deployment Guides

### Option A: Oracle Cloud Ubuntu (24/7 Service via Systemd)
1. Copy the project folder to `/home/ubuntu/metaphysics_app`.
2. Configure `.env` with your API keys.
3. Install systemd service:
```bash
sudo cp metaphysics_suite.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable metaphysics_suite
sudo systemctl start metaphysics_suite
```
4. Check status and logs:
```bash
sudo systemctl status metaphysics_suite
sudo journalctl -u metaphysics_suite -f
```

### Option B: Render / Cloud PaaS
1. Create a **Web Service** on Render connected to your repository.
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `python run_all.py` (or `uvicorn main:app --host 0.0.0.0 --port $PORT`)
4. Add Environment Variables in Render Dashboard:
   - `GEMINI_API_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `GEMINI_MODEL`

---

## 🤖 Telegram Bot Commands
| Command | Description | Example |
| :--- | :--- | :--- |
| `/start` | Welcome message & interactive buttons menu | `/start` |
| `/help` | Detailed instructions & examples | `/help` |
| `/qimen_date` | Auspicious date selection (Zhi Run Fa) | `/qimen_date Launch Oct 10-25, 1990 Horse Ding Fire` |
| `/qimen_fs` | Qi Men Feng Shui audit & forecasting | `/qimen_fs Period 8, Facing South Li, Door at Xu NW1` |
| `/bazi` | Four Pillars & 10 Gods PSPR | `/bazi 1988-08-08 09:30 Male Career & wealth potential` |
| `/fengshui` | Classical landforms & 9 Palaces | `/fengshui Period 8 Facing East Door at SE` |

---

## 📡 REST API Endpoints
- `GET /`: Interactive web interface
- `GET /health`: Health status & loaded skills
- `GET /api/skills`: Metadata for all 4 skills
- `POST /api/consult`: Universal consultation (`{"skill_id": "...", "query": "..."}`)
- `POST /api/qimen-date`: Dedicated Qi Men date selection
- `POST /api/qimen-fengshui`: Dedicated Qi Men Feng Shui audit
- `POST /api/bazi`: Dedicated BaZi chart analysis
- `POST /api/fengshui`: Dedicated Feng Shui property audit
- `POST /api/telegram/webhook`: Webhook endpoint for Telegram updates
- `GET /api/telegram-set-webhook`: Helper to activate Telegram webhook (`?url=...`)
- `GET /api/telegram-delete-webhook`: Helper to revert Telegram bot to polling

---

## ☁️ Deployment

### Hosting on Render
The application is pre-configured for 1-click or blueprint deployment on [Render](https://render.com):
- **Blueprint file**: [`render.yaml`](file:///d:/metaphysics_app/render.yaml)
- **Step-by-step instructions**: See [DEPLOY_RENDER.md](file:///d:/metaphysics_app/DEPLOY_RENDER.md)

Both the **Web Suite** and the **Telegram Bot** run concurrently on a single Render instance. Webhook mode is also supported to automatically wake up sleeping instances on Render's Free tier.

