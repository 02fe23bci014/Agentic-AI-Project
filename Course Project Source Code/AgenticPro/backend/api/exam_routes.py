from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.database.connection import get_connection
from backend.models.exam import Exam


router = APIRouter()


class ExamCreateRequest(BaseModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    starts_at: datetime | None = None
    duration_minutes: int = Field(gt=0)
    question_ids: list[str] = Field(default_factory=list)


@router.get("/", response_model=list[Exam])
def list_exams() -> list[Exam]:
    """Retrieve all exams with their associated question IDs."""
    with get_connection() as connection:
        exam_rows = connection.execute(
            """
            SELECT id, title, starts_at, duration_minutes
            FROM exams
            ORDER BY id
            """
        ).fetchall()

        relation_rows = connection.execute(
            """
            SELECT exam_id, question_id
            FROM exam_questions
            ORDER BY question_id
            """
        ).fetchall()

    questions_by_exam: dict[str, list[str]] = {}
    for rel in relation_rows:
        questions_by_exam.setdefault(rel["exam_id"], []).append(rel["question_id"])

    exams = []
    for row in exam_rows:
        starts_at = (
            datetime.fromisoformat(row["starts_at"])
            if row["starts_at"]
            else None
        )
        exams.append(
            Exam(
                id=row["id"],
                title=row["title"],
                starts_at=starts_at,
                duration_minutes=row["duration_minutes"],
                question_ids=questions_by_exam.get(row["id"], []),
            )
        )
    return exams


@router.post("/", response_model=Exam, status_code=201)
def create_exam(request: ExamCreateRequest) -> Exam:
    """Create an exam and associate existing questions with it."""

    exam_id = request.id.strip()
    title = request.title.strip()

    if not exam_id or not title:
        raise HTTPException(
            status_code=400,
            detail="Exam ID and title cannot be empty.",
        )

    question_ids = list(dict.fromkeys(request.question_ids))

    with get_connection() as connection:
        existing_exam = connection.execute(
            "SELECT id FROM exams WHERE id = ?",
            (exam_id,),
        ).fetchone()

        if existing_exam:
            raise HTTPException(
                status_code=409,
                detail=f"Exam '{exam_id}' already exists.",
            )

        if question_ids:
            placeholders = ",".join("?" for _ in question_ids)

            rows = connection.execute(
                f"SELECT id FROM questions WHERE id IN ({placeholders})",
                question_ids,
            ).fetchall()

            found_ids = {row["id"] for row in rows}
            missing_ids = [
                question_id
                for question_id in question_ids
                if question_id not in found_ids
            ]

            if missing_ids:
                raise HTTPException(
                    status_code=400,
                    detail=f"Questions not found: {missing_ids}",
                )

        starts_at = (
            request.starts_at.isoformat()
            if request.starts_at
            else None
        )

        connection.execute(
            """
            INSERT INTO exams (id, title, starts_at, duration_minutes)
            VALUES (?, ?, ?, ?)
            """,
            (
                exam_id,
                title,
                starts_at,
                request.duration_minutes,
            ),
        )

        connection.executemany(
            """
            INSERT INTO exam_questions (exam_id, question_id)
            VALUES (?, ?)
            """,
            [(exam_id, question_id) for question_id in question_ids],
        )

    return Exam(
        id=exam_id,
        title=title,
        starts_at=request.starts_at,
        duration_minutes=request.duration_minutes,
        question_ids=question_ids,
    )


@router.post(
    "/{exam_id}/questions/{question_id}",
    status_code=200,
)
def add_question_to_exam(
    exam_id: str,
    question_id: str,
) -> dict[str, str]:
    """Associate an existing question with an existing exam."""

    with get_connection() as connection:
        exam = connection.execute(
            "SELECT id FROM exams WHERE id = ?",
            (exam_id,),
        ).fetchone()

        if exam is None:
            raise HTTPException(
                status_code=404,
                detail=f"Exam '{exam_id}' was not found.",
            )

        question = connection.execute(
            "SELECT id FROM questions WHERE id = ?",
            (question_id,),
        ).fetchone()

        if question is None:
            raise HTTPException(
                status_code=404,
                detail=f"Question '{question_id}' was not found.",
            )

        existing = connection.execute(
            """
            SELECT exam_id
            FROM exam_questions
            WHERE exam_id = ? AND question_id = ?
            """,
            (exam_id, question_id),
        ).fetchone()

        if existing:
            return {
                "message": "Question is already associated with this exam."
            }

        connection.execute(
            """
            INSERT INTO exam_questions (exam_id, question_id)
            VALUES (?, ?)
            """,
            (exam_id, question_id),
        )

    return {"message": "Question added to exam successfully."}


@router.get("/{exam_id}", response_model=Exam)
def get_exam(exam_id: str) -> Exam:
    """Retrieve an exam and its associated question IDs."""

    with get_connection() as connection:
        exam_row = connection.execute(
            """
            SELECT id, title, starts_at, duration_minutes
            FROM exams
            WHERE id = ?
            """,
            (exam_id,),
        ).fetchone()

        if exam_row is None:
            raise HTTPException(
                status_code=404,
                detail=f"Exam '{exam_id}' was not found.",
            )

        question_rows = connection.execute(
            """
            SELECT question_id
            FROM exam_questions
            WHERE exam_id = ?
            ORDER BY question_id
            """,
            (exam_id,),
        ).fetchall()

    starts_at = (
        datetime.fromisoformat(exam_row["starts_at"])
        if exam_row["starts_at"]
        else None
    )

    return Exam(
        id=exam_row["id"],
        title=exam_row["title"],
        starts_at=starts_at,
        duration_minutes=exam_row["duration_minutes"],
        question_ids=[row["question_id"] for row in question_rows],
    )


@router.delete("/{exam_id}", status_code=200)
def delete_exam(exam_id: str) -> dict[str, str]:
    """Delete an exam and its associations."""
    with get_connection() as connection:
        exam = connection.execute(
            "SELECT id FROM exams WHERE id = ?",
            (exam_id,),
        ).fetchone()

        if exam is None:
            raise HTTPException(
                status_code=404,
                detail=f"Exam '{exam_id}' was not found.",
            )

        connection.execute("DELETE FROM exam_questions WHERE exam_id = ?", (exam_id,))
        connection.execute("DELETE FROM exams WHERE id = ?", (exam_id,))

    return {"message": f"Exam '{exam_id}' deleted successfully."}
