"""Deterministic guardrails for obvious unsafe and prompt-injection requests."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Pattern


@dataclass(frozen=True)
class GuardrailDecision:
    allowed: bool
    rule: str | None = None
    reason: str | None = None


_DEFAULT_RULES: tuple[tuple[str, Pattern[str], str], ...] = (
    (
        "instruction_override",
        re.compile(
            r"\b(?:ignore|disregard|forget|override)\b.{0,50}"
            r"\b(?:previous|prior|system|developer|all)\b.{0,30}"
            r"\b(?:instruction|instructions|prompt|rules?)\b",
            re.IGNORECASE | re.DOTALL,
        ),
        "The request attempts to override existing instructions.",
    ),
    (
        "prompt_exfiltration",
        re.compile(
            r"\b(?:show|reveal|display|print|repeat|leak|expose)\b.{0,50}"
            r"\b(?:system|developer|hidden|internal)\b.{0,20}"
            r"\b(?:prompt|instructions?|message|rules?)\b",
            re.IGNORECASE | re.DOTALL,
        ),
        "The request attempts to expose hidden instructions.",
    ),
    (
        "private_data_exfiltration",
        re.compile(
            r"\b(?:show|reveal|display|print|leak|expose|send)\b.{0,50}"
            r"\b(?:private|confidential|secret|personal)\b.{0,20}"
            r"\b(?:data|information|records?|credentials?|keys?|passwords?)\b",
            re.IGNORECASE | re.DOTALL,
        ),
        "The request attempts to expose private or confidential data.",
    ),
    (
        "safety_bypass",
        re.compile(
            r"\b(?:bypass|disable|evade|circumvent|remove)\b.{0,40}"
            r"\b(?:safety|security|guardrail|filter|restriction|permission)s?\b",
            re.IGNORECASE | re.DOTALL,
        ),
        "The request attempts to bypass a safety or security control.",
    ),
)


class Guardrail:
    """Block explicit injection, exfiltration, and safety-bypass requests."""

    def __init__(
        self,
        rules: tuple[tuple[str, Pattern[str], str], ...] | None = None,
    ) -> None:
        self._rules = _DEFAULT_RULES if rules is None else rules

    def evaluate(self, message: str) -> GuardrailDecision:
        """Evaluate a request without retaining its content."""

        for name, pattern, reason in self._rules:
            if pattern.search(message or ""):
                return GuardrailDecision(False, name, reason)
        return GuardrailDecision(True)

    def is_blocked(self, message: str) -> bool:
        return not self.evaluate(message).allowed
