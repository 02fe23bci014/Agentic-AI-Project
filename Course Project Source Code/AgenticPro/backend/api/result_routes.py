from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.database.connection import get_connection
from backend.models.result import Result


router = APIRouter()


class PublishRequest(BaseModel):
    published: bool = True


@router.get("/", response_model=list[Result])
def list_results(
    exam_id: str | None = None,
    student_id: str | None = None,
) -> list[Result]:
    """Retrieve all stored results with optional filtering."""
    query = "SELECT student_id, exam_id, score, max_score, published FROM results"
    params: list[str] = []
    clauses: list[str] = []
    if isinstance(exam_id, str) and exam_id.strip():
        clauses.append("exam_id = ?")
        params.append(exam_id.strip())
    if isinstance(student_id, str) and student_id.strip():
        clauses.append("student_id = ?")
        params.append(student_id.strip())

    if clauses:
        query += " WHERE " + " AND ".join(clauses)

    with get_connection() as connection:
        rows = connection.execute(query, params).fetchall()

    return [
        Result(
            student_id=row["student_id"],
            exam_id=row["exam_id"],
            score=float(row["score"]),
            max_score=float(row["max_score"]),
            published=bool(row["published"]),
        )
        for row in rows
    ]


@router.get("/{exam_id}/{student_id}", response_model=Result)
def get_result(exam_id: str, student_id: str) -> Result:
    """Calculate or retrieve a student's result."""

    with get_connection() as connection:
        # First check if an existing result is stored
        stored = connection.execute(
            """
            SELECT student_id, exam_id, score, max_score, published
            FROM results
            WHERE exam_id = ? AND student_id = ?
            """,
            (exam_id, student_id),
        ).fetchone()

        if stored:
            return Result(
                student_id=stored["student_id"],
                exam_id=stored["exam_id"],
                score=float(stored["score"]),
                max_score=float(stored["max_score"]),
                published=bool(stored["published"]),
            )

        exam = connection.execute(
            """
            SELECT id
            FROM exams
            WHERE id = ?
            """,
            (exam_id,),
        ).fetchone()

        if exam is None:
            raise HTTPException(
                status_code=404,
                detail=f"Exam '{exam_id}' was not found.",
            )

        rows = connection.execute(
            """
            SELECT
                q.id AS question_id,
                q.points AS question_points,
                s.id AS submission_id,
                e.passed,
                e.total,
                e.score AS evaluation_score,
                e.status
            FROM exam_questions AS eq
            JOIN questions AS q
                ON q.id = eq.question_id
            LEFT JOIN submissions AS s
                ON s.question_id = q.id
                AND s.exam_id = eq.exam_id
                AND s.student_id = ?
            LEFT JOIN evaluations AS e
                ON e.submission_id = s.id
            WHERE eq.exam_id = ?
            """,
            (student_id, exam_id),
        ).fetchall()

    max_score = sum(float(row["question_points"]) for row in rows)
    score = 0.0

    for row in rows:
        if row["status"] != "completed":
            continue

        total_tests = row["total"] or 0
        passed_tests = row["passed"] or 0

        if total_tests > 0:
            question_score = (
                float(row["question_points"])
                * passed_tests
                / total_tests
            )
        else:
            question_score = 0.0

        score += question_score

    res = Result(
        student_id=student_id,
        exam_id=exam_id,
        score=round(score, 2),
        max_score=round(max_score, 2),
        published=False,
    )

    # Save to SQLite
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO results (student_id, exam_id, score, max_score, published)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(student_id, exam_id) DO UPDATE SET
                score = excluded.score,
                max_score = excluded.max_score
            """,
            (student_id, exam_id, res.score, res.max_score, int(res.published)),
        )

    return res


@router.post("/publish/{exam_id}/{student_id}", response_model=dict)
def toggle_publish(
    exam_id: str,
    student_id: str,
    request: PublishRequest = PublishRequest(published=True),
) -> dict:
    """Publish or unpublish an exam result for a student."""
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE results
            SET published = ?
            WHERE exam_id = ? AND student_id = ?
            """,
            (int(request.published), exam_id, student_id),
        )

    return {
        "exam_id": exam_id,
        "student_id": student_id,
        "published": request.published,
        "message": f"Result {'published' if request.published else 'unpublished'} successfully.",
    }
