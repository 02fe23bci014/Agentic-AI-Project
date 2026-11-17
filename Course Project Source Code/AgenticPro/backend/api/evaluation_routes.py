import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.database.connection import get_connection
from backend.models.evaluation import Evaluation
from backend.services.evaluation_service import EvaluationService
from backend.tools.code_execution_tool import execute_code


router = APIRouter()
evaluation_service = EvaluationService()


class RunCodeRequest(BaseModel):
    source_code: str = Field(min_length=1)
    language: str = "python"
    stdin: str = ""


@router.post("/run-code")
def run_code_directly(request: RunCodeRequest) -> dict:
    """Execute code against stdin directly for testing in editor."""
    try:
        result = execute_code(
            source_code=request.source_code,
            language=request.language,
            stdin=request.stdin,
            timeout_seconds=5,
        )
        return {
            "stdout": result.get("stdout", ""),
            "stderr": result.get("stderr", ""),
            "returncode": result.get("returncode", 0),
            "timed_out": result.get("timed_out", False),
        }
    except Exception as exc:
        return {
            "stdout": "",
            "stderr": str(exc),
            "returncode": 1,
            "timed_out": False,
        }


@router.post("/{submission_id}/run", response_model=Evaluation)
def run_evaluation(submission_id: str) -> Evaluation:
    """Execute stored test cases and save the evaluation result."""

    try:
        return evaluation_service.evaluate_submission(submission_id)
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Evaluation failed: {error}",
        ) from error


@router.get("/{submission_id}", response_model=Evaluation)
def get_evaluation(submission_id: str) -> Evaluation:
    """Retrieve the saved evaluation record from SQLite."""

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT submission_id, passed, total, score, feedback, status, agent_insights
            FROM evaluations
            WHERE submission_id = ?
            """,
            (submission_id,),
        ).fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail=f"Evaluation for submission '{submission_id}' was not found.",
        )

    insights = None
    if "agent_insights" in row.keys() and row["agent_insights"]:
        try:
            insights = json.loads(row["agent_insights"])
        except Exception:
            insights = None

    return Evaluation(
        submission_id=row["submission_id"],
        passed=row["passed"],
        total=row["total"],
        score=row["score"],
        feedback=row["feedback"],
        status=row["status"],
        agent_insights=insights,
    )
