"""
SmartStudy Planner AI - Modern Light UI Styles & Interactive Components
Contains custom CSS styles, web banner templates, and embedded HTML5/JS Pomodoro timer.
"""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    color: #0F172A;
}

.stApp {
    background-color: #F8FAFC !important;
}

#MainMenu {visibility: hidden;}
header[data-testid="stHeader"] {
    background: rgba(248, 250, 252, 0.85) !important;
    backdrop-filter: blur(10px);
}
footer {visibility: hidden;}

/* Custom Top Navigation Banner */
.web-navbar {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 18px 24px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04);
}
.brand-group {
    display: flex;
    align-items: center;
    gap: 14px;
}
.brand-icon-wrapper {
    background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%);
    width: 48px;
    height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    border: 1px solid #C7D2FE;
    box-shadow: 0 2px 4px rgba(79, 70, 229, 0.1);
}
.brand-title {
    margin: 0;
    font-size: 22px;
    font-weight: 800;
    color: #1E1B4B;
    letter-spacing: -0.02em;
}
.brand-subtitle {
    margin: 2px 0 0 0;
    font-size: 13px;
    color: #64748B;
    font-weight: 500;
}
.badge-stack {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
}
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 12px;
    border-radius: 9999px;
    font-size: 12px;
    font-weight: 600;
    transition: all 0.2s ease;
}
.pill-green {
    background-color: #DCFCE7;
    color: #15803D;
    border: 1px solid #BBF7D0;
}
.pill-blue {
    background-color: #EEF2FF;
    color: #4338CA;
    border: 1px solid #C7D2FE;
}
.pill-purple {
    background-color: #FAF5FF;
    color: #7E22CE;
    border: 1px solid #E9D5FF;
}

/* Metric Cards */
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 14px;
    margin-bottom: 22px;
}
.metric-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 16px 18px;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.03);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.metric-card:hover {
    box-shadow: 0 6px 12px -2px rgba(0, 0, 0, 0.06);
    transform: translateY(-2px);
}
.metric-label {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #64748B;
    margin-bottom: 4px;
}
.metric-value {
    font-size: 26px;
    font-weight: 800;
    color: #0F172A;
    line-height: 1.1;
}
.metric-sub {
    font-size: 12px;
    color: #94A3B8;
    margin-top: 5px;
    font-weight: 500;
}
.progress-track {
    width: 100%;
    height: 8px;
    background-color: #F1F5F9;
    border-radius: 9999px;
    overflow: hidden;
    margin-top: 8px;
}
.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #4F46E5 0%, #10B981 100%);
    border-radius: 9999px;
    transition: width 0.5s ease;
}

/* Tabs Redesign */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: #F1F5F9;
    padding: 6px;
    border-radius: 12px;
    border: 1px solid #E2E8F0;
    margin-bottom: 18px;
}
.stTabs [data-baseweb="tab"] {
    height: 40px;
    border-radius: 9px;
    font-weight: 600;
    font-size: 13.5px;
    color: #64748B;
    background-color: transparent;
    padding: 0 18px;
    border: none !important;
    transition: all 0.2s ease;
}
.stTabs [aria-selected="true"] {
    background-color: #FFFFFF !important;
    color: #4F46E5 !important;
    box-shadow: 0 2px 4px 0 rgba(0, 0, 0, 0.05) !important;
}

/* Card Containers */
.web-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 18px;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.03);
}
.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 14px;
}
.card-title {
    font-size: 17px;
    font-weight: 700;
    color: #0F172A;
    margin: 0;
}
.card-desc {
    font-size: 13px;
    color: #64748B;
    margin-top: 2px;
}

/* Countdown Cards */
.countdown-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 12px;
    margin-bottom: 18px;
}
.countdown-card {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 14px 16px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
    transition: all 0.2s ease;
}
.countdown-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 10px -2px rgba(0, 0, 0, 0.06);
}
.countdown-urgent {
    border-left: 5px solid #EF4444;
    background: linear-gradient(135deg, #FEF2F2 0%, #FFFFFF 100%);
}
.countdown-warning {
    border-left: 5px solid #F59E0B;
    background: linear-gradient(135deg, #FFFBEB 0%, #FFFFFF 100%);
}
.countdown-normal {
    border-left: 5px solid #3B82F6;
    background: linear-gradient(135deg, #EFF6FF 0%, #FFFFFF 100%);
}

/* Badges & Chips */
.chip {
    display: inline-block;
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 11.5px;
    font-weight: 600;
    margin-right: 6px;
}
.chip-date {
    background-color: #F1F5F9;
    color: #475569;
}
.chip-subject {
    background-color: #EEF2FF;
    color: #4F46E5;
    border: 1px solid #C7D2FE;
}
.chip-status-completed {
    background-color: #DCFCE7;
    color: #166534;
}
.chip-status-pending {
    background-color: #FEF3C7;
    color: #92400E;
}
.chip-status-missed {
    background-color: #FEE2E2;
    color: #991B1B;
}

/* Interactive Quick Buttons */
.stButton>button {
    border-radius: 9px !important;
    font-weight: 600 !important;
    font-size: 13.5px !important;
    padding: 6px 14px !important;
    transition: all 0.2s ease !important;
}
.stButton>button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.07);
}
button[kind="primary"] {
    background: linear-gradient(135deg, #4F46E5 0%, #4338CA 100%) !important;
    border: none !important;
    color: #FFFFFF !important;
}

/* Task Item Box */
.task-box {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 10px;
    transition: all 0.15s ease;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}
.task-box:hover {
    border-color: #CBD5E1;
    box-shadow: 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}
.task-box-completed {
    background: #F0FDF4;
    border-color: #BBF7D0;
}
.task-box-missed {
    background: #FEF2F2;
    border-color: #FECACA;
}

/* Sidebar Custom Styling */
section[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E2E8F0 !important;
}
</style>
"""


def get_web_navbar_html(engine_name=None):
    if engine_name and "Oracle" in engine_name:
        db_badge = '<span class="status-pill pill-purple">🏛️ Oracle PL/SQL Connected</span>'
    else:
        db_badge = '<span class="status-pill pill-green">🗄️ Database: SQLite / PL-SQL Ready</span>'

    return f"""
    <div class="web-navbar">
        <div class="brand-group">
            <div class="brand-icon-wrapper">📚</div>
            <div>
                <h1 class="brand-title">SmartStudy Planner AI</h1>
                <p class="brand-subtitle">Simple, Interactive Academic Scheduling & AI Study Assistant</p>
            </div>
        </div>
        <div class="badge-stack">
            {db_badge}
            <span class="status-pill pill-blue">⏱️ Focus Timer</span>
            <span class="status-pill pill-purple">🤖 AI Quiz Coach</span>
        </div>
    </div>
    """


def get_metric_cards_html(total_tasks, completed_tasks, missed_tasks, plan_days):
    pending_tasks = total_tasks - completed_tasks - missed_tasks
    completion_pct = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0

    return f"""
    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-label">Total Plan</div>
            <div class="metric-value">{total_tasks} <span style="font-size: 15px; font-weight: 500; color: #64748B;">({total_tasks} hrs)</span></div>
            <div class="metric-sub">📅 Over {plan_days} days timetable</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Completed</div>
            <div class="metric-value" style="color: #15803D;">{completed_tasks}</div>
            <div class="metric-sub">🎯 {completion_pct:.1f}% syllabus completed</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Remaining / Missed</div>
            <div class="metric-value" style="color: {'#DC2626' if missed_tasks > 0 else '#D97706'};">{pending_tasks + missed_tasks}</div>
            <div class="metric-sub">⚠️ {missed_tasks} marked missed</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Overall Progress</div>
            <div class="metric-value">{completion_pct:.0f}%</div>
            <div class="progress-track">
                <div class="progress-fill" style="width: {completion_pct}%;"></div>
            </div>
        </div>
    </div>
    """


POMODORO_HTML = """
<div id="pomodoro-app" style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px; padding: 22px; text-align: center; font-family: 'Inter', -apple-system, sans-serif; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
    <div style="display: flex; justify-content: center; gap: 8px; margin-bottom: 18px; flex-wrap: wrap;">
        <button onclick="setMode(25, 'Focus Session')" id="btn-focus" style="padding: 6px 14px; border-radius: 20px; border: 1px solid #C7D2FE; background: #EEF2FF; color: #4338CA; font-weight: 700; cursor: pointer; font-size: 13px;">⚡ Focus (25m)</button>
        <button onclick="setMode(15, 'Quick Review')" id="btn-quick" style="padding: 6px 14px; border-radius: 20px; border: 1px solid #E2E8F0; background: #F8FAFC; color: #64748B; font-weight: 600; cursor: pointer; font-size: 13px;">🚀 Quick (15m)</button>
        <button onclick="setMode(5, 'Short Break')" id="btn-short" style="padding: 6px 14px; border-radius: 20px; border: 1px solid #E2E8F0; background: #F8FAFC; color: #64748B; font-weight: 600; cursor: pointer; font-size: 13px;">☕ Break (5m)</button>
    </div>

    <div style="position: relative; width: 190px; height: 190px; margin: 0 auto;">
        <svg width="190" height="190" style="transform: rotate(-90deg);">
            <circle cx="95" cy="95" r="82" stroke="#F1F5F9" stroke-width="12" fill="none" />
            <circle id="progress-circle" cx="95" cy="95" r="82" stroke="#4F46E5" stroke-width="12" fill="none" stroke-dasharray="515.22" stroke-dashoffset="0" stroke-linecap="round" style="transition: stroke-dashoffset 0.5s ease;" />
        </svg>
        <div style="position: absolute; top: 0; left: 0; width: 190px; height: 190px; display: flex; flex-direction: column; align-items: center; justify-content: center;">
            <div id="time-display" style="font-size: 38px; font-weight: 800; color: #0F172A; letter-spacing: -0.03em;">25:00</div>
            <div id="mode-display" style="font-size: 12px; font-weight: 600; color: #64748B; text-transform: uppercase; margin-top: 2px;">Focus Session</div>
        </div>
    </div>

    <div style="margin-top: 20px; display: flex; justify-content: center; gap: 10px;">
        <button onclick="toggleTimer()" id="btn-play" style="padding: 9px 22px; border-radius: 9px; background: #4F46E5; color: #ffffff; font-weight: 700; border: none; cursor: pointer; font-size: 13.5px; box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.2);">▶ Start Focus</button>
        <button onclick="resetTimer()" style="padding: 9px 18px; border-radius: 9px; background: #F1F5F9; color: #475569; font-weight: 600; border: 1px solid #E2E8F0; cursor: pointer; font-size: 13.5px;">↺ Reset</button>
    </div>
</div>

<script>
let totalSeconds = 25 * 60;
let remainingSeconds = totalSeconds;
let timerInterval = null;
let isRunning = false;
const circleLength = 515.22;

function playChime() {
    try {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(587.33, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(880, ctx.currentTime + 0.3);
        gain.gain.setValueAtTime(0.3, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 1.2);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 1.2);
    } catch (e) {}
}

function updateUI() {
    const m = Math.floor(remainingSeconds / 60);
    const s = remainingSeconds % 60;
    document.getElementById('time-display').innerText = `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    const offset = circleLength - (remainingSeconds / totalSeconds) * circleLength;
    document.getElementById('progress-circle').style.strokeDashoffset = offset;
}

function toggleTimer() {
    if (isRunning) {
        clearInterval(timerInterval);
        isRunning = false;
        document.getElementById('btn-play').innerText = "▶ Resume";
        document.getElementById('btn-play').style.background = "#4F46E5";
    } else {
        isRunning = true;
        document.getElementById('btn-play').innerText = "⏸ Pause";
        document.getElementById('btn-play').style.background = "#D97706";
        timerInterval = setInterval(() => {
            if (remainingSeconds > 0) {
                remainingSeconds--;
                updateUI();
            } else {
                clearInterval(timerInterval);
                isRunning = false;
                playChime();
                document.getElementById('btn-play').innerText = "🎉 Finished!";
                document.getElementById('btn-play').style.background = "#10B981";
            }
        }, 1000);
    }
}

function resetTimer() {
    clearInterval(timerInterval);
    isRunning = false;
    remainingSeconds = totalSeconds;
    updateUI();
    document.getElementById('btn-play').innerText = "▶ Start Focus";
    document.getElementById('btn-play').style.background = "#4F46E5";
}

function setMode(mins, label) {
    clearInterval(timerInterval);
    isRunning = false;
    totalSeconds = mins * 60;
    remainingSeconds = totalSeconds;
    document.getElementById('mode-display').innerText = label;
    document.getElementById('btn-play').innerText = "▶ Start " + label;
    document.getElementById('btn-play').style.background = "#4F46E5";

    ['btn-focus', 'btn-quick', 'btn-short'].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.style.background = '#F8FAFC';
            el.style.color = '#64748B';
            el.style.borderColor = '#E2E8F0';
        }
    });
    const activeId = mins === 25 ? 'btn-focus' : mins === 15 ? 'btn-quick' : 'btn-short';
    const activeEl = document.getElementById(activeId);
    if (activeEl) {
        activeEl.style.background = '#EEF2FF';
        activeEl.style.color = '#4338CA';
        activeEl.style.borderColor = '#C7D2FE';
    }

    updateUI();
}
updateUI();
</script>
"""
