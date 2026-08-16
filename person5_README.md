# Person 5 — Automated Testing and API/Web Integration

This implementation follows the lab PDF and `WORK_ALLOCATION.md`.

## API and browser integration

`CampusBot/serve.py` is the new application entry point. The existing Windows
launcher automatically chooses it when present, so `Start CampusBot.cmd` now
uses the complete flow:

```text
Browser/API -> Guardrail -> Runtime -> Router -> Skill -> Audit -> Response
```

The browser's original `{ "message": "..." }` request remains supported. API
clients may also provide `user`:

```json
{
  "user": "user01",
  "message": "Where is the library?"
}
```

Responses contain `request_id`, `skill`, `status`, `response`, and
`duration_ms`. The browser displays the selected Skill and labels blocked
requests as Guardrail results.

## Automated validation

`CampusBot/tests/test_api.py` checks:

- health and browser-page availability;
- backward-compatible browser requests;
- Campus, Library, and Translation routing;
- structured unmatched responses;
- the PDF prompt-injection example;
- privacy-safe audit creation;
- API input validation.

Run the complete deterministic suite with `Run Tests.cmd`. These tests inject
a static LLM backend and therefore do not require Ollama.
