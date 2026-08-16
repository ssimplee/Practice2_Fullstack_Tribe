"""Privacy-conscious JSON Lines audit logging for CampusBot."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from threading import Lock


@dataclass(frozen=True)
class AuditRecord:
    """Execution metadata; request and response content are intentionally absent."""

    timestamp: str
    request_id: str
    user: str
    skill: str | None
    status: str
    duration_ms: int
    guardrail_rule: str | None = None

    @classmethod
    def create(
        cls,
        *,
        request_id: str,
        user: str,
        skill: str | None,
        status: str,
        duration_ms: int,
        guardrail_rule: str | None = None,
    ) -> "AuditRecord":
        return cls(
            timestamp=datetime.now(timezone.utc).isoformat(),
            request_id=request_id,
            user=user,
            skill=skill,
            status=status,
            duration_ms=max(0, int(duration_ms)),
            guardrail_rule=guardrail_rule,
        )


class AuditLogger:
    """Append one privacy-safe JSON record for each execution."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._lock = Lock()

    def log(self, record: AuditRecord) -> None:
        payload = json.dumps(asdict(record), ensure_ascii=False, separators=(",", ":"))
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8", newline="\n") as stream:
                stream.write(payload + "\n")
