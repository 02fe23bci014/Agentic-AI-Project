from fastapi import APIRouter, HTTPException

from backend.database.connection import get_connection
from backend.models.submission import Submission


router = APIRouter()


@router.get("/", response_model=list[Submission])
def list_submissions(
    exam_id: str | None = None,
    student_id: str | None = None,
) -> list[Submission]:
    """Retrieve submissions with optional filtering."""
    query = """
        SELECT id, exam_id, question_id, student_id, language, source_code, submitted_at
        FROM submissions
    """
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
    query += " ORDER BY submitted_at DESC"

    with get_connection() as connection:
        rows = connection.execute(query, params).fetchall()

    return [
        Submission(
            id=row["id"],
            exam_id=row["exam_id"],
            question_id=row["question_id"],
            student_id=row["student_id"],
            language=row["language"],
            source_code=row["source_code"],
            submitted_at=row["submitted_at"],
        )
        for row in rows
    ]


@router.get("/{submission_id}", response_model=Submission)
def get_submission(submission_id: str) -> Submission:
    """Retrieve a single submission by ID."""
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, exam_id, question_id, student_id, language, source_code, submitted_at
            FROM submissions
            WHERE id = ?
            """,
            (submission_id,),
        ).fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail=f"Submission '{submission_id}' was not found.",
            )

        return Submission(
            id=row["id"],
            exam_id=row["exam_id"],
            question_id=row["question_id"],
            student_id=row["student_id"],
            language=row["language"],
            source_code=row["source_code"],
            submitted_at=row["submitted_at"],
        )


@router.post("/", response_model=Submission, status_code=201)
def create_submission(submission: Submission) -> Submission:
    """Save a student submission in the SQLite database."""

    with get_connection() as connection:
        exam = connection.execute(
            "SELECT id FROM exams WHERE id = ?",
            (submission.exam_id,),
        ).fetchone()

        if exam is None:
            raise HTTPException(
                status_code=404,
                detail=f"Exam '{submission.exam_id}' was not found.",
            )

        question = connection.execute(
            """
            SELECT question_id
            FROM exam_questions
            WHERE exam_id = ? AND question_id = ?
            """,
            (submission.exam_id, submission.question_id),
        ).fetchone()

        if question is None:
            raise HTTPException(
                status_code=400,
                detail="The question is not associated with this exam.",
            )

        existing = connection.execute(
            "SELECT id FROM submissions WHERE id = ?",
            (submission.id,),
        ).fetchone()

        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Submission '{submission.id}' already exists.",
            )

        connection.execute(
            """
            INSERT INTO submissions (
                id, exam_id, question_id, student_id,
                language, source_code, submitted_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                submission.id,
                submission.exam_id,
                submission.question_id,
                submission.student_id,
                submission.language,
                submission.source_code,
                submission.submitted_at.isoformat(),
            ),
        )

    return submission
