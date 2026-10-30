import json
from datetime import date, datetime, timedelta
from pathlib import Path

import requests
import streamlit as st

APP_DIR = Path(__file__).parent
DATA_FILE = APP_DIR / "study_data.json"
OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3.2"

st.set_page_config(page_title="SmartStudy Planner AI", page_icon="📚", layout="wide")

def load_data():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"subjects": [], "tasks": []}

def save_data(data):
    DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

def days_until(exam_date):
    return max(0, (exam_date - date.today()).days)

def make_plan(subjects, hours_per_day, start_day, number_of_days):
    """Create a simple weighted plan; nearer exams and harder subjects get more sessions."""
    tasks = []
    available_days = [start_day + timedelta(days=i) for i in range(number_of_days)]
    if not subjects or not available_days:
        return tasks

    weights = []
    for subject in subjects:
        days_left = max(1, (subject["exam_date"] - start_day).days)
        difficulty = int(subject["difficulty"])
        weight = (difficulty + 1) / min(days_left, 30)
        weights.append(weight)

    total_weight = sum(weights) or 1
    sessions_per_day = max(1, int(hours_per_day))
    subject_index = 0

    for study_day in available_days:
        # Spread sessions over subjects using weighted selection, without scheduling after exam date.
        day_sessions = []
        eligible = [
            (i, s, weights[i]) for i, s in enumerate(subjects)
            if s["exam_date"] >= study_day
        ]
        if not eligible:
            continue

        for session_num in range(sessions_per_day):
            if not eligible:
                break
            # Weighted round-robin approximation, rotated daily.
            eligible.sort(key=lambda item: (
                (item[1]["exam_date"] - study_day).days,
                -int(item[1]["difficulty"])
            ))
            pick_index = (subject_index + session_num) % len(eligible)
            _, subject, _ = eligible[pick_index]
            tasks.append({
                "id": f"{study_day.isoformat()}-{len(tasks)}",
                "date": study_day.isoformat(),
                "subject": subject["name"],
                "title": f"{subject['name']} — focused study session",
                "status": "Pending",
                "duration": 60,
            })
        subject_index += 1
    return tasks

def ask_ollama(prompt, model):
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=120,
        )
        response.raise_for_status()
        return response.json().get("response", "The model returned an empty response.")
    except requests.exceptions.ConnectionError:
        return ("I couldn't connect to Ollama. Open the Ollama app and run "
                f"`ollama run {model}` in Command Prompt, then try again.")
    except requests.exceptions.Timeout:
        return "The model took too long to respond. Try a smaller model or a shorter question."
    except requests.exceptions.RequestException as exc:
        return f"Ollama request failed: {exc}"

if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data
st.title("📚 SmartStudy Planner AI")
st.caption("Your local study planner — create a timetable, track progress, and ask Ollama for study advice.")

with st.sidebar:
    st.header("⚙️ Planner settings")
    model_name = st.text_input("Ollama model name", value=DEFAULT_MODEL, help="Use a model installed in Ollama, e.g. llama3.2 or gemma3:4b.")
    hours_per_day = st.slider("Study hours per day", min_value=1, max_value=10, value=3)
    plan_days = st.slider("Plan length (days)", min_value=3, max_value=30, value=7)
    st.markdown("**Local AI status**")
    st.caption("Ollama normally listens at `http://localhost:11434`.")

tab_setup, tab_plan, tab_ai = st.tabs(["1. My Subjects", "2. Study Plan", "3. AI Study Assistant"])

with tab_setup:
    st.subheader("Add your subjects and exam dates")
    st.write("Enter at least one subject. Difficulty: 1 = easy, 5 = very difficult.")
    with st.form("subject_form", clear_on_submit=False):
        existing = data.get("subjects", [])
        default_rows = [
            {
                "Subject": s["name"],
                "Exam date": date.fromisoformat(s["exam_date"]),
                "Difficulty (1-5)": int(s["difficulty"]),
            } for s in existing
        ]
        if not default_rows:
            default_rows = [
                {"Subject": "Python", "Exam date": date.today() + timedelta(days=14), "Difficulty (1-5)": 4},
                {"Subject": "DBMS", "Exam date": date.today() + timedelta(days=10), "Difficulty (1-5)": 3},
            ]
        edited = st.data_editor(
            default_rows,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Subject": st.column_config.TextColumn("Subject", required=True),
                "Exam date": st.column_config.DateColumn("Exam date", required=True),
                "Difficulty (1-5)": st.column_config.NumberColumn(
                    "Difficulty (1-5)", min_value=1, max_value=5, step=1, required=True
                ),
            },
            key="subject_editor",
        )
        submitted = st.form_submit_button("💾 Save subjects")
    if submitted:
        cleaned = []
        for row in edited:
            name = str(row.get("Subject") or "").strip()
            exam = row.get("Exam date")
            difficulty = row.get("Difficulty (1-5)", 3)
            if isinstance(exam, str):
                try:
                    exam = date.fromisoformat(exam)
                except ValueError:
                    exam = None
            elif isinstance(exam, datetime):
                exam = exam.date()

            if name and isinstance(exam, date):
                cleaned.append({
                    "name": name,
                    "exam_date": exam.isoformat(),
                    "difficulty": int(difficulty or 3),
                })
        data["subjects"] = cleaned
        save_data(data)
        st.session_state.data = data
        st.success(f"Saved {len(cleaned)} subject(s).")

    if st.button("🗑️ Clear all saved data"):
        st.session_state.data = {"subjects": [], "tasks": []}
        save_data(st.session_state.data)
        st.rerun()

with tab_plan:
    st.subheader("Your timetable")
    if not data.get("subjects"):
        st.info("First add and save your subjects in the My Subjects tab.")
    else:
        if st.button("✨ Generate / replace study plan", type="primary"):
            subjects = [
                {**s, "exam_date": date.fromisoformat(s["exam_date"])}
                for s in data["subjects"]
            ]
            new_plan = make_plan(subjects, hours_per_day, date.today(), plan_days)
            if not new_plan:
                st.warning("No study sessions could be scheduled. Make sure your subject exam dates are today or in the future.")
            else:
                data["tasks"] = new_plan
                save_data(data)
                st.session_state.data = data
                st.success("Your study plan has been generated.")
                st.rerun()

        tasks = data.get("tasks", [])
        if tasks:
            total = len(tasks)
            completed = sum(t["status"] == "Completed" for t in tasks)
            missed = sum(t["status"] == "Missed" for t in tasks)
            c1, c2, c3 = st.columns(3)
            c1.metric("Total sessions", total)
            c2.metric("Completed", completed)
            c3.metric("Pending / missed", total - completed)
            st.progress(completed / total if total else 0)

            today_str = date.today().isoformat()
            today_tasks = [t for t in tasks if t["date"] == today_str]
            st.markdown("#### Today's sessions")
            if today_tasks:
                for task in today_tasks:
                    st.write(f"• **{task['subject']}** — {task['title']} ({task['duration']} min) · {task['status']}")
            else:
                st.caption("No sessions scheduled for today. See the full plan below.")

            st.markdown("#### Update session status")
            status_options = ["Pending", "Completed", "Missed"]
            for task in tasks:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    col1.write(f"**{task['date']} · {task['subject']}**")
                    col1.caption(task["title"])
                    current_status = task.get("status", "Pending")
                    status_idx = status_options.index(current_status) if current_status in status_options else 0
                    status = col2.selectbox(
                        "Status", status_options,
                        index=status_idx,
                        key=f"status_{task['id']}",
                        label_visibility="collapsed",
                    )
                    if col3.button("Save", key=f"save_{task['id']}"):
                        task["status"] = status
                        save_data(data)
                        st.session_state.data = data
                        st.rerun()

            if st.button("🔄 Reschedule missed sessions"):
                missed_tasks = [t for t in tasks if t.get("status") == "Missed"]
                if not missed_tasks:
                    st.info("No missed sessions found to reschedule.")
                else:
                    pending_days = [
                        (date.today() + timedelta(days=i)).isoformat()
                        for i in range(1, plan_days + 8)
                    ]
                    rescheduled_count = 0
                    for task in missed_tasks:
                        new_date = next((d for d in pending_days if d >= date.today().isoformat()), None)
                        if new_date:
                            task["date"] = new_date
                            task["status"] = "Pending"
                            task["title"] = f"{task['subject']} — rescheduled study session"
                            pending_days.remove(new_date)
                            rescheduled_count += 1
                    save_data(data)
                    st.session_state.data = data
                    st.success(f"Rescheduled {rescheduled_count} missed session(s).")
                    st.rerun()
        else:
            st.info("Click **Generate / replace study plan** to create your timetable.")

with tab_ai:
    st.subheader("Ask your local AI study assistant")
    st.write("Examples: “How should I revise DBMS in 5 days?” or “Give me a simple study strategy for Python.”")
    question = st.text_area("Your question", placeholder="Type your study question here...")
    if st.button("🤖 Ask Ollama", type="primary"):
        if not question.strip():
            st.warning("Please type a question first.")
        else:
            subject_summary = "\n".join(
                f"- {s['name']}: exam on {s['exam_date']}, difficulty {s['difficulty']}/5"
                for s in data.get("subjects", [])
            ) or "No subjects have been saved yet."
            prompt = (
                "You are SmartStudy Planner AI, a supportive and practical study coach. "
                "Give clear, realistic, concise advice. Do not claim to change the timetable yourself.\n\n"
                f"Student's subjects:\n{subject_summary}\n"
                f"Available study hours per day: {hours_per_day}\n"
                f"Student question: {question}\n\n"
                "Answer with actionable steps and a short schedule when useful."
            )
            with st.spinner("Ollama is thinking..."):
                answer = ask_ollama(prompt, model_name.strip() or DEFAULT_MODEL)
            st.markdown("#### AI response")
            st.write(answer)

st.divider()
st.caption("Data is saved locally in study_data.json in this project folder. This is a beginner-friendly demo, not a replacement for your own exam timetable.")
