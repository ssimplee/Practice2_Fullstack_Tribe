"""Campus Skill — factual questions about Shenzhen University itself.

Person 2 deliverable. Implements the common Skill interface defined by
Person 1 in app/skills/base.py:

    class Skill(ABC):
        name: str = ""
        def matches(self, message: str) -> bool: ...
        def execute(self, message: str) -> str: ...

Design notes
------------
* Deterministic: answers are built from knowledge.json, so this skill works
  and is testable WITHOUT Ollama (the lab recommends deterministic tests).
* Missing-information behaviour: if the question is clearly about the
  university but the specific fact is not in the knowledge base, the skill
  says it does not have enough information instead of inventing an answer.
* Routing: matches() is keyword-based and deliberately defers explicit
  translate/summarise requests to Person 3's skills.
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


# Keywords that signal a campus / university fact question.
_CAMPUS_KEYWORDS = (
    "motto", "founded", "established", "campus", "campuses",
    "university", "szu", "shenzhen university",
    "深圳大学", "校区", "校训", "成立", "建立",
)

# Topics that match "about the university" but are NOT in the knowledge base.
# The skill must admit it lacks the information instead of inventing one.
_UNAVAILABLE_TOPICS = (
    "president", "chancellor", "vice chancellor", "rector", "principal",
    "ranking", "qs", "tuition", "fee", "acceptance rate",
    "international office", "student number", "enrollment", "admission",
    "校长", "排名", "学费", "录取",
)

# Intents this skill must defer to other skills so it does not steal them
# (campus matches on "university", which also appears in library questions).
_DEFER_KEYWORDS = (
    "library", "libraries", "图书馆", "book", "borrow",
    "translate", "summar", "summary",
)


class CampusSkill(Skill):
    """Answers factual questions about Shenzhen University."""

    name = "campus"

    def matches(self, message: str) -> bool:
        text = (message or "").lower()
        if not text.strip():
            return False
        # Defer to Library / Translation / Summary skills when their intent
        # is present, otherwise "university" would steal library questions.
        if any(w in text for w in _DEFER_KEYWORDS):
            return False
        return any(k in text for k in _CAMPUS_KEYWORDS)

    def execute(self, message: str) -> str:
        knowledge = _load_knowledge()
        uni = knowledge.get("university", {})
        uni_name = uni.get("name", "Shenzhen University")
        text = (message or "").lower()

        # 1) Clearly about the university, but the fact is unavailable.
        if any(w in text for w in _UNAVAILABLE_TOPICS):
            return (
                f"I don't have enough information to answer that about "
                f"{uni_name}. Please check the official university website."
            )

        # 2) Known facts.
        if "motto" in text or "校训" in text:
            return f"{uni_name}'s motto is: {uni.get('motto')}."

        if (
            "founded" in text
            or "established" in text
            or "成立" in text
            or "建立" in text
        ):
            return f"{uni_name} was founded in {uni.get('established')}."

        if "campus" in text or "校区" in text:
            campuses = uni.get("campuses", [])
            if not campuses:
                return "I don't have enough information about the campuses."
            if len(campuses) == 2:
                listed = " and ".join(campuses)
            else:
                listed = ", ".join(campuses)
            return (
                f"{uni_name} has {len(campuses)} campuses: {listed}."
            )

        if "abbreviation" in text or "short name" in text:
            return f"The abbreviation of {uni_name} is {uni.get('abbreviation')}."

        # 3) Matched as a campus question, but the specific fact is unknown.
        return (
            "I don't have enough information to answer that. "
            f"I can tell you about {uni_name}'s motto, founding year, "
            "campuses, and abbreviation."
        )
