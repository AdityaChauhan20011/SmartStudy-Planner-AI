"""
SmartStudy Planner AI - Main Application Entrypoint
A clean, light, and interactive study scheduling suite powered by SQLite and local AI.
"""

import sys
from datetime import date, datetime, timedelta
from streamlit.runtime.scriptrunner import get_script_run_ctx

# ---------------------------------------------------------
# Auto-Launch Streamlit if executed directly via bare Python
# Prevents "Thread 'MainThread': missing ScriptRunContext!" warning
# ---------------------------------------------------------
if __name__ == "__main__":
    if get_script_run_ctx(suppress_warning=True) is None:
        from streamlit.web import cli as stcli
        sys.exit(stcli.main(["run", sys.argv[0]] + sys.argv[1:]))

import altair as alt
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

# Modular subsystem imports
import database as db
import plsql_manager as pm
import planner
import ai_assistant as ai
import styles


def main():
    # ---------------------------------------------------------
    # Page Configuration & Styling
    # ---------------------------------------------------------
    st.set_page_config(
        page_title="SmartStudy Planner AI",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(styles.CUSTOM_CSS, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # Database Initialization (SQLite)
    # ---------------------------------------------------------
    db.init_db()

    # Query current state from SQLite
    subjects_data = db.get_all_subjects()
    tasks_data = db.get_all_tasks()

    # ---------------------------------------------------------
    # Top Navigation Banner
    # ---------------------------------------------------------
    active_engine_name = db.get_current_engine_name()
    st.markdown(styles.get_web_navbar_html(active_engine_name), unsafe_allow_html=True)

    # ---------------------------------------------------------
    # Sidebar: Simple Settings & Health
    # ---------------------------------------------------------
    with st.sidebar:
        st.markdown("### ⚙️ Study Settings")
        hours_per_day = st.slider("Daily Study Hours", min_value=1, max_value=8, value=3, help="Target study time allocated per day.")
        plan_days = st.slider("Planning Horizon (Days)", min_value=3, max_value=21, value=7, help="How many days into the future to schedule.")

        st.markdown("---")
        st.markdown("### 🤖 AI Coach Model")
        model_name = st.text_input(
            "Local Model",
            value=ai.DEFAULT_MODEL,
            help="Ollama model name (e.g. llama3.2, gemma3:4b, mistral).",
        )

        ollama_online, model_available, installed_models = ai.check_ollama_status(model_name.strip() or ai.DEFAULT_MODEL)
        if ollama_online:
            if model_available:
                st.success(f"🟢 Ollama online • `{model_name}` ready", icon="✅")
            else:
                st.warning(f"🟡 Ollama online, but `{model_name}` not found. Installed: {', '.join(installed_models) or 'None'}")
        else:
            st.info("💡 Local AI offline. Built-in interactive quiz and study guides are active!", icon="ℹ️")

        st.markdown("---")
        st.markdown("### 🗄️ Relational Database")
        db_stats = db.get_database_stats()
        st.caption(f"⚙️ **Engine:** `{db_stats.get('engine', 'SQLite')}`")
        if "file" in db_stats:
            st.caption(f"📁 **File:** `{db_stats['file']}` ({db_stats['size_kb']} KB)")
        elif "dsn" in db_stats:
            st.caption(f"🌐 **Oracle DSN:** `{db_stats['dsn']}`")
        st.caption(f"📚 **Subjects:** {db_stats['subjects_count']} • 📅 **Tasks:** {db_stats['tasks_count']}")
        st.caption(f"⏱️ **Pomodoro Sprints:** {db_stats['pomodoro_count']} completed")
        if db_stats.get("audit_count", 0) > 0:
            st.caption(f"🛡️ **Trigger Audits:** {db_stats['audit_count']} logged")

    # ---------------------------------------------------------
    # Summary Metrics Cards
    # ---------------------------------------------------------
    total_tasks = len(tasks_data)
    completed_tasks = sum(1 for t in tasks_data if t.get("status") == "Completed")
    missed_tasks = sum(1 for t in tasks_data if t.get("status") == "Missed")

    st.markdown(
        styles.get_metric_cards_html(total_tasks, completed_tasks, missed_tasks, plan_days),
        unsafe_allow_html=True,
    )

    # ---------------------------------------------------------
    # Friendly Quick-Start if Database is Fresh / Empty
    # ---------------------------------------------------------
    if not subjects_data and not tasks_data:
        st.markdown(
            """
            <div class="web-card" style="text-align: center; padding: 32px 20px; border: 2px dashed #CBD5E1;">
                <div style="font-size: 40px; margin-bottom: 10px;">🚀</div>
                <h3 style="font-size: 19px; font-weight: 800; color: #1E1B4B; margin: 0;">Welcome to SmartStudy Planner AI!</h3>
                <p style="font-size: 14px; color: #64748B; max-width: 550px; margin: 6px auto 18px auto;">
                    Organize your upcoming exams, auto-generate a balanced daily study schedule, practice with interactive quizzes, and stay focused with Pomodoro timers.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        col_qs1, col_qs2, col_qs_spacer = st.columns([3, 3, 4])
        with col_qs1:
            if st.button("✨ Load Sample Schedule (1-Click)", type="primary", use_container_width=True):
                db.seed_sample_plan_data()
                st.balloons()
                st.success("🎉 Sample curriculum and schedule loaded into SQLite!")
                st.rerun()
        with col_qs2:
            if st.button("➕ Add My Own Subjects First", use_container_width=True):
                st.session_state.active_tab = 1
                st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # Main Navigation Tabs (Clean, Basic & Highly Interactive)
    # ---------------------------------------------------------
    tab_tasks, tab_subjects, tab_pomodoro, tab_ai, tab_analytics = st.tabs([
        "  📅 Daily Schedule & Tasks  ",
        "  📚 Subjects & Exam Countdowns  ",
        "  ⏱️ Focus Pomodoro Timer  ",
        "  🤖 AI Study Coach & Quiz  ",
        "  📊 Progress & Database  ",
    ])

    today_str = date.today().isoformat()

    # ---------------------------------------------------------
    # TAB 1: DAILY SCHEDULE & INTERACTIVE TASKS
    # ---------------------------------------------------------
    with tab_tasks:
        if not subjects_data:
            st.info("👉 You don't have any subjects yet. Click the button below to load a sample or add your courses.", icon="ℹ️")
            if st.button("✨ Load Sample MCA Schedule (1-Click)", type="primary"):
                db.seed_sample_plan_data()
                st.balloons()
                st.rerun()
        else:
            # Action Toolbar
            col_a1, col_a2, col_a3, col_filter = st.columns([3, 3, 2, 3])
            with col_a1:
                if st.button("✨ Generate / Refresh Schedule", type="primary", use_container_width=True):
                    new_plan = planner.make_plan(subjects_data, hours_per_day, date.today(), plan_days)
                    if new_plan:
                        db.set_all_tasks(new_plan)
                        st.balloons()
                        st.toast(f"Generated {len(new_plan)} study sessions!")
                        st.rerun()
                    else:
                        st.warning("No sessions scheduled. Check if exam dates are in the future.")

            with col_a2:
                missed_count = sum(1 for t in tasks_data if t.get("status") == "Missed")
                resched_label = f"🔄 Reschedule Missed ({missed_count})" if missed_count else "🔄 Reschedule Missed"
                if st.button(resched_label, use_container_width=True, disabled=(missed_count == 0)):
                    missed_items = [t for t in tasks_data if t.get("status") == "Missed"]
                    rescheduled_map = planner.calculate_reschedule_mapping(missed_items, plan_days)
                    db.reschedule_tasks(rescheduled_map)
                    st.toast(f"Rescheduled {len(rescheduled_map)} missed session(s) into upcoming slots!")
                    st.rerun()

            with col_a3:
                with st.popover("➕ Add Task"):
                    st.markdown("##### Add Custom Study Session")
                    custom_sub = st.selectbox("Subject", [s["name"] for s in subjects_data], key="custom_sub")
                    custom_date = st.date_input("Date", value=date.today(), key="custom_date")
                    custom_title = st.text_input("Session Title", value=f"{custom_sub} - Deep Revision", key="custom_title")
                    custom_dur = st.number_input("Duration (minutes)", min_value=15, max_value=180, value=60, step=15)
                    if st.button("Save Session", type="primary", use_container_width=True):
                        import uuid
                        new_t = {
                            "id": f"custom_{uuid.uuid4().hex[:6]}",
                            "date": custom_date.isoformat(),
                            "subject": custom_sub,
                            "title": custom_title.strip() or f"{custom_sub} Study Session",
                            "status": "Pending",
                            "duration": int(custom_dur),
                        }
                        all_t = db.get_all_tasks() + [new_t]
                        db.set_all_tasks(all_t)
                        st.success("Session added!")
                        st.rerun()

            with col_filter:
                filter_mode = st.selectbox(
                    "Filter",
                    ["All Sessions", "Today's Sessions", "Pending Only", "Completed Only", "Missed Only"],
                    label_visibility="collapsed",
                )

            # Search & Course Filter
            c_srch, c_crs = st.columns([3, 2])
            with c_srch:
                search_q = st.text_input("Search", placeholder="🔍 Search by topic, subject, or date...", label_visibility="collapsed")
            with c_crs:
                crs_options = ["All Courses"] + [s["name"] for s in subjects_data]
                selected_crs = st.selectbox("Course", crs_options, label_visibility="collapsed")

            if not tasks_data:
                st.markdown(
                    """
                    <div class="web-card" style="text-align: center; padding: 35px 20px;">
                        <h4 style="color: #1E293B; margin: 0;">No Timetable Generated Yet</h4>
                        <p style="color: #64748B; font-size: 13.5px; margin-top: 4px;">Click <b>Generate / Refresh Schedule</b> above to create your study plan.</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                # Filter Tasks
                visible_tasks = tasks_data

                if filter_mode == "Today's Sessions":
                    visible_tasks = [t for t in visible_tasks if t.get("date") == today_str]
                elif filter_mode == "Pending Only":
                    visible_tasks = [t for t in visible_tasks if t.get("status") == "Pending"]
                elif filter_mode == "Completed Only":
                    visible_tasks = [t for t in visible_tasks if t.get("status") == "Completed"]
                elif filter_mode == "Missed Only":
                    visible_tasks = [t for t in visible_tasks if t.get("status") == "Missed"]

                if selected_crs != "All Courses":
                    visible_tasks = [t for t in visible_tasks if t.get("subject") == selected_crs]

                if search_q.strip():
                    q = search_q.strip().lower()
                    visible_tasks = [
                        t for t in visible_tasks
                        if q in t.get("subject", "").lower() or q in t.get("title", "").lower() or q in t.get("date", "").lower()
                    ]

                # Today's Progress Banner
                today_all = [t for t in tasks_data if t.get("date") == today_str]
                if today_all:
                    today_done = sum(1 for t in today_all if t.get("status") == "Completed")
                    today_pct = int(today_done / len(today_all) * 100)
                    all_today_done = (today_done == len(today_all))

                    st.markdown(
                        f"""
                        <div style="background: linear-gradient(135deg, {'#DCFCE7 0%, #BBF7D0 100%' if all_today_done else '#EEF2FF 0%, #E0E7FF 100%'}); border: 1px solid {'#86EFAC' if all_today_done else '#C7D2FE'}; border-radius: 12px; padding: 14px 18px; margin: 12px 0 16px 0; display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="font-weight: 800; color: {'#166534' if all_today_done else '#3730A3'}; font-size: 15px;">
                                    {'🎉 All Set for Today!' if all_today_done else f"🎯 Today's Target ({today_str})"}
                                </span>
                                <div style="font-size: 13px; color: {'#15803D' if all_today_done else '#4338CA'}; margin-top: 2px;">
                                    {today_done} of {len(today_all)} sessions completed ({today_pct}%)
                                </div>
                            </div>
                            <span class="status-pill {'pill-green' if all_today_done else 'pill-blue'}">
                                {'✓ Goal Reached' if all_today_done else f"{len(today_all) - today_done} Left Today"}
                            </span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                if not visible_tasks:
                    st.caption("No study sessions match your current filter.")
                else:
                    curr_date = None
                    for task in visible_tasks:
                        task_date = task.get("date", "")
                        if task_date != curr_date:
                            curr_date = task_date
                            is_today = (task_date == today_str)
                            tag = " — (Today)" if is_today else ""
                            st.markdown(f"##### 📆 {task_date}{tag}")

                        status = task.get("status", "Pending")
                        box_class = "task-box-completed" if status == "Completed" else "task-box-missed" if status == "Missed" else ""

                        col_t_info, col_t_act = st.columns([7, 4])
                        with col_t_info:
                            status_chip = (
                                "chip-status-completed" if status == "Completed"
                                else "chip-status-missed" if status == "Missed"
                                else "chip-status-pending"
                            )
                            st.markdown(
                                f"""
                                <div class="task-box {box_class}">
                                    <div style="display: flex; gap: 6px; align-items: center; margin-bottom: 4px;">
                                        <span class="chip chip-subject">{task.get('subject')}</span>
                                        <span class="chip {status_chip}">{status}</span>
                                        <span class="chip chip-date">⏱️ {task.get('duration', 60)} min</span>
                                    </div>
                                    <div style="font-size: 14.5px; font-weight: 600; color: #1E293B;">{task.get('title')}</div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                        with col_t_act:
                            b1, b2, b3 = st.columns(3)
                            with b1:
                                if st.button("✅ Done", key=f"d_{task['id']}", use_container_width=True, disabled=(status == "Completed")):
                                    db.update_task_status(task["id"], "Completed")
                                    st.toast("🎉 Great job! Session marked complete.")
                                    # Check if all today's tasks are done
                                    remaining = sum(1 for t in db.get_all_tasks() if t.get("date") == today_str and t.get("status") != "Completed")
                                    if remaining == 0 and len(today_all) > 0:
                                        st.balloons()
                                    st.rerun()

                            with b2:
                                if st.button("❌ Missed", key=f"m_{task['id']}", use_container_width=True, disabled=(status == "Missed")):
                                    db.update_task_status(task["id"], "Missed")
                                    st.toast("Marked as missed. You can reschedule anytime.")
                                    st.rerun()

                            with b3:
                                if st.button("↺ Reset", key=f"r_{task['id']}", use_container_width=True, disabled=(status == "Pending")):
                                    db.update_task_status(task["id"], "Pending")
                                    st.rerun()

    # ---------------------------------------------------------
    # TAB 2: SUBJECTS & EXAM COUNTDOWN
    # ---------------------------------------------------------
    with tab_subjects:
        st.markdown(
            """
            <div class="web-card">
                <div class="card-header">
                    <div>
                        <h3 class="card-title">📚 My Courses & Exam Deadlines</h3>
                        <p class="card-desc">Track days remaining until each exam and manage your curriculum stored in SQLite.</p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Active Exam Countdown Cards
        if subjects_data:
            st.markdown("#### ⏳ Exam Countdowns")
            cols_cd = st.columns(min(len(subjects_data), 4))
            for idx, sub in enumerate(subjects_data):
                col_c = cols_cd[idx % len(cols_cd)]
                with col_c:
                    d_left = planner.days_until(sub["exam_date"])
                    urgent_class = "countdown-urgent" if d_left <= 3 else "countdown-warning" if d_left <= 7 else "countdown-normal"
                    urgency_label = "🚨 High Urgency" if d_left <= 3 else "⚠️ Upcoming" if d_left <= 7 else "📅 In Prep"

                    sub_tasks = [t for t in tasks_data if t.get("subject") == sub["name"]]
                    sub_completed = sum(1 for t in sub_tasks if t.get("status") == "Completed")

                    st.markdown(
                        f"""
                        <div class="countdown-card {urgent_class}">
                            <div style="font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase;">{urgency_label}</div>
                            <div style="font-size: 16px; font-weight: 800; color: #0F172A; margin: 3px 0;">{sub['name']}</div>
                            <div style="font-size: 24px; font-weight: 900; color: {'#DC2626' if d_left <= 3 else '#D97706' if d_left <= 7 else '#2563EB'};">
                                {d_left} <span style="font-size: 13px; font-weight: 600;">days left</span>
                            </div>
                            <div style="font-size: 12px; color: #64748B; margin-top: 4px;">
                                Exam: <b>{sub['exam_date']}</b> • Diff: <b>{sub['difficulty']}/5</b>
                            </div>
                            <div style="font-size: 12px; color: #475569; margin-top: 3px;">
                                ⏱️ {len(sub_tasks)} sessions planned ({sub_completed} done)
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            st.markdown("<br>", unsafe_allow_html=True)

        # Interactive Quick-Add Subject Form
        st.markdown("#### ➕ Add New Course")
        with st.container():
            c_name, c_date, c_diff, c_btn = st.columns([4, 3, 3, 2])
            with c_name:
                new_sub_name = st.text_input("Course Name", placeholder="e.g. Operating Systems", label_visibility="collapsed")
            with c_date:
                new_sub_date = st.date_input("Target Exam Date", value=date.today() + timedelta(days=12), label_visibility="collapsed")
            with c_diff:
                new_sub_diff = st.selectbox("Difficulty", [1, 2, 3, 4, 5], index=2, format_func=lambda x: f"Difficulty: {x}/5", label_visibility="collapsed")
            with c_btn:
                if st.button("➕ Add Course", type="primary", use_container_width=True):
                    if new_sub_name.strip():
                        db.add_single_subject(new_sub_name.strip(), new_sub_date.isoformat(), new_sub_diff)
                        st.toast(f"Added {new_sub_name}!")
                        st.rerun()
                    else:
                        st.warning("Please enter a course name.")

        # Quick Preset Suggestions
        st.markdown("<p style='font-size: 12px; color: #64748B; margin: 4px 0 14px 0;'>💡 Quick presets: Click to add standard subjects in 1 click:</p>", unsafe_allow_html=True)
        col_p1, col_p2, col_p3, col_p4 = st.columns(4)
        with col_p1:
            if st.button("+ Python Programming", use_container_width=True):
                db.add_single_subject("Python Programming", (date.today() + timedelta(days=14)).isoformat(), 4)
                st.rerun()
        with col_p2:
            if st.button("+ DBMS", use_container_width=True):
                db.add_single_subject("Database Management Systems (DBMS)", (date.today() + timedelta(days=10)).isoformat(), 3)
                st.rerun()
        with col_p3:
            if st.button("+ Computer Networks", use_container_width=True):
                db.add_single_subject("Advanced Computer Networks", (date.today() + timedelta(days=6)).isoformat(), 3)
                st.rerun()
        with col_p4:
            if st.button("+ Cloud Architecture", use_container_width=True):
                db.add_single_subject("Cloud Computing Architecture", (date.today() + timedelta(days=18)).isoformat(), 4)
                st.rerun()

        st.markdown("---")

        # Curriculum Table with 1-Click Delete Action
        st.markdown("#### 📋 Enrolled Subjects List")
        if not subjects_data:
            st.caption("No subjects configured yet.")
        else:
            for s in subjects_data:
                c_s1, c_s2, c_s3, c_s4 = st.columns([5, 3, 2, 2])
                with c_s1:
                    st.markdown(f"**{s['name']}**")
                with c_s2:
                    st.caption(f"📅 Exam: {s['exam_date']} ({planner.days_until(s['exam_date'])} days left)")
                with c_s3:
                    st.caption(f"⭐ Difficulty: {s['difficulty']}/5")
                with c_s4:
                    if st.button("🗑️ Remove", key=f"del_{s['id']}", use_container_width=True):
                        db.delete_single_subject(s["id"])
                        st.toast(f"Removed {s['name']}")
                        st.rerun()
                st.markdown("<hr style='margin: 4px 0; border: none; border-top: 1px solid #F1F5F9;'>", unsafe_allow_html=True)

        col_seed, col_space, col_reset = st.columns([3, 5, 3])
        with col_seed:
            if st.button("✨ Load Default MCA Curriculum", use_container_width=True):
                db.seed_default_curriculum()
                st.toast("Loaded default curriculum!")
                st.rerun()
        with col_reset:
            with st.popover("⚠️ Reset Database"):
                st.write("This will erase all subjects, tasks, and pomodoro logs.")
                if st.button("Confirm Reset Everything", type="primary", use_container_width=True):
                    db.clear_database()
                    st.success("Database cleared!")
                    st.rerun()

    # ---------------------------------------------------------
    # TAB 3: FOCUS POMODORO TIMER
    # ---------------------------------------------------------
    with tab_pomodoro:
        st.markdown(
            """
            <div class="web-card">
                <div class="card-header">
                    <div>
                        <h3 class="card-title">⏱️ Interactive Focus Pomodoro Timer</h3>
                        <p class="card-desc">Execute distraction-free 25-minute study sprints with built-in Web Audio alerts and automatic SQLite logging.</p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_pomo_widget, col_pomo_log = st.columns([5, 4])

        with col_pomo_widget:
            components.html(styles.POMODORO_HTML, height=330)

        with col_pomo_log:
            st.markdown("#### 🎯 Quick Session Logger")
            st.write("Log completed focus minutes directly to SQLite:")

            today_pending = [t for t in tasks_data if t.get("date") == today_str and t.get("status") == "Pending"]

            if today_pending:
                chosen_task_title = st.selectbox(
                    "Link to active today's task:",
                    [t["title"] for t in today_pending],
                    key="pomo_task_select",
                )
                if st.button("🏁 Log 25m Sprint & Mark Done", type="primary", use_container_width=True):
                    for t in tasks_data:
                        if t.get("title") == chosen_task_title and t.get("date") == today_str:
                            db.update_task_status(t["id"], "Completed")
                            db.log_pomodoro(t["subject"], 25)
                            break
                    st.balloons()
                    st.toast(f"Logged 25m sprint for '{chosen_task_title}'!")
                    st.rerun()
            else:
                st.success("🌟 All scheduled tasks for today are completed!")
                free_sub = subjects_data[0]["name"] if subjects_data else "General Study"
                if st.button("⏱️ Log 25m Free Focus Sprint", use_container_width=True):
                    db.log_pomodoro(free_sub, 25)
                    st.toast(f"Logged 25m focus sprint for {free_sub}!")
                    st.rerun()

            st.markdown("---")
            st.markdown("##### 📜 Recent Focus Sprints")
            recent_sprints = db.get_pomodoro_logs()[:5]
            if recent_sprints:
                for s in recent_sprints:
                    st.markdown(f"• **{s['subject']}** — ⏱️ {s['duration_mins']} mins ({s['session_date']})")
            else:
                st.caption("No sprints logged yet. Complete a timer session to record your focus.")

    # ---------------------------------------------------------
    # TAB 4: AI STUDY COACH & INTERACTIVE QUIZ
    # ---------------------------------------------------------
    with tab_ai:
        st.markdown(
            """
            <div class="web-card">
                <div class="card-header">
                    <div>
                        <h3 class="card-title">🤖 Local AI Study Coach & Interactive Practice Quiz</h3>
                        <p class="card-desc">Take interactive practice quizzes with instant grading, or request custom study strategies from your AI coach.</p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        all_subject_names = [s["name"] for s in subjects_data] if subjects_data else ["Python Programming", "Database Management Systems (DBMS)", "Advanced Computer Networks", "Cloud Computing Architecture"]

        col_q_sub, col_q_mode = st.columns([3, 2])
        with col_q_sub:
            chosen_ai_subject = st.selectbox("Select Target Course", all_subject_names, key="ai_sub_choice")

        sub_tab_quiz, sub_tab_coach = st.tabs(["  📝 Interactive Practice Quiz  ", "  💡 AI Study Guidance  "])

        # -----------------------------
        # Sub-Tab A: Interactive Quiz
        # -----------------------------
        with sub_tab_quiz:
            quiz_questions = ai.get_interactive_quiz(chosen_ai_subject)
            st.markdown(f"#### 🎯 Practice Quiz: **{chosen_ai_subject}** (5 Questions)")
            st.caption("Select your answers and click **Submit Quiz** below to receive instant scoring and detailed explanations:")

            with st.form(f"quiz_form_{chosen_ai_subject}"):
                user_answers = {}
                for idx, q in enumerate(quiz_questions):
                    st.markdown(f"**Q{idx + 1}. {q['question']}**")
                    user_answers[idx] = st.radio(
                        f"Select your answer for Q{idx + 1}:",
                        q["options"],
                        key=f"q_{chosen_ai_subject}_{idx}",
                        label_visibility="collapsed",
                    )
                    st.markdown("<br>", unsafe_allow_html=True)

                quiz_submitted = st.form_submit_button("🏁 Submit Quiz & Check Score", type="primary", use_container_width=True)

            if quiz_submitted:
                correct_count = 0
                st.markdown("---")
                st.markdown("### 📊 Quiz Results & Explanations")

                for idx, q in enumerate(quiz_questions):
                    selected = user_answers[idx]
                    is_correct = (selected == q["answer"])
                    if is_correct:
                        correct_count += 1
                        st.success(f"**Q{idx + 1}: Correct!** ✅ (Your answer: *{selected}*)")
                    else:
                        st.error(f"**Q{idx + 1}: Incorrect** ❌ (Your answer: *{selected}* • Correct: **{q['answer']}**)")
                    st.info(f"💡 **Explanation:** {q['explanation']}")
                    st.markdown("<br>", unsafe_allow_html=True)

                score_pct = int(correct_count / len(quiz_questions) * 100)
                if score_pct >= 80:
                    st.balloons()
                    st.success(f"🎉 Outstanding! Score: **{correct_count} / {len(quiz_questions)} ({score_pct}%)** — You are well prepared!")
                elif score_pct >= 50:
                    st.warning(f"👍 Good effort! Score: **{correct_count} / {len(quiz_questions)} ({score_pct}%)** — Review the explanations above to reinforce your weak areas.")
                else:
                    st.error(f"📚 Score: **{correct_count} / {len(quiz_questions)} ({score_pct}%)** — Dedicate another 25-minute Pomodoro sprint to this subject today.")

        # -----------------------------
        # Sub-Tab B: AI Study Guidance
        # -----------------------------
        with sub_tab_coach:
            st.markdown("#### ⚡ Quick AI Modes")
            c_gm1, c_gm2, c_gm3 = st.columns(3)
            quick_prompt = None

            with c_gm1:
                if st.button("⚡ 3-Day Intensive Cram Plan", use_container_width=True):
                    quick_prompt = f"Give me a high-intensity 3-day revision strategy for {chosen_ai_subject}."

            with c_gm2:
                if st.button("🧠 Active Recall & Feynman Guide", use_container_width=True):
                    quick_prompt = f"How can I use active recall and the Feynman Technique to master {chosen_ai_subject}?"

            with c_gm3:
                if st.button("🎯 High-Yield Topics Breakdown", use_container_width=True):
                    quick_prompt = f"What are the top 5 high-yield topics and exam questions for {chosen_ai_subject}?"

            custom_user_q = st.text_area(
                "Or ask a specific question:",
                value=quick_prompt if quick_prompt else "",
                placeholder=f"e.g. How to prepare for {chosen_ai_subject} in 2 days? What are the key formulas?",
                height=90,
            )

            if st.button("🚀 Ask Study Coach", type="primary", use_container_width=True):
                if not custom_user_q.strip():
                    st.warning("Please type a question or click one of the quick mode buttons above.")
                else:
                    prompt = ai.build_study_prompt(
                        subjects_data,
                        hours_per_day,
                        plan_days,
                        chosen_ai_subject,
                        custom_user_q,
                    )
                    with st.spinner("🧠 Generating your customized study strategy..."):
                        if ollama_online and model_available:
                            response_text = ai.ask_ollama(prompt, model_name.strip() or ai.DEFAULT_MODEL)
                        else:
                            response_text = None

                        if not response_text:
                            response_text = ai.get_smart_fallback_response(custom_user_q, chosen_ai_subject, hours_per_day, plan_days)

                    st.markdown(
                        f"""
                        <div class="web-card" style="border: 1px solid #C7D2FE; margin-top: 14px;">
                            <div style="font-weight: 700; color: #4338CA; margin-bottom: 6px; display: flex; justify-content: space-between;">
                                <span>🧠 Study Coach Insights</span>
                                <span style="font-size: 11px; font-weight: 500; color: #64748B;">{f'Ollama: {model_name}' if (ollama_online and model_available) else 'Built-in Study Engine'}</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.markdown(response_text)

    # ---------------------------------------------------------
    # TAB 5: PROGRESS & DATABASE
    # ---------------------------------------------------------
    with tab_analytics:
        st.markdown(
            """
            <div class="web-card">
                <div class="card-header">
                    <div>
                        <h3 class="card-title">📊 Revision Analytics & SQLite Database Inspector</h3>
                        <p class="card-desc">Visual workload allocation, task completion breakdown, and direct table records inspection.</p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not tasks_data:
            st.info("No study sessions scheduled yet. Generate a timetable to view visual analytics.")
        else:
            df_tasks = pd.DataFrame(tasks_data)

            col_c1, col_c2 = st.columns(2)

            with col_c1:
                st.markdown("##### 📚 Hours Allocated per Subject")
                sub_counts = df_tasks["subject"].value_counts().reset_index()
                sub_counts.columns = ["Subject", "Hours"]

                bar_chart = (
                    alt.Chart(sub_counts)
                    .mark_bar(cornerRadiusTopRight=6, cornerRadiusBottomRight=6)
                    .encode(
                        x=alt.X("Hours:Q", title="Total Hours"),
                        y=alt.Y("Subject:N", sort="-x", title=None),
                        color=alt.Color("Subject:N", legend=None, scale=alt.Scale(scheme="indigo")),
                        tooltip=["Subject", "Hours"],
                    )
                    .properties(height=240)
                )
                st.altair_chart(bar_chart, use_container_width=True)

            with col_c2:
                st.markdown("##### 🎯 Task Status Breakdown")
                status_counts = df_tasks["status"].value_counts().reset_index()
                status_counts.columns = ["Status", "Count"]

                donut_chart = (
                    alt.Chart(status_counts)
                    .mark_arc(innerRadius=50, cornerRadius=4)
                    .encode(
                        theta=alt.Theta("Count:Q"),
                        color=alt.Color(
                            "Status:N",
                            scale=alt.Scale(
                                domain=["Completed", "Pending", "Missed"],
                                range=["#22C55E", "#F59E0B", "#EF4444"],
                            ),
                        ),
                        tooltip=["Status", "Count"],
                    )
                    .properties(height=240)
                )
                st.altair_chart(donut_chart, use_container_width=True)

        # Direct Relational Database & PL/SQL Management
        st.markdown("---")
        st.markdown("#### 🗄️ Relational Database & Oracle PL/SQL Management")
        st.caption(f"Active Backend: **{active_engine_name}**")

        tab_db_records, tab_db_plsql, tab_db_code = st.tabs([
            "  📋 Live Database Records  ",
            "  🏛️ Oracle PL/SQL Connection  ",
            "  📜 Stored Procedures & Package (PL/SQL)  ",
        ])

        # -----------------------------
        # Sub-tab 1: Live Records
        # -----------------------------
        with tab_db_records:
            t1, t2, t3, t4 = st.tabs(["📋 SUBJECTS", "📅 TASKS", "⏱️ POMODORO_LOGS", "🛡️ AUDIT_LOGS"])
            with t1:
                raw_s = db.get_all_subjects()
                if raw_s:
                    st.dataframe(pd.DataFrame(raw_s), use_container_width=True)
                else:
                    st.caption("No records in subjects table.")

            with t2:
                raw_t = db.get_all_tasks()
                if raw_t:
                    st.dataframe(pd.DataFrame(raw_t), use_container_width=True)
                else:
                    st.caption("No records in tasks table.")

            with t3:
                raw_p = db.get_pomodoro_logs()
                if raw_p:
                    st.dataframe(pd.DataFrame(raw_p), use_container_width=True)
                else:
                    st.caption("No records in pomodoro_logs table.")

            with t4:
                if db.is_oracle_mode():
                    try:
                        raw_a = pm.plsql_get_audit_logs()
                        if raw_a:
                            st.dataframe(pd.DataFrame(raw_a), use_container_width=True)
                        else:
                            st.caption("No audit entries yet. Triggers record all insert/update operations.")
                    except Exception as e:
                        st.caption(f"Audit log query error: {e}")
                else:
                    st.info("💡 Trigger audit logs are maintained in Oracle Database via `TRG_TASKS_AUDIT` trigger in the `AUDIT_LOGS` table.")

        # -----------------------------
        # Sub-tab 2: Oracle PL/SQL Connection
        # -----------------------------
        with tab_db_plsql:
            st.markdown("##### 🏛️ Oracle Database & PL/SQL Configuration")
            st.write("Connect to your local or remote Oracle Database (11g, 12c, 19c, 21c, 23ai Express / Enterprise) via `oracledb` Thin mode:")

            curr_cfg = pm.load_oracle_config()

            col_o1, col_o2 = st.columns(2)
            with col_o1:
                o_host = st.text_input("Oracle Host", value=curr_cfg.get("host", "localhost"))
                o_port = st.number_input("Oracle Port", value=int(curr_cfg.get("port", 1521)), step=1)
                o_service = st.text_input("Service Name / SID", value=curr_cfg.get("service_name", "XE"), help="Defaults: XE for Express Edition, ORCL for Enterprise, or XEPDB1 for pluggable DB.")

            with col_o2:
                o_user = st.text_input("Username", value=curr_cfg.get("user", "system"))
                o_pass = st.text_input("Password", value=curr_cfg.get("password", ""), type="password")
                o_enable = st.checkbox("Enable Oracle PL/SQL as Active Database Engine", value=curr_cfg.get("enabled", False))

            c_btn_test, c_btn_save, c_btn_init, c_btn_sync = st.columns([2, 2, 3, 3])

            with c_btn_test:
                if st.button("🔌 Test Connection", use_container_width=True):
                    if not o_pass:
                        st.warning("Please enter your Oracle password.")
                    else:
                        ok, msg = pm.test_oracle_connection(o_user, o_pass, o_host, o_port, o_service)
                        if ok:
                            st.success(f"✅ {msg}")
                        else:
                            st.error(f"❌ Connection Failed: {msg}")

            with c_btn_save:
                if st.button("💾 Save Settings", use_container_width=True):
                    new_cfg = {
                        "enabled": o_enable,
                        "user": o_user,
                        "password": o_pass,
                        "host": o_host,
                        "port": int(o_port),
                        "service_name": o_service,
                    }
                    pm.save_oracle_config(new_cfg)
                    st.toast("Oracle configuration saved!")
                    st.rerun()

            with c_btn_init:
                if st.button("⚡ Compile PL/SQL Script", use_container_width=True):
                    if not o_pass:
                        st.warning("Please configure and test Oracle connection credentials first.")
                    else:
                        with st.spinner("Compiling tables, sequences, triggers, and STUDY_PLANNER_PKG on Oracle..."):
                            ok, msg = pm.plsql_init_schema()
                            if ok:
                                st.balloons()
                                st.success(f"🎉 {msg}")
                                st.rerun()
                            else:
                                st.error(f"❌ PL/SQL Compilation Error: {msg}")

            with c_btn_sync:
                if st.button("🔄 Sync SQLite -> Oracle", use_container_width=True):
                    ok, msg = db.sync_sqlite_to_oracle()
                    if ok:
                        st.toast(msg)
                        st.rerun()
                    else:
                        st.warning(msg)

        # -----------------------------
        # Sub-tab 3: PL/SQL Code & Package Viewer
        # -----------------------------
        with tab_db_code:
            st.markdown("##### 📜 Oracle PL/SQL Package (`STUDY_PLANNER_PKG`) & Architecture")
            st.write("All application data operations are handled via compiled PL/SQL stored procedures, triggers, sequences, and package bodies:")

            sql_file_path = Path(__file__).parent / "database_plsql.sql"
            if sql_file_path.exists():
                sql_content = sql_file_path.read_text(encoding="utf-8")
                st.download_button(
                    label="📥 Download database_plsql.sql (Ready for Oracle SQL Developer / SQL*Plus)",
                    data=sql_content,
                    file_name="database_plsql.sql",
                    mime="text/x-sql",
                    type="primary",
                )
                with st.expander("👁️ View Full PL/SQL Script (DDL, Sequences, Triggers, Functions & Package)", expanded=True):
                    st.code(sql_content, language="sql")
            else:
                st.caption("database_plsql.sql file not found.")

    # ---------------------------------------------------------
    # Web Footer
    # ---------------------------------------------------------
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="border-top: 1px solid #E2E8F0; padding: 18px 0; text-align: center; color: #94A3B8; font-size: 12px;">
            SmartStudy Planner AI • Clean, Interactive Local Study Suite • Relational Engine (SQLite & Oracle PL/SQL <code>STUDY_PLANNER_PKG</code>)
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
