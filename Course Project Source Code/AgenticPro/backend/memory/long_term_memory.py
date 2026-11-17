import json
from pathlib import Path
from typing import Any

from backend.memory.retrieval import retrieve


class LongTermMemory:
    def __init__(
        self,
        path: Path = Path("./database/memory.jsonl"),
    ) -> None:
        self.path = path

    def add(self, item: dict[str, Any]) -> None:
        """Save a memory permanently."""
        self.path.parent.mkdir(parents=True, exist_ok=True)

        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(item, ensure_ascii=True) + "\n")

    def all(self) -> list[dict[str, Any]]:
        """Return all saved memories."""
        if not self.path.exists():
            return []

        with self.path.open(encoding="utf-8") as stream:
            return [
                json.loads(line)
                for line in stream
                if line.strip()
            ]

    def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """Find saved memories matching a query."""
        if limit < 1:
            return []

        return retrieve(
            records=self.all(),
            query=query,
            text_key="text",
            limit=limit,
        )