"""Summary Skill — summarise provided text.

Person 3 deliverable. Implements the common Skill interface defined by
Person 1 in app/skills/base.py.

Design notes
------------
* General-purpose: calls the LLM backend to produce a concise summary of
  the text the user supplies in the message.
* Testable: accepts an injectable LLMBackend; tests use StaticBackend so
  no Ollama is required.
* Routing: keyword-based; does not defer (summary intent is specific
  enough that it won't be stolen by Campus/Library skills, which already
  defer on "summar"/"summary").
* Failure behaviour: if no text to summarise can be extracted, the skill
  returns a clear prompt instead of calling the LLM.
"""

from __future__ import annotations

import re

from app.llm import LLMBackend, OllamaBackend
from app.skills.base import Skill


# Keywords that signal a summary request.
_SUMMARY_KEYWORDS = (
    "summarize", "summarise", "summary",
    "总结", "摘要", "概括",
    "briefly", "in short", "简短", "简要",
)

# Command prefixes to strip when extracting the text to summarise.
_COMMAND_PREFIXES = (
    "summarize:", "summarise:", "summary:",
    "summarize", "summarise",
    "总结：", "总结:", "总结一下：", "总结一下:",
    "总结一下", "总结",
    "摘要：", "摘要:", "摘要",
    "概括：", "概括:", "概括",
)


class SummarySkill(Skill):
    """Summarises user-provided text using an LLM backend."""

    name = "summary"

    def __init__(self, llm: LLMBackend | None = None) -> None:
        self._llm = llm or OllamaBackend()

    def matches(self, message: str) -> bool:
        text = (message or "").lower()
        if not text.strip():
            return False
        return any(k in text for k in _SUMMARY_KEYWORDS)

    def execute(self, message: str) -> str:
        source = _extract_text_to_summarise(message)
        if not source:
            return (
                "Please provide the text to summarise, for example: "
                "Summarize: <your text here>"
            )

        prompt = (
            "Summarise the following text in one or two sentences. "
            "Reply with only the summary, no explanation.\n\n"
            f"Text: {source}"
        )
        return self._llm.ask(prompt)


# Words that indicate the user did not actually provide text to summarise.
_PLACEHOLDER_WORDS = {
    "this", "that", "it", "these", "those",
    "这", "这个", "那个", "它",
}


def _is_placeholder(text: str) -> bool:
    """Return True when *text* is too short or a known placeholder word."""
    cleaned = text.strip().rstrip(".。!！?？")
    return cleaned.lower() in _PLACEHOLDER_WORDS or len(cleaned) < 3


def _extract_text_to_summarise(message: str) -> str | None:
    """Extract the text to summarise from the user message.

    Strips known command prefixes/keywords and returns the remaining
    text. Returns None if nothing meaningful is left.
    """
    text = message.strip()

    # Try stripping a colon-prefixed command first (e.g. "Summarize: ...").
    colon_match = re.match(
        r"^\s*(summar(?:ize|ise|y)|summary|总结一下|总结|摘要|概括)\s*[:：]\s*(.+)$",
        text,
        re.IGNORECASE,
    )
    if colon_match:
        result = colon_match.group(2).strip()
        return None if _is_placeholder(result) else (result or None)

    # Strip leading command keyword without colon.
    lower = text.lower()
    for prefix in _COMMAND_PREFIXES:
        if lower.startswith(prefix):
            result = text[len(prefix):].strip()
            return None if _is_placeholder(result) else (result or None)

    # If the keyword appears mid-sentence (e.g. "briefly summarise ..."),
    # take everything after the keyword.
    for kw in ("summarize", "summarise", "总结一下", "总结", "摘要", "概括"):
        idx = lower.find(kw)
        if idx != -1:
            result = text[idx + len(kw):].strip()
            return None if _is_placeholder(result) else (result or None)

    return None
