from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import (
    auth_routes,
    evaluation_routes,
    exam_routes,
    question_routes,
    result_routes,
    submission_routes,
    test_case_routes,
    research_routes,
    cloud_ops_routes,
    sdlc_routes,
    governance_routes,
    discipline_routes,
    capstone_routes,
)
from backend.config.settings import settings
from backend.database.connection import get_connection
from backend.database.schema import initialize_schema


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)

# Allow common development origins as well as configured origins
allowed_origins = list(dict.fromkeys(settings.allowed_origins + [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(
    auth_routes.router,
    prefix="/api/auth",
    tags=["authentication"],
)

app.include_router(
    exam_routes.router,
    prefix="/api/exams",
    tags=["exams"],
)

app.include_router(
    question_routes.router,
    prefix="/api/questions",
    tags=["questions"],
)

app.include_router(
    submission_routes.router,
    prefix="/api/submissions",
    tags=["submissions"],
)

app.include_router(
    evaluation_routes.router,
    prefix="/api/evaluations",
    tags=["evaluations"],
)

app.include_router(
    result_routes.router,
    prefix="/api/results",
    tags=["results"],
)

app.include_router(
    test_case_routes.router,
    prefix="/api/test-cases",
    tags=["test cases"],
)

app.include_router(
    research_routes.router,
    prefix="/api/research",
    tags=["research"],
)

app.include_router(
    cloud_ops_routes.router,
    prefix="/api/cloud-ops",
    tags=["cloud operations"],
)

app.include_router(
    sdlc_routes.router,
    prefix="/api/sdlc",
    tags=["sdlc factory"],
)

app.include_router(
    governance_routes.router,
    prefix="/api/governance",
    tags=["safety governance"],
)

app.include_router(
    discipline_routes.router,
    prefix="/api/discipline",
    tags=["discipline specific"],
)

app.include_router(
    capstone_routes.router,
    prefix="/api/capstone",
    tags=["capstone studio"],
)


@app.on_event("startup")
def on_startup() -> None:
    """Initialize database tables when the application starts."""
    initialize_schema()


@app.get("/health")
def health() -> dict[str, str]:
    """Check whether the API is running."""
    return {"status": "ok"}


@app.get("/api/stats")
def get_system_stats() -> dict:
    """Return platform statistics for the dashboards."""
    with get_connection() as connection:
        exams_count = connection.execute("SELECT COUNT(*) FROM exams").fetchone()[0]
        questions_count = connection.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
        submissions_count = connection.execute("SELECT COUNT(*) FROM submissions").fetchone()[0]
        evaluations_count = connection.execute("SELECT COUNT(*) FROM evaluations").fetchone()[0]
        results_count = connection.execute("SELECT COUNT(*) FROM results").fetchone()[0]
        test_cases_count = connection.execute("SELECT COUNT(*) FROM test_cases").fetchone()[0]
        users_count = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        research_reports_count = connection.execute("SELECT COUNT(*) FROM research_reports").fetchone()[0]
        cloud_incidents_count = connection.execute("SELECT COUNT(*) FROM cloud_incidents").fetchone()[0]
        sdlc_projects_count = connection.execute("SELECT COUNT(*) FROM sdlc_projects").fetchone()[0]
        governance_audits_count = connection.execute("SELECT COUNT(*) FROM governance_audits").fetchone()[0]
        discipline_worklets_count = connection.execute("SELECT COUNT(*) FROM discipline_worklets").fetchone()[0]
        capstone_projects_count = connection.execute("SELECT COUNT(*) FROM capstone_projects").fetchone()[0]

        avg_score_row = connection.execute("SELECT AVG(score) FROM results").fetchone()
        avg_score = round(float(avg_score_row[0]), 2) if avg_score_row and avg_score_row[0] is not None else 0.0

    return {
        "status": "online",
        "counts": {
            "exams": exams_count,
            "questions": questions_count,
            "submissions": submissions_count,
            "evaluations": evaluations_count,
            "results": results_count,
            "test_cases": test_cases_count,
            "users": users_count,
            "research_reports": research_reports_count,
            "cloud_incidents": cloud_incidents_count,
            "sdlc_projects": sdlc_projects_count,
            "governance_audits": governance_audits_count,
            "discipline_worklets": discipline_worklets_count,
            "capstone_projects": capstone_projects_count,
        },
        "averages": {
            "score": avg_score,
        },
        "agents": [
            {"name": "Sandbox Runner Agent", "role": "Isolated execution of Python, C++, Java", "status": "active"},
            {"name": "Question Generation Agent", "role": "Automated problem & constraint generation", "status": "active"},
            {"name": "Test Case Agent", "role": "Public & hidden test generation", "status": "active"},
            {"name": "Scoring Swarm Agent", "role": "Multi-criteria evaluation & points calculation", "status": "active"},
            {"name": "Feedback Swarm Agent", "role": "Code critique & algorithmic advice", "status": "active"},
            {"name": "Similarity Agent", "role": "Plagiarism & solution uniqueness detection", "status": "active"},
            {"name": "Deep Research Agent", "role": "AI topic briefings & systematic evidence tables (Lab 9)", "status": "active"},
            {"name": "Cloud Operations Agent", "role": "Automated failure diagnosis & remediation patches (Lab 10)", "status": "active"},
            {"name": "Agentic SDLC Factory", "role": "Requirements to tested implementation pipeline (Lab 11)", "status": "active"},
            {"name": "Safety & Governance Agent", "role": "Risk scoring, policy eval, HITL approvals, and rollback simulation (Lab 12)", "status": "active"},
            {"name": "Discipline-Specific Agent", "role": "Analytical derivations, code compliance & simulations for ME / CE / EE (Lab 13)", "status": "active"},
            {"name": "Capstone Studio Agent", "role": "Full team-owned agentic system coordination & deliverables synthesis (Lab 14)", "status": "active"},
        ],
    }
