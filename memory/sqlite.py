"""Long-term memory over past runs (ideas, reports, analysed competitors).

Backed by SQLite. Distinct from LangGraph's *checkpointer* (short-term run
state); this is cross-session recall the Planner can use to compare a new idea
against previous ones. STUB interface for now.
"""

from __future__ import annotations

from dataclasses import dataclass

from config import settings


@dataclass
class MemoryStore:
    db_path: str = settings.memory_db

    def remember_idea(self, idea: str, report: str) -> None:
        """Persist a completed run. STUB."""
        # TODO: CREATE TABLE runs(id, idea, report, created_at); INSERT.
        ...

    def recall_similar(self, idea: str, limit: int = 3) -> list[dict]:
        """Return past runs similar to `idea`. STUB (returns nothing yet)."""
        # TODO: naive LIKE match now; embeddings later.
        return []


store = MemoryStore()
