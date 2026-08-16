"""LLM backend abstraction for CampusBot skills.

Person 3 deliverable. Provides a common interface so that Translation and
Summary skills can call a language model while remaining testable without
Ollama (the lab recommends deterministic, mock-backed tests).

Classes
-------
LLMBackend    : Protocol with a single ask(prompt) -> str method.
OllamaBackend : Calls the local Ollama API (reuses main.py's logic).
StaticBackend : Deterministic stub that returns a canned response; used in
                tests so no network/Ollama is required.
"""

from __future__ import annotations

import os
from typing import Callable, Protocol, Union, runtime_checkable

import httpx


@runtime_checkable
class LLMBackend(Protocol):
    """Minimal LLM interface used by skills."""

    def ask(self, prompt: str) -> str:
        """Return the model's text response for *prompt*."""
        ...


class OllamaBackend:
    """LLM backend backed by the local Ollama service.

    Mirrors the request logic in ``main.py`` so skills get the same model
    behaviour as the original single-file prototype.
    """

    def __init__(
        self,
        url: str | None = None,
        model: str | None = None,
    ) -> None:
        self.url = url or os.getenv(
            "OLLAMA_URL", "http://127.0.0.1:11434/api/chat"
        )
        self.model = model or os.getenv("OLLAMA_MODEL", "qwen3:0.6b")

    def ask(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "think": False,
            "options": {
                "temperature": 0.0,
                "num_ctx": 4096,
                "seed": 42,
            },
        }

        response = httpx.post(self.url, json=payload, timeout=90)
        response.raise_for_status()

        answer = (
            response.json().get("message", {}).get("content", "").strip()
        )
        if not answer:
            raise RuntimeError("The model returned an empty response.")
        return answer


class StaticBackend:
    """Deterministic LLM stub for tests.

    *response* may be:
    - a ``str``  -> always returned as-is;
    - a ``callable`` -> invoked with the prompt, must return a ``str``.

    Example::

        backend = StaticBackend("translated text")
        backend = StaticBackend(lambda p: "summary" if "summ" in p else "translation")
    """

    def __init__(
        self, response: Union[str, Callable[[str], str]] = ""
    ) -> None:
        self._response = response

    def ask(self, prompt: str) -> str:
        if callable(self._response):
            return self._response(prompt)
        return self._response
