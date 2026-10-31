"""
SmartStudy Planner AI (StudyFlow) - Main Application Entrypoint
Faithfully recreates the modern StudyFlow SaaS UI:
- Dark sleek sidebar navigation (#0F172A) with purple active pill (#7C3AED)
- Center feed: AI Study Recommendations, Priority Tasks, and Colored Course Cards
- Right sidebar: Study Session focus timer and Tasks Progress with study streaks
- Dual-engine backend: SQLite local engine & Oracle PL/SQL (STUDY_PLANNER_PKG)
"""

import sys
from datetime import date, datetime, timedelta
from pathlib import Path
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

# Subsystem imports
import database as db
import plsql_manager as pm
import planner
import ai_assistant as ai
import styles


def get_course_code(subject_name, idx=1):
    """Generates a clean course code (e.g. CS-433) for UI matching."""
    s = subject_name.lower()
    if "python" in s:
        return "CS-101"
    if "data structure" in s or "dbms" in s or "database" in s:
        return "CS-201"
    if "network" in s:
        return "CS-304"
    if "cloud" in s or "machine" in s or "ml" in s:
        return "CS-433"
    return f"CS-{100 + (idx * 101)}"


def main():
    # ---------------------------------------------------------
    # Page Configuration & Modern Theme Styles
    # ---------------------------------------------------------
    st.set_page_config(
        page_title="StudyFlow - AI Study Planner",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(styles.CUSTOM_CSS, unsafe_allow_html=True)

    # Initialize Database (SQLite / Oracle PL/SQL check)
    db.init_db()

    # Query persistent data
    subjects_data = db.get_all_subjects()
    tasks_data = db.get_all_tasks()
    pomodoro_logs = db.get_pomodoro_logs()

    # Auto-seed clean default plan if brand new so UI looks complete immediately
    if not subjects_data and not tasks_data:
        db.seed_sample_plan_data()
        subjects_data = db.get_all_subjects()
        tasks_data = db.get_all_tasks()
        pomodoro_logs = db.get_pomodoro_logs()

    # ---------------------------------------------------------
    # LEFT SLEEK DARK SIDEBAR (StudyFlow Navigation)
    # ---------------------------------------------------------
    with st.sidebar:
        st.markdown(styles.get_sidebar_brand_html(), unsafe_allow_html=True)

        # Navigation Menu matching screenshot exactly
        nav_options = [
            "Dashboard",
            "Courses",
            "Tasks",
            "Study Sessions",
            "Schedule",
            "Analytics",
            "Settings",
        ]

        # Use session state to support cross-page jumps (e.g. "View all ↗")
        if "nav_page" not in st.session_state:
            st.session_state.nav_page = "Dashboard"

        nav_choice = st.radio(
            "Navigation",
            nav_options,
            index=nav_options.index(st.session_state.nav_page) if st.session_state.nav_page in nav_options else 0,
            label_visibility="collapsed",
            key="main_nav_radio",
        )
        st.session_state.nav_page = nav_choice

        # Bottom AI Assistant Box
        st.markdown(styles.get_sidebar_ai_assistant_html(), unsafe_allow_html=True)

    today_str = date.today().isoformat()

    # =========================================================
    # VIEW 1: DASHBOARD (EXACT SCREENSHOT LAYOUT)
    # =========================================================
    if st.session_state.nav_page == "Dashboard":
        # Header Greeting
        st.markdown(styles.get_main_greeting_html("Student"), unsafe_allow_html=True)

        # Layout: Center Main Feed (approx 65%) + Right Widgets (approx 35%)
        col_center, col_right = st.columns([6.8, 3.2])

        # -----------------------------------------------------
        # CENTER COLUMN: Feed
        # -----------------------------------------------------
        with col_center:
            # 1. AI Study Recommendations Card
            with st.container():
                st.markdown(styles.get_ai_recommendations_banner_html(), unsafe_allow_html=True)

                c_rec_space1, c_rec_btn, c_rec_space2 = st.columns([3, 4, 3])
                with c_rec_btn:
                    if st.button("✨ Generate Recommendations", type="primary", use_container_width=True):
                        st.session_state.show_ai_recs = True

                # Expandable or popup AI recommendation content
                if st.session_state.get("show_ai_recs", False):
                    with st.spinner("🤖 Analyzing upcoming exams and pending tasks..."):
                        top_sub = subjects_data[0]["name"] if subjects_data else "General Study"
                        ollama_online, model_available, _ = ai.check_ollama_status()
                        if ollama_online and model_available:
                            prompt = ai.build_study_prompt(subjects_data, 3, 7, top_sub, "Give me 3 prioritized study recommendations for today.")
                            rec_text = ai.ask_ollama(prompt)
                        else:
                            rec_text = ai.get_smart_fallback_response("urgent cram 3-day plan", top_sub, 3, 7)

                    st.markdown(
                        f"""
                        <div class="sf-card" style="border: 1px solid #C4B5FD; background: #FAF5FF; margin-top: 14px;">
                            <div style="font-size: 13.5px; font-weight: 700; color: #6D28D9; margin-bottom: 6px;">
                                ✦ Personalized Study Strategy (Based on your curriculum):
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.markdown(rec_text)
                    if st.button("✕ Dismiss Recommendations"):
                        st.session_state.show_ai_recs = False
                        st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)

            # 2. Priority Tasks Section
            c_task_hdr, c_task_link = st.columns([8, 2])
            with c_task_hdr:
                st.markdown("<h3 style='font-size: 18px; font-weight: 800; color: #0F172A; margin: 0 0 12px 0;'>Priority Tasks</h3>", unsafe_allow_html=True)
            with c_task_link:
                if st.button("View all ↗", key="btn_view_all_tasks"):
                    st.session_state.nav_page = "Tasks"
                    st.rerun()

            # Filter for Priority Tasks (Tasks scheduled for today or pending)
            priority_tasks = [t for t in tasks_data if t.get("status") != "Completed"]
            if not priority_tasks:
                priority_tasks = tasks_data[:4]  # fallback to first few if all completed

            display_tasks = priority_tasks[:3]  # show top 3 matching screenshot

            for idx, task in enumerate(display_tasks):
                task_id = task.get("id")
                task_status = task.get("status", "Pending")
                task_sub = task.get("subject", "Course")
                task_title = task.get("title", "Study Session")
                course_code = get_course_code(task_sub, idx + 1)

                # Assign priority pill based on difficulty or position
                priority_label = "high" if idx in [0, 2] else "medium"
                p_badge_class = f"badge-priority-{priority_label}"

                dur_hours = int(task.get("duration", 60) / 60) or 1
                deadline_text = "Tomorrow at 11:59 PM" if idx == 0 else "Friday at 6:00 PM" if idx == 1 else "Next Monday"

                c_check, c_body = st.columns([1, 11])
                with c_check:
                    # Circular toggle button resembling radio button ○ / ●
                    is_done = (task_status == "Completed")
                    check_icon = "●" if is_done else "○"
                    if st.button(check_icon, key=f"dash_toggle_{task_id}", help="Click to toggle completion"):
                        new_status = "Pending" if is_done else "Completed"
                        db.update_task_status(task_id, new_status)
                        if new_status == "Completed":
                            st.toast(f"Completed: {task_title}!")
                        st.rerun()

                with c_body:
                    row_completed_class = "task-row-completed" if is_done else ""
                    st.markdown(
                        f"""
                        <div class="task-row-container {row_completed_class}">
                            <div>
                                <div style="font-size: 14px; font-weight: 700; color: #1E293B; {'text-decoration: line-through; opacity: 0.6;' if is_done else ''}">
                                    {task_title}
                                </div>
                                <div style="display: flex; align-items: center; gap: 8px; margin-top: 4px;">
                                    <span class="badge-course-code">{course_code}</span>
                                    <span style="font-size: 12px; color: #64748B;">⏱️ {dur_hours}h</span>
                                    <span style="font-size: 12px; color: #64748B;">📅 {deadline_text}</span>
                                </div>
                            </div>
                            <div>
                                <span class="badge-priority {p_badge_class}">{priority_label}</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            st.markdown("<br>", unsafe_allow_html=True)

            # 3. Course Cards (Horizontal Grid)
            if subjects_data:
                col_c1, col_c2 = st.columns(2)
                palette = ["blue", "green", "purple", "amber"]

                # Card 1: Left Course
                sub1 = subjects_data[0]
                code1 = get_course_code(sub1["name"], 1)
                sub1_tasks = [t for t in tasks_data if t.get("subject") == sub1["name"]]
                sub1_done = sum(1 for t in sub1_tasks if t.get("status") == "Completed")
                sub1_pct = (sub1_done / len(sub1_tasks) * 100) if sub1_tasks else 65.0
                sub1_hours = sum(t.get("duration", 60) for t in sub1_tasks) // 60 or 24

                with col_c1:
                    st.markdown(
                        styles.get_course_card_html(
                            code=code1,
                            name=sub1["name"],
                            progress_pct=sub1_pct,
                            tasks_count=len(sub1_tasks),
                            hours_spent=sub1_hours,
                            color="blue",
                            next_info=f"Exam: {sub1['exam_date']} ({planner.days_until(sub1['exam_date'])}d left)",
                        ),
                        unsafe_allow_html=True,
                    )

                # Card 2: Right Course
                if len(subjects_data) > 1:
                    sub2 = subjects_data[1]
                else:
                    sub2 = {"name": "Data Structures", "exam_date": (date.today() + timedelta(days=10)).isoformat()}

                code2 = get_course_code(sub2["name"], 2)
                sub2_tasks = [t for t in tasks_data if t.get("subject") == sub2["name"]]
                sub2_done = sum(1 for t in sub2_tasks if t.get("status") == "Completed")
                sub2_pct = (sub2_done / len(sub2_tasks) * 100) if sub2_tasks else 48.0
                sub2_hours = sum(t.get("duration", 60) for t in sub2_tasks) // 60 or 18

                with col_c2:
                    st.markdown(
                        styles.get_course_card_html(
                            code=code2,
                            name=sub2["name"],
                            progress_pct=sub2_pct,
                            tasks_count=len(sub2_tasks),
                            hours_spent=sub2_hours,
                            color="green",
                            next_info=f"Exam: {sub2['exam_date']} ({planner.days_until(sub2['exam_date'])}d left)",
                        ),
                        unsafe_allow_html=True,
                    )

        # -----------------------------------------------------
        # RIGHT COLUMN: Study Session & Tasks Progress Widgets
        # -----------------------------------------------------
        with col_right:
            # 1. Study Session Widget
            with st.container():
                st.markdown(
                    """
                    <div class="sf-card" style="padding: 20px;">
                        <div class="sf-card-header" style="margin-bottom: 12px;">
                            <span class="sf-card-title">⏱ Study Session</span>
                        </div>
                    """,
                    unsafe_allow_html=True,
                )

                sub_choices = ["Select a course"] + [s["name"] for s in subjects_data]
                chosen_timer_course = st.selectbox("Course", sub_choices, label_visibility="visible", key="dash_session_sub")
                chosen_timer_dur = st.selectbox("Duration", ["25 minutes", "15 minutes", "45 minutes", "50 minutes"], index=0, key="dash_session_dur")

                # Digital clock countdown display matching screenshot
                st.markdown(
                    """
                        <div class="digital-clock-display">00:25:00</div>
                        <div class="digital-clock-caption">Select a course to begin</div>
                    """,
                    unsafe_allow_html=True,
                )

                # Reset and Start buttons side by side
                c_t_reset, c_t_start = st.columns([1, 1])
                with c_t_reset:
                    if st.button("⏭ Reset", use_container_width=True, key="dash_btn_reset"):
                        st.toast("Timer reset to 25:00")
                with c_t_start:
                    if st.button("▶ Start", type="primary", use_container_width=True, key="dash_btn_start"):
                        if chosen_timer_course == "Select a course":
                            st.warning("Please choose a course first.")
                        else:
                            # Log 25m sprint directly to SQLite / Oracle PL/SQL
                            mins = int(chosen_timer_dur.split()[0])
                            db.log_pomodoro(chosen_timer_course, mins)
                            st.balloons()
                            st.toast(f"Focus sprint for {chosen_timer_course} logged to database!")
                            st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # 2. Tasks Progress Widget with Segmented Study Streak
            total_t = len(tasks_data)
            done_t = sum(1 for t in tasks_data if t.get("status") == "Completed")
            streak_days = max(1, len(pomodoro_logs) * 3 or 12)

            st.markdown(
                styles.get_task_progress_widget_html(
                    completed_count=done_t,
                    total_count=total_t or 35,
                    streak_days=streak_days,
                ),
                unsafe_allow_html=True,
            )

    # =========================================================
    # VIEW 2: COURSES
    # =========================================================
    elif st.session_state.nav_page == "Courses":
        st.markdown("<h1 style='font-size: 26px; font-weight: 800; color: #0F172A; margin-bottom: 4px;'>📚 My Courses & Exam Deadlines</h1>", unsafe_allow_html=True)
        st.caption("Manage your enrolled curriculum, track countdowns, and configure difficulty ratings.")

        # Quick Add Course Row
        with st.container():
            c_n, c_d, c_diff, c_add = st.columns([4, 3, 3, 2])
            with c_n:
                add_sub_name = st.text_input("Course Name", placeholder="e.g. Artificial Intelligence", label_visibility="collapsed")
            with c_d:
                add_sub_date = st.date_input("Target Exam Date", value=date.today() + timedelta(days=14), label_visibility="collapsed")
            with c_diff:
                add_sub_diff = st.selectbox("Difficulty (1-5)", [1, 2, 3, 4, 5], index=2, format_func=lambda x: f"Difficulty: {x}/5", label_visibility="collapsed")
            with c_add:
                if st.button("➕ Add Course", type="primary", use_container_width=True):
                    if add_sub_name.strip():
                        db.add_single_subject(add_sub_name.strip(), add_sub_date.isoformat(), add_sub_diff)
                        st.toast(f"Added {add_sub_name}!")
                        st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # Course Cards Grid
        cols_course_grid = st.columns(2)
        for idx, sub in enumerate(subjects_data):
            col_target = cols_course_grid[idx % 2]
            with col_target:
                sub_tasks = [t for t in tasks_data if t.get("subject") == sub["name"]]
                sub_done = sum(1 for t in sub_tasks if t.get("status") == "Completed")
                sub_pct = (sub_done / len(sub_tasks) * 100) if sub_tasks else 0
                sub_hours = sum(t.get("duration", 60) for t in sub_tasks) // 60
                d_left = planner.days_until(sub["exam_date"])
                code = get_course_code(sub["name"], idx + 1)
                color = "blue" if idx % 4 == 0 else "green" if idx % 4 == 1 else "purple" if idx % 4 == 2 else "amber"

                st.markdown(
                    styles.get_course_card_html(
                        code=code,
                        name=sub["name"],
                        progress_pct=sub_pct,
                        tasks_count=len(sub_tasks),
                        hours_spent=sub_hours,
                        color=color,
                        next_info=f"Exam: {sub['exam_date']} • {d_left} days left",
                    ),
                    unsafe_allow_html=True,
                )
                if st.button(f"🗑️ Delete {sub['name']}", key=f"del_crs_{sub['id']}"):
                    db.delete_single_subject(sub["id"])
                    st.toast(f"Deleted {sub['name']}")
                    st.rerun()
                st.markdown("<br>", unsafe_allow_html=True)

    # =========================================================
    # VIEW 3: TASKS
    # =========================================================
    elif st.session_state.nav_page == "Tasks":
        st.markdown("<h1 style='font-size: 26px; font-weight: 800; color: #0F172A; margin-bottom: 4px;'>☑️ Study Tasks & Daily Timetable</h1>", unsafe_allow_html=True)
        st.caption("Track, check off, and reschedule daily study sessions stored in SQLite & Oracle PL/SQL.")

        col_t_btn1, col_t_btn2, col_t_btn3, col_t_filter = st.columns([3, 3, 2, 3])
        with col_t_btn1:
            if st.button("✨ Generate / Refresh Plan", type="primary", use_container_width=True):
                new_plan = planner.make_plan(subjects_data, 3, date.today(), 7)
                if new_plan:
                    db.set_all_tasks(new_plan)
                    st.balloons()
                    st.toast("Generated balanced timetable!")
                    st.rerun()

        with col_t_btn2:
            missed_count = sum(1 for t in tasks_data if t.get("status") == "Missed")
            if st.button(f"🔄 Reschedule Missed ({missed_count})", use_container_width=True, disabled=(missed_count == 0)):
                missed_items = [t for t in tasks_data if t.get("status") == "Missed"]
                resched_map = planner.calculate_reschedule_mapping(missed_items, 7)
                db.reschedule_tasks(resched_map)
                st.toast("Rescheduled missed sessions!")
                st.rerun()

        with col_t_btn3:
            with st.popover("➕ New Task"):
                p_sub = st.selectbox("Subject", [s["name"] for s in subjects_data])
                p_date = st.date_input("Date", value=date.today())
                p_title = st.text_input("Title", value=f"{p_sub} Session")
                if st.button("Add Task", type="primary"):
                    import uuid
                    new_item = {
                        "id": f"t_{uuid.uuid4().hex[:6]}",
                        "date": p_date.isoformat(),
                        "subject": p_sub,
                        "title": p_title,
                        "status": "Pending",
                        "duration": 60,
                    }
                    db.set_all_tasks(db.get_all_tasks() + [new_item])
                    st.rerun()

        with col_t_filter:
            t_filter_view = st.selectbox("Filter", ["All Tasks", "Today's Focus", "Pending", "Completed", "Missed"], label_visibility="collapsed")

        # Task Items List
        visible_tasks = tasks_data
        if t_filter_view == "Today's Focus":
            visible_tasks = [t for t in visible_tasks if t.get("date") == today_str]
        elif t_filter_view == "Pending":
            visible_tasks = [t for t in visible_tasks if t.get("status") == "Pending"]
        elif t_filter_view == "Completed":
            visible_tasks = [t for t in visible_tasks if t.get("status") == "Completed"]
        elif t_filter_view == "Missed":
            visible_tasks = [t for t in visible_tasks if t.get("status") == "Missed"]

        for idx, task in enumerate(visible_tasks):
            t_id = task.get("id")
            t_status = task.get("status", "Pending")
            is_done = (t_status == "Completed")
            course_code = get_course_code(task.get("subject", "Course"), idx + 1)

            c_chk, c_info = st.columns([1, 11])
            with c_chk:
                chk_icon = "●" if is_done else "○"
                if st.button(chk_icon, key=f"tbl_chk_{t_id}"):
                    new_st = "Pending" if is_done else "Completed"
                    db.update_task_status(t_id, new_st)
                    st.rerun()

            with c_info:
                st.markdown(
                    f"""
                    <div class="task-row-container {'task-row-completed' if is_done else ''}">
                        <div>
                            <div style="font-weight: 700; font-size: 14.5px; {'text-decoration: line-through; color: #94A3B8;' if is_done else 'color: #0F172A;'}">
                                {task.get('title')}
                            </div>
                            <div style="font-size: 12px; color: #64748B; margin-top: 4px;">
                                <span class="badge-course-code">{course_code}</span> • 📆 {task.get('date')} • ⏱️ {task.get('duration', 60)}m
                            </div>
                        </div>
                        <div>
                            <span class="badge-priority badge-priority-{'high' if idx % 2 == 0 else 'medium'}">{t_status}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # =========================================================
    # VIEW 4: STUDY SESSIONS (POMODORO FOCUS STATION)
    # =========================================================
    elif st.session_state.nav_page == "Study Sessions":
        st.markdown("<h1 style='font-size: 26px; font-weight: 800; color: #0F172A; margin-bottom: 4px;'>⏱️ Focus Pomodoro Study Sessions</h1>", unsafe_allow_html=True)
        st.caption("Execute 25-minute distraction-free study sprints with Web Audio chimes and automatic logging.")

        col_p1, col_p2 = st.columns([5, 4])
        with col_p1:
            components.html(styles.POMODORO_HTML, height=330)

        with col_p2:
            st.markdown("#### 🎯 Quick Session Logger")
            p_sub = st.selectbox("Select Course", [s["name"] for s in subjects_data] or ["General Review"], key="pomo_station_sub")
            p_mins = st.slider("Session Duration (minutes)", min_value=15, max_value=60, value=25, step=5)
            if st.button("🏁 Log Completed Sprint", type="primary", use_container_width=True):
                db.log_pomodoro(p_sub, p_mins)
                st.balloons()
                st.toast(f"Logged {p_mins}m focus sprint for {p_sub}!")
                st.rerun()

            st.markdown("---")
            st.markdown("##### 📜 Recent Study Sprints")
            if pomodoro_logs:
                for p in pomodoro_logs[:5]:
                    st.markdown(f"• **{p['subject']}** — ⏱️ {p['duration_mins']} mins ({p['session_date']})")
            else:
                st.caption("No sprints logged yet.")

    # =========================================================
    # VIEW 5: SCHEDULE (TIMELINE & LOAD DISTRIBUTION)
    # =========================================================
    elif st.session_state.nav_page == "Schedule":
        st.markdown("<h1 style='font-size: 26px; font-weight: 800; color: #0F172A; margin-bottom: 4px;'>📅 Study Schedule & Workload Timeline</h1>", unsafe_allow_html=True)
        st.caption("Inspect daily study hour allocations balanced across your exam horizon.")

        if tasks_data:
            df_tasks = pd.DataFrame(tasks_data)
            daily_counts = df_tasks.groupby(["date", "subject"]).size().reset_index(name="Sessions")
            timeline_chart = (
                alt.Chart(daily_counts)
                .mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5)
                .encode(
                    x=alt.X("date:N", title="Study Date"),
                    y=alt.Y("Sessions:Q", title="Study Hours (Sessions)"),
                    color=alt.Color("subject:N", title="Course", scale=alt.Scale(scheme="purpleblue")),
                    tooltip=["date", "subject", "Sessions"],
                )
                .properties(height=350)
            )
            st.altair_chart(timeline_chart, use_container_width=True)
        else:
            st.info("No study sessions scheduled yet. Click below to generate your schedule.")
            if st.button("✨ Generate Schedule", type="primary"):
                db.seed_sample_plan_data()
                st.rerun()

    # =========================================================
    # VIEW 6: ANALYTICS (CHARTS & DATABASE TABLES)
    # =========================================================
    elif st.session_state.nav_page == "Analytics":
        st.markdown("<h1 style='font-size: 26px; font-weight: 800; color: #0F172A; margin-bottom: 4px;'>📊 Study Analytics & Performance Breakdown</h1>", unsafe_allow_html=True)
        st.caption("Visual time allocation and completion metrics.")

        if tasks_data:
            df_tasks = pd.DataFrame(tasks_data)
            col_an1, col_an2 = st.columns(2)

            with col_an1:
                st.markdown("##### 📚 Hours Allocated per Course")
                sub_counts = df_tasks["subject"].value_counts().reset_index()
                sub_counts.columns = ["Course", "Hours"]
                bar_chart = (
                    alt.Chart(sub_counts)
                    .mark_bar(cornerRadiusTopRight=6, cornerRadiusBottomRight=6)
                    .encode(
                        x=alt.X("Hours:Q", title="Total Hours"),
                        y=alt.Y("Course:N", sort="-x", title=None),
                        color=alt.Color("Course:N", legend=None, scale=alt.Scale(scheme="purples")),
                        tooltip=["Course", "Hours"],
                    )
                    .properties(height=260)
                )
                st.altair_chart(bar_chart, use_container_width=True)

            with col_an2:
                st.markdown("##### 🎯 Tasks Status Breakdown")
                status_counts = df_tasks["status"].value_counts().reset_index()
                status_counts.columns = ["Status", "Count"]
                donut = (
                    alt.Chart(status_counts)
                    .mark_arc(innerRadius=50, cornerRadius=4)
                    .encode(
                        theta=alt.Theta("Count:Q"),
                        color=alt.Color("Status:N", scale=alt.Scale(domain=["Completed", "Pending", "Missed"], range=["#10B981", "#F59E0B", "#EF4444"])),
                        tooltip=["Status", "Count"],
                    )
                    .properties(height=260)
                )
                st.altair_chart(donut, use_container_width=True)

    # =========================================================
    # VIEW 7: SETTINGS & DATABASE MANAGEMENT
    # =========================================================
    elif st.session_state.nav_page == "Settings":
        st.markdown("<h1 style='font-size: 26px; font-weight: 800; color: #0F172A; margin-bottom: 4px;'>⚙️ Planner Settings & Database Hub</h1>", unsafe_allow_html=True)
        st.caption(f"Active Backend Engine: **{db.get_current_engine_name()}**")

        tab_cfg_ai, tab_cfg_oracle, tab_cfg_sqlite = st.tabs([
            "  🤖 AI Coach Configuration  ",
            "  🏛️ Oracle PL/SQL Engine  ",
            "  🗄️ SQLite Database Inspector  ",
        ])

        with tab_cfg_ai:
            st.markdown("##### Local Ollama Settings")
            ai_model_name = st.text_input("Ollama Model Name", value=ai.DEFAULT_MODEL)
            online, avail, models = ai.check_ollama_status(ai_model_name)
            if online:
                st.success(f"🟢 Ollama is reachable • Installed models: {', '.join(models) or 'None'}")
            else:
                st.info("💡 Ollama offline. Built-in interactive quiz and study recommendation engines are active!")

        with tab_cfg_oracle:
            st.markdown("##### Oracle PL/SQL Configuration (STUDY_PLANNER_PKG)")
            cfg = pm.load_oracle_config()
            co1, co2 = st.columns(2)
            with co1:
                ohost = st.text_input("Host", value=cfg.get("host", "localhost"))
                oport = st.number_input("Port", value=int(cfg.get("port", 1521)))
                oservice = st.text_input("Service Name", value=cfg.get("service_name", "XE"))
            with co2:
                ouser = st.text_input("User", value=cfg.get("user", "system"))
                opass = st.text_input("Password", value=cfg.get("password", ""), type="password")
                oenabled = st.checkbox("Enable Oracle PL/SQL Engine", value=cfg.get("enabled", False))

            if st.button("💾 Save Oracle Settings"):
                pm.save_oracle_config({"enabled": oenabled, "user": ouser, "password": opass, "host": ohost, "port": int(oport), "service_name": oservice})
                st.toast("Saved Oracle configuration!")
                st.rerun()

            sql_path = Path(__file__).parent / "database_plsql.sql"
            if sql_path.exists():
                st.download_button("📥 Download database_plsql.sql", data=sql_path.read_text(encoding="utf-8"), file_name="database_plsql.sql", mime="text/x-sql")

        with tab_cfg_sqlite:
            st.markdown("##### Embedded SQLite Engine (study_database.db)")
            st.caption("Live relational records in SQLite tables:")
            st.dataframe(pd.DataFrame(db.get_all_subjects()), use_container_width=True)
            if st.button("🗑️ Reset & Re-Seed Default Curriculum"):
                db.seed_sample_plan_data()
                st.toast("Reset to sample plan!")
                st.rerun()


if __name__ == "__main__":
    main()
