"""
SmartStudy Planner AI (StudyFlow) - UI Styles & Layout Components
Replicates modern StudyFlow SaaS aesthetics:
- Dark sleek sidebar (#0F172A) with vibrant purple pill navigation (#7C3AED)
- Clean, bright card containers (#FFFFFF on #F8FAFC)
- Interactive Priority Tasks list with priority pills
- Colored course cards with progress tracks
- Live Study Session widget with digital timer
- Tasks Progress card with segmented study streak indicators
"""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: #0F172A;
}

.stApp {
    background-color: #F8FAFC !important;
}

#MainMenu {visibility: hidden;}
header[data-testid="stHeader"] {
    background: transparent !important;
}
footer {visibility: hidden;}

/* -------------------------------------------------------------
   DARK SLEEK SIDEBAR (#0F172A)
------------------------------------------------------------- */
section[data-testid="stSidebar"] {
    background-color: #0F172A !important;
    border-right: 1px solid #1E293B !important;
}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
    color: #F8FAFC !important;
}

/* Sidebar Brand Header */
.sidebar-brand-box {
    padding: 12px 6px 20px 6px;
    display: flex;
    align-items: center;
    gap: 12px;
}
.sidebar-brand-icon {
    width: 38px;
    height: 38px;
    border-radius: 10px;
    background: linear-gradient(135deg, #7C3AED 0%, #4F46E5 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    color: #FFFFFF;
    box-shadow: 0 4px 10px rgba(124, 58, 237, 0.4);
}
.sidebar-brand-title {
    font-size: 18px;
    font-weight: 800;
    color: #FFFFFF !important;
    letter-spacing: -0.02em;
    margin: 0;
    line-height: 1.2;
}
.sidebar-brand-subtitle {
    font-size: 11.5px;
    color: #94A3B8 !important;
    margin: 0;
    font-weight: 500;
}

/* Sidebar Radio Navigation Items */
section[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 4px !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] > label {
    padding: 10px 14px !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 13.5px !important;
    color: #94A3B8 !important;
    transition: all 0.15s ease !important;
    border: none !important;
    background: transparent !important;
    margin: 0 !important;
    cursor: pointer !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
    background-color: #1E293B !important;
    color: #FFFFFF !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
    background: #7C3AED !important; /* Active vibrant purple */
    color: #FFFFFF !important;
    box-shadow: 0 4px 12px rgba(124, 58, 237, 0.35) !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] input {
    display: none !important;
}

/* Sidebar AI Assistant Box at bottom */
.sidebar-ai-box {
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 14px;
    margin-top: 30px;
}
.sidebar-ai-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12.5px;
    font-weight: 700;
    color: #C4B5FD;
    margin-bottom: 5px;
}
.sidebar-ai-text {
    font-size: 11.5px;
    color: #94A3B8;
    line-height: 1.4;
    margin: 0;
}

/* -------------------------------------------------------------
   WHITE SAAS CARDS & CONTAINERS
------------------------------------------------------------- */
.sf-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 18px;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.02);
    transition: all 0.2s ease;
}
.sf-card:hover {
    box-shadow: 0 4px 12px -2px rgba(0, 0, 0, 0.05);
}

.sf-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 14px;
}
.sf-card-title {
    font-size: 16px;
    font-weight: 700;
    color: #0F172A;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* -------------------------------------------------------------
   AI STUDY RECOMMENDATIONS BANNER
------------------------------------------------------------- */
.ai-rec-banner {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 26px 20px;
    text-align: center;
    margin-bottom: 22px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}
.ai-rec-title {
    font-size: 17px;
    font-weight: 700;
    color: #0F172A;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    margin-bottom: 6px;
}
.ai-rec-desc {
    font-size: 13.5px;
    color: #64748B;
    margin: 0 auto 18px auto;
    max-width: 500px;
}

/* -------------------------------------------------------------
   PRIORITY TASKS ROW
------------------------------------------------------------- */
.task-row-container {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 10px;
    transition: all 0.15s ease;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.task-row-container:hover {
    border-color: #CBD5E1;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.task-row-completed {
    background: #F8FAFC;
    border-color: #E2E8F0;
    opacity: 0.75;
}

/* Priority Badges */
.badge-priority {
    font-size: 11px;
    font-weight: 700;
    padding: 3px 9px;
    border-radius: 6px;
    text-transform: lowercase;
    display: inline-block;
}
.badge-priority-high {
    background: #FEE2E2;
    color: #DC2626;
}
.badge-priority-medium {
    background: #FEF3C7;
    color: #D97706;
}
.badge-priority-low {
    background: #EEF2FF;
    color: #4F46E5;
}

/* Course Code Badge */
.badge-course-code {
    font-size: 11.5px;
    font-weight: 600;
    color: #64748B;
    background: #F1F5F9;
    padding: 2px 8px;
    border-radius: 5px;
    display: inline-block;
}

/* -------------------------------------------------------------
   COURSE CARDS (HORIZONTAL GRID)
------------------------------------------------------------- */
.course-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.course-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 14px -2px rgba(0, 0, 0, 0.07);
}
.course-card-blue {
    border-top: 4px solid #3B82F6;
}
.course-card-green {
    border-top: 4px solid #10B981;
}
.course-card-purple {
    border-top: 4px solid #8B5CF6;
}
.course-card-amber {
    border-top: 4px solid #F59E0B;
}

.course-card-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}
.course-code-text {
    font-size: 12px;
    font-weight: 600;
    color: #64748B;
}
.course-icon-circle {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
}
.circle-blue {
    background: #EFF6FF;
    color: #2563EB;
}
.circle-green {
    background: #ECFDF5;
    color: #059669;
}
.circle-purple {
    background: #FAF5FF;
    color: #7C3AED;
}
.circle-amber {
    background: #FFFBEB;
    color: #D97706;
}

.course-card-name {
    font-size: 17px;
    font-weight: 800;
    color: #0F172A;
    margin: 0 0 12px 0;
    letter-spacing: -0.01em;
}

.progress-header {
    display: flex;
    justify-content: space-between;
    font-size: 11.5px;
    color: #64748B;
    margin-bottom: 6px;
    font-weight: 600;
}
.sf-progress-track {
    width: 100%;
    height: 6px;
    background-color: #F1F5F9;
    border-radius: 9999px;
    overflow: hidden;
    margin-bottom: 12px;
}
.sf-progress-fill {
    height: 100%;
    border-radius: 9999px;
    transition: width 0.4s ease;
}

.course-meta-footer {
    display: flex;
    gap: 16px;
    font-size: 12px;
    color: #64748B;
    padding-top: 10px;
    border-top: 1px solid #F1F5F9;
}

/* -------------------------------------------------------------
   RIGHT SIDEBAR: STUDY SESSION CLOCK & PROGRESS
------------------------------------------------------------- */
.digital-clock-display {
    font-family: 'Plus Jakarta Sans', monospace;
    font-size: 40px;
    font-weight: 800;
    color: #0F172A;
    letter-spacing: -0.03em;
    text-align: center;
    margin: 16px 0 4px 0;
}
.digital-clock-caption {
    font-size: 12px;
    color: #94A3B8;
    text-align: center;
    margin-bottom: 18px;
}

/* Tasks Progress Widget */
.progress-fraction {
    font-size: 14px;
    font-weight: 700;
    color: #0F172A;
}
.streak-pills-row {
    display: flex;
    gap: 6px;
    margin-top: 8px;
}
.streak-pill {
    flex: 1;
    height: 8px;
    border-radius: 4px;
}
.streak-pill-active {
    background: #1E3A8A; /* Dark blue from screenshot */
}
.streak-pill-empty {
    background: #E2E8F0;
}

/* Custom Primary Buttons */
button[kind="primary"] {
    background: #7C3AED !important;
    border: none !important;
    color: #FFFFFF !important;
    border-radius: 9px !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 10px rgba(124, 58, 237, 0.25) !important;
    transition: all 0.2s ease !important;
}
button[kind="primary"]:hover {
    background: #6D28D9 !important;
    transform: translateY(-1px);
    box-shadow: 0 6px 14px rgba(124, 58, 237, 0.35) !important;
}
.stButton>button {
    border-radius: 9px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}
</style>
"""


def get_sidebar_brand_html():
    return """
    <div class="sidebar-brand-box">
        <div class="sidebar-brand-icon">📚</div>
        <div>
            <h1 class="sidebar-brand-title">StudyFlow</h1>
            <p class="sidebar-brand-subtitle">AI Study Planner</p>
        </div>
    </div>
    """


def get_sidebar_ai_assistant_html():
    return """
    <div class="sidebar-ai-box">
        <div class="sidebar-ai-header">
            <span>●</span> AI Assistant
        </div>
        <p class="sidebar-ai-text">
            I've optimized your schedule based on upcoming deadlines.
        </p>
    </div>
    """


def get_main_greeting_html(student_name="Student"):
    return f"""
    <div style="margin-bottom: 22px;">
        <h1 style="font-size: 28px; font-weight: 800; color: #0F172A; margin: 0; letter-spacing: -0.02em;">Hello, {student_name}</h1>
        <p style="font-size: 14px; color: #64748B; margin-top: 4px;">Here's an overview of your study progress</p>
    </div>
    """


def get_ai_recommendations_banner_html():
    return """
    <div class="ai-rec-banner">
        <div class="ai-rec-title">
            <span style="color: #7C3AED; font-size: 18px;">✦</span> AI Study Recommendations
        </div>
        <p class="ai-rec-desc">
            Get personalized study recommendations based on your courses and upcoming tasks.
        </p>
    </div>
    """


def get_course_card_html(code, name, progress_pct, tasks_count, hours_spent, color="blue", next_info=None):
    border_class = f"course-card-{color}"
    circle_class = f"circle-{color}"
    fill_color = "#3B82F6" if color == "blue" else "#10B981" if color == "green" else "#8B5CF6" if color == "purple" else "#F59E0B"

    next_html = f"<div style='font-size: 11.5px; color: #64748B; margin-top: 8px;'>📅 {next_info}</div>" if next_info else ""

    return f"""
    <div class="course-card {border_class}">
        <div class="course-card-top">
            <span class="course-code-text">{code}</span>
            <div class="course-icon-circle {circle_class}">📖</div>
        </div>
        <div class="course-card-name">{name}</div>
        <div class="progress-header">
            <span>Progress</span>
            <span style="font-weight: 700; color: #0F172A;">{int(progress_pct)}%</span>
        </div>
        <div class="sf-progress-track">
            <div class="sf-progress-fill" style="width: {int(progress_pct)}%; background-color: {fill_color};"></div>
        </div>
        <div class="course-meta-footer">
            <span>📋 {tasks_count} tasks</span>
            <span>⏱️ {hours_spent}h spent</span>
        </div>
        {next_html}
    </div>
    """


def get_task_progress_widget_html(completed_count, total_count, streak_days=12):
    pct = (completed_count / total_count * 100) if total_count > 0 else 0
    return f"""
    <div class="sf-card" style="padding: 18px 20px;">
        <div class="sf-card-header">
            <span class="sf-card-title">Tasks Progress</span>
            <span style="background: #ECFDF5; color: #059669; padding: 3px 7px; border-radius: 6px; font-size: 13px; font-weight: 700;">☑</span>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 13px; font-weight: 600; color: #64748B; margin-bottom: 6px;">
            <span>Completed</span>
            <span class="progress-fraction">{completed_count}/{total_count}</span>
        </div>
        <div class="sf-progress-track" style="height: 7px; margin-bottom: 16px;">
            <div class="sf-progress-fill" style="width: {pct}%; background: #10B981;"></div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 13px; font-weight: 600; color: #64748B;">
            <span>Study Streak</span>
            <span style="font-weight: 700; color: #0F172A;">{streak_days} days</span>
        </div>
        <div class="streak-pills-row">
            <div class="streak-pill streak-pill-active"></div>
            <div class="streak-pill streak-pill-active"></div>
            <div class="streak-pill streak-pill-active"></div>
            <div class="streak-pill streak-pill-active"></div>
            <div class="streak-pill streak-pill-active"></div>
            <div class="streak-pill streak-pill-empty"></div>
        </div>
        <div style="margin-top: 14px; font-size: 12px; font-weight: 600; color: #64748B; text-align: right;">
            View detailed analytics →
        </div>
    </div>
    """
