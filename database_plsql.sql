-- ============================================================================
-- SmartStudy Planner AI - Oracle PL/SQL Database Script
-- Comprehensive Relational Schema, Sequences, Triggers, Functions, 
-- Stored Procedures, and PL/SQL Package (STUDY_PLANNER_PKG)
-- Compatible with Oracle Database 11g / 12c / 19c / 21c / 23ai (Express / Enterprise)
-- ============================================================================

SET SERVEROUTPUT ON;

-- ----------------------------------------------------------------------------
-- 1. DROP EXISTING OBJECTS (CLEAN SLATE EXECUTION)
-- ----------------------------------------------------------------------------
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE AUDIT_LOGS CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE POMODORO_LOGS CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE TASKS CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE SUBJECTS CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
    EXECUTE IMMEDIATE 'DROP SEQUENCE SEQ_SUBJECTS_ID';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
    EXECUTE IMMEDIATE 'DROP SEQUENCE SEQ_POMODORO_ID';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
    EXECUTE IMMEDIATE 'DROP SEQUENCE SEQ_AUDIT_ID';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

-- ----------------------------------------------------------------------------
-- 2. SEQUENCES FOR PRIMARY KEY GENERATION
-- ----------------------------------------------------------------------------
CREATE SEQUENCE SEQ_SUBJECTS_ID START WITH 1 INCREMENT BY 1 NOCACHE NOCYCLE;
CREATE SEQUENCE SEQ_POMODORO_ID START WITH 1 INCREMENT BY 1 NOCACHE NOCYCLE;
CREATE SEQUENCE SEQ_AUDIT_ID START WITH 1 INCREMENT BY 1 NOCACHE NOCYCLE;

-- ----------------------------------------------------------------------------
-- 3. RELATIONAL TABLE DEFINITIONS WITH INTEGRITY CONSTRAINTS
-- ----------------------------------------------------------------------------

-- Table 1: Subjects (Academic curriculum courses & exam deadlines)
CREATE TABLE SUBJECTS (
    ID          NUMBER(10) PRIMARY KEY,
    NAME        VARCHAR2(100) NOT NULL UNIQUE,
    EXAM_DATE   DATE NOT NULL,
    DIFFICULTY  NUMBER(1) NOT NULL,
    CREATED_AT  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT CHK_SUBJECT_DIFFICULTY CHECK (DIFFICULTY BETWEEN 1 AND 5)
);

-- Table 2: Tasks (Daily study sessions scheduled across planning horizon)
CREATE TABLE TASKS (
    ID          VARCHAR2(50) PRIMARY KEY,
    TASK_DATE   DATE NOT NULL,
    SUBJECT     VARCHAR2(100) NOT NULL,
    TITLE       VARCHAR2(250) NOT NULL,
    STATUS      VARCHAR2(20) DEFAULT 'Pending' NOT NULL,
    DURATION    NUMBER(5) DEFAULT 60 NOT NULL,
    CREATED_AT  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT CHK_TASK_STATUS CHECK (STATUS IN ('Pending', 'Completed', 'Missed'))
);

-- Table 3: Pomodoro Logs (Track completed 25-minute focus sprints)
CREATE TABLE POMODORO_LOGS (
    ID             NUMBER(10) PRIMARY KEY,
    SESSION_DATE   DATE NOT NULL,
    SUBJECT        VARCHAR2(100) NOT NULL,
    DURATION_MINS  NUMBER(5) DEFAULT 25 NOT NULL,
    COMPLETED_AT   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 4: Audit Logs (PL/SQL Trigger audit trail for data governance)
CREATE TABLE AUDIT_LOGS (
    AUDIT_ID    NUMBER(10) PRIMARY KEY,
    TABLE_NAME  VARCHAR2(50) NOT NULL,
    OPERATION   VARCHAR2(20) NOT NULL,
    RECORD_ID   VARCHAR2(100),
    CHANGED_AT  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    DETAILS     VARCHAR2(400)
);

-- ----------------------------------------------------------------------------
-- 4. DATABASE TRIGGERS
-- ----------------------------------------------------------------------------

-- Trigger 1: Auto-assign primary key sequence to SUBJECTS
CREATE OR REPLACE TRIGGER TRG_SUBJECTS_BI
BEFORE INSERT ON SUBJECTS
FOR EACH ROW
BEGIN
    IF :NEW.ID IS NULL THEN
        SELECT SEQ_SUBJECTS_ID.NEXTVAL INTO :NEW.ID FROM DUAL;
    END IF;
END;
/

-- Trigger 2: Auto-assign primary key sequence to POMODORO_LOGS
CREATE OR REPLACE TRIGGER TRG_POMODORO_BI
BEFORE INSERT ON POMODORO_LOGS
FOR EACH ROW
BEGIN
    IF :NEW.ID IS NULL THEN
        SELECT SEQ_POMODORO_ID.NEXTVAL INTO :NEW.ID FROM DUAL;
    END IF;
END;
/

-- Trigger 3: Audit trigger on TASKS state transitions (Pending -> Completed / Missed)
CREATE OR REPLACE TRIGGER TRG_TASKS_AUDIT
AFTER INSERT OR UPDATE ON TASKS
FOR EACH ROW
DECLARE
    v_op VARCHAR2(20);
    v_details VARCHAR2(400);
BEGIN
    IF INSERTING THEN
        v_op := 'INSERT';
        v_details := 'Created task: ' || :NEW.TITLE || ' (' || :NEW.SUBJECT || ')';
    ELSE
        v_op := 'UPDATE';
        v_details := 'Status changed from ' || :OLD.STATUS || ' to ' || :NEW.STATUS;
    END IF;

    INSERT INTO AUDIT_LOGS (AUDIT_ID, TABLE_NAME, OPERATION, RECORD_ID, DETAILS)
    VALUES (SEQ_AUDIT_ID.NEXTVAL, 'TASKS', v_op, :NEW.ID, v_details);
END;
/

-- ----------------------------------------------------------------------------
-- 5. STANDALONE STORED FUNCTIONS
-- ----------------------------------------------------------------------------

-- Function 1: Compute days remaining until examination date
CREATE OR REPLACE FUNCTION FN_DAYS_UNTIL_EXAM(p_exam_date IN DATE) 
RETURN NUMBER IS
    v_days NUMBER;
BEGIN
    v_days := TRUNC(p_exam_date) - TRUNC(SYSDATE);
    IF v_days < 0 THEN
        RETURN 0;
    ELSE
        RETURN v_days;
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RETURN 0;
END;
/

-- Function 2: Calculate overall task completion percentage
CREATE OR REPLACE FUNCTION FN_COMPLETION_RATE 
RETURN NUMBER IS
    v_total NUMBER := 0;
    v_done  NUMBER := 0;
BEGIN
    SELECT COUNT(*) INTO v_total FROM TASKS;
    IF v_total = 0 THEN
        RETURN 0;
    END IF;
    SELECT COUNT(*) INTO v_done FROM TASKS WHERE STATUS = 'Completed';
    RETURN ROUND((v_done / v_total) * 100, 1);
EXCEPTION
    WHEN OTHERS THEN
        RETURN 0;
END;
/

-- ----------------------------------------------------------------------------
-- 6. PL/SQL PACKAGE SPECIFICATION (STUDY_PLANNER_PKG)
-- ----------------------------------------------------------------------------
CREATE OR REPLACE PACKAGE STUDY_PLANNER_PKG AS
    -- Reference cursor type for procedural queries
    TYPE ref_cur IS REF CURSOR;

    -- Subject procedures
    PROCEDURE SP_ADD_SUBJECT(
        p_name       IN VARCHAR2,
        p_exam_date  IN VARCHAR2, -- format 'YYYY-MM-DD'
        p_difficulty IN NUMBER
    );

    PROCEDURE SP_DELETE_SUBJECT(p_id IN NUMBER);

    PROCEDURE SP_GET_ALL_SUBJECTS(p_cursor OUT ref_cur);

    -- Task scheduling procedures
    PROCEDURE SP_INSERT_TASK(
        p_id       IN VARCHAR2,
        p_date     IN VARCHAR2, -- format 'YYYY-MM-DD'
        p_subject  IN VARCHAR2,
        p_title    IN VARCHAR2,
        p_status   IN VARCHAR2 DEFAULT 'Pending',
        p_duration IN NUMBER DEFAULT 60
    );

    PROCEDURE SP_UPDATE_TASK_STATUS(
        p_task_id    IN VARCHAR2,
        p_new_status IN VARCHAR2
    );

    PROCEDURE SP_RESCHEDULE_TASK(
        p_task_id   IN VARCHAR2,
        p_new_date  IN VARCHAR2,
        p_new_title IN VARCHAR2
    );

    PROCEDURE SP_GET_ALL_TASKS(p_cursor OUT ref_cur);

    -- Pomodoro focus logging procedures
    PROCEDURE SP_LOG_POMODORO(
        p_session_date IN VARCHAR2,
        p_subject      IN VARCHAR2,
        p_duration     IN NUMBER DEFAULT 25
    );

    PROCEDURE SP_GET_POMODORO_LOGS(p_cursor OUT ref_cur);

    -- Administrative & Seeding procedures
    PROCEDURE SP_CLEAR_DATABASE;
    PROCEDURE SP_SEED_DEFAULT_DATA;

    -- Diagnostics procedure
    PROCEDURE SP_GET_STATS(
        p_subjects_count OUT NUMBER,
        p_tasks_count    OUT NUMBER,
        p_pomodoro_count OUT NUMBER
    );
END STUDY_PLANNER_PKG;
/

-- ----------------------------------------------------------------------------
-- 7. PL/SQL PACKAGE BODY (STUDY_PLANNER_PKG)
-- ----------------------------------------------------------------------------
CREATE OR REPLACE PACKAGE BODY STUDY_PLANNER_PKG AS

    -- Add or update a subject record
    PROCEDURE SP_ADD_SUBJECT(
        p_name       IN VARCHAR2,
        p_exam_date  IN VARCHAR2,
        p_difficulty IN NUMBER
    ) IS
        v_date DATE;
    BEGIN
        v_date := TO_DATE(p_exam_date, 'YYYY-MM-DD');

        MERGE INTO SUBJECTS s
        USING (SELECT p_name AS name FROM DUAL) src
        ON (s.NAME = src.name)
        WHEN MATCHED THEN
            UPDATE SET s.EXAM_DATE = v_date, s.DIFFICULTY = p_difficulty
        WHEN NOT MATCHED THEN
            INSERT (NAME, EXAM_DATE, DIFFICULTY)
            VALUES (p_name, v_date, p_difficulty);

        COMMIT;
    EXCEPTION
        WHEN OTHERS THEN
            ROLLBACK;
            RAISE;
    END SP_ADD_SUBJECT;

    -- Delete a subject and its associated tasks
    PROCEDURE SP_DELETE_SUBJECT(p_id IN NUMBER) IS
        v_name VARCHAR2(100);
    BEGIN
        SELECT NAME INTO v_name FROM SUBJECTS WHERE ID = p_id;
        DELETE FROM TASKS WHERE SUBJECT = v_name;
        DELETE FROM SUBJECTS WHERE ID = p_id;
        COMMIT;
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            NULL;
        WHEN OTHERS THEN
            ROLLBACK;
            RAISE;
    END SP_DELETE_SUBJECT;

    -- Query all subjects ordered by exam date ascending
    PROCEDURE SP_GET_ALL_SUBJECTS(p_cursor OUT ref_cur) IS
    BEGIN
        OPEN p_cursor FOR
            SELECT ID, NAME, TO_CHAR(EXAM_DATE, 'YYYY-MM-DD') AS EXAM_DATE, DIFFICULTY
            FROM SUBJECTS
            ORDER BY EXAM_DATE ASC;
    END SP_GET_ALL_SUBJECTS;

    -- Insert a scheduled study task
    PROCEDURE SP_INSERT_TASK(
        p_id       IN VARCHAR2,
        p_date     IN VARCHAR2,
        p_subject  IN VARCHAR2,
        p_title    IN VARCHAR2,
        p_status   IN VARCHAR2 DEFAULT 'Pending',
        p_duration IN NUMBER DEFAULT 60
    ) IS
    BEGIN
        INSERT INTO TASKS (ID, TASK_DATE, SUBJECT, TITLE, STATUS, DURATION)
        VALUES (
            p_id,
            TO_DATE(p_date, 'YYYY-MM-DD'),
            p_subject,
            p_title,
            p_status,
            p_duration
        );
        COMMIT;
    EXCEPTION
        WHEN DUP_VAL_ON_INDEX THEN
            UPDATE TASKS
            SET TASK_DATE = TO_DATE(p_date, 'YYYY-MM-DD'),
                SUBJECT = p_subject,
                TITLE = p_title,
                STATUS = p_status,
                DURATION = p_duration
            WHERE ID = p_id;
            COMMIT;
        WHEN OTHERS THEN
            ROLLBACK;
            RAISE;
    END SP_INSERT_TASK;

    -- Atomically update status of a task
    PROCEDURE SP_UPDATE_TASK_STATUS(
        p_task_id    IN VARCHAR2,
        p_new_status IN VARCHAR2
    ) IS
    BEGIN
        UPDATE TASKS
        SET STATUS = p_new_status
        WHERE ID = p_task_id;
        COMMIT;
    EXCEPTION
        WHEN OTHERS THEN
            ROLLBACK;
            RAISE;
    END SP_UPDATE_TASK_STATUS;

    -- Reschedule a task to a future date
    PROCEDURE SP_RESCHEDULE_TASK(
        p_task_id   IN VARCHAR2,
        p_new_date  IN VARCHAR2,
        p_new_title IN VARCHAR2
    ) IS
    BEGIN
        UPDATE TASKS
        SET TASK_DATE = TO_DATE(p_new_date, 'YYYY-MM-DD'),
            TITLE = p_new_title,
            STATUS = 'Pending'
        WHERE ID = p_task_id;
        COMMIT;
    EXCEPTION
        WHEN OTHERS THEN
            ROLLBACK;
            RAISE;
    END SP_RESCHEDULE_TASK;

    -- Query all tasks ordered by date
    PROCEDURE SP_GET_ALL_TASKS(p_cursor OUT ref_cur) IS
    BEGIN
        OPEN p_cursor FOR
            SELECT ID, TO_CHAR(TASK_DATE, 'YYYY-MM-DD') AS TASK_DATE, SUBJECT, TITLE, STATUS, DURATION
            FROM TASKS
            ORDER BY TASK_DATE ASC, ID ASC;
    END SP_GET_ALL_TASKS;

    -- Log a completed Pomodoro sprint
    PROCEDURE SP_LOG_POMODORO(
        p_session_date IN VARCHAR2,
        p_subject      IN VARCHAR2,
        p_duration     IN NUMBER DEFAULT 25
    ) IS
    BEGIN
        INSERT INTO POMODORO_LOGS (SESSION_DATE, SUBJECT, DURATION_MINS)
        VALUES (
            TO_DATE(p_session_date, 'YYYY-MM-DD'),
            p_subject,
            p_duration
        );
        COMMIT;
    EXCEPTION
        WHEN OTHERS THEN
            ROLLBACK;
            RAISE;
    END SP_LOG_POMODORO;

    -- Query recent Pomodoro logs
    PROCEDURE SP_GET_POMODORO_LOGS(p_cursor OUT ref_cur) IS
    BEGIN
        OPEN p_cursor FOR
            SELECT ID, TO_CHAR(SESSION_DATE, 'YYYY-MM-DD') AS SESSION_DATE, SUBJECT, DURATION_MINS, TO_CHAR(COMPLETED_AT, 'YYYY-MM-DD HH24:MI:SS') AS COMPLETED_AT
            FROM POMODORO_LOGS
            ORDER BY ID DESC;
    END SP_GET_POMODORO_LOGS;

    -- Clear all application tables
    PROCEDURE SP_CLEAR_DATABASE IS
    BEGIN
        DELETE FROM TASKS;
        DELETE FROM SUBJECTS;
        DELETE FROM POMODORO_LOGS;
        DELETE FROM AUDIT_LOGS;
        COMMIT;
    EXCEPTION
        WHEN OTHERS THEN
            ROLLBACK;
            RAISE;
    END SP_CLEAR_DATABASE;

    -- Seed sample MCA curriculum
    PROCEDURE SP_SEED_DEFAULT_DATA IS
        v_today DATE := TRUNC(SYSDATE);
    BEGIN
        SP_CLEAR_DATABASE;

        SP_ADD_SUBJECT('Python Programming', TO_CHAR(v_today + 14, 'YYYY-MM-DD'), 4);
        SP_ADD_SUBJECT('Database Management Systems (DBMS)', TO_CHAR(v_today + 10, 'YYYY-MM-DD'), 3);
        SP_ADD_SUBJECT('Advanced Computer Networks', TO_CHAR(v_today + 5, 'YYYY-MM-DD'), 3);
        SP_ADD_SUBJECT('Cloud Computing Architecture', TO_CHAR(v_today + 20, 'YYYY-MM-DD'), 4);

        COMMIT;
    END SP_SEED_DEFAULT_DATA;

    -- Get database statistics
    PROCEDURE SP_GET_STATS(
        p_subjects_count OUT NUMBER,
        p_tasks_count    OUT NUMBER,
        p_pomodoro_count OUT NUMBER
    ) IS
    BEGIN
        SELECT COUNT(*) INTO p_subjects_count FROM SUBJECTS;
        SELECT COUNT(*) INTO p_tasks_count FROM TASKS;
        SELECT COUNT(*) INTO p_pomodoro_count FROM POMODORO_LOGS;
    END SP_GET_STATS;

END STUDY_PLANNER_PKG;
/

-- ----------------------------------------------------------------------------
-- 8. ANONYMOUS EXECUTION BLOCK (VERIFICATION TEST)
-- ----------------------------------------------------------------------------
DECLARE
    v_s_count NUMBER;
    v_t_count NUMBER;
    v_p_count NUMBER;
BEGIN
    DBMS_OUTPUT.PUT_LINE('--- Initializing SmartStudy PL/SQL Seed Data ---');
    STUDY_PLANNER_PKG.SP_SEED_DEFAULT_DATA;
    STUDY_PLANNER_PKG.SP_GET_STATS(v_s_count, v_t_count, v_p_count);
    
    DBMS_OUTPUT.PUT_LINE('Subjects Initialized: ' || v_s_count);
    DBMS_OUTPUT.PUT_LINE('Tasks Initialized:    ' || v_t_count);
    DBMS_OUTPUT.PUT_LINE('PL/SQL Schema and Package compilation successful!');
END;
/

