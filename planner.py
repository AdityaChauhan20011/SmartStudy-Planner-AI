"""
SmartStudy Planner AI - Heuristic Timetable Planning Engine
Calculates dynamic priority weights and balances study sessions across available days.
"""

from datetime import date, datetime, timedelta


def days_until(exam_date):
    """Calculates days remaining from today until the examination date."""
    if isinstance(exam_date, str):
        try:
            exam_date = date.fromisoformat(exam_date)
        except ValueError:
            return 0
    elif isinstance(exam_date, datetime):
        exam_date = exam_date.date()
    return max(0, (exam_date - date.today()).days)


def make_plan(subjects, hours_per_day, start_day, number_of_days):
    """
    Weighted Round-Robin Heuristic Planner:
    Urgency = (Difficulty + 1) / min(max(Days Until Exam, 1), 30).
    Rotates daily eligible subjects to prevent burnout and bounds to pre-exam dates.
    """
    tasks = []
    available_days = [start_day + timedelta(days=i) for i in range(number_of_days)]
    if not subjects or not available_days:
        return tasks

    # Calculate urgency weight for each subject
    weights = []
    normalized_subjects = []
    for s in subjects:
        exam_d = s["exam_date"]
        if isinstance(exam_d, str):
            exam_d = date.fromisoformat(exam_d)
        elif isinstance(exam_d, datetime):
            exam_d = exam_d.date()

        days_left = max(1, (exam_d - start_day).days)
        difficulty = int(s.get("difficulty", 3))
        weight = (difficulty + 1) / min(days_left, 30)
        weights.append(weight)
        normalized_subjects.append({
            "name": s["name"],
            "exam_date": exam_d,
            "difficulty": difficulty,
        })

    sessions_per_day = max(1, int(hours_per_day))
    subject_index = 0

    for study_day in available_days:
        # Eligible candidates: subjects whose exams have not yet passed relative to study_day
        eligible = [
            (i, s, weights[i]) for i, s in enumerate(normalized_subjects)
            if s["exam_date"] >= study_day
        ]
        if not eligible:
            continue

        for session_num in range(sessions_per_day):
            if not eligible:
                break
            # Sort eligible candidates: closer exams first, then higher difficulty
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


def calculate_reschedule_mapping(missed_tasks, plan_days):
    """
    Finds future available dates for missed sessions and generates a mapping for SQLite update.
    """
    pending_days = [
        (date.today() + timedelta(days=i)).isoformat()
        for i in range(1, plan_days + 8)
    ]
    rescheduled_map = {}
    for task in missed_tasks:
        new_date = next((d for d in pending_days if d >= date.today().isoformat()), None)
        if new_date:
            rescheduled_map[task["id"]] = {
                "date": new_date,
                "title": f"{task['subject']} — rescheduled study session",
            }
            pending_days.remove(new_date)
    return rescheduled_map

