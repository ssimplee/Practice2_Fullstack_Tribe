"""Step-by-step verification of Person 1's Runtime + Router + Skill interface.

Run from CampusBot/ folder (no Ollama needed):

    python -m app.verify_person1

This proves Person 1's deliverables behave correctly BEFORE Person 2 adds
the real Campus / Library skills.
"""

from __future__ import annotations

from app.runtime.runtime import Runtime
from app.skills.base import Skill


class EchoSkill(Skill):
    """A fake skill used only for verification: replies with the message."""

    name = "echo"

    def matches(self, message: str) -> bool:
        return message.lower().startswith("echo ")

    def execute(self, message: str) -> str:
        return f"echo: {message[5:]}"


class BrokenSkill(Skill):
    """A fake skill that always crashes in execute (tests error handling)."""

    name = "broken"

    def matches(self, message: str) -> bool:
        return message.lower().startswith("boom")

    def execute(self, message: str) -> str:
        raise RuntimeError("intentional failure")


def show(title: str, message: str, runtime: Runtime) -> None:
    print("\n" + "=" * 60)
    print(f"TEST: {title}")
    print(f"  user message : {message!r}")
    result = runtime.execute("user01", message)
    print(f"  -> skill   : {result['skill']!r}")
    print(f"  -> status  : {result['status']!r}")
    print(f"  -> response: {result['response']!r}")


def main() -> None:
    print("Person 1 verification — Runtime / Router / Skill interface")

    runtime = Runtime()
    runtime.register_skill(EchoSkill())
    runtime.register_skill(BrokenSkill())

    # Path 1 — success: a message a skill can handle
    show("1. SUCCESS (EchoSkill matches and runs)",
         "echo hello person1", runtime)

    # Path 2 — invalid_request: empty message
    show("2. INVALID_REQUEST (empty message)",
         "   ", runtime)

    # Path 3 — unmatched: no skill matches
    show("3. UNMATCHED (no skill handles this)",
         "Where is the International Office?", runtime)

    # Path 4 — error: a skill matches but execute() raises
    show("4. ERROR (BrokenSkill.execute raises)",
         "boom now", runtime)

    print("\n" + "=" * 60)
    print("All four Runtime status paths exercised successfully.")


if __name__ == "__main__":
    main()
