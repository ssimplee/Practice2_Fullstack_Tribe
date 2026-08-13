from typing import Iterable, Optional

from app.skills.base import Skill


class SkillRouter:
    """Selects the appropriate skill for a user message."""

    def __init__(self, skills: Iterable[Skill] | None = None):
        self.skills: list[Skill] = list(skills or [])

    def register(self, skill: Skill) -> None:
        """Register a skill with the router."""
        self.skills.append(skill)

    def select(self, message: str) -> Optional[Skill]:
        """Return the first matching skill, or None if no skill matches."""
        for skill in self.skills:
            if skill.matches(message):
                return skill

        return None