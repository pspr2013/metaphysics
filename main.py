from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import threading
import uvicorn
import logging

from config import SKILLS, HOST, PORT, TELEGRAM_BOT_TOKEN
from gemini_engine import call_gemini
from bazi_engine import build_grounded_bazi_prompt, generate_natal_chart_html
import bot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("metaphysics_app")

app = FastAPI(
    title="Classical Chinese Metaphysics & QiMen Suite (Zhi Run Fa)",
    description="Unified API & Web Suite integrating Classical BaZi, Feng Shui, Qi Men Dun Jia (Zhi Run Fa), and Calendar ephemeris.",
    version="1.0.0"
)

class ConsultRequest(BaseModel):
    skill_id: Optional[str] = None
    query: str
    context: Optional[str] = None

class BaZiRequest(BaseModel):
    client_name: Optional[str] = "Client"
    birth_date: str
    birth_time: Optional[str] = "Unknown"
    gender: str
    question: Optional[str] = "Provide a comprehensive BaZi reading and 10 Gods quality evaluation."

class FengShuiRequest(BaseModel):
    period: int
    facing: str
    door_mountain: str
    property_type: Optional[str] = "Residential"
    inquiry: Optional[str] = "Full 13 household sectors audit."

class QiMenFSRequest(BaseModel):
    mode: str = "forecasting"  # "forecasting" or "audit"
    details: str

class QiMenDateRequest(BaseModel):
    event_type: str
    target_dates: str
    day_master_or_year: Optional[str] = ""
    requirements: Optional[str] = ""
 
@app.on_event("startup")
def startup_event():
    enable_polling = os.getenv("ENABLE_BOT_POLLING", "true").lower() in ("true", "1", "yes")
    if TELEGRAM_BOT_TOKEN and enable_polling:
        t = threading.Thread(target=bot.start_polling, daemon=True, name="bot_poller")
        t.start()
        logger.info("Telegram Bot background polling thread initiated.")

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "skills_loaded": list(SKILLS.keys()),
        "telegram_configured": bool(TELEGRAM_BOT_TOKEN)
    }

@app.post("/api/telegram/webhook")
@app.post("/api/telegram-webhook")
async def telegram_webhook(request: Request):
    """Telegram webhook receiver for serverless/container platforms like Render."""
    try:
        data = await request.json()
        bot.handle_update(data)
        return {"ok": True}
    except Exception as e:
        logger.error(f"Error processing Telegram webhook: {e}")
        return {"ok": False, "error": str(e)}

@app.get("/api/telegram-set-webhook")
def set_telegram_webhook(url: str):
    """
    Convenience endpoint to configure Telegram webhook:
    e.g. https://your-service.onrender.com/api/telegram-set-webhook?url=https://your-service.onrender.com/api/telegram-webhook
    """
    if not TELEGRAM_BOT_TOKEN:
        return {"error": "TELEGRAM_BOT_TOKEN not configured in environment"}
    res = bot.send_telegram_request("setWebhook", {"url": url})
    return res

@app.get("/api/telegram-delete-webhook")
def delete_telegram_webhook():
    """Removes webhook so the bot can revert to polling mode."""
    if not TELEGRAM_BOT_TOKEN:
        return {"error": "TELEGRAM_BOT_TOKEN not configured in environment"}
    res = bot.send_telegram_request("deleteWebhook", {"drop_pending_updates": True})
    return res

@app.get("/api/skills")
def get_skills():
    return JSONResponse(content=SKILLS)

@app.post("/api/consult")
def consult(req: ConsultRequest):
    response_text = call_gemini(
        prompt=req.query,
        skill_key=req.skill_id,
        user_context=req.context
    )
    return {"skill_id": req.skill_id, "response": response_text}

@app.post("/api/bazi")
def consult_bazi(req: BaZiRequest):
    prompt, pillars = build_grounded_bazi_prompt(
        birth_date_str=req.birth_date,
        birth_time_str=req.birth_time,
        gender=req.gender,
        question=req.question or "Provide a comprehensive BaZi reading and 10 Gods quality evaluation.",
        client_name=req.client_name or "Client"
    )
    res = call_gemini(prompt=prompt, skill_key="bazi")
    chart_html = generate_natal_chart_html(pillars) if pillars else ""
    return {"skill": "bazi", "chart_html": chart_html, "result": res}

@app.post("/api/fengshui")
def consult_fengshui(req: FengShuiRequest):
    prompt = (
        f"Feng Shui Audit Request:\n"
        f"- House Period: Period {req.period}\n"
        f"- Facing Direction: {req.facing}\n"
        f"- Main Door Location: {req.door_mountain} (24 Mountains)\n"
        f"- Property Type: {req.property_type}\n"
        f"- Specific Inquiries: {req.inquiry}\n"
        f"Evaluate the spatial Qi according to Classical Feng Shui and Yang Mansion principles."
    )
    res = call_gemini(prompt=prompt, skill_key="fengshui")
    return {"skill": "fengshui", "result": res}

@app.post("/api/qimen-fengshui")
def consult_qimen_fengshui(req: QiMenFSRequest):
    prompt = (
        f"Qi Men Dun Jia Feng Shui Request ({req.mode.upper()}):\n"
        f"Default System Engine: Zhi Run Fa (置閏法 - Intercalation Method)\n"
        f"Details: {req.details}\n"
        f"Analyze using the 13 household sectors, 9 Palaces, 8 Doors, 9 Stars, and 8 Deities."
    )
    res = call_gemini(prompt=prompt, skill_key="qimen_fs")
    return {"skill": "qimen_fs", "result": res}

@app.post("/api/qimen-date")
def consult_qimen_date(req: QiMenDateRequest):
    prompt = (
        f"Qi Men Dun Jia Date Selection (Ze Ri) Request:\n"
        f"Default Calculation Engine: Zhi Run Fa (置閏法 - Intercalation Method)\n"
        f"- Event Type: {req.event_type}\n"
        f"- Date Window: {req.target_dates}\n"
        f"- Client BaZi / Day Master / Year: {req.day_master_or_year}\n"
        f"- Goals / Constraints: {req.requirements}\n"
        f"Provide the standardized 5-part deliverable including Date & Double-Hour, Macro/Personal Rationale, "
        f"Qi Men Plate alignment, Direction of execution, and Action protocol."
    )
    res = call_gemini(prompt=prompt, skill_key="qimen_date")
    return {"skill": "qimen_date", "result": res}

@app.post("/api/calendar")
def consult_calendar(req: ConsultRequest):
    res = call_gemini(prompt=req.query, skill_key="calendar")
    return {"skill": "calendar", "result": res}



# Frontend Web Interface
@app.get("/", response_class=HTMLResponse)
def index():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Chinese Metaphysics & QiMen Suite (Zhi Run Fa)</title>
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <style>
    :root {
      --bg: #0f172a;
      --card-bg: #1e293b;
      --primary: #d97706;
      --primary-hover: #b45309;
      --accent: #10b981;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --border: #334155;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; }
    body { background: var(--bg); color: var(--text); padding: 20px; line-height: 1.6; }
    .container { max-width: 1000px; margin: 0 auto; }
    header { text-align: center; margin-bottom: 30px; }
    h1 { color: #f59e0b; font-size: 2rem; margin-bottom: 8px; }
    p.sub { color: var(--text-muted); font-size: 1rem; }
    .badge { display: inline-block; background: #065f46; color: #6ee7b7; padding: 4px 10px; border-radius: 9999px; font-size: 0.8rem; font-weight: 600; margin-top: 5px; }
    .tabs { display: flex; gap: 8px; overflow-x: auto; padding-bottom: 10px; margin-bottom: 20px; border-bottom: 1px solid var(--border); }
    .tab-btn { background: var(--card-bg); color: var(--text-muted); border: 1px solid var(--border); padding: 10px 16px; border-radius: 8px; cursor: pointer; white-space: nowrap; font-weight: 500; transition: all 0.2s; }
    .tab-btn.active { background: var(--primary); color: white; border-color: var(--primary); }
    .card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; padding: 24px; margin-bottom: 20px; }
    .form-group { margin-bottom: 16px; }
    label { display: block; font-size: 0.9rem; font-weight: 600; color: #cbd5e1; margin-bottom: 6px; }
    input, select, textarea { width: 100%; background: #0f172a; border: 1px solid var(--border); color: white; padding: 10px 14px; border-radius: 6px; font-size: 0.95rem; }
    input:focus, select:focus, textarea:focus { outline: none; border-color: var(--primary); }
    button.submit-btn { background: var(--primary); color: white; border: none; padding: 12px 24px; border-radius: 6px; font-weight: 600; font-size: 1rem; cursor: pointer; transition: background 0.2s; width: 100%; }
    button.submit-btn:hover { background: var(--primary-hover); }
    .output-card { display: none; background: #0b1329; border: 1px solid #1e3a8a; border-radius: 12px; padding: 24px; }
    .output-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; border-bottom: 1px solid #1e3a8a; padding-bottom: 10px; }
    .output-content { font-size: 0.95rem; color: #e2e8f0; }
    .output-content h2, .output-content h3 { color: #f59e0b; margin-top: 15px; margin-bottom: 8px; }
    .output-content ul, .output-content ol { margin-left: 20px; margin-bottom: 10px; }
    .loading { display: none; text-align: center; color: #f59e0b; font-weight: 600; margin: 20px 0; }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>Classical Chinese Metaphysics Suite</h1>
      <p class="sub">Classical Chinese Metaphysics — BaZi, Feng Shui, Qi Men Dun Jia & Ephemeris Engine</p>
      <span class="badge">Qi Men Engine: Zhi Run Fa (置閏法)</span>
    </header>

    <div class="tabs">
      <button class="tab-btn active" onclick="switchTab('qimen_date', this)">📅 Qi Men Date Selection</button>
      <button class="tab-btn" onclick="switchTab('qimen_fs', this)">🧭 Qi Men Feng Shui</button>
      <button class="tab-btn" onclick="switchTab('bazi', this)">🔮 BaZi Reading</button>
      <button class="tab-btn" onclick="switchTab('fengshui', this)">🏡 Feng Shui Audit</button>
      <button class="tab-btn" onclick="switchTab('calendar', this)">📜 10K Calendar</button>
    </div>

    <!-- Qi Men Date Selection Form -->
    <div id="panel-qimen_date" class="card tab-panel">
      <h3 style="margin-bottom: 15px; color: #f59e0b;">Qi Men Dun Jia Date Selection (Zhi Run Fa 置閏法)</h3>
      <div class="form-group">
        <label>Activity / Event Type</label>
        <select id="qd-type">
          <option value="Product / Business Launch">Product / Business Launch</option>
          <option value="Contract Signing / VIP Negotiation">Contract Signing / VIP Negotiation</option>
          <option value="Housewarming / Move-in (Ru Zhai)">Housewarming / Move-in (Ru Zhai)</option>
          <option value="Marriage / Wedding Registration">Marriage / Wedding Registration</option>
          <option value="Medical Procedure / Surgery">Medical Procedure / Surgery</option>
        </select>
      </div>
      <div class="form-group">
        <label>Target Date Range</label>
        <input type="text" id="qd-range" placeholder="e.g. October 1 to October 15, 2026">
      </div>
      <div class="form-group">
        <label>Client Natal Data / Day Master & Year</label>
        <input type="text" id="qd-bazi" placeholder="e.g. Born 1988 Earth Dragon (Wu Chen), Day Master Jia Wood">
      </div>
      <div class="form-group">
        <label>Specific Objectives or Directional Requirements</label>
        <textarea id="qd-req" rows="3" placeholder="e.g. Need high wealth/commercial outcome with Back to Direction seated execution."></textarea>
      </div>
      <button class="submit-btn" onclick="submitQiMenDate()">Select Auspicious Dates</button>
    </div>

    <!-- Qi Men Feng Shui Form -->
    <div id="panel-qimen_fs" class="card tab-panel" style="display:none;">
      <h3 style="margin-bottom: 15px; color: #f59e0b;">Qi Men Dun Jia Feng Shui (Zhi Run Fa 置閏法)</h3>
      <div class="form-group">
        <label>Operational Mode</label>
        <select id="qmfs-mode">
          <option value="forecasting">Remote Dynamic Forecasting (Hour Chart 時家奇門)</option>
          <option value="audit">Onsite Static Audit (Yang Mansion 陽宅定局)</option>
        </select>
      </div>
      <div class="form-group">
        <label>Inquiry Details / Spatial Layout</label>
        <textarea id="qmfs-details" rows="5" placeholder="For forecasting: Describe inquiry and exact current time.\nFor audit: Specify Move-in Period, House Facing Trigram, and Main Door 24-Mountain."></textarea>
      </div>
      <button class="submit-btn" onclick="submitQiMenFS()">Evaluate Spatial Qi</button>
    </div>

    <!-- BaZi Form -->
    <div id="panel-bazi" class="card tab-panel" style="display:none;">
      <h3 style="margin-bottom: 15px; color: #f59e0b;">BaZi Reading & Destiny Analysis (PSPR)</h3>
      <div class="form-group">
        <label>Client Name</label>
        <input type="text" id="bz-name" value="Atithreaksmey" placeholder="e.g. Atithreaksmey">
      </div>
      <div class="form-group">
        <label>Birth Date (YYYY-MM-DD)</label>
        <input type="date" id="bz-date" value="1986-12-07">
      </div>
      <div class="form-group">
        <label>Birth Time</label>
        <input type="time" id="bz-time" value="09:30">
      </div>
      <div class="form-group">
        <label>Gender</label>
        <select id="bz-gender">
          <option value="Male">Male</option>
          <option value="Female">Female</option>
        </select>
      </div>
      <div class="form-group">
        <label>Specific Life Focus / Question</label>
        <textarea id="bz-question" rows="3" placeholder="Career transition, business wealth potential, relationship dynamics..."></textarea>
      </div>
      <button class="submit-btn" onclick="submitBaZi()">Analyze BaZi Chart</button>
    </div>

    <!-- Feng Shui Audit Form -->
    <div id="panel-fengshui" class="card tab-panel" style="display:none;">
      <h3 style="margin-bottom: 15px; color: #f59e0b;">Classical Feng Shui Homebuyer & Layout Audit</h3>
      <div class="form-group">
        <label>House Period</label>
        <select id="fs-period">
          <option value="9">Period 9 (2024 - 2043)</option>
          <option value="8" selected>Period 8 (2004 - 2023)</option>
          <option value="7">Period 7 (1984 - 2003)</option>
        </select>
      </div>
      <div class="form-group">
        <label>House Facing Direction</label>
        <input type="text" id="fs-facing" placeholder="e.g. South (Li Trigram, 180°)">
      </div>
      <div class="form-group">
        <label>Main Door 24-Mountain Location</label>
        <input type="text" id="fs-door" placeholder="e.g. Northwest 1 (Xu Mountain)">
      </div>
      <div class="form-group">
        <label>Rooms to Evaluate</label>
        <textarea id="fs-inquiry" rows="3" placeholder="e.g. Master bedroom in Southwest, Stove facing East, Toilet in North."></textarea>
      </div>
      <button class="submit-btn" onclick="submitFengShui()">Perform Audit</button>
    </div>

    <!-- Calendar Form -->
    <div id="panel-calendar" class="card tab-panel" style="display:none;">
      <h3 style="margin-bottom: 15px; color: #f59e0b;">Ten Thousand Year Calendar Ephemeris</h3>
      <div class="form-group">
        <label>Calendar Calculation Query</label>
        <textarea id="cal-query" rows="4" placeholder="e.g. Convert 1988-08-08 14:30 to 4 Pillars, identify Solar Term, and calculate 24 Mountain bearings."></textarea>
      </div>
      <button class="submit-btn" onclick="submitCalendar()">Calculate Ephemeris</button>
    </div>

    <div id="loading" class="loading">Consulting Chinese Metaphysics Engine... Please wait.</div>

    <div id="output-card" class="output-card">
      <div class="output-header">
        <h3 id="output-title" style="color: #f59e0b;">Analysis Report</h3>
        <button onclick="document.getElementById('output-card').style.display='none'" style="background:none; border:none; color:var(--text-muted); cursor:pointer;">✕ Close</button>
      </div>
      <div id="output-content" class="output-content"></div>
    </div>
  </div>

  <script>
    function switchTab(tabId, btn) {
      document.querySelectorAll('.tab-panel').forEach(p => p.style.display = 'none');
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      const targetPanel = document.getElementById('panel-' + tabId);
      if (targetPanel) {
        targetPanel.style.display = 'block';
      }
      if (btn) {
        btn.classList.add('active');
      } else {
        const found = document.querySelector(`.tab-btn[onclick*="'${tabId}'"]`);
        if (found) found.classList.add('active');
      }
    }

    async function sendRequest(url, payload) {
      const loading = document.getElementById('loading');
      const outCard = document.getElementById('output-card');
      const outContent = document.getElementById('output-content');
      
      loading.style.display = 'block';
      outCard.style.display = 'none';

      try {
        const res = await fetch(url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (!res.ok) {
          const errText = await res.text();
          throw new Error(`Server status ${res.status}: ${errText}`);
        }
        const data = await res.json();
        let htmlOutput = '';
        if (data.chart_html) {
          htmlOutput += data.chart_html;
        }
        let text = data.result || data.response || '';
        if (text) {
          htmlOutput += '<div style="margin-top:20px; line-height: 1.7;">' + marked.parse(text) + '</div>';
        }
        if (!htmlOutput) {
          htmlOutput = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
        }
        outContent.innerHTML = htmlOutput;
        outCard.style.display = 'block';
      } catch (err) {
        outContent.innerHTML = '<p style="color:#ef4444;">Error: ' + err.message + '</p>';
        outCard.style.display = 'block';
      } finally {
        loading.style.display = 'none';
      }
    }

    function submitQiMenDate() {
      sendRequest('/api/qimen-date', {
        event_type: document.getElementById('qd-type').value,
        target_dates: document.getElementById('qd-range').value,
        day_master_or_year: document.getElementById('qd-bazi').value,
        requirements: document.getElementById('qd-req').value
      });
    }

    function submitQiMenFS() {
      sendRequest('/api/qimen-fengshui', {
        mode: document.getElementById('qmfs-mode').value,
        details: document.getElementById('qmfs-details').value
      });
    }

    function submitBaZi() {
      sendRequest('/api/bazi', {
        client_name: document.getElementById('bz-name').value || 'Client',
        birth_date: document.getElementById('bz-date').value,
        birth_time: document.getElementById('bz-time').value,
        gender: document.getElementById('bz-gender').value,
        question: document.getElementById('bz-question').value
      });
    }

    function submitFengShui() {
      sendRequest('/api/fengshui', {
        period: parseInt(document.getElementById('fs-period').value),
        facing: document.getElementById('fs-facing').value,
        door_mountain: document.getElementById('fs-door').value,
        inquiry: document.getElementById('fs-inquiry').value
      });
    }

    function submitCalendar() {
      sendRequest('/api/calendar', {
        query: document.getElementById('cal-query').value
      });
    }
  </script>
</body>
</html>
"""

if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
