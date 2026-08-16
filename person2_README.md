## Person 2 - Campus and Library Skills

Implemented two knowledge-based Skills on top of Person 1's Runtime and
`Skill` interface.

### Implemented
- `CampusSkill` (`app/skills/campus.py`)
  - Answers factual questions about Shenzhen University: motto, founding
    year, campuses, abbreviation
  - Reads facts from `knowledge.json` (deterministic, no Ollama required)
- `LibrarySkill` (`app/skills/library.py`)
  - Answers library location and available-information questions
  - Returns the main branches and official address from `knowledge.json`
- Missing-information handling
  - If a matched question asks for something not in the knowledge base
    (e.g. "Who is the president?"), the skill states that it lacks the
    information instead of inventing an official answer
- Routing safety
  - Both skills defer explicit translate/summarise requests to Person 3
  - Campus defers library-keyword questions to LibrarySkill (avoids the
    "university" keyword stealing library questions)

### Files Added
- `CampusBot/app/skills/campus.py`
- `CampusBot/app/skills/library.py`
- `CampusBot/app/skills/registration_example.py` (registration helper +
  self-check; hands the skill list to Person 1 / Person 5 for `serve.py`)

### Interface Contract (from Person 1)
Each skill implements `app/skills/base.py`:
- `name: str`
- `matches(message: str) -> bool`
- `execute(message: str) -> str`

The `SkillRouter` selects the first skill whose `matches()` is `True`, so
registration order and keyword mutual-exclusion matter.

### Verified Scenarios (no Ollama needed)
Run from `CampusBot/`:
```bash
python -m app.skills.registration_example
```
| Question | Skill | Status |
|---|---|---|
| What is SZU's motto? | campus | success |
| When was SZU founded? | campus | success |
| What are SZU's two campuses? | campus | success |
| Where is SZU Library? | library | success |
| What library information is available? | library | success |
| Who is the current president? | campus | success (info unavailable) |
| Where is the International Office? | none | unmatched |

### Registration (for Person 1 / Person 5)
```python
from app.runtime.runtime import Runtime
from app.skills.campus import CampusSkill
from app.skills.library import LibrarySkill

runtime = Runtime()
runtime.register_skill(CampusSkill())
runtime.register_skill(LibrarySkill())
# Person 3 adds TranslationSkill() and SummarySkill()
result = runtime.execute("user01", "Where is the library?")
```

### Notes for Integration
- Person 3: please make Translation/Summary `matches()` return False for
  pure campus/library fact questions, or register them after campus/library.
- Person 5: the `/chat` endpoint should call `runtime.execute()` and return
  the structured `{skill, status, response}` result.
