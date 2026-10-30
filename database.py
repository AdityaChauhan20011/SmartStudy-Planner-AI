"""
SmartStudy Planner AI - SQLite Database Engine
Handles schema creation, relational CRUD operations, and atomic transactions.
"""

import sqlite3
from datetime import datetime, date, timedelta
from pathlib import Path

APP_DIR = Path(__file__).parent
DB_FILE = APP_DIR / "study_database.db"


def get_connection():
    """Returns a SQLite connection with dict-like row access."""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes the SQLite schema with tables for subjects, tasks, and pomodoro logs."""
    with get_connection() as conn:
        cursor = conn.cursor()

        # 1. Subjects Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                exam_date TEXT NOT NULL,
                difficulty INTEGER NOT NULL CHECK(difficulty BETWEEN 1 AND 5),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. Scheduled Tasks Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                date TEXT NOT NULL,
                subject TEXT NOT NULL,
                title TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('Pending', 'Completed', 'Missed')),
                duration INTEGER NOT NULL DEFAULT 60,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 3. Pomodoro Sprints Log Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pomodoro_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_date TEXT NOT NULL,
                subject TEXT NOT NULL,
                duration_mins INTEGER NOT NULL DEFAULT 25,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()


def get_all_subjects():
    """Retrieves all subjects ordered by target exam date ascending."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, exam_date, difficulty FROM subjects ORDER BY exam_date ASC")
        return [dict(row) for row in cursor.fetchall()]


def set_all_subjects(subjects_list):
    """Replaces or updates the subjects list inside an atomic transaction."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM subjects")
        for s in subjects_list:
            cursor.execute("""
                INSERT INTO subjects (name, exam_date, difficulty)
                VALUES (?, ?, ?)
            """, (s["name"].strip(), s["exam_date"], int(s["difficulty"])))
        conn.commit()


def get_all_tasks():
    """Retrieves all scheduled tasks ordered by date ascending."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, date, subject, title, status, duration FROM tasks ORDER BY date ASC, id ASC")
        return [dict(row) for row in cursor.fetchall()]


def set_all_tasks(tasks_list):
    """Replaces the scheduled tasks list inside an atomic transaction."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks")
        for t in tasks_list:
            cursor.execute("""
                INSERT INTO tasks (id, date, subject, title, status, duration)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (t["id"], t["date"], t["subject"], t["title"], t.get("status", "Pending"), int(t.get("duration", 60))))
        conn.commit()


def update_task_status(task_id, new_status):
    """Atomically updates a single task's status in SQLite."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id))
        conn.commit()


def reschedule_tasks(rescheduled_map):
    """Updates dates, titles, and statuses for rescheduled tasks in bulk."""
    with get_connection() as conn:
        cursor = conn.cursor()
        for task_id, info in rescheduled_map.items():
            cursor.execute("""
                UPDATE tasks 
                SET date = ?, status = 'Pending', title = ?
                WHERE id = ?
            """, (info["date"], info["title"], task_id))
        conn.commit()


def log_pomodoro(subject, duration_mins=25):
    """Logs a completed Pomodoro sprint in SQLite."""
    with get_connection() as conn:
        cursor = conn.cursor()
        today_str = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("""
            INSERT INTO pomodoro_logs (session_date, subject, duration_mins)
            VALUES (?, ?, ?)
        """, (today_str, subject, duration_mins))
        conn.commit()


def get_pomodoro_logs():
    """Retrieves all logged Pomodoro focus sessions."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, session_date, subject, duration_mins, completed_at FROM pomodoro_logs ORDER BY id DESC")
        return [dict(row) for row in cursor.fetchall()]


def clear_database():
    """Completely truncates all SQLite tables."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks")
        cursor.execute("DELETE FROM subjects")
        cursor.execute("DELETE FROM pomodoro_logs")
        conn.commit()


def add_single_subject(name, exam_date, difficulty=3):
    """Inserts a single subject into SQLite."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO subjects (name, exam_date, difficulty)
            VALUES (?, ?, ?)
        """, (name.strip(), exam_date, int(difficulty)))
        conn.commit()


def delete_single_subject(subject_id):
    """Deletes a single subject and associated tasks by ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM subjects WHERE id = ?", (subject_id,))
        row = cursor.fetchone()
        if row:
            sub_name = row["name"]
            cursor.execute("DELETE FROM tasks WHERE subject = ?", (sub_name,))
        cursor.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
        conn.commit()


def delete_single_task(task_id):
    """Deletes a single task by ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()


def seed_default_curriculum():
    """Populates sample MCA curriculum subjects into SQLite."""
    today = date.today()
    sample_subs = [
        {"name": "Python Programming", "exam_date": (today + timedelta(days=14)).isoformat(), "difficulty": 4},
        {"name": "Database Management Systems (DBMS)", "exam_date": (today + timedelta(days=10)).isoformat(), "difficulty": 3},
        {"name": "Advanced Computer Networks", "exam_date": (today + timedelta(days=5)).isoformat(), "difficulty": 3},
        {"name": "Cloud Computing Architecture", "exam_date": (today + timedelta(days=20)).isoformat(), "difficulty": 4},
    ]
    set_all_subjects(sample_subs)


def seed_sample_plan_data():
    """Populates sample subjects and automatically generates a complete 7-day study schedule."""
    seed_default_curriculum()
    import planner
    subs = get_all_subjects()
    new_plan = planner.make_plan(subs, 3, date.today(), 7)
    if new_plan:
        set_all_tasks(new_plan)
        # Mark one task as Completed for instant interactive progress demonstration
        today_str = date.today().isoformat()
        today_tasks = [t for t in new_plan if t.get("date") == today_str]
        if today_tasks:
            update_task_status(today_tasks[0]["id"], "Completed")
            log_pomodoro(today_tasks[0]["subject"], 25)



def get_database_stats():
    """Returns metadata and statistics about the SQLite database."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM subjects")
        num_subjects = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM tasks")
        num_tasks = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM pomodoro_logs")
        num_sprints = cursor.fetchone()[0]
        size_bytes = DB_FILE.stat().st_size if DB_FILE.exists() else 0
        return {
            "file": DB_FILE.name,
            "path": str(DB_FILE),
            "size_kb": round(size_bytes / 1024, 2),
            "subjects_count": num_subjects,
            "tasks_count": num_tasks,
            "pomodoro_count": num_sprints,
        }
