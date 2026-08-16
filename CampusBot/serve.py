"""CampusBot Agent Harness API and browser entry point.

The Windows launcher prefers this file over the original ``main.py``. Requests
therefore follow the required flow:

    Browser/API -> Guardrail -> Runtime -> Router -> Skill -> Audit -> Result
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.skills.registration_example import build_governed_runtime


ROOT = Path(__file__).resolve().parent
WEB_ROOT = ROOT / "web"


class AgentContract(Protocol):
    def execute(self, user: str, message: str) -> dict[str, Any]:
        ...


class ChatRequest(BaseModel):
    """Structured Agent request; ``user`` defaults for the existing browser."""

    user: str = Field(default="web-user", min_length=1, max_length=128)
    message: str = Field(min_length=1, max_length=12000)


class ChatResponse(BaseModel):
    request_id: str
    skill: str | None
    status: str
    response: str
    duration_ms: int


app = FastAPI(title="CampusBot Agent Harness", version="1.0.0")
app.state.agent = build_governed_runtime()
app.mount("/static", StaticFiles(directory=WEB_ROOT), name="static")


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(WEB_ROOT / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    user = request.user.strip()
    if not user:
        raise HTTPException(status_code=400, detail="User cannot be empty.")

    result = app.state.agent.execute(user, request.message)
    return ChatResponse(
        request_id=str(result["request_id"]),
        skill=result.get("skill"),
        status=str(result["status"]),
        response=str(result["response"]),
        duration_ms=int(result["duration_ms"]),
    )


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
