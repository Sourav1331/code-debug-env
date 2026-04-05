# server/environment.py
# Core environment: manages episode state, dispatches to task banks and graders.

import random
from uuid import uuid4
from typing import Optional

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

from models import DebugAction, DebugObservation, DebugState
from server.tasks.task_easy import get_random_easy_task
from server.tasks.task_medium import get_random_medium_task
from server.tasks.task_hard import get_random_hard_task
from server.graders.grader_easy import grade_easy
from server.graders.grader_medium import grade_medium
from server.graders.grader_hard import grade_hard


TASK_GETTERS = {
    "easy": get_random_easy_task,
    "medium": get_random_medium_task,
    "hard": get_random_hard_task,
}

GRADERS = {
    "easy": grade_easy,
    "medium": grade_medium,
    "hard": grade_hard,
}

MAX_STEPS = 5


class CodeDebugEnvironment(Environment):
    """
    OpenEnv environment for LLM-based code debugging.
    Supports 3 difficulty levels with partial rewards.
    """

    def __init__(self):
        self._episode_id: str = str(uuid4())
        self._difficulty: str = "easy"
        self._current_task: Optional[dict] = None
        self._step_count: int = 0
        self._best_reward: float = 0.0
        self._current_reward: float = 0.0
        self._done: bool = False

    def reset(self, difficulty: Optional[str] = None) -> DebugObservation:
        """
        Start a new episode. Optionally specify difficulty: easy | medium | hard.
        If not specified, cycles randomly.
        """
        self._episode_id = str(uuid4())
        self._step_count = 0
        self._best_reward = 0.0
        self._current_reward = 0.0
        self._done = False

        # Validate difficulty
        if difficulty and difficulty in TASK_GETTERS:
            self._difficulty = difficulty
        else:
            self._difficulty = random.choice(["easy", "medium", "hard"])

        # Load a task
        self._current_task = TASK_GETTERS[self._difficulty]()

        return DebugObservation(
            task_id=self._current_task["task_id"],
            difficulty=self._difficulty,
            buggy_code=self._current_task["buggy_code"],
            instructions=self._current_task["instructions"],
            test_cases_description=self._current_task["test_cases_description"],
            reward=None,
            passed_tests=None,
            total_tests=len(self._current_task["test_cases"]),
            feedback=None,
            done=False,
        )

    def step(self, action: DebugAction) -> DebugObservation:
        """
        Agent submits fixed_code (and optionally explanation for hard tasks).
        Returns observation with reward, feedback, and done flag.
        """
        if self._done:
            return DebugObservation(
                task_id=self._current_task["task_id"] if self._current_task else "none",
                difficulty=self._difficulty,
                buggy_code=self._current_task["buggy_code"] if self._current_task else "",
                instructions="Episode is already done. Call reset() to start a new episode.",
                test_cases_description="",
                reward=self._best_reward,
                passed_tests=None,
                total_tests=0,
                feedback="Episode ended. Please call reset() to start a new task.",
                done=True,
            )

        self._step_count += 1

        # ── Invalid action penalty ──────────────────────────────────────────
        code = action.fixed_code.strip() if action.fixed_code else ""
        if not code:
            done = self._step_count >= MAX_STEPS
            self._done = done
            return DebugObservation(
                task_id=self._current_task["task_id"],
                difficulty=self._difficulty,
                buggy_code=self._current_task["buggy_code"],
                instructions=self._current_task["instructions"],
                test_cases_description=self._current_task["test_cases_description"],
                reward=0.0,
                passed_tests=0,
                total_tests=len(self._current_task["test_cases"]),
                feedback="❌ Invalid action: fixed_code is empty. Penalty applied. Submit valid Python code.",
                done=done,
            )

        # Check for obvious non-Python (very short or no 'def' keyword)
        if len(code) < 5 or ("def " not in code and "lambda" not in code and "=" not in code):
            done = self._step_count >= MAX_STEPS
            self._done = done
            return DebugObservation(
                task_id=self._current_task["task_id"],
                difficulty=self._difficulty,
                buggy_code=self._current_task["buggy_code"],
                instructions=self._current_task["instructions"],
                test_cases_description=self._current_task["test_cases_description"],
                reward=0.0,
                passed_tests=0,
                total_tests=len(self._current_task["test_cases"]),
                feedback="❌ Invalid action: submission does not appear to be valid Python. Penalty applied.",
                done=done,
            )

        # Grade the submission
        grader = GRADERS[self._difficulty]
        if self._difficulty == "hard":
            reward, passed, total, feedback, _ = grader(
                action.fixed_code, self._current_task, action.explanation
            )
        else:
            reward, passed, total, feedback, _ = grader(
                action.fixed_code, self._current_task
            )

        self._current_reward = reward
        self._best_reward = max(self._best_reward, reward)

        # Episode ends if: perfect score OR max steps reached
        done = (reward == 1.0) or (self._step_count >= MAX_STEPS)
        self._done = done

        return DebugObservation(
            task_id=self._current_task["task_id"],
            difficulty=self._difficulty,
            buggy_code=self._current_task["buggy_code"],
            instructions=self._current_task["instructions"],
            test_cases_description=self._current_task["test_cases_description"],
            reward=reward,
            passed_tests=passed,
            total_tests=total,
            feedback=feedback,
            done=done,
        )

    @property
    def state(self) -> DebugState:
        """Return current episode metadata."""
        return DebugState(
            episode_id=self._episode_id,
            step_count=self._step_count,
            task_id=self._current_task["task_id"] if self._current_task else "none",
            difficulty=self._difficulty,
            max_steps=MAX_STEPS,
            current_reward=self._current_reward,
            best_reward=self._best_reward,
            done=self._done,
        )