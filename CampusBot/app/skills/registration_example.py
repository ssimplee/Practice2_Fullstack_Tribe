"""EXAMPLE — how to register all skills into Person 1's Runtime.

This is NOT a module that the app imports automatically. It is a snippet to
hand to Person 1 / Person 5 when they wire the Runtime into serve.py (or
main.py). Persons 2 and 3 register their skills here.

Quick self-check (run from the CampusBot/ folder, no Ollama needed):

    cd CampusBot
    python -c "from app.skills.registration_example import build_runtime; \
from app.llm import StaticBackend; \
r=build_runtime(llm=StaticBackend('mock')); \
import json; print(json.dumps(r.execute('user01','Translate \"hi\" into Chinese.'),ensure_ascii=False,indent=2))"
"""

from __future__ import annotations

from pathlib import Path

from app.governance import AuditLogger, GovernedRuntime, Guardrail
from app.llm import LLMBackend, OllamaBackend
from app.runtime.runtime import Runtime
from app.skills.campus import CampusSkill
from app.skills.composition import CompositionSkill
from app.skills.library import LibrarySkill
from app.skills.summary import SummarySkill
from app.skills.translation import TranslationSkill


def build_runtime(llm: LLMBackend | None = None) -> Runtime:
    """Build a Runtime pre-loaded with all skills.

    Parameters
    ----------
    llm : LLMBackend, optional
        Shared LLM backend injected into Translation, Summary, and
        Composition skills. Defaults to ``OllamaBackend()`` when omitted.
        Tests should pass a ``StaticBackend`` so no Ollama is required.
    """
    runtime = Runtime()
    # CompositionSkill is registered first: it only matches when all three
    # intents (campus + summary + translation) are present, so it won't
    # steal single-intent requests.
    runtime.register_skill(CompositionSkill(llm))
    runtime.register_skill(CampusSkill())
    runtime.register_skill(LibrarySkill())
    runtime.register_skill(TranslationSkill(llm))
    runtime.register_skill(SummarySkill(llm))
    return runtime


def build_governed_runtime(
    llm: LLMBackend | None = None,
    audit_path: str | Path | None = None,
    guardrail: Guardrail | None = None,
) -> GovernedRuntime:
    """Build the complete Person 1–4 execution flow.

    Guardrails run before Person 1's Runtime. Allowed, blocked, unmatched,
    and failed results are audited without retaining request/response text.
    """

    if audit_path is None:
        project_root = Path(__file__).resolve().parents[2]
        audit_path = project_root / "logs" / "audit.jsonl"
    return GovernedRuntime(
        runtime=build_runtime(llm),
        audit_logger=AuditLogger(audit_path),
        guardrail=guardrail,
    )


if __name__ == "__main__":
    demo = [
        "What is Shenzhen University's motto?",
        "When was Shenzhen University founded?",
        "What are Shenzhen University's two campuses?",
        "Where is Shenzhen University Library?",
        "What library information is available?",
        "Who is the current president of Shenzhen University?",  # missing info
        "Where is the International Office?",                    # unmatched
        'Translate "Welcome to Shenzhen University" into Chinese.',
        "Summarize: Shenzhen University was founded in 1983 and has two campuses.",
        "Tell me briefly when Shenzhen University was founded and answer in Chinese.",
    ]
    runtime = build_runtime(llm=OllamaBackend())
    for q in demo:
        print(f"\nQ: {q}")
        print(runtime.execute("user01", q))
