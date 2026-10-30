# SmartStudy Planner AI

A beginner-friendly local study planner built with Python, Streamlit, and Ollama.

## Requirements
- Windows 10/11
- Python installed
- Ollama installed
- Internet connection for the initial Ollama model download

## Setup
1. Install Ollama from https://ollama.com/download
2. Open Command Prompt and download/run a model:
   ```
   ollama run llama3.2
   ```
   Wait for the model to download. You can exit the chat afterward.
3. Open Command Prompt in this project folder.
4. Install Python packages (already configured in `.venv`):
   ```
   .\.venv\Scripts\pip install -r requirements.txt
   ```
5. Start the app:
   ```
   .\.venv\Scripts\streamlit run app.py
   ```
   (Or if running from an active venv: `streamlit run app.py`)
6. A browser tab should open with SmartStudy Planner AI.

## Use
1. Open **My Subjects**, enter subjects, exam dates, and difficulty, then save.
2. Open **Study Plan**, generate your plan, and mark sessions completed or missed.
3. Use **Reschedule missed sessions** to move missed sessions.
4. Open **AI Study Assistant** to ask Ollama for revision advice.

## Troubleshooting
- If `ollama` is not recognized, open/restart Command Prompt after installing Ollama.
- If the AI assistant cannot connect, open the Ollama app and run `ollama run llama3.2`.
- If you use another model, type its exact installed name in the sidebar.
- If the model is slow, try a smaller model such as `llama3.2:1b`.

The app stores data in `study_data.json` in the same folder.
