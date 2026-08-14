"""Library Skill — questions about Shenzhen University Library.

Person 2 deliverable. Implements the common Skill interface defined by
Person 1 in app/skills/base.py.

Design notes
------------
* Deterministic: answers are built from knowledge.json (testable without
  Ollama).
* Missing-information behaviour: if a library question asks for something
  not present in the knowledge base, the skill admits it lacks the
  information instead of inventing an official answer.
* Routing: keyword-based; defers explicit translate/summarise requests to
  Person 3's skills.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.skills.base import Skill


# CampusBot/  (parents: [0]=skills, [1]=app, [2]=CampusBot)
_ROOT = Path(__file__).resolve().parents[2]
_KNOWLEDGE_PATH = _ROOT / "knowledge.json"


def _load_knowledge() -> dict:
    with _KNOWLEDGE_PATH.open(encoding="utf-8") as f:
        return json.load(f)


_LIBRARY_KEYWORDS = (
    "library", "libraries", "book", "borrow", " librarian",
    "图书馆",
)


class LibrarySkill(Skill):
    """Answers questions about the university library."""

    name = "library"

    def matches(self, message: str) -> bool:
        text = (message or "").lower()
        if not text.strip():
            return False
        if any(w in text for w in ("translate", "summar", "summary")):
            return False
        return any(k in text for k in _LIBRARY_KEYWORDS)

    def execute(self, message: str) -> str:
        knowledge = _load_knowledge()
        lib = knowledge.get("library", {})
        uni_name = knowledge.get("university", {}).get("name", "the university")
        text = (message or "").lower()

        branches = lib.get("main_branches", [])
        address = lib.get("official_address", "")

        # Location / address questions.
        if any(w in text for w in ("where", "location", "address", "在哪", "地址")):
            parts = []
            if branches:
                parts.append(
                    "The main library branches are: " + "; ".join(branches) + "."
                )
            if address:
                parts.append(f"Official address: {address}.")
            if parts:
                return " ".join(parts)
            return "I don't have enough information about the library location."

        # General "what info is available" questions.
        if any(w in text for w in ("information", "info", "available", "what", "介绍")):
            if branches:
                return (
                    f"Available library information for {uni_name}: "
                    f"main branches — {', '.join(branches)}; "
                    f"official address — {address}."
                )
            return "I don't have enough library information to share."

        # Matched as a library question, but the specific answer is unknown.
        if branches:
            return (
                "I don't have enough information for that specific question. "
                f"Known library branches: {', '.join(branches)}."
            )
        return "I don't have enough information about the library."
