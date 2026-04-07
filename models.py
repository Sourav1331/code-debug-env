# models.py — Typed Pydantic models for Action, Observation, and State

from typing import Optional
from pydantic import Field
from openenv.core.env_server.types import Action, Observation, State


class DebugAction(Action):
    """Action submitted by the agent: fixed code + optional explanation."""

    fixed_code: str = Field(
        ...,
        description="Complete corrected Python function. Must be valid Python including imports."
    )
    explanation: Optional[str] = Field(
        default=None,
        description="Required for hard tasks. Explain what was wrong and why your fix is correct."
    )


class DebugObservation(Observation):
    """Observation returned after reset() and step()."""

    task_id: str = Field(..., description="Unique task identifier e.g. easy_003")
    difficulty: str = Field(..., description="Task difficulty: easy | medium | hard")
    buggy_code: str = Field(..., description="The buggy Python code the agent must fix")
    instructions: str = Field(..., description="Natural language instructions for the task")
    test_cases_description: str = Field(..., description="What the test cases check")

    # Step feedback fields
    reward: Optional[float] = Field(default=None, description="Immediate reward 0.0-1.0 (null on reset)")
    cumulative_reward: float = Field(default=0.0, description="Total reward accumulated this episode")
    best_reward: float = Field(default=0.0, description="Best reward achieved this episode")
    passed_tests: Optional[int] = Field(default=None, description="Tests passed (null on reset)")
    total_tests: Optional[int] = Field(default=None, description="Total test cases (always 3)")
    feedback: Optional[str] = Field(default=None, description="Per-test feedback: Input, Expected, Got")
    done: bool = Field(default=False, description="True when episode complete")


class DebugState(State):
    """Internal environment state returned by GET /state."""

    episode_id: str = ""
    task_id: str = "none"
    difficulty: str = "easy"
    step_count: int = 0
    max_steps: int = 5
    current_reward: float = 0.0
    cumulative_reward: float = 0.0
    best_reward: float = 0.0
    done: bool = False
