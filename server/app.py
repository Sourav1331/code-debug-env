# server/app.py — FastAPI server for Code Debug Environment
# Port 7860 required for Hugging Face Spaces.

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
    description="OpenEnv RL environment where LLM agents fix buggy Python code. 3 difficulty levels: easy, medium, hard.",
    version="1.0.0",
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

env = CodeDebugEnvironment()


class ResetRequest(BaseModel):
    difficulty: Optional[str] = None

class StepRequest(BaseModel):
    fixed_code: str
    explanation: Optional[str] = None

class StepResponse(BaseModel):
    observation: dict
    reward: float
    done: bool


@app.get("/", response_class=HTMLResponse)
async def root():
    """Homepage with live interactive tester."""
    html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    from fastapi.responses import Response
    return Response(content=b"", media_type="image/x-icon")


@app.get("/health")
async def health():
    """Health check — must return 200 for submission validation."""
    return {"status": "ok", "environment": "code-debug-env", "version": "1.0.0"}


@app.post("/reset")
async def reset(request: ResetRequest = ResetRequest()) -> dict:
    """Reset environment to start a new episode. Pass difficulty: easy | medium | hard"""
    try:
        obs = env.reset(difficulty=request.difficulty)
        return {"observation": obs.model_dump(), "reward": 0.0, "done": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reset failed: {str(e)}")


@app.post("/step")
async def step(request: StepRequest) -> StepResponse:
    """Submit fixed code. Returns reward (0.0-1.0), feedback, done flag."""
    if not request.fixed_code or not request.fixed_code.strip():
        raise HTTPException(status_code=400, detail="fixed_code must not be empty.")
    try:
        action = DebugAction(fixed_code=request.fixed_code, explanation=request.explanation)
        obs = env.step(action)
        return StepResponse(observation=obs.model_dump(), reward=obs.reward or 0.0, done=obs.done)
    except TimeoutError:
        return StepResponse(
            observation={"task_id": "unknown", "difficulty": "unknown", "buggy_code": "",
                         "instructions": "", "test_cases_description": "", "reward": 0.0,
                         "passed_tests": 0, "total_tests": 3, "done": False,
                         "feedback": "TimeoutError: Infinite loop detected. Add a visited set for graph traversal."},
            reward=0.0, done=False,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Step failed: {str(e)}")


@app.get("/state")
async def state() -> dict:
    """Return current episode state."""
    try:
        return env.state.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"State failed: {str(e)}")


@app.get("/tasks")
async def list_tasks() -> dict:
    """List all 45 task IDs across difficulty levels."""
    from server.tasks.task_easy import EASY_TASKS
    from server.tasks.task_medium import MEDIUM_TASKS
    from server.tasks.task_hard import HARD_TASKS
    return {
        "easy":   [t["task_id"] for t in EASY_TASKS],
        "medium": [t["task_id"] for t in MEDIUM_TASKS],
        "hard":   [t["task_id"] for t in HARD_TASKS],
        "total":  len(EASY_TASKS) + len(MEDIUM_TASKS) + len(HARD_TASKS),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server.app:app", host="127.0.0.1", port=7860, reload=True)
