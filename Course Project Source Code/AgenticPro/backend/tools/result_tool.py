
from backend.database.connection import get_connection
from backend.models.result import Result


def get_result(exam_id: str, student_id: str) -> Result | None:
    """Retrieve a student's result from SQLite."""

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT student_id, exam_id, score, max_score, published
            FROM results
            WHERE exam_id = ? AND student_id = ?
            """,
            (exam_id, student_id),
        ).fetchone()

    if row is None:
        return None

    return Result(
        student_id=row["student_id"],
        exam_id=row["exam_id"],
        score=row["score"],
        max_score=row["max_score"],
        published=bool(row["published"]),
    )


def publish_result(result: Result) -> Result:
    """Save a published result to SQLite."""

    published_result = result.model_copy(
        update={"published": True}
    )

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO results (
                student_id,
                exam_id,
                score,
                max_score,
                published
            )
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(exam_id, student_id)
            DO UPDATE SET
                score = excluded.score,
                max_score = excluded.max_score,
                published = excluded.published
            """,
            (
                published_result.student_id,
                published_result.exam_id,
                published_result.score,
                published_result.max_score,
                int(published_result.published),
            ),
        )

    return published_result
