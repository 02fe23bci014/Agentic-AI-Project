from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from backend.database.connection import get_connection
from backend.models.test_case import TestCase


router = APIRouter()


class TestCaseCreateRequest(BaseModel):
    id: str = Field(min_length=1)
    question_id: str = Field(min_length=1)
    stdin: str = ""
    expected_stdout: str
    points: float = Field(default=1, ge=0)
    is_hidden: bool = True


@router.post("/", response_model=TestCase, status_code=201)
def create_test_case(test_case: TestCaseCreateRequest) -> TestCase:
    """Save a test case for an existing programming question."""

    with get_connection() as connection:
        question = connection.execute(
            "SELECT id FROM questions WHERE id = ?",
            (test_case.question_id,),
        ).fetchone()

        if question is None:
            raise HTTPException(
                status_code=404,
                detail=f"Question '{test_case.question_id}' was not found.",
            )

        existing = connection.execute(
            "SELECT id FROM test_cases WHERE id = ?",
            (test_case.id,),
        ).fetchone()

        if existing is not None:
            raise HTTPException(
                status_code=409,
                detail=f"Test case '{test_case.id}' already exists.",
            )

        connection.execute(
            """
            INSERT INTO test_cases (
                id, question_id, stdin, expected_stdout, points, is_hidden
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                test_case.id,
                test_case.question_id,
                test_case.stdin,
                test_case.expected_stdout,
                test_case.points,
                int(test_case.is_hidden),
            ),
        )

    return TestCase(**test_case.model_dump())


@router.get("/question/{question_id}", response_model=list[TestCase])
def list_test_cases(
    question_id: str,
    include_hidden: bool = Query(default=True),
) -> list[TestCase]:
    """Retrieve test cases for a question."""

    with get_connection() as connection:
        question = connection.execute(
            "SELECT id FROM questions WHERE id = ?",
            (question_id,),
        ).fetchone()

        if question is None:
            raise HTTPException(
                status_code=404,
                detail=f"Question '{question_id}' was not found.",
            )

        if include_hidden:
            rows = connection.execute(
                """
                SELECT id, question_id, stdin, expected_stdout, points, is_hidden
                FROM test_cases
                WHERE question_id = ?
                ORDER BY id
                """,
                (question_id,),
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT id, question_id, stdin, expected_stdout, points, is_hidden
                FROM test_cases
                WHERE question_id = ? AND is_hidden = 0
                ORDER BY id
                """,
                (question_id,),
            ).fetchall()

    return [
        TestCase(
            id=row["id"],
            question_id=row["question_id"],
            stdin=row["stdin"],
            expected_stdout=row["expected_stdout"],
            points=row["points"],
            is_hidden=bool(row["is_hidden"]),
        )
        for row in rows
    ]