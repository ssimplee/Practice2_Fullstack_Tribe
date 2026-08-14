"""Step-by-step verification of Person 3's Translation, Summary, and
Composition skills.

Run from CampusBot/ folder (no Ollama needed):

    python -m app.verify_person3

Exercises: translation routing, translation success, missing-language
prompt, missing-source prompt, Chinese translation, summary routing,
summary success, no-text prompt, Chinese summary, LLM failure graceful
degradation, and Skill Composition (Campus → Summary → Translation).
"""

from __future__ import annotations

from app.llm import StaticBackend
from app.skills.registration_example import build_runtime


class _FailingBackend:
    """LLM backend stub that always raises, for error-path verification."""

    def ask(self, prompt: str) -> str:
        raise RuntimeError("intentional failure for verification")


def _has(text: str, *needles: str) -> bool:
    t = text.lower()
    return all(n.lower() in t for n in needles)


# (name, question, expected_skill, response_check)
CASES = [
    # --- Translation: success ---
    ("translate en->zh (quoted)", 'Translate "Welcome to Shenzhen University" into Chinese.',
     "translation", lambda s: True),
    ("translate en->zh (no quotes)", "Translate welcome into Chinese.",
     "translation", lambda s: True),
    ("translate zh->en", '把"深圳大学"翻译成英文',
     "translation", lambda s: True),

    # --- Translation: prompts (no LLM call) ---
    ("translate no target language", 'Translate "hello"',
     "translation", lambda s: _has(s, "target language")),
    ("translate no source text", "Translate into Chinese.",
     "translation", lambda s: _has(s, "provide")),

    # --- Summary: success ---
    ("summary success", "Summarize: Shenzhen University was founded in 1983 and has two campuses.",
     "summary", lambda s: True),
    ("summary chinese", "总结：深圳大学成立于1983年，有两个校区。",
     "summary", lambda s: True),

    # --- Summary: prompt (no LLM call) ---
    ("summary no text (placeholder)", "Summarize this.",
     "summary", lambda s: _has(s, "provide")),
    ("summary no text (empty)", "Summarize:",
     "summary", lambda s: _has(s, "provide")),
]


def main() -> None:
    print("Person 3 verification — Translation & Summary skills\n")

    # --- Deterministic backend tests ---
    runtime = build_runtime(llm=StaticBackend("mock-llm-response"))
    passed = 0
    failed = 0

    for name, question, expected_skill, check in CASES:
        result = runtime.execute("user01", question)
        skill = result["skill"]
        status = result["status"]
        response = result["response"]

        skill_ok = skill == expected_skill and status == "success"
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

    # --- LLM failure graceful degradation ---
    print("=" * 60)
    print("LLM failure test (TranslationSkill + FailingBackend):")
    fail_runtime = build_runtime(llm=_FailingBackend())
    r = fail_runtime.execute("user01", 'Translate "hello" into Chinese.')
    fail_ok = r["skill"] == "translation" and r["status"] == "error"
    mark = "PASS" if fail_ok else "FAIL"
    print(f"[{mark}] translation LLM failure -> status={r['status']}")
    if fail_ok:
        passed += 1
    else:
        failed += 1

    r = fail_runtime.execute("user01", "Summarize: some text here")
    fail_ok = r["skill"] == "summary" and r["status"] == "error"
    mark = "PASS" if fail_ok else "FAIL"
    print(f"[{mark}] summary LLM failure -> status={r['status']}")
    if fail_ok:
        passed += 1
    else:
        failed += 1

    # --- Routing: no stealing ---
    print("\n" + "=" * 60)
    print("Routing edge cases (no skill stealing):")
    edge_cases = [
        ("campus not stolen", "What is Shenzhen University's motto?", "campus"),
        ("library not stolen", "Where is the library?", "library"),
        ("composition doesn't steal campus-only",
         "When was Shenzhen University founded?", "campus"),
        ("composition doesn't steal translation-only",
         'Translate "hello" into Chinese.', "translation"),
        ("composition doesn't steal summary-only",
         "Summarize: some text here", "summary"),
    ]
    for name, q, expected in edge_cases:
        r = runtime.execute("user01", q)
        ok = r["skill"] == expected
        mark = "PASS" if ok else "FAIL"
        print(f"[{mark}] {name}: skill={r['skill']}")
        if ok:
            passed += 1
        else:
            failed += 1

    # --- Skill Composition (Bonus) ---
    print("\n" + "=" * 60)
    print("Skill Composition (Campus → Summary → Translation):")

    def _composition_llm(prompt: str) -> str:
        lower = prompt.lower()
        if "summarise" in lower or "summarize" in lower:
            return "Shenzhen University was founded in 1983."
        if "translate" in lower:
            return "深圳大学成立于1983年。"
        return "mock"

    comp_runtime = build_runtime(llm=StaticBackend(_composition_llm))

    # Composition routing + success
    comp_q = ("Tell me briefly when Shenzhen University was founded "
              "and answer in Chinese.")
    r = comp_runtime.execute("user01", comp_q)
    comp_ok = (r["skill"] == "composition" and r["status"] == "success"
               and r["response"] == "深圳大学成立于1983年。")
    mark = "PASS" if comp_ok else "FAIL"
    print(f"[{mark}] composition chain success")
    print(f"        Q      : {comp_q}")
    print(f"        skill  : {r['skill']}  status: {r['status']}")
    print(f"        answer : {r['response']}")
    if comp_ok:
        passed += 1
    else:
        failed += 1

    # Composition LLM failure
    comp_fail_runtime = build_runtime(llm=_FailingBackend())
    r = comp_fail_runtime.execute("user01", comp_q)
    comp_fail_ok = r["skill"] == "composition" and r["status"] == "error"
    mark = "PASS" if comp_fail_ok else "FAIL"
    print(f"[{mark}] composition LLM failure -> status={r['status']}")
    if comp_fail_ok:
        passed += 1
    else:
        failed += 1

    print("\n" + "=" * 60)
    print(f"RESULT: {passed} passed, {failed} failed, {passed + failed} total")
    print("ALL GOOD" if failed == 0 else "SOME TESTS FAILED")


if __name__ == "__main__":
    main()
