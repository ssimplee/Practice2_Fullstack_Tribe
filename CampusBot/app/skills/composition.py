"""Composition Skill — chain Campus → Summary → Translation.

Person 3 bonus deliverable. Implements the common Skill interface.

When a single request carries all three intents — a campus fact query,
a summary request, and a translation request — this skill executes them
in sequence:

    CampusSkill.execute(message)
        ↓  (factual answer)
    LLM summarise
        ↓  (brief summary)
    LLM translate
        ↓  (translated summary)

Example request:

    Tell me briefly when Shenzhen University was founded and answer in Chinese.

Routing: registered FIRST so it gets priority for composition requests.
``matches()`` requires all three intents, so single-intent requests
(campus-only, translate-only, summary-only) fall through to the
respective skills.
"""

from __future__ import annotations

from app.llm import LLMBackend, OllamaBackend
from app.skills.base import Skill
from app.skills.campus import CampusSkill
from app.skills.translation import _detect_target_language


# Campus-fact signals.
_CAMPUS_SIGNALS = (
    "university", "szu", "shenzhen university",
    "深圳大学", "campus", "motto", "founded", "established",
    "校区", "校训", "成立", "建立",
)

# Summary signals.
_SUMMARY_SIGNALS = (
    "briefly", "summarize", "summarise", "summary", "short",
    "总结", "简短", "简要", "概括",
)

# Translation signals.
_TRANSLATION_SIGNALS = (
    "in chinese", "in english", "into chinese", "into english",
    "to chinese", "to english",
    "用中文", "用英文", "翻译成", "成中文", "成英文",
)


class CompositionSkill(Skill):
    """Chains Campus → Summary → Translation for multi-intent requests."""

    name = "composition"

    def __init__(
        self,
        llm: LLMBackend | None = None,
        campus_skill: CampusSkill | None = None,
    ) -> None:
        self._llm = llm or OllamaBackend()
        self._campus = campus_skill or CampusSkill()

    def matches(self, message: str) -> bool:
        text = (message or "").lower()
        if not text.strip():
            return False
        has_campus = any(s in text for s in _CAMPUS_SIGNALS)
        has_summary = any(s in text for s in _SUMMARY_SIGNALS)
        has_translation = any(s in text for s in _TRANSLATION_SIGNALS)
        return has_campus and has_summary and has_translation

    def execute(self, message: str) -> str:
        # Step 1 — Campus fact.
        campus_answer = self._campus.execute(message)

        # Step 2 — Summarise the campus answer.
        summary_prompt = (
            "Summarise the following answer in one short sentence. "
            "Reply with only the summary.\n\n"
            f"{campus_answer}"
        )
        summary = self._llm.ask(summary_prompt)

        # Step 3 — Translate the summary.
        target = _detect_target_language(message) or "Chinese"
        translate_prompt = (
            f"Translate the following into {target}. "
            "Reply with only the translation.\n\n"
            f"{summary}"
        )
        return self._llm.ask(translate_prompt)
