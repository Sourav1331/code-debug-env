# models.py
# Typed Pydantic models for Action, Observation, and State
# These are the contracts between the agent and the environment.

from typing import Optional, List
from pydantic import Field
from openenv.core.env_server.types import Action, Observation, State


class DebugAction(Action):
    """Action submitted by the agent: fixed code + optional explanation."""

    fixed_code: str = Field(
        ...,
        description="The corrected Python function as a string. Must be valid Python."
    )
    explanation: Optional[str] = Field(
        default=None,
        description=(
            "Required for 'hard' difficulty tasks. Explain what was wrong "
            "and why your fix is correct. Affects reward on hard tasks."
        )
    )


class TestResult(Action):
    """Sub-model: result of a single test case."""
    test_id: int
    passed: bool
    expected: str
    got: str


class DebugObservation(Observation):
    """Observation returned after each step()."""

    # Task info
    task_id: str = Field(..., description="Unique ID of the current task instance")
    difficulty: str = Field(..., description="Task difficulty: easy | medium | hard")
    buggy_code: str = Field(..., description="The buggy Python code the agent must fix")
    instructions: str = Field(..., description="Natural language instructions for the task")
    test_cases_description: str = Field(
        ..., description="Description of what the test cases check"
    )

    # After step() — feedback
    reward: Optional[float] = Field(
        default=None, description="Score from 0.0 to 1.0 for this step"
    )
    passed_tests: Optional[int] = Field(
        default=None, description="Number of test cases passed"
    )
    total_tests: Optional[int] = Field(
        default=None, description="Total number of test cases"
    )
    feedback: Optional[str] = Field(
        default=None,
        description="Detailed feedback: which tests failed and why"
    )
    done: bool = Field(default=False, description="True when episode is complete")


class DebugState(State):
    """Internal environment state, returned by GET /state."""

    episode_id: str = ""          # ← required by validator: GET /state must return episode_id
    task_id: str
    difficulty: str
    step_count: int = 0
    max_steps: int = 3
    current_reward: float = 0.0
    best_reward: float = 0.0
    done: bool = False
