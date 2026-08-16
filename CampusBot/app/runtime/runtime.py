from typing import Any, Iterable

from app.runtime.router import SkillRouter
from app.skills.base import Skill


class Runtime:
    """Central execution runtime for CampusBot."""

    def __init__(self, skills: Iterable[Skill] | None = None):
        self.router = SkillRouter(skills)

    def register_skill(self, skill: Skill) -> None:
        """Register a new skill."""
        self.router.register(skill)

    def execute(self, user: str, message: str) -> dict[str, Any]:
        """Route a request to a skill and return a structured result."""

        if not message or not message.strip():
            return {
                "skill": None,
                "status": "invalid_request",
                "response": "Message cannot be empty.",
            }

        try:
            skill = self.router.select(message)
        except Exception:
            return {
                "skill": None,
                "status": "error",
                "response": "The request could not be routed.",
            }

        if skill is None:
            return {
                "skill": None,
                "status": "unmatched",
                "response": "No available skill can handle this request.",
            }

        try:
            response = skill.execute(message)
        except Exception:
            return {
                "skill": skill.name,
                "status": "error",
                "response": "The selected skill could not complete the request.",
            }

        return {
            "skill": skill.name,
            "status": "success",
            "response": response,
        }