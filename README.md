# SmartStudy Planner AI 📚

An intelligent, local study planner and revision coach built with Python, Streamlit, SQLite, and Ollama.

## 🚀 Key Architectural Features
- **Heuristic Weighted Scheduler (`planner.py`)**: Dynamically balances daily study sessions using exam countdowns and subject difficulty weights to prevent burnout and post-exam scheduling.
- **Relational Storage (`database.py`)**: Pure, robust SQLite database engine (`study_database.db`) with tables for `subjects`, `tasks`, and `pomodoro_logs`. Fully ACID compliant with zero legacy JSON dependencies.
- **Interactive Focus Pomodoro Timer (`styles.py`)**: 25-minute sprints with circular SVG progress, sound alerts (Web Audio API), and direct session logging to the database.
- **On-Premise AI Study Coach (`ai_assistant.py`)**: Offline revision strategies, active recall tips, and practice quiz generation powered by local Ollama (`llama3.2`).
- **Live Database Inspector**: In-app inspection of SQLite relational tables (`subjects`, `tasks`, `pomodoro_logs`).

---

## 📁 Clean Modular Project Structure
```text
SmartStudy_Planner_AI/
├── .streamlit/
│   └── config.toml          # Forced clean light theme & UI configuration
├── .vscode/
│   └── settings.json        # Python interpreter path (.venv)
├── app.py                   # Main application entry point & reactive UI coordinator
├── database.py              # Pure SQLite database layer (DDL, DML, atomic transactions)
├── planner.py               # Heuristic scheduling algorithm & urgency calculations
├── ai_assistant.py          # Local Ollama LLM integration, health ping, prompt orchestrator
├── styles.py                # Modern light CSS styling & HTML components (navbar, cards, timer)
├── study_database.db        # Fresh, clean SQLite database (started from beginning)
├── requirements.txt         # Project dependencies (streamlit, requests, pandas, altair)
├── README.md                # Comprehensive project documentation
└── .gitignore               # Clean gitignore excluding .venv, __pycache__, etc.
```

---

## 🛠️ Setup & Execution

### 1. Requirements
- Windows 10/11, macOS, or Linux
- Python 3.10+
- Ollama installed (https://ollama.com)

### 2. Pull Local Model (One-Time)
```bash
ollama run llama3.2
```

### 3. Install Dependencies
```powershell
.\.venv\Scripts\pip install -r requirements.txt
```

### 4. Run Application
```powershell
.\.venv\Scripts\streamlit run app.py
```
Open **`http://localhost:8501`** in your browser.

