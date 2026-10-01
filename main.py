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
    description="Unified API & Web Suite integrating Classical BaZi, Feng Shui, and Qi Men Dun Jia (Zhi Run Fa).",
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
    target_year: Optional[int] = 2026

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
    prompt_to_send = req.query
    skill_key = req.skill_id

    from bazi_engine import parse_date_and_time
    y, m, d, _, _ = parse_date_and_time(req.query, req.context)
    if y and m and d:
        combined_text = f"{req.query} {req.context or ''}"
        prompt_to_send, _ = build_grounded_bazi_prompt(combined_text, combined_text, "Unspecified", req.query)
        if not skill_key:
            skill_key = "bazi"

    response_text = call_gemini(
        prompt=prompt_to_send,
        skill_key=skill_key,
        user_context=req.context
    )
    return {"skill_id": skill_key or req.skill_id, "response": response_text}

@app.post("/api/bazi")
def consult_bazi(req: BaZiRequest):
    target_yr = req.target_year or 2026
    q = req.question or "Provide a comprehensive BaZi reading and 10 Gods quality evaluation."
    if str(target_yr) not in q:
        q = f"{q} (Annual Analysis Target Year: {target_yr})"
    prompt, pillars = build_grounded_bazi_prompt(
        birth_date_str=req.birth_date,
        birth_time_str=req.birth_time,
        gender=req.gender,
        question=q,
        client_name=req.client_name or "Client"
    )
    res = call_gemini(prompt=prompt, skill_key="bazi")
    chart_html = generate_natal_chart_html(pillars, current_year=target_yr) if pillars else ""
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




# Frontend Web Interface
@app.get("/", response_class=HTMLResponse)
def index():
    return r"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Chinese Metaphysics & QiMen Suite (Zhi Run Fa)</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Kantumruy+Pro:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet">
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
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: 'Kantumruy Pro', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    body {
      background: var(--bg);
      color: var(--text);
      padding: 24px;
      line-height: 1.75;
      font-size: 15px;
      letter-spacing: 0.01em;
    }
    .container { max-width: 1140px; margin: 0 auto; }
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
    
    /* Output Card & Content Styling */
    .output-card { display: none; background: #0b1329; border: 1px solid #1e3a8a; border-radius: 14px; padding: 26px; box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.5); }
    .output-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid #1e3a8a; padding-bottom: 12px; }
    .output-content { font-size: 0.95rem; color: #e2e8f0; line-height: 1.75; }
    .output-content h1, .output-content h2, .output-content h3, .output-content h4 { color: #f59e0b; font-weight: 700; margin-top: 24px; margin-bottom: 12px; line-height: 1.45; }
    .output-content h2 { font-size: 1.4rem; border-bottom: 1px solid rgba(245, 158, 11, 0.3); padding-bottom: 8px; }
    .output-content h3 { font-size: 1.25rem; }
    .output-content p { margin-bottom: 14px; line-height: 1.8; color: #cbd5e1; }
    .output-content strong { color: #f8fafc; font-weight: 600; }
    .output-content ul, .output-content ol { margin-left: 24px; margin-bottom: 16px; line-height: 1.75; }
    .output-content li { margin-bottom: 6px; }

    /* Responsive Table Styles (For AI Markdown Analysis Tables) */
    .table-container {
      width: 100%;
      overflow-x: auto;
      margin: 22px 0;
      border-radius: 12px;
      border: 1px solid #1e3a8a;
      background: #0f172a;
      box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.45);
      -webkit-overflow-scrolling: touch;
    }
    .table-container table {
      width: 100%;
      min-width: 880px;
      border-collapse: collapse;
      font-size: 0.93rem;
      line-height: 1.75;
      color: #e2e8f0;
      background: #0b1329;
      text-align: left;
    }
    .table-container thead {
      background: linear-gradient(180deg, #1e293b 0%, #101c36 100%);
      border-bottom: 2px solid #d97706;
    }
    .table-container th {
      color: #fbbf24;
      font-weight: 700;
      font-size: 0.95rem;
      padding: 14px 16px;
      letter-spacing: 0.02em;
      border-right: 1px solid rgba(51, 65, 85, 0.45);
      vertical-align: middle;
    }
    .table-container th:last-child {
      border-right: none;
    }
    .table-container td {
      padding: 14px 16px;
      border-bottom: 1px solid #1e293b;
      border-right: 1px solid rgba(51, 65, 85, 0.3);
      vertical-align: top;
      line-height: 1.75;
    }
    .table-container td:last-child {
      border-right: none;
    }
    .table-container tbody tr:nth-child(even) {
      background: rgba(30, 41, 59, 0.35);
    }
    .table-container tbody tr:nth-child(odd) {
      background: rgba(11, 19, 41, 0.6);
    }
    .table-container tbody tr:hover {
      background: rgba(245, 158, 11, 0.08);
    }

    /* Column Widths & Highlights */
    .table-container td:nth-child(1), .table-container th:nth-child(1) {
      width: 18%;
      min-width: 160px;
      font-weight: 600;
      color: #38bdf8;
    }
    .table-container td:nth-child(2), .table-container th:nth-child(2) {
      width: 13%;
      min-width: 110px;
      color: #f1f5f9;
    }
    .table-container td:nth-child(3), .table-container th:nth-child(3) {
      width: 24%;
      min-width: 210px;
    }
    .table-container td:nth-child(4), .table-container th:nth-child(4) {
      width: 15%;
      min-width: 140px;
    }
    .table-container td:nth-child(5), .table-container th:nth-child(5) {
      width: 30%;
      min-width: 270px;
      color: #cbd5e1;
    }

    /* Quality Tier Badges */
    .tier-badge {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 4px 10px;
      border-radius: 9999px;
      font-size: 0.83rem;
      font-weight: 600;
      line-height: 1.4;
      text-align: center;
      box-shadow: 0 1px 3px rgba(0,0,0,0.25);
    }
    .tier-superior {
      background: rgba(16, 185, 129, 0.16);
      color: #34d399;
      border: 1px solid #059669;
    }
    .tier-good {
      background: rgba(14, 165, 233, 0.16);
      color: #38bdf8;
      border: 1px solid #0284c7;
    }
    .tier-average {
      background: rgba(245, 158, 11, 0.16);
      color: #fbbf24;
      border: 1px solid #d97706;
    }
    .tier-poor {
      background: rgba(239, 68, 68, 0.16);
      color: #f87171;
      border: 1px solid #dc2626;
    }

    /* Cell List Items */
    .cell-item {
      display: flex;
      align-items: baseline;
      gap: 7px;
      margin-bottom: 6px;
    }
    .cell-item:last-child {
      margin-bottom: 0;
    }
    .cell-dot {
      color: #f59e0b;
      font-size: 1.05rem;
      line-height: 1;
      flex-shrink: 0;
    }

    .loading { display: none; text-align: center; color: #f59e0b; font-weight: 600; margin: 20px 0; }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>Classical Chinese Metaphysics Suite</h1>
      <p class="sub">Classical Chinese Metaphysics — BaZi, Feng Shui & Qi Men Dun Jia Suite</p>
      <span class="badge">Qi Men Engine: Zhi Run Fa (置閏法)</span>
    </header>

    <div class="tabs">
      <button class="tab-btn active" onclick="switchTab('qimen_date', this)">📅 Qi Men Date Selection</button>
      <button class="tab-btn" onclick="switchTab('qimen_fs', this)">🧭 Qi Men Feng Shui</button>
      <button class="tab-btn" onclick="switchTab('bazi', this)">🔮 BaZi Reading</button>
      <button class="tab-btn" onclick="switchTab('fengshui', this)">🏡 Feng Shui Audit</button>
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
      <h3 style="margin-bottom: 15px; color: #f59e0b;">BaZi Reading & Destiny Analysis</h3>
      <div class="form-group">
        <label>Client Name</label>
        <input type="text" id="bz-name" placeholder="Enter client name">
      </div>
      <div class="form-group">
        <label>Birth Date</label>
        <input type="date" id="bz-date">
      </div>
      <div class="form-group">
        <label>Birth Time</label>
        <input type="time" id="bz-time">
      </div>
      <div class="form-group">
        <label>Gender</label>
        <select id="bz-gender">
          <option value="Male">Male</option>
          <option value="Female">Female</option>
        </select>
      </div>
      <div class="form-group">
        <label>Target Annual Year (流年)</label>
        <select id="bz-target-year">
          <option value="2026" selected>2026 (Bing Wu 丙午 - Yang Fire Horse)</option>
          <option value="2027">2027 (Ding Wei 丁未 - Yin Fire Goat)</option>
          <option value="2028">2028 (Wu Shen 戊申 - Yang Earth Monkey)</option>
          <option value="2029">2029 (Ji You 己酉 - Yin Earth Rooster)</option>
          <option value="2030">2030 (Geng Xu 庚戌 - Yang Metal Dog)</option>
          <option value="2025">2025 (Yi Si 乙巳 - Yin Wood Snake)</option>
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
        formatRenderedContent(outContent);
        outCard.style.display = 'block';
      } catch (err) {
        outContent.innerHTML = '<p style="color:#ef4444;">Error: ' + err.message + '</p>';
        outCard.style.display = 'block';
      } finally {
        loading.style.display = 'none';
      }
    }

    function formatRenderedContent(container) {
      if (!container) return;
      // 1. Wrap markdown tables in responsive .table-container (skip .personal-natal-chart)
      container.querySelectorAll('table').forEach(table => {
        if (table.closest('.personal-natal-chart')) return;
        if (!table.parentElement.classList.contains('table-container')) {
          const wrapper = document.createElement('div');
          wrapper.className = 'table-container';
          table.parentNode.insertBefore(wrapper, table);
          wrapper.appendChild(table);
        }
      });

      // 2. Format table cells for markdown analysis tables
      container.querySelectorAll('.table-container td').forEach(td => {
        let html = td.innerHTML;

        // Clean up asterisks or dash bullets
        if (html.includes('*') || html.includes('-') || html.includes('•')) {
          const lines = html.split(/<br\s*\/?>|\n/);
          if (lines.length > 1 || lines.some(l => l.trim().match(/^[*•\-]/))) {
            const formatted = lines.map(line => {
              const trimmed = line.trim();
              if (trimmed.match(/^[*•\-]\s*/)) {
                const clean = trimmed.replace(/^[*•\-]\s*/, '');
                return `<div class="cell-item"><span class="cell-dot">•</span><span>${clean}</span></div>`;
              }
              return trimmed ? `<div>${trimmed}</div>` : '';
            }).filter(Boolean).join('');
            if (formatted) {
              td.innerHTML = formatted;
            }
          }
        }

        // Add badges for Quality Tiers
        const rawText = td.textContent.trim();
        if (rawText.length > 0 && rawText.length < 50) {
          if (/Superior|គុណភាពខ្ពស់/i.test(rawText)) {
            td.innerHTML = `<span class="tier-badge tier-superior">${td.innerHTML}</span>`;
            td.style.textAlign = 'center';
          } else if (/Good|គុណភាពល្អ/i.test(rawText)) {
            td.innerHTML = `<span class="tier-badge tier-good">${td.innerHTML}</span>`;
            td.style.textAlign = 'center';
          } else if (/Average|គុណភាពមធ្យម/i.test(rawText)) {
            td.innerHTML = `<span class="tier-badge tier-average">${td.innerHTML}</span>`;
            td.style.textAlign = 'center';
          } else if (/Poor|គុណភាពទន់ខ្សោយ|គុណភាពខ្សោយ/i.test(rawText)) {
            td.innerHTML = `<span class="tier-badge tier-poor">${td.innerHTML}</span>`;
            td.style.textAlign = 'center';
          }
        }
      });
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
      const birthDate = document.getElementById('bz-date').value;
      if (!birthDate) {
        alert('Please enter a birth date.');
        return;
      }
      sendRequest('/api/bazi', {
        client_name: document.getElementById('bz-name').value || 'Client',
        birth_date: birthDate,
        birth_time: document.getElementById('bz-time').value || '12:00',
        gender: document.getElementById('bz-gender').value,
        question: document.getElementById('bz-question').value,
        target_year: parseInt(document.getElementById('bz-target-year').value || '2026')
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


  </script>
</body>
</html>
"""

if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
