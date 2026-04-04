# server/app.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from typing import Optional
from pydantic import BaseModel
import os

from server.environment import CodeDebugEnvironment
from models import DebugAction, DebugObservation, DebugState

app = FastAPI(
    title="Code Debug Environment",
    description=(
        "An OpenEnv environment where LLM agents fix buggy Python code. "
        "3 difficulty levels: easy (1 bug), medium (2 bugs), hard (algorithmic + explanation)."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

env = CodeDebugEnvironment()


@app.get("/", response_class=HTMLResponse)
async def root():
    """Homepage with live tester UI."""
    html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()


@app.get("/health")
async def health():
    return {"status": "ok", "environment": "code-debug-env", "version": "1.0.0"}


class ResetRequest(BaseModel):
    difficulty: Optional[str] = None


class StepRequest(BaseModel):
    fixed_code: str
    explanation: Optional[str] = None


class StepResponse(BaseModel):
    observation: dict
    reward: float
    done: bool


@app.post("/reset")
async def reset(request: ResetRequest = ResetRequest()) -> dict:
    try:
        observation = env.reset(difficulty=request.difficulty)
        return {"observation": observation.model_dump(), "reward": 0.0, "done": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reset failed: {str(e)}")


@app.post("/step")
async def step(request: StepRequest) -> StepResponse:
    if not request.fixed_code or not request.fixed_code.strip():
        raise HTTPException(status_code=400, detail="fixed_code must not be empty.")
    try:
        action = DebugAction(fixed_code=request.fixed_code, explanation=request.explanation)
        observation = env.step(action)
        return StepResponse(
            observation=observation.model_dump(),
            reward=observation.reward or 0.0,
            done=observation.done,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Step failed: {str(e)}")


@app.get("/state")
async def state() -> dict:
    try:
        return env.state.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"State failed: {str(e)}")


@app.get("/tasks")
async def list_tasks() -> dict:
    from server.tasks.task_easy import EASY_TASKS
    from server.tasks.task_medium import MEDIUM_TASKS
    from server.tasks.task_hard import HARD_TASKS
    return {
        "easy": [t["task_id"] for t in EASY_TASKS],
        "medium": [t["task_id"] for t in MEDIUM_TASKS],
        "hard": [t["task_id"] for t in HARD_TASKS],
        "total": len(EASY_TASKS) + len(MEDIUM_TASKS) + len(HARD_TASKS),
    }


# ─── Run directly with: python server/app.py ─────────────────────────────────
if __name__ == "__main__":
    import sys
    import uvicorn
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    uvicorn.run("server.app:app", host="127.0.0.1", port=7860, reload=True)