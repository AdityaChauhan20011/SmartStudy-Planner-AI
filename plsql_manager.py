"""
SmartStudy Planner AI - Oracle PL/SQL Database Manager
Connects to Oracle Database using modern 'oracledb' Thin Mode and executes
stored procedures and functions within the STUDY_PLANNER_PKG package.
"""

import json
from datetime import datetime, date
from pathlib import Path

try:
    import oracledb
except ImportError:
    oracledb = None

CONFIG_FILE = Path(__file__).parent / "oracle_config.json"

DEFAULT_CONFIG = {
    "enabled": False,
    "user": "system",
    "password": "",
    "host": "localhost",
    "port": 1521,
    "service_name": "XE",  # common defaults: XE, XEPDB1, ORCL
}


def load_oracle_config():
    """Loads Oracle configuration from local file or returns defaults."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {**DEFAULT_CONFIG, **data}
        except Exception:
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()


def save_oracle_config(config_dict):
    """Saves Oracle connection configuration."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config_dict, f, indent=4)


def get_dsn(config=None):
    """Generates the Oracle Easy Connect string."""
    cfg = config or load_oracle_config()
    host = cfg.get("host", "localhost")
    port = cfg.get("port", 1521)
    service = cfg.get("service_name", "XE")
    return f"{host}:{port}/{service}"


def get_oracle_connection(config=None):
    """Establishes an Oracle connection in pure Thin mode (zero Oracle client required)."""
    if oracledb is None:
        raise ImportError("The 'oracledb' library is not installed.")

    cfg = config or load_oracle_config()
    dsn = get_dsn(cfg)
    return oracledb.connect(
        user=cfg.get("user", "system"),
        password=cfg.get("password", ""),
        dsn=dsn,
    )


def test_oracle_connection(user, password, host="localhost", port=1521, service_name="XE"):
    """Validates connectivity to an Oracle Database server."""
    if oracledb is None:
        return False, "oracledb driver is missing. Install with 'pip install oracledb'."

    dsn = f"{host}:{port}/{service_name}"
    try:
        conn = oracledb.connect(user=user, password=password, dsn=dsn)
        with conn.cursor() as cur:
            cur.execute("SELECT banner FROM v$version WHERE ROWNUM = 1")
            row = cur.fetchone()
            banner = row[0] if row else "Oracle Database"
        conn.close()
        return True, f"Connected successfully! Server: {banner}"
    except Exception as exc:
        return False, str(exc)


def is_oracle_active():
    """Returns True if Oracle PL/SQL is configured and reachable."""
    cfg = load_oracle_config()
    if not cfg.get("enabled", False) or not cfg.get("password"):
        return False
    ok, _ = test_oracle_connection(
        user=cfg["user"],
        password=cfg["password"],
        host=cfg["host"],
        port=cfg["port"],
        service_name=cfg["service_name"],
    )
    return ok


# -----------------------------------------------------------------------------
# PL/SQL STORED PROCEDURES WRAPPERS (STUDY_PLANNER_PKG)
# -----------------------------------------------------------------------------

def plsql_init_schema():
    """Executes the DDL & Package creation script against the active Oracle database."""
    sql_file = Path(__file__).parent / "database_plsql.sql"
    if not sql_file.exists():
        return False, "database_plsql.sql not found."

    with open(sql_file, "r", encoding="utf-8") as f:
        script = f.read()

    # Split script into blocks by '/' and ';'
    # Oracle DDL and PL/SQL blocks end with '/'
    blocks = [b.strip() for b in script.split("/") if b.strip()]

    with get_oracle_connection() as conn:
        with conn.cursor() as cur:
            for block in blocks:
                # Clean up command-line artifacts
                lines = [l for l in block.splitlines() if not l.strip().startswith("SET ") and not l.strip().startswith("--")]
                clean_block = "\n".join(lines).strip()
                if clean_block:
                    try:
                        cur.execute(clean_block)
                    except Exception as e:
                        # Continue if drop statements fail on non-existent objects
                        if "ORA-00942" not in str(e) and "ORA-02289" not in str(e):
                            pass
        conn.commit()
    return True, "PL/SQL tables, sequences, triggers, and STUDY_PLANNER_PKG compiled successfully."


def plsql_add_subject(name, exam_date, difficulty=3):
    """Calls STUDY_PLANNER_PKG.SP_ADD_SUBJECT via PL/SQL."""
    with get_oracle_connection() as conn:
        with conn.cursor() as cur:
            cur.callproc("STUDY_PLANNER_PKG.SP_ADD_SUBJECT", [name.strip(), exam_date, int(difficulty)])


def plsql_delete_subject(subject_id):
    """Calls STUDY_PLANNER_PKG.SP_DELETE_SUBJECT via PL/SQL."""
    with get_oracle_connection() as conn:
        with conn.cursor() as cur:
            cur.callproc("STUDY_PLANNER_PKG.SP_DELETE_SUBJECT", [int(subject_id)])


def plsql_get_all_subjects():
    """Retrieves all subjects via STUDY_PLANNER_PKG.SP_GET_ALL_SUBJECTS REF CURSOR."""
    with get_oracle_connection() as conn:
        with conn.cursor() as cur:
            out_cur = cur.var(oracledb.CURSOR)
            cur.callproc("STUDY_PLANNER_PKG.SP_GET_ALL_SUBJECTS", [out_cur])
            rows = out_cur.getvalue().fetchall()
            return [
                {"id": r[0], "name": r[1], "exam_date": str(r[2]), "difficulty": int(r[3])}
                for r in rows
            ]


def plsql_set_all_subjects(subjects_list):
    """Overwrites all subjects through PL/SQL procedures inside an atomic transaction."""
    with get_oracle_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM SUBJECTS")
            for s in subjects_list:
                cur.callproc("STUDY_PLANNER_PKG.SP_ADD_SUBJECT", [
                    s["name"].strip(),
                    s["exam_date"],
                    int(s["difficulty"]),
                ])
        conn.commit()


def plsql_insert_task(task_id, task_date, subject, title, status="Pending", duration=60):
    """Calls STUDY_PLANNER_PKG.SP_INSERT_TASK via PL/SQL."""
    with get_oracle_connection() as conn:
        with conn.cursor() as cur:
            cur.callproc("STUDY_PLANNER_PKG.SP_INSERT_TASK", [
                task_id,
                task_date,
                subject,
                title,
                status,
                int(duration),
            ])


def plsql_set_all_tasks(tasks_list):
    """Overwrites all scheduled tasks through PL/SQL stored procedures."""
    with get_oracle_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM TASKS")
            for t in tasks_list:
                cur.callproc("STUDY_PLANNER_PKG.SP_INSERT_TASK", [
                    t["id"],
                    t["date"],
                    t["subject"],
                    t["title"],
                    t.get("status", "Pending"),
                    int(t.get("duration", 60)),
                ])
        conn.commit()


def plsql_get_all_tasks():
    """Retrieves all tasks via STUDY_PLANNER_PKG.SP_GET_ALL_TASKS REF CURSOR."""
    with get_oracle_connection() as conn:
        with conn.cursor() as cur:
            out_cur = cur.var(oracledb.CURSOR)
            cur.callproc("STUDY_PLANNER_PKG.SP_GET_ALL_TASKS", [out_cur])
            rows = out_cur.getvalue().fetchall()
            return [
                {
                    "id": str(r[0]),
                    "date": str(r[1]),
                    "subject": r[2],
                    "title": r[3],
                    "status": r[4],
                    "duration": int(r[5]),
                }
                for r in rows
            ]


def plsql_update_task_status(task_id, new_status):
    """Calls STUDY_PLANNER_PKG.SP_UPDATE_TASK_STATUS via PL/SQL."""
    with get_oracle_connection() as conn:
        with conn.cursor() as cur:
            cur.callproc("STUDY_PLANNER_PKG.SP_UPDATE_TASK_STATUS", [task_id, new_status])


def plsql_reschedule_tasks(rescheduled_map):
    """Calls STUDY_PLANNER_PKG.SP_RESCHEDULE_TASK in bulk."""
    with get_oracle_connection() as conn:
        with conn.cursor() as cur:
            for task_id, info in rescheduled_map.items():
                cur.callproc("STUDY_PLANNER_PKG.SP_RESCHEDULE_TASK", [
                    task_id,
                    info["date"],
                    info["title"],
                ])
        conn.commit()


def plsql_log_pomodoro(subject, duration_mins=25):
    """Calls STUDY_PLANNER_PKG.SP_LOG_POMODORO via PL/SQL."""
    today_str = datetime.now().strftime("%Y-%m-%d")
    with get_oracle_connection() as conn:
        with conn.cursor() as cur:
            cur.callproc("STUDY_PLANNER_PKG.SP_LOG_POMODORO", [
                today_str,
                subject,
                int(duration_mins),
            ])


def plsql_get_pomodoro_logs():
    """Retrieves recent sprints via STUDY_PLANNER_PKG.SP_GET_POMODORO_LOGS REF CURSOR."""
    with get_oracle_connection() as conn:
        with conn.cursor() as cur:
            out_cur = cur.var(oracledb.CURSOR)
            cur.callproc("STUDY_PLANNER_PKG.SP_GET_POMODORO_LOGS", [out_cur])
            rows = out_cur.getvalue().fetchall()
            return [
                {
                    "id": r[0],
                    "session_date": str(r[1]),
                    "subject": r[2],
                    "duration_mins": int(r[3]),
                    "completed_at": str(r[4]),
                }
                for r in rows
            ]


def plsql_clear_database():
    """Calls STUDY_PLANNER_PKG.SP_CLEAR_DATABASE via PL/SQL."""
    with get_oracle_connection() as conn:
        with conn.cursor() as cur:
            cur.callproc("STUDY_PLANNER_PKG.SP_CLEAR_DATABASE")


def plsql_seed_default_curriculum():
    """Calls STUDY_PLANNER_PKG.SP_SEED_DEFAULT_DATA via PL/SQL."""
    with get_oracle_connection() as conn:
        with conn.cursor() as cur:
            cur.callproc("STUDY_PLANNER_PKG.SP_SEED_DEFAULT_DATA")


def plsql_get_database_stats():
    """Returns metadata and statistics from Oracle PL/SQL package."""
    with get_oracle_connection() as conn:
        with conn.cursor() as cur:
            s_count = cur.var(oracledb.NUMBER)
            t_count = cur.var(oracledb.NUMBER)
            p_count = cur.var(oracledb.NUMBER)
            cur.callproc("STUDY_PLANNER_PKG.SP_GET_STATS", [s_count, t_count, p_count])
            
            # Fetch audit logs count
            cur.execute("SELECT COUNT(*) FROM AUDIT_LOGS")
            audit_count = cur.fetchone()[0]

            cfg = load_oracle_config()
            return {
                "engine": "Oracle PL/SQL",
                "dsn": get_dsn(cfg),
                "user": cfg.get("user", "system"),
                "subjects_count": int(s_count.getvalue() or 0),
                "tasks_count": int(t_count.getvalue() or 0),
                "pomodoro_count": int(p_count.getvalue() or 0),
                "audit_count": int(audit_count or 0),
            }


def plsql_get_audit_logs(limit=20):
    """Fetches recent trigger-generated audit records from AUDIT_LOGS table."""
    with get_oracle_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT AUDIT_ID, TABLE_NAME, OPERATION, RECORD_ID, 
                       TO_CHAR(CHANGED_AT, 'YYYY-MM-DD HH24:MI:SS') AS CHANGED_AT, DETAILS
                FROM AUDIT_LOGS
                ORDER BY AUDIT_ID DESC
                FETCH FIRST :lim ROWS ONLY
            """, {"lim": limit})
            rows = cur.fetchall()
            return [
                {
                    "audit_id": r[0],
                    "table_name": r[1],
                    "operation": r[2],
                    "record_id": r[3],
                    "changed_at": str(r[4]),
                    "details": r[5],
                }
                for r in rows
            ]

