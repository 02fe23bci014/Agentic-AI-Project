import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.database.connection import get_connection
from backend.models.question import Question


router = APIRouter()


class QuestionCreateRequest(BaseModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    prompt: str = Field(min_length=1)
    language: str = "python"
    points: float = Field(default=1, ge=0)
    difficulty: str = "L1"
    domain: str = "Algorithms"


class QuestionGenerateRequest(BaseModel):
    topic: str = "Arrays"
    difficulty: str = "Easy"
    language: str = "python"
    marks: int = 10


@router.get("/", response_model=list[Question])
def list_questions() -> list[Question]:
    """Retrieve all questions from SQLite."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, title, prompt, language, points,
                   COALESCE(difficulty, 'L1') AS difficulty,
                   COALESCE(domain, 'Algorithms') AS domain
            FROM questions
            ORDER BY id
            """
        ).fetchall()

    return [
        Question(
            id=row["id"],
            title=row["title"],
            prompt=row["prompt"],
            language=row["language"],
            points=row["points"],
            difficulty=row["difficulty"],
            domain=row["domain"],
        )
        for row in rows
    ]


@router.post("/", response_model=Question, status_code=201)
def create_question(request: QuestionCreateRequest) -> Question:
    """Save a new question in SQLite."""

    question_id = request.id.strip()
    title = request.title.strip()
    prompt = request.prompt.strip()
    difficulty = (request.difficulty or "L1").strip().upper()
    domain = (request.domain or "Algorithms").strip()

    if not question_id or not title or not prompt:
        raise HTTPException(
            status_code=400,
            detail="Question ID, title, and prompt cannot be empty.",
        )

    with get_connection() as connection:
        existing = connection.execute(
            "SELECT id FROM questions WHERE id = ?",
            (question_id,),
        ).fetchone()

        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Question '{question_id}' already exists.",
            )

        connection.execute(
            """
            INSERT INTO questions (id, title, prompt, language, points, difficulty, domain)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                question_id,
                title,
                prompt,
                request.language.strip(),
                request.points,
                difficulty,
                domain,
            ),
        )

    return Question(
        id=question_id,
        title=title,
        prompt=prompt,
        language=request.language.strip(),
        points=request.points,
        difficulty=difficulty,
        domain=domain,
    )


@router.post("/generate", response_model=dict)
def generate_question(request: QuestionGenerateRequest) -> dict:
    """Generate a question using the Question Generation Agent with fallback."""
    topic = request.topic.strip()
    difficulty = request.difficulty.strip()
    language = request.language.strip()
    marks = request.marks

    # Attempt agent generation
    try:
        from backend.agents.question_generation_agent import QuestionGenerationAgent
        agent = QuestionGenerationAgent()
        result = agent.generate_question(
            topic=topic,
            difficulty=difficulty,
            language=language,
            marks=marks,
        )
        return {
            "id": f"gen-{uuid.uuid4().hex[:8]}",
            "title": result.get("title", f"{topic} Problem"),
            "prompt": result.get("description") or f"Solve the following {topic} challenge in {language}.",
            "language": language,
            "points": marks,
            "constraints": result.get("constraints", ""),
            "input_format": result.get("input_format", ""),
            "output_format": result.get("output_format", ""),
            "examples": result.get("examples", []),
            "generated_by": "ollama_agent",
        }
    except Exception as exc:
        # High-quality agentic fallback templates based on topic and difficulty
        templates = {
            "Arrays": {
                "Easy": {
                    "title": "Find Maximum Element in Array",
                    "prompt": "Write a program that takes an integer N followed by N integers, and prints the maximum value found in the array.",
                    "input_format": "Line 1: An integer N (1 <= N <= 1000)\nLine 2: N space-separated integers",
                    "output_format": "Print the maximum integer.",
                    "sample_input": "5\n4 2 9 7 5",
                    "sample_output": "9",
                },
                "Medium": {
                    "title": "Subarray Sum Equals K",
                    "prompt": "Given an array of integers and an integer K, find the total number of continuous subarrays whose sum equals to K.",
                    "input_format": "Line 1: Two space-separated integers N and K\nLine 2: N integers",
                    "output_format": "Print the number of subarrays.",
                    "sample_input": "3 2\n1 1 1",
                    "sample_output": "2",
                },
            },
            "Strings": {
                "Easy": {
                    "title": "Valid Palindrome Check",
                    "prompt": "Given a string S consisting of alphanumeric characters, determine if it is a palindrome ignoring case and non-alphanumeric symbols.",
                    "input_format": "A single string on standard input.",
                    "output_format": "Print 'true' if palindrome, 'false' otherwise.",
                    "sample_input": "racecar",
                    "sample_output": "true",
                },
                "Medium": {
                    "title": "Longest Substring Without Repeating Characters",
                    "prompt": "Given a string S, find the length of the longest substring without repeating characters.",
                    "input_format": "A single line containing the string S.",
                    "output_format": "Print an integer denoting the maximum length.",
                    "sample_input": "abcabcbb",
                    "sample_output": "3",
                },
            },
            "Math": {
                "Easy": {
                    "title": "Sum of Digits",
                    "prompt": "Read an integer N from standard input and print the sum of its decimal digits.",
                    "input_format": "A single integer N (1 <= N <= 10^9).",
                    "output_format": "Print the sum of digits.",
                    "sample_input": "12345",
                    "sample_output": "15",
                },
            },
        }

        topic_data = templates.get(topic, templates["Arrays"])
        diff_data = topic_data.get(difficulty, next(iter(topic_data.values())))

        full_prompt = (
            f"{diff_data['prompt']}\n\n"
            f"Input format:\n{diff_data['input_format']}\n\n"
            f"Output format:\n{diff_data['output_format']}"
        )

        return {
            "id": f"gen-{uuid.uuid4().hex[:8]}",
            "title": diff_data["title"],
            "prompt": full_prompt,
            "language": language,
            "points": marks,
            "sample_input": diff_data.get("sample_input", "2 3"),
            "sample_output": diff_data.get("sample_output", "5"),
            "generated_by": "smart_agent_template",
            "agent_note": f"Fallback template applied (Ollama reason: {exc})",
        }


@router.get("/{question_id}", response_model=Question)
def get_question(question_id: str) -> Question:
    """Retrieve a question from SQLite."""

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, title, prompt, language, points,
                   COALESCE(difficulty, 'L1') AS difficulty,
                   COALESCE(domain, 'Algorithms') AS domain
            FROM questions
            WHERE id = ?
            """,
            (question_id,),
        ).fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail=f"Question '{question_id}' was not found.",
            )

        return Question(
            id=row["id"],
            title=row["title"],
            prompt=row["prompt"],
            language=row["language"],
            points=row["points"],
            difficulty=row["difficulty"],
            domain=row["domain"],
        )


@router.delete("/{question_id}", status_code=200)
def delete_question(question_id: str) -> dict[str, str]:
    """Delete a question from SQLite."""
    with get_connection() as connection:
        row = connection.execute(
            "SELECT id FROM questions WHERE id = ?",
            (question_id,),
        ).fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail=f"Question '{question_id}' was not found.",
            )

        connection.execute("DELETE FROM test_cases WHERE question_id = ?", (question_id,))
        connection.execute("DELETE FROM exam_questions WHERE question_id = ?", (question_id,))
        connection.execute("DELETE FROM questions WHERE id = ?", (question_id,))

    return {"message": f"Question '{question_id}' deleted successfully."}
