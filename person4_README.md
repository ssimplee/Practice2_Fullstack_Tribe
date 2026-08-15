# Person 4 — Governance and Audit Logging

This implementation follows the lab PDF and `WORK_ALLOCATION.md` and provides
both recommended Person 4 mechanisms.

## Implemented mechanisms

- `Guardrail` runs before Runtime execution and blocks obvious instruction
  overrides, hidden-prompt extraction, private-data extraction, and attempts
  to disable safety controls.
- `AuditLogger` writes JSON Lines records containing timestamp, request ID,
  user, selected Skill, status, duration, and matched guardrail rule.
- Request and response content are deliberately excluded from audit records.
- `GovernedRuntime` wraps Person 1's
  `execute(user, message) -> {skill, status, response}` contract and audits
  successful, blocked, unmatched, and failed results.

## Runtime integration

Person 1–3 are present on this branch. Use the integrated factory:

```python
from app.skills.registration_example import build_governed_runtime

agent = build_governed_runtime()
result = agent.execute("user01", "Where is the library?")
```

The factory registers the Campus, Library, Translation, Summary, and bonus
Composition Skills, then wraps their Runtime with the Guardrail and Audit
Logger. The default audit path is `CampusBot/logs/audit.jsonl`.

Person 5 should make `/chat` call `agent.execute(...)` so the final flow is:

```text
Request -> Guardrail -> Runtime -> Skill -> Result -> Audit Log
```

## Verification

Run all tests from the repository root:

```text
Run Tests.cmd
```

Generate observable allowed/blocked output and audit evidence from
`CampusBot/`:

```text
..\runtime\python\python.exe app\verify_person4.py
```
