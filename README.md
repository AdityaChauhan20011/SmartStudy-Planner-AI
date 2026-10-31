# SmartStudy Planner AI 📚

An intelligent, interactive academic study planner and revision coach built with Python, Streamlit, Oracle PL/SQL, SQLite, and Ollama.

---

## 🚀 Key Architectural Features
- **Dual-Engine Relational Storage (`database.py` & `plsql_manager.py`)**:
  - **Enterprise Oracle PL/SQL Mode**: Complete procedural schema driven by stored procedures and packages (`STUDY_PLANNER_PKG`), sequences (`SEQ_SUBJECTS_ID`, `SEQ_POMODORO_ID`), and database triggers (`TRG_TASKS_AUDIT`, `TRG_SUBJECTS_BI`) for full data governance and audit trails.
  - **Embedded SQLite Mode**: Zero-configuration, offline local engine (`study_database.db`) ensuring immediate out-of-the-box execution with zero setup friction.
- **Heuristic Weighted Scheduler (`planner.py`)**: Dynamically balances daily study sessions using exam countdowns and subject difficulty weights to prevent burnout and avoid post-exam scheduling.
- **Interactive Focus Pomodoro Timer (`styles.py`)**: 25-minute sprints with circular SVG progress, sound alerts (Web Audio API), and direct session logging to the database.
- **On-Premise AI Study Coach & Quiz (`ai_assistant.py`)**: Built-in 5-question interactive quizzes with instant grading and offline fallbacks, plus optional deep reasoning powered by local Ollama (`llama3.2`).
- **Live Database & PL/SQL Management Hub**: In-app inspection of relational tables (`SUBJECTS`, `TASKS`, `POMODORO_LOGS`, `AUDIT_LOGS`), Oracle connection testing, and 1-click execution and download of the complete `database_plsql.sql` script.

---

## 🏛️ Oracle PL/SQL Database Architecture (`database_plsql.sql`)

The project includes an enterprise-grade Oracle PL/SQL implementation covering:

1. **Relational Tables & Integrity Constraints**:
   - `SUBJECTS`: Primary key (`ID`), unique course names, check constraints on difficulty (1–5).
   - `TASKS`: Primary key (`ID`), check constraint on status (`Pending`, `Completed`, `Missed`).
   - `POMODORO_LOGS`: Session focus logs with timestamps and duration.
   - `AUDIT_LOGS`: Automated trigger audit trail capturing task insertions and status transitions.
2. **Sequences**:
   - `SEQ_SUBJECTS_ID`, `SEQ_POMODORO_ID`, `SEQ_AUDIT_ID`.
3. **Database Triggers**:
   - `TRG_SUBJECTS_BI`: Before-insert trigger to assign sequence values.
   - `TRG_POMODORO_BI`: Before-insert trigger for sprint IDs.
   - `TRG_TASKS_AUDIT`: After insert/update trigger logging state transitions to `AUDIT_LOGS`.
4. **Stored Functions**:
   - `FN_DAYS_UNTIL_EXAM(p_exam_date)`: Calculates remaining preparation days.
   - `FN_COMPLETION_RATE`: Returns overall syllabus completion percentage.
5. **PL/SQL Package (`STUDY_PLANNER_PKG`)**:
   - `SP_ADD_SUBJECT`, `SP_DELETE_SUBJECT`, `SP_GET_ALL_SUBJECTS` (returns `SYS_REFCURSOR`)
   - `SP_INSERT_TASK`, `SP_UPDATE_TASK_STATUS`, `SP_RESCHEDULE_TASK`, `SP_GET_ALL_TASKS` (returns `SYS_REFCURSOR`)
   - `SP_LOG_POMODORO`, `SP_GET_POMODORO_LOGS` (returns `SYS_REFCURSOR`)
   - `SP_CLEAR_DATABASE`, `SP_SEED_DEFAULT_DATA`, `SP_GET_STATS`

---

## 📁 Clean Modular Project Structure
```text
SmartStudy_Planner_AI/
├── .streamlit/
│   └── config.toml          # Forced clean light theme & UI configuration
├── .vscode/
│   └── settings.json        # Python interpreter path (.venv)
├── app.py                   # Main application entry point & reactive UI coordinator
├── database.py              # Dual-engine relational database layer (Oracle PL/SQL & SQLite)
├── plsql_manager.py         # Oracle Database connector via oracledb Thin Mode
├── database_plsql.sql       # Complete Oracle PL/SQL script (DDL, Triggers, Package, Spec & Body)
├── planner.py               # Heuristic scheduling algorithm & urgency calculations
├── ai_assistant.py          # Local Ollama LLM integration & curated interactive quiz banks
├── styles.py                # Modern light CSS styling & HTML components (navbar, cards, timer)
├── study_database.db        # Embedded local SQLite database engine
├── oracle_config.json       # Optional Oracle connection configuration
├── requirements.txt         # Project dependencies (streamlit, oracledb, requests, pandas, altair)
├── README.md                # Comprehensive project documentation
└── .gitignore               # Clean gitignore excluding .venv, __pycache__, etc.
```

---

## 🛠️ Setup & Execution

### 1. Requirements
- Windows 10/11, macOS, or Linux
- Python 3.10+
- Optional: Oracle Database (11g, 12c, 19c, 21c, or 23ai Express / Enterprise) or local Oracle XE
- Optional: Ollama installed (https://ollama.com) for local AI generation

### 2. Install Dependencies
```powershell
.\.venv\Scripts\pip install -r requirements.txt
```

### 3. Run Application
```powershell
.\.venv\Scripts\streamlit run app.py
```
Open **`http://localhost:8501`** in your browser.

### 4. Running Oracle PL/SQL (Optional)
1. In the app, navigate to the **📊 Progress & Database** tab.
2. Under **🏛️ Oracle PL/SQL Connection**, enter your Oracle credentials (e.g. `localhost:1521/XE`, user: `system`).
3. Click **"⚡ Compile PL/SQL Script"** to execute `database_plsql.sql` and compile `STUDY_PLANNER_PKG`.
4. Alternatively, open [`database_plsql.sql`](file:///c:/MCA/ai%20tools/project/SmartStudy_Planner_AI/database_plsql.sql) in **Oracle SQL Developer** or **SQL*Plus** and run:
   ```sql
   @database_plsql.sql;
   ```
