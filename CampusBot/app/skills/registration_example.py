"""EXAMPLE — how to register Person 2's skills into Person 1's Runtime.

This is NOT a module that the app imports automatically. It is a snippet to
hand to Person 1 / Person 5 when they wire the Runtime into serve.py (or
main.py). Person 3 will add TranslationSkill and SummarySkill to the same
list.

Quick self-check (run from the CampusBot/ folder, no Ollama needed):

    cd CampusBot
    python -c "from app.skills.registration_example import build_runtime; \
r=build_runtime(); import json; print(json.dumps(r.execute('user01','Where is the library?'),ensure_ascii=False,indent=2))"
"""

from __future__ import annotations

from app.runtime.runtime import Runtime
from app.skills.campus import CampusSkill
from app.skills.library import LibrarySkill


def build_runtime() -> Runtime:
    """Build a Runtime pre-loaded with Person 2's skills."""
    runtime = Runtime()
    runtime.register_skill(CampusSkill())
    runtime.register_skill(LibrarySkill())
    # Person 3 adds:
    # runtime.register_skill(TranslationSkill())
    # runtime.register_skill(SummarySkill())
    return runtime


if __name__ == "__main__":
    demo = [
        "What is Shenzhen University's motto?",
        "When was Shenzhen University founded?",
        "What are Shenzhen University's two campuses?",
        "Where is Shenzhen University Library?",
        "What library information is available?",
        "Who is the current president of Shenzhen University?",  # missing info
        "Where is the International Office?",                    # unmatched
    ]
    runtime = build_runtime()
    for q in demo:
        print(f"\nQ: {q}")
        print(runtime.execute("user01", q))
