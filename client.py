# client.py
# Python client for connecting to the Code Debug Environment.
# Use this in training loops / evaluation scripts.
#
# Usage (sync):
#   with CodeDebugEnv(base_url="https://your-space.hf.space").sync() as env:
#       result = env.reset(difficulty="easy")
#       result = env.step(DebugAction(fixed_code="..."))
#
# Usage (async):
#   async with CodeDebugEnv(base_url="https://your-space.hf.space") as env:
#       result = await env.reset(difficulty="medium")
#       result = await env.step(DebugAction(fixed_code="..."))

from openenv.core.env_client import EnvClient
from openenv.core.client_types import StepResult
from models import DebugAction, DebugObservation, DebugState


class CodeDebugEnv(EnvClient[DebugAction, DebugObservation, DebugState]):
    """
    Client for the Code Debug Environment.
    Wraps OpenEnv EnvClient with typed action/observation models.
    """

    def _step_payload(self, action: DebugAction) -> dict:
        payload = {"fixed_code": action.fixed_code}
        if action.explanation:
            payload["explanation"] = action.explanation
        return payload

    def _parse_result(self, payload: dict) -> StepResult[DebugObservation]:
        obs_data = payload.get("observation", {})
        obs = DebugObservation(
            task_id=obs_data.get("task_id", ""),
            difficulty=obs_data.get("difficulty", "easy"),
            buggy_code=obs_data.get("buggy_code", ""),
            instructions=obs_data.get("instructions", ""),
            test_cases_description=obs_data.get("test_cases_description", ""),
            reward=obs_data.get("reward"),
            passed_tests=obs_data.get("passed_tests"),
            total_tests=obs_data.get("total_tests"),
            feedback=obs_data.get("feedback"),
            done=payload.get("done", False),
        )
        return StepResult(
            observation=obs,
            reward=payload.get("reward", 0.0),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: dict) -> DebugState:
        return DebugState(
            episode_id=payload.get("episode_id", ""),
            step_count=payload.get("step_count", 0),
            task_id=payload.get("task_id", ""),
            difficulty=payload.get("difficulty", "easy"),
            max_steps=payload.get("max_steps", 3),
            current_reward=payload.get("current_reward", 0.0),
            best_reward=payload.get("best_reward", 0.0),
            done=payload.get("done", False),
        )
