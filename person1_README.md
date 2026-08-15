## Person 1 - Runtime and Skill Router

Implemented the core runtime and skill routing structure for CampusBot.

### Implemented
- Common `Skill` interface
  - `name`
  - `matches(message)`
  - `execute(message)`
- `SkillRouter`
  - Registers available skills
  - Selects the first matching skill
- `Runtime`
  - Routes requests through the Skill Router
  - Executes the selected skill
  - Returns structured results
- Fallback and error handling
  - Empty message → `invalid_request`
  - No matching skill → `unmatched`
  - Skill execution failure → `error`
  - Successful execution → `success`

### Files Added

- `CampusBot/app/skills/base.py`
- `CampusBot/app/skills/__init__.py`
- `CampusBot/app/runtime/router.py`
- `CampusBot/app/runtime/runtime.py`
- `CampusBot/app/runtime/__init__.py`
- `CampusBot/app/__init__.py`

### Runtime Flow

User Request  
→ Runtime  
→ Skill Router  
→ Selected Skill  
→ Structured Result

Example result:

```json
{
  "skill": "library",
  "status": "success",
  "response": "..."
}