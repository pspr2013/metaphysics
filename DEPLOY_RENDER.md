# 🚀 Deploying to Render

This guide provides step-by-step instructions to host the **Classical Chinese Metaphysics & QiMen Suite** on [Render](https://render.com).

Render allows hosting both the **Interactive Web App / REST API** and the **Telegram Bot** concurrently on a single service.

---

## 📋 Prerequisites

1. A [GitHub](https://github.com) account.
2. A [Render](https://render.com) account (Free tier available).
3. A **Google Gemini API Key** (from [Google AI Studio](https://aistudio.google.com/)).
4. *(Optional)* A **Telegram Bot Token** (from [@BotFather](https://t.me/BotFather)).

---

## 🛠️ Step 1: Push Your Code to GitHub

Open PowerShell or Terminal in your project directory (`d:\metaphysics_app`) and run:

```bash
# 1. Initialize git (if not already initialized)
git init

# 2. Add files (sensitive .env is automatically excluded by .gitignore)
git add .

# 3. Create your first commit
git commit -m "Prepare Chinese Metaphysics Suite for Render deployment"

# 4. Set default branch to main
git branch -M main

# 5. Link to your GitHub repository (replace with your repo URL)
git remote add origin https://github.com/<your-username>/<your-repo-name>.git

# 6. Push to GitHub
git push -u origin main
```

---

## 🌐 Step 2: Deploy on Render

Choose either **Method A (Blueprint - Easiest)** or **Method B (Manual)**:

### Method A: Deploy via Blueprint (`render.yaml`) — Recommended ⭐

1. Go to your [Render Dashboard](https://dashboard.render.com).
2. Click **New +** in the top navigation bar and select **Blueprint**.
3. Connect your GitHub repository.
4. Render will read [`render.yaml`](file:///d:/metaphysics_app/render.yaml) automatically.
5. In the configuration prompt, enter your secrets:
   - `GEMINI_API_KEY`: Paste your Gemini API key from Google AI Studio.
   - `TELEGRAM_BOT_TOKEN`: *(Optional)* Paste your Telegram Bot token.
6. Click **Apply**. Render will automatically build and deploy the app!

---

### Method B: Manual Web Service Setup

If you prefer to configure manually:

1. In Render Dashboard, click **New +** → **Web Service**.
2. Connect your GitHub repository.
3. Configure the settings:
   - **Name**: `metaphysics-suite` (or your choice)
   - **Region**: Choose the region closest to you (e.g., Singapore, Frankfurt, Oregon)
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**:
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     uvicorn main:app --host 0.0.0.0 --port $PORT
     ```
   - **Instance Type**: `Free`
4. Under **Advanced** → **Environment Variables**, add:
   | Key | Value | Notes |
   |---|---|---|
   | `GEMINI_API_KEY` | `AIzaSy...` | Required |
   | `TELEGRAM_BOT_TOKEN` | `123456:ABC...` | Optional (for Telegram bot) |
   | `GEMINI_MODEL` | `gemini-3.6-flash` | Default model |
   | `PYTHON_VERSION` | `3.11.9` | Matches `.python-version` |
5. Under **Health Check Path**, enter: `/health`
6. Click **Create Web Service**.

---

## 🤖 Step 3: Telegram Bot Configuration (Webhook vs Polling)

Your app supports **both** Long-Polling and Webhooks:

### 1. Polling Mode (Default)
If you add `TELEGRAM_BOT_TOKEN`, the app automatically launches background polling on startup. No extra setup required!

### 2. Webhook Mode (Recommended for Render Free Tier) ⚡
On Render's Free tier, the web service spins down after 15 minutes of inactivity. With **Webhooks**, whenever a user sends a message to your Telegram bot, Telegram sends an HTTP POST request to Render, which **automatically wakes up the instance**!

To activate Webhook mode:
1. Once your Render service is deployed, note your service URL (e.g., `https://metaphysics-suite.onrender.com`).
2. Open your web browser and visit:
   ```text
   https://<your-render-url>/api/telegram-set-webhook?url=https://<your-render-url>/api/telegram/webhook
   ```
3. You will receive: `{"ok": true, "result": true, "description": "Webhook was set"}`.
4. That's it! Your bot is now in Webhook mode.

> **Note**: To revert to polling mode at any time, simply visit:
> `https://<your-render-url>/api/telegram-delete-webhook`

---

## ⏱️ Step 4: Keeping Render Free Tier Active (Optional)

Render Free web services spin down after 15 minutes without inbound HTTP traffic. If you want 24/7 instant response times without cold starts:

1. Create a free account on [UptimeRobot](https://uptimerobot.com) or [cron-job.org](https://cron-job.org).
2. Add a new HTTP Monitor targeting your health check endpoint:
   - **URL**: `https://<your-render-url>/health`
   - **Interval**: Every `10 minutes`
3. This keeps your free Render container warm and responsive 24/7!

---

## 🔍 Verification & Testing

Once deployed:

1. **Web Dashboard**: Visit `https://<your-render-url>/` in your browser. You should see the Classical Chinese Metaphysics UI.
2. **Health Check**: Visit `https://<your-render-url>/health`.
   ```json
   {
     "status": "ok",
     "skills_loaded": ["bazi", "fengshui", "qimen_fs", "qimen_date", "calendar"],
     "telegram_configured": true
   }
   ```
3. **API Docs**: Interactive Swagger documentation is available at:
   `https://<your-render-url>/docs`
4. **Telegram Bot**: Send `/start` or `/menu` to your Telegram bot.
