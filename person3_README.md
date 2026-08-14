## Person 3 - Translation, Summary, and Composition Skills

Implemented two general-purpose Skills plus an LLM backend abstraction
layer and a bonus Composition skill on top of Person 1's Runtime and
`Skill` interface.

### Implemented
- `TranslationSkill` (`app/skills/translation.py`)
  - Translates text between languages (English ↔ Chinese)
  - Parses quoted text or `translate ... into ...` patterns for source
  - Detects target language from cues like `into Chinese`, `翻译成英文`
  - Returns a clear prompt when source text or target language is missing
    (no LLM call)
- `SummarySkill` (`app/skills/summary.py`)
  - Summarises user-provided text in one or two sentences
  - Strips command prefixes (`Summarize:`, `总结：`, etc.) to extract text
  - Filters placeholder words (`this`, `that`, `这`) — returns a prompt
    when no real text is supplied (no LLM call)
- `CompositionSkill` (`app/skills/composition.py`) — bonus
  - Chains Campus → Summary → Translation for multi-intent requests
  - Only matches when all three intents are present, so single-intent
    requests fall through to their respective skills
- `LLMBackend` abstraction (`app/llm/`)
  - `LLMBackend` protocol with a single `ask(prompt) -> str` method
  - `OllamaBackend` — calls the local Ollama API (reuses `main.py` logic)
  - `StaticBackend` — deterministic stub for tests (string or callable)
- Routing safety
  - Translation defers explicit summary requests to SummarySkill
  - Both skills are registered after Campus/Library so they don't steal
    fact queries

### Files Added
- `CampusBot/app/llm/__init__.py`
- `CampusBot/app/llm/backend.py`
- `CampusBot/app/skills/translation.py`
- `CampusBot/app/skills/summary.py`
- `CampusBot/app/skills/composition.py`
- `CampusBot/tests/test_translation_summary.py`
- `CampusBot/app/verify_person3.py`
- `runtime/python/Lib/site-packages/sitecustomize.py` (fixes embedded
  Python `._pth` path restriction so `app` is importable in tests)

### Files Modified
- `CampusBot/app/skills/registration_example.py` — registers all five
  skills; `build_runtime(llm=None)` accepts an injectable backend
- `CampusBot/tests/test_skills.py` — updated translate test to expect
  `translation` routing; injected `StaticBackend` for determinism
- `CampusBot/app/skills/campus.py` — added Chinese defer keywords
  (`翻译`, `总结`, `摘要`, `概括`)
- `CampusBot/app/skills/library.py` — same Chinese defer keywords
- `CampusBot/app/verify_person2.py` — updated translate expectation;
  injected `StaticBackend`

### Interface Contract (from Person 1)
Each skill implements `app/skills/base.py`:
- `name: str`
- `matches(message: str) -> bool`
- `execute(message: str) -> str`

The `SkillRouter` selects the first skill whose `matches()` is `True`.
Registration order in `build_runtime()`:

```
CompositionSkill   (first — only matches all three intents)
CampusSkill
LibrarySkill
TranslationSkill
SummarySkill       (last)
```

### Verified Scenarios (no Ollama needed)
Run from `CampusBot/`:
```bash
python -m app.verify_person3
```
| Question | Skill | Status |
|---|---|---|
| Translate "Welcome to SZU" into Chinese. | translation | success |
| 把"深圳大学"翻译成英文 | translation | success |
| Translate "hello" (no target language) | translation | success (prompt) |
| Translate into Chinese. (no source text) | translation | success (prompt) |
| Summarize: SZU was founded in 1983... | summary | success |
| 总结：深圳大学成立于1983年... | summary | success |
| Summarize this. (no text) | summary | success (prompt) |
| Tell me briefly when SZU was founded and answer in Chinese. | composition | success |
| What is SZU's motto? (campus-only, not stolen) | campus | success |
| Translate "hello" into Chinese. (not stolen by composition) | translation | success |

LLM failure graceful degradation:
| Scenario | Skill | Status |
|---|---|---|
| Translation with FailingBackend | translation | error |
| Summary with FailingBackend | summary | error |
| Composition with FailingBackend | composition | error |

### Registration (for Person 1 / Person 5)
```python
from app.skills.registration_example import build_runtime
from app.llm import StaticBackend  # for tests

# Production (uses Ollama):
runtime = build_runtime()

# Tests (deterministic, no Ollama):
runtime = build_runtime(llm=StaticBackend("mock-response"))

result = runtime.execute("user01", 'Translate "hello" into Chinese.')
```

### Test Suite
Run from `CampusBot/`:
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```
- 35 tests total, 0 failures
- `test_skills.py` — 14 tests (Person 2's campus/library + routing)
- `test_translation_summary.py` — 21 tests (translation, summary,
  composition, routing edge cases, LLM failure)

### Notes for Integration
- Person 4 (Governance): the `LLMBackend` abstraction can be reused if
  the guardrail needs to call the model for content classification.
- Person 5 (API/Web): call `build_runtime()` once at startup and use
  `runtime.execute(user, message)` in the `/chat` handler. Inject
  `StaticBackend` in tests.
- All tests use `StaticBackend` — no Ollama required for `Run Tests.cmd`.
