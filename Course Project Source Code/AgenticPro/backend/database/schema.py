from backend.database.connection import get_connection


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('student', 'faculty')),
    full_name TEXT NOT NULL,
    email TEXT
);

CREATE TABLE IF NOT EXISTS exams (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    starts_at TEXT,
    duration_minutes INTEGER NOT NULL CHECK (duration_minutes > 0)
);

CREATE TABLE IF NOT EXISTS questions (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    prompt TEXT NOT NULL,
    language TEXT NOT NULL DEFAULT 'python',
    points REAL NOT NULL DEFAULT 1 CHECK (points >= 0),
    difficulty TEXT NOT NULL DEFAULT 'L1',
    domain TEXT NOT NULL DEFAULT 'Algorithms'
);

CREATE TABLE IF NOT EXISTS exam_questions (
    exam_id TEXT NOT NULL,
    question_id TEXT NOT NULL,
    PRIMARY KEY (exam_id, question_id),
    FOREIGN KEY (exam_id) REFERENCES exams(id),
    FOREIGN KEY (question_id) REFERENCES questions(id)
);

CREATE TABLE IF NOT EXISTS test_cases (
    id TEXT PRIMARY KEY,
    question_id TEXT NOT NULL,
    stdin TEXT NOT NULL DEFAULT '',
    expected_stdout TEXT NOT NULL,
    points REAL NOT NULL DEFAULT 1 CHECK (points >= 0),
    is_hidden INTEGER NOT NULL DEFAULT 1
        CHECK (is_hidden IN (0, 1)),
    FOREIGN KEY (question_id) REFERENCES questions(id)
);

CREATE TABLE IF NOT EXISTS submissions (
    id TEXT PRIMARY KEY,
    exam_id TEXT NOT NULL,
    question_id TEXT NOT NULL,
    student_id TEXT NOT NULL,
    language TEXT NOT NULL,
    source_code TEXT NOT NULL,
    submitted_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS evaluations (
    submission_id TEXT PRIMARY KEY,
    passed INTEGER NOT NULL DEFAULT 0,
    total INTEGER NOT NULL DEFAULT 0,
    score REAL NOT NULL DEFAULT 0,
    feedback TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'queued',
    agent_insights TEXT DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS results (
    student_id TEXT NOT NULL,
    exam_id TEXT NOT NULL,
    score REAL NOT NULL CHECK (score >= 0),
    max_score REAL NOT NULL CHECK (max_score >= 0),
    published INTEGER NOT NULL DEFAULT 0
        CHECK (published IN (0, 1)),
    PRIMARY KEY (exam_id, student_id),
    FOREIGN KEY (exam_id) REFERENCES exams(id)
);

CREATE TABLE IF NOT EXISTS research_reports (
    id TEXT PRIMARY KEY,
    topic TEXT NOT NULL,
    summary TEXT NOT NULL,
    briefing_json TEXT NOT NULL,
    evidence_count INTEGER NOT NULL DEFAULT 0,
    created_by TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cloud_incidents (
    id TEXT PRIMARY KEY,
    service_name TEXT NOT NULL,
    environment TEXT NOT NULL,
    severity TEXT NOT NULL,
    error_category TEXT NOT NULL,
    root_cause TEXT NOT NULL,
    report_json TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'diagnosed',
    created_by TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sdlc_projects (
    id TEXT PRIMARY KEY,
    project_name TEXT NOT NULL,
    requirement_text TEXT NOT NULL,
    target_language TEXT NOT NULL,
    framework TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'completed',
    artifact_json TEXT NOT NULL,
    created_by TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS governance_audits (
    id TEXT PRIMARY KEY,
    action_title TEXT NOT NULL,
    target_system TEXT NOT NULL,
    overall_risk_score INTEGER NOT NULL DEFAULT 0,
    risk_tier TEXT NOT NULL DEFAULT 'LOW',
    status TEXT NOT NULL DEFAULT 'PENDING_REVIEW',
    audit_json TEXT NOT NULL,
    initiator TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS discipline_worklets (
    id TEXT PRIMARY KEY,
    discipline TEXT NOT NULL,
    worklet_type TEXT NOT NULL,
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'computed',
    compliance_verdict TEXT NOT NULL DEFAULT 'COMPLIANT',
    worklet_json TEXT NOT NULL,
    created_by TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS capstone_projects (
    id TEXT PRIMARY KEY,
    team_name TEXT NOT NULL,
    project_title TEXT NOT NULL,
    domain TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'completed',
    risk_score INTEGER NOT NULL DEFAULT 15,
    tests_passed INTEGER NOT NULL DEFAULT 0,
    artifact_json TEXT NOT NULL,
    created_by TEXT,
    created_at TEXT NOT NULL
);
"""


def initialize_schema() -> None:
    """Create missing database tables without deleting existing records."""

    with get_connection() as connection:
        connection.executescript(SCHEMA)
        try:
            connection.execute("ALTER TABLE evaluations ADD COLUMN agent_insights TEXT DEFAULT '{}'")
        except Exception:
            pass
        try:
            connection.execute("ALTER TABLE questions ADD COLUMN difficulty TEXT NOT NULL DEFAULT 'L1'")
        except Exception:
            pass
        try:
            connection.execute("ALTER TABLE questions ADD COLUMN domain TEXT NOT NULL DEFAULT 'Algorithms'")
        except Exception:
            pass

    # Ensure default student and faculty users exist
    from backend.services.auth_service import seed_default_users
    seed_default_users()

    # Ensure rich multi-domain questions with L1/L2/L3 difficulties exist
    from backend.database.seed_questions import seed_domain_questions
    seed_domain_questions()
