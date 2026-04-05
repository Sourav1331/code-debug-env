# server/app.py
# FastAPI server exposing the OpenEnv standard endpoints.
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

# One global environment instance (single session)
# For concurrent sessions, instantiate per-request with a session dict
env = CodeDebugEnvironment()


# ─── Request Models ─────────────────────────────────────────────────────────

class ResetRequest(BaseModel):
    difficulty: Optional[str] = None  # "easy" | "medium" | "hard" | None (random)


class StepRequest(BaseModel):
    fixed_code: str
    explanation: Optional[str] = None


# ─── Response wrapper matching OpenEnv StepResult shape ──────────────────────

class StepResponse(BaseModel):
    observation: dict
    reward: float
    done: bool


# ─── Endpoints ───────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def root():
    """Homepage — shows environment info and API endpoints."""
    html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    with open(html_path, "r") as f:
        return f.read()


@app.get("/health")
async def health():
    """Health check endpoint — must return 200 for submission validation."""
    return {"status": "ok", "environment": "code-debug-env", "version": "1.0.0"}


@app.post("/reset")
async def reset(request: ResetRequest = ResetRequest()) -> dict:
    """
    Reset the environment to start a new episode.
    Optionally pass difficulty: 'easy' | 'medium' | 'hard'
    """
    try:
        observation = env.reset(difficulty=request.difficulty)
        return {
            "observation": observation.model_dump(),
            "reward": 0.0,
            "done": False,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reset failed: {str(e)}")


@app.post("/step")
async def step(request: StepRequest) -> StepResponse:
    """
    Submit a code fix (and optional explanation for hard tasks).
    Returns observation with reward (0.0-1.0), feedback, and done flag.
    """
    if not request.fixed_code or not request.fixed_code.strip():
        raise HTTPException(status_code=400, detail="fixed_code must not be empty.")

    try:
        action = DebugAction(
            fixed_code=request.fixed_code,
            explanation=request.explanation,
        )
        observation = env.step(action)
        return StepResponse(
            observation=observation.model_dump(),
            reward=observation.reward or 0.0,
            done=observation.done,
        )
    except TimeoutError as e:
        # Code execution timed out — return 0 reward instead of 500
        import traceback
        print(f"[ERROR] TimeoutError in step: {e}\n{traceback.format_exc()}", flush=True)
        return StepResponse(
            observation={"task_id": env._current_task.get("task_id", "unknown") if env._current_task else "unknown",
                        "difficulty": env._difficulty,
                        "buggy_code": env._current_task.get("buggy_code", "") if env._current_task else "",
                        "instructions": env._current_task.get("instructions", "") if env._current_task else "",
                        "test_cases_description": env._current_task.get("test_cases_description", "") if env._current_task else "",
                        "reward": 0.0,
                        "passed_tests": 0,
                        "total_tests": len(env._current_task.get("test_cases", [])) if env._current_task else 3,
                        "feedback": "TimeoutError: Code execution timed out. Possible infinite loop or very slow code.",
                        "done": False},
            reward=0.0,
            done=False,
        )
    except Exception as e:
        import traceback
        print(f"[ERROR] Exception in step: {e}\n{traceback.format_exc()}", flush=True)
        raise HTTPException(status_code=500, detail=f"Step failed: {str(e)}")


@app.get("/state")
async def state() -> dict:
    """Return the current episode state."""
    try:
        s = env.state
        return s.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"State failed: {str(e)}")


@app.get("/tasks")
async def list_tasks() -> dict:
    """List available task IDs per difficulty (for inspection)."""
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