from pydantic import BaseModel, Field


class Question(BaseModel):
    id: str
    title: str
    prompt: str
    language: str = "python"
    points: float = Field(default=1, ge=0)
    difficulty: str = "L1"
    domain: str = "Algorithms"
    test_case_ids: list[str] = []
