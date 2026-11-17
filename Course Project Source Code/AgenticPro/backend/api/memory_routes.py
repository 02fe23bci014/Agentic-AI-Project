from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.agents.memory_agent import MemoryAgent

router = APIRouter()
memory_agent = MemoryAgent()


class MemoryRequest(BaseModel):
    text: str = Field(..., min_length=1)


class MemorySearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    limit: int = Field(default=5, ge=1, le=100)


@router.post("/")
def save_memory(request: MemoryRequest) -> dict:
    try:
        return memory_agent.save(request.text)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/")
def get_memories() -> list[dict]:
    return memory_agent.recall()


@router.post("/search")
def search_memories(request: MemorySearchRequest) -> list[dict]:
    return memory_agent.search(request.query, request.limit)