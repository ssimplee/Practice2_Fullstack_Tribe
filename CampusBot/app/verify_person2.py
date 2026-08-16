"""Comprehensive verification of Person 2's Campus & Library skills.

Run from CampusBot/ folder (no Ollama needed):

    python -m app.verify_person2

Exercises: known facts, missing-information (no fabrication), routing
edge cases (campus must not steal library questions), and Chinese input.
"""

from __future__ import annotations

from app.llm import StaticBackend
from app.skills.registration_example import build_runtime


def _has(text: str, *needles: str) -> bool:
    t = text.lower()
    return all(n.lower() in t for n in needles)


def _not_has(text: str, *needles: str) -> bool:
    t = text.lower()
    return not any(n.lower() in t for n in needles)


# (name, question, expected_skill, response_check)
CASES = [
    # --- Campus: known facts ---
    ("campus motto", "What is Shenzhen University's motto?",
     "campus", lambda s: _has(s, "self-reliance", "self-discipline")),
    ("campus founded", "When was Shenzhen University founded?",
     "campus", lambda s: _has(s, "1983")),
    ("campuses", "What are Shenzhen University's two campuses?",
     "campus", lambda s: _has(s, "Yuehai", "Lihu")),
    ("abbreviation", "What is SZU's abbreviation?",
     "campus", lambda s: _has(s, "SZU")),

    # --- Library: known facts ---
    ("library where", "Where is Shenzhen University Library?",
     "library", lambda s: _has(s, "Nanhai Avenue")),
    ("library info", "What library information is available?",
     "library", lambda s: _has(s, "North Library")),

    # --- Missing information: must NOT fabricate ---
    ("president (no fabrication)", "Who is the current president of Shenzhen University?",
     "campus", lambda s: _has(s, "don't have enough") and _not_has(s, "Nanhai Avenue")),
    ("international office (no fabrication)", "Where is Shenzhen University's International Office?",
     "campus", lambda s: _has(s, "don't have enough") and _not_has(s, "Nanhai Avenue")),
    ("ranking (no fabrication)", "What is Shenzhen University's QS ranking?",
     "campus", lambda s: _has(s, "don't have enough")),

    # --- Routing edge cases ---
    ("library not stolen by campus", "Where is the university library?",
     "library", lambda s: _has(s, "Nanhai Avenue")),
    ("translate routes to translation", "Translate welcome into Chinese.",
     "translation", lambda s: True),
    ("international office unmatched", "Where is the International Office?",
     None, lambda s: True),

    # --- Runtime-level ---
    ("empty message", "   ",
     None, lambda s: True),  # status checked separately

    # --- Chinese ---
    ("chinese founded", "深圳大学是哪一年成立的？",
     "campus", lambda s: _has(s, "1983")),
]


def main() -> None:
    runtime = build_runtime(llm=StaticBackend("mock-response"))
    passed = 0
    failed = 0

    for name, question, expected_skill, check in CASES:
        result = runtime.execute("user01", question)
        skill = result["skill"]
        status = result["status"]
        response = result["response"]

        # Skill expectation (None means unmatched/invalid)
        if expected_skill is None:
            skill_ok = skill is None and status in ("unmatched", "invalid_request")
        else:
            skill_ok = skill == expected_skill and status == "success"

        # Response content check
        resp_ok = check(response)

        ok = skill_ok and resp_ok
        mark = "PASS" if ok else "FAIL"
        if ok:
            passed += 1
        else:
            failed += 1

        print(f"[{mark}] {name}")
        print(f"        Q      : {question}")
        print(f"        skill  : {skill}  status: {status}")
        print(f"        answer : {response[:110]}")
        if not ok:
            print(f"        expect skill={expected_skill}; skill_ok={skill_ok} resp_ok={resp_ok}")
        print()

    print("=" * 60)
    print(f"RESULT: {passed} passed, {failed} failed, {passed + failed} total")
    print("ALL GOOD" if failed == 0 else "SOME TESTS FAILED")


if __name__ == "__main__":
    main()
