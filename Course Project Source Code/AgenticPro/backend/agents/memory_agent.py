from typing import Any

from backend.memory.long_term_memory import LongTermMemory


class MemoryAgent:
    """Manage persistent application memories."""

    def __init__(self, memory: LongTermMemory | None = None) -> None:
        self.memory = memory or LongTermMemory()

    def save(self, text: str) -> dict[str, Any]:
        """Save a new memory."""
        text = text.strip()

        if not text:
            raise ValueError("Memory text cannot be empty.")

        item = {"text": text}
        self.memory.add(item)
        return item

    def recall(self) -> list[dict[str, Any]]:
        """Return all saved memories."""
        return self.memory.all()

    def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """Search saved memories."""
        query = query.strip()

        if not query:
            return []

        return self.memory.search(query, limit=limit)