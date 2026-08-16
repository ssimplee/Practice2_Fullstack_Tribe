"""Translation Skill — translate text between languages.

Person 3 deliverable. Implements the common Skill interface defined by
Person 1 in app/skills/base.py.

Design notes
------------
* General-purpose: calls the LLM backend for actual translation, so any
  text/language pair is supported (unlike a fixed dictionary).
* Testable: accepts an injectable LLMBackend; tests use StaticBackend so
  no Ollama is required.
* Routing: keyword-based; defers explicit summary requests to SummarySkill.
* Failure behaviour: if no target language or no source text can be
  parsed, the skill returns a clear prompt instead of calling the LLM.
"""

from __future__ import annotations

import re

from app.llm import LLMBackend, OllamaBackend
from app.skills.base import Skill


# Keywords that signal a translation request.
_TRANSLATE_KEYWORDS = (
    "translate", "translation",
    "翻译",
)

# Keywords that signal a summary request — defer to SummarySkill.
_DEFER_KEYWORDS = (
    "summarize", "summarise", "summary", "总结", "摘要",
)

# Target language mapping (normalised label -> display name).
_LANGUAGE_MAP = {
    "chinese": "Chinese",
    "中文": "Chinese",
    "汉语": "Chinese",
    "english": "English",
    "英文": "English",
    "英语": "English",
}

# Quote patterns for extracting the source text.
_QUOTE_RE = re.compile(
    r'["\']([^"\']+)["\']'          # "..." or '...'
    r'|[「『]([^」』]+)[」』]'        # Chinese quotes
)


def _detect_target_language(text: str) -> str | None:
    """Return the target language name or None if not found."""
    lower = text.lower()
    # English cues
    for cue in ("into chinese", "to chinese", "in chinese"):
        if cue in lower:
            return "Chinese"
    for cue in ("into english", "to english", "in english"):
        if cue in lower:
            return "English"
    # Chinese cues
    if "中文" in text:
        return "Chinese"
    if "英文" in text or "英语" in text:
        return "English"
    return None


def _extract_source_text(message: str) -> str | None:
    """Extract the text to translate from the user message.

    Tries quoted text first, then falls back to patterns like
    ``translate ... into ...`` and ``把 ... 翻译``.
    """
    # 1) Quoted text (English or Chinese quotes).
    for match in _QUOTE_RE.finditer(message):
        return (match.group(1) or match.group(2)).strip()

    # 2) "translate <text> into/to <language>"
    m = re.search(
        r"translate\s+(.+?)\s+(?:into|to|in)\s+",
        message,
        re.IGNORECASE,
    )
    if m:
        return m.group(1).strip()

    # 3) Chinese pattern: 把<text>翻译 / 翻译<text>成
    m = re.search(r"把(.+?)翻译", message)
    if m:
        return m.group(1).strip()
    m = re.search(r"翻译(.+?)成", message)
    if m:
        return m.group(1).strip()

    return None


class TranslationSkill(Skill):
    """Translates text between languages using an LLM backend."""

    name = "translation"

    def __init__(self, llm: LLMBackend | None = None) -> None:
        self._llm = llm or OllamaBackend()

    def matches(self, message: str) -> bool:
        text = (message or "").lower()
        if not text.strip():
            return False
        # Defer to SummarySkill when summary intent is present.
        if any(w in text for w in _DEFER_KEYWORDS):
            return False
        return any(k in text for k in _TRANSLATE_KEYWORDS)

    def execute(self, message: str) -> str:
        target = _detect_target_language(message)
        if not target:
            return (
                "Please specify the target language, for example: "
                "Translate \"hello\" into Chinese."
            )

        source = _extract_source_text(message)
        if not source:
            return (
                "Please provide the text to translate, for example: "
                "Translate \"Welcome\" into Chinese."
            )

        prompt = (
            f"Translate the following text into {target}. "
            f"Reply with only the translation, no explanation.\n\n"
            f"Text: {source}"
        )
        return self._llm.ask(prompt)
