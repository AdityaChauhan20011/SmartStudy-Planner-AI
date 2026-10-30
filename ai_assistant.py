"""
SmartStudy Planner AI - Local AI Coach Module
Manages communication with local Ollama daemon (Llama 3.2), prompt context formatting,
and instant offline interactive quiz & study guides.
"""

import requests

OLLAMA_BASE = "http://localhost:11434"
OLLAMA_URL = f"{OLLAMA_BASE}/api/generate"
DEFAULT_MODEL = "llama3.2"


# Curated question bank for instant interactive quizzes
CURATED_QUIZZES = {
    "Python Programming": [
        {
            "question": "What is the time complexity of searching for an element in a Python dictionary (average case)?",
            "options": ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
            "answer": "O(1)",
            "explanation": "Python dictionaries are implemented using hash tables, giving average-case O(1) lookup time.",
        },
        {
            "question": "Which Python built-in is used to iterate over a sequence while keeping track of the current index?",
            "options": ["map()", "zip()", "enumerate()", "filter()"],
            "answer": "enumerate()",
            "explanation": "enumerate() returns pairs of (index, item) as you iterate through an iterable.",
        },
        {
            "question": "What happens when you use mutable default arguments (e.g., def fn(lst=[])) in Python?",
            "options": [
                "A TypeError is raised at definition time",
                "The default list is shared across all function calls",
                "A fresh list is created on each call",
                "The list becomes immutable automatically",
            ],
            "answer": "The default list is shared across all function calls",
            "explanation": "Default arguments are evaluated once when the function is defined, so a mutable default persists across invocations.",
        },
        {
            "question": "Which keyword is used in Python to create a generator function?",
            "options": ["return", "generate", "yield", "emit"],
            "answer": "yield",
            "explanation": "Using 'yield' produces a generator object that lazily emits values one at a time.",
        },
        {
            "question": "Which module in Python is used for deep and shallow copying of objects?",
            "options": ["clone", "copy", "duplication", "os"],
            "answer": "copy",
            "explanation": "The 'copy' module provides copy.copy() for shallow copies and copy.deepcopy() for deep copies.",
        },
    ],
    "Database Management Systems (DBMS)": [
        {
            "question": "Which Normal Form removes transitive dependencies on candidate keys?",
            "options": ["1NF", "2NF", "3NF", "BCNF"],
            "answer": "3NF",
            "explanation": "3NF requires the relation to be in 2NF and that no non-prime attribute is transitively dependent on the primary key.",
        },
        {
            "question": "What does the 'I' stand for in the ACID properties of database transactions?",
            "options": ["Indexing", "Integrity", "Isolation", "Iterability"],
            "answer": "Isolation",
            "explanation": "Isolation ensures concurrent transactions execute without interfering with one another.",
        },
        {
            "question": "Which SQL clause is used to filter groups created by the GROUP BY statement?",
            "options": ["WHERE", "ORDER BY", "HAVING", "LIMIT"],
            "answer": "HAVING",
            "explanation": "WHERE filters individual rows before grouping, whereas HAVING filters aggregated groups.",
        },
        {
            "question": "What index structure is most widely used by relational database engines (like SQLite, PostgreSQL)?",
            "options": ["Binary Search Tree", "B+ Tree", "Linked List", "Radix Tree"],
            "answer": "B+ Tree",
            "explanation": "B+ Trees maintain balanced height and keep all data pointers in leaf nodes connected by links for efficient range scans.",
        },
        {
            "question": "Which command permanently saves all changes made during the current transaction in SQL?",
            "options": ["ROLLBACK", "SAVEPOINT", "COMMIT", "TRUNCATE"],
            "answer": "COMMIT",
            "explanation": "COMMIT makes all modifications made in the transaction permanent in the database.",
        },
    ],
    "Advanced Computer Networks": [
        {
            "question": "Which layer of the OSI model is responsible for routing packets across interconnected networks?",
            "options": ["Data Link Layer (Layer 2)", "Network Layer (Layer 3)", "Transport Layer (Layer 4)", "Session Layer (Layer 5)"],
            "answer": "Network Layer (Layer 3)",
            "explanation": "The Network Layer manages logical IP addressing and path determination (routing).",
        },
        {
            "question": "What is the primary function of the Address Resolution Protocol (ARP)?",
            "options": [
                "Translate domain names to IP addresses",
                "Translate IP addresses to physical MAC addresses",
                "Encrypt transport layer payloads",
                "Assign dynamic IP addresses",
            ],
            "answer": "Translate IP addresses to physical MAC addresses",
            "explanation": "ARP maps a 32-bit IPv4 address to a 48-bit physical MAC address on a local link.",
        },
        {
            "question": "How many packets are exchanged in a standard TCP connection handshake?",
            "options": ["2 (SYN, ACK)", "3 (SYN, SYN-ACK, ACK)", "4 (SYN, ACK, FIN, ACK)", "1 (CONNECT)"],
            "answer": "3 (SYN, SYN-ACK, ACK)",
            "explanation": "TCP establishes reliable connection state via a 3-way handshake: SYN -> SYN-ACK -> ACK.",
        },
        {
            "question": "Which protocol operates over UDP port 53?",
            "options": ["HTTP", "SSH", "DNS", "FTP"],
            "answer": "DNS",
            "explanation": "Domain Name System (DNS) queries use UDP port 53 for lightweight, low-latency lookups.",
        },
        {
            "question": "What subnet mask corresponds to CIDR prefix /24?",
            "options": ["255.0.0.0", "255.255.0.0", "255.255.255.0", "255.255.255.255"],
            "answer": "255.255.255.0",
            "explanation": "/24 represents 24 consecutive binary 1s (8 + 8 + 8 = 24), which is 255.255.255.0.",
        },
    ],
    "Cloud Computing Architecture": [
        {
            "question": "In which cloud delivery model does the cloud provider manage everything up to the runtime and application layer?",
            "options": ["IaaS (Infrastructure as a Service)", "PaaS (Platform as a Service)", "SaaS (Software as a Service)", "BaaS"],
            "answer": "SaaS (Software as a Service)",
            "explanation": "In SaaS, the provider manages the entire stack (infrastructure, OS, middleware, and application software).",
        },
        {
            "question": "What cloud design pattern helps maintain system availability when a dependency fails?",
            "options": ["Circuit Breaker", "Singleton", "Factory Method", "Monolithic Cache"],
            "answer": "Circuit Breaker",
            "explanation": "The Circuit Breaker pattern prevents an application from repeatedly trying to execute an operation that's likely to fail.",
        },
        {
            "question": "Which of the following is an example of an open-source container orchestration engine?",
            "options": ["Docker Engine", "Kubernetes (K8s)", "Ansible", "Terraform"],
            "answer": "Kubernetes (K8s)",
            "explanation": "Kubernetes is the standard container orchestration platform for automated deployment, scaling, and management.",
        },
        {
            "question": "What type of cloud storage is best suited for unstructured data like images, videos, and backups?",
            "options": ["Block Storage", "Relational Database", "Object Storage (e.g. S3 / GCS)", "In-memory cache"],
            "answer": "Object Storage (e.g. S3 / GCS)",
            "explanation": "Object storage stores data as discrete objects with metadata and unique identifiers, ideal for scalable media and backups.",
        },
        {
            "question": "What does RTO stand for in cloud disaster recovery planning?",
            "options": [
                "Recovery Time Objective",
                "Real Time Operations",
                "Redundant Traffic Optimization",
                "Resource Transfer Overhead",
            ],
            "answer": "Recovery Time Objective",
            "explanation": "RTO is the maximum acceptable duration of downtime that an application can sustain before normal service is restored.",
        },
    ],
}


def get_interactive_quiz(subject_name):
    """Returns curated MCQs for the given subject or fallback general CS questions."""
    for key in CURATED_QUIZZES:
        if key.lower() in subject_name.lower() or subject_name.lower() in key.lower():
            return CURATED_QUIZZES[key]
    return CURATED_QUIZZES["Python Programming"]


def check_ollama_status(model_name=DEFAULT_MODEL):
    """Checks whether the local Ollama daemon and the requested model are reachable."""
    try:
        res = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=2)
        if res.status_code == 200:
            models_info = res.json().get("models", [])
            names = [m.get("name", "") for m in models_info]
            has_model = any(model_name in n for n in names)
            return True, has_model, names
        return False, False, []
    except Exception:
        return False, False, []


def ask_ollama(prompt, model=DEFAULT_MODEL):
    """Sends a study advice prompt to local Ollama and handles exceptions gracefully."""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=90,
        )
        response.raise_for_status()
        return response.json().get("response", "The local model returned an empty response.")
    except Exception:
        return None


def get_smart_fallback_response(query, target_course, hours_per_day, plan_days):
    """Provides high-yield, structured academic study advice when Ollama daemon is offline."""
    q = query.lower()
    
    if "cram" in q or "3-day" in q or "urgent" in q:
        return f"""
### ⚡ High-Intensity 3-Day Revision Plan for {target_course}

This focused framework maximizes retention in short horizons using prioritized Pomodoro sprints:

#### 📅 Day 1: High-Weightage Core Theory & Formulas
- **Morning (2 hrs):** Review fundamental principles, definitions, and architectural diagrams.
- **Afternoon (2 hrs):** Solve past 3 years' exam questions on key modules.
- **Evening (1 hr):** Active recall: explain concepts aloud without looking at your notes.

#### 📅 Day 2: Problem Solving & Numerical Applications
- **Morning (2 hrs):** Practice standard algorithm traces, query building, or analytical calculations.
- **Afternoon (2 hrs):** Time yourself solving 5 complex scenario questions.
- **Evening (1 hr):** Make a 1-page condensed formula/cheat sheet.

#### 📅 Day 3: Mock Testing & Final Polishing
- **Morning (2 hrs):** Take a timed self-assessment mock test under exam conditions.
- **Afternoon (1 hr):** Review mistakes and reinforce weak areas.
- **Night:** Light review of your 1-page summary. Sleep for at least 7 hours for memory consolidation.
"""

    if "feynman" in q or "recall" in q or "memory" in q:
        return f"""
### 🧠 Active Recall & Feynman Technique Guide for {target_course}

Rote memorization causes rapid forgetting. Use this 4-step Feynman cycle:

1. **Step 1: Choose a Core Concept**
   - Pick a single topic (e.g. *Database Normalization*, *TCP Congestion Control*, or *Python Decorators*).
2. **Step 2: Teach It to a Beginner**
   - Write or speak an explanation using plain, everyday language without technical jargon.
3. **Step 3: Identify Your Knowledge Gaps**
   - Whenever you get stuck or use vague terms, check your textbook and note down precisely what was missing.
4. **Step 4: Simplify & Create an Analogy**
   - Refine the explanation and link it to an intuitive physical metaphor.

> **Active Recall Rule:** Always test yourself *before* re-reading notes. Testing builds neural retrieval pathways.
"""

    return f"""
### 🎯 Academic Study Strategy for {target_course}

Based on your schedule ({hours_per_day} hrs/day over {plan_days} days):

1. **Phase 1: High-Yield Topic Prioritization (First 40% of time)**
   - Identify topics accounting for 60%+ of past exam marks.
   - Build conceptual clarity before moving to advanced corner cases.

2. **Phase 2: Active Problem Solving & Exercises (Next 40% of time)**
   - Switch from passive reading to active coding, query writing, and architectural design.
   - Group sessions into 25-minute Pomodoro sprints followed by 5-minute rest breaks.

3. **Phase 3: Cumulative Revision & Exam Simulation (Final 20% of time)**
   - Revisit all missed sessions.
   - Solve previous semester question papers against the clock.

*Tip: For dynamic AI responses, start your local Ollama server in terminal with `ollama run llama3.2`.*
"""


def build_study_prompt(subjects, hours_per_day, plan_days, target_course, query):
    """Formats student context, deadlines, and study capacity into an actionable LLM prompt."""
    if subjects:
        subject_summary = "\n".join(
            f"- {s['name']}: Exam on {s['exam_date']}, Difficulty: {s['difficulty']}/5"
            for s in subjects
        )
    else:
        subject_summary = "No subjects configured yet."

    return (
        "You are SmartStudy Planner AI, a supportive, practical, and highly knowledgeable academic coach. "
        "Provide realistic, highly actionable, concise study advice with clear bullet points. "
        "Do not pretend to modify the user's database directly.\n\n"
        f"Student Enrolled Subjects:\n{subject_summary}\n\n"
        f"Target Course Focus: {target_course}\n"
        f"Daily Study Capacity: {hours_per_day} hours/day\n"
        f"Planning Horizon: {plan_days} days\n"
        f"Student Query: {query}\n\n"
        "Give a direct, actionable answer with prioritized steps."
    )
