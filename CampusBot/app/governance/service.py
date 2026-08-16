"""Governance wrapper around Person 1's agreed Runtime contract."""

from __future__ import annotations

from time import perf_counter
from typing import Any, Protocol
from uuid import uuid4

from .audit import AuditLogger, AuditRecord
from .guardrail import Guardrail


class RuntimeContract(Protocol):
    def execute(self, user: str, message: str) -> dict[str, Any]:
        ...


class GovernedRuntime:
    """Guard requests before Runtime execution and audit every outcome."""

    def __init__(
        self,
        runtime: RuntimeContract,
        audit_logger: AuditLogger,
        guardrail: Guardrail | None = None,
    ) -> None:
        self._runtime = runtime
        self._audit_logger = audit_logger
        self._guardrail = guardrail or Guardrail()

    def execute(self, user: str, message: str) -> dict[str, Any]:
        started = perf_counter()
        request_id = uuid4().hex
        decision = self._guardrail.evaluate(message)

        if not decision.allowed:
            result: dict[str, Any] = {
                "skill": None,
                "status": "blocked",
                "response": "Request blocked.",
            }
        else:
            try:
                result = dict(self._runtime.execute(user, message))
            except Exception:
                result = {
                    "skill": None,
                    "status": "error",
                    "response": "The request could not be completed.",
                }

        duration_ms = max(0, round((perf_counter() - started) * 1000))
        result["request_id"] = request_id
        result["duration_ms"] = duration_ms

        self._audit_logger.log(
            AuditRecord.create(
                request_id=request_id,
                user=user,
                skill=result.get("skill"),
                status=str(result.get("status", "error")),
                duration_ms=duration_ms,
                guardrail_rule=decision.rule,
            )
        )
        return result
