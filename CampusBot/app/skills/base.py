from abc import ABC, abstractmethod


class Skill(ABC):
    """Common interface for all CampusBot skills."""

    name: str = ""

    @abstractmethod
    def matches(self, message: str) -> bool:
        """Return True when this skill can handle the message."""
        raise NotImplementedError

    @abstractmethod
    def execute(self, message: str) -> str:
        """Execute the skill and return its response."""
        raise NotImplementedError