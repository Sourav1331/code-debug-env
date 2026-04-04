#!/usr/bin/env python3
# inference.py
# ─────────────────────────────────────────────────────────────────────────────
# Baseline inference script for the Code Debug Environment.
# Must be run from the project root.
#
# Required environment variables:
#   API_BASE_URL  — LLM API endpoint (OpenAI-compatible)
#   MODEL_NAME    — Model identifier
#   HF_TOKEN      — Hugging Face / API key
#
# Usage:
#   python inference.py
#   python inference.py --url https://your-hf-space.hf.space
#   python inference.py --difficulty easy
#
# Log format: [START], [STEP], [END] — strictly followed for evaluation scoring.
# ─────────────────────────────────────────────────────────────────────────────

import os
import sys
import json
import time
import argparse
import requests
from openai import OpenAI

# ─── Configuration ────────────────────────────────────────────────────────────

API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.environ.get("HF_TOKEN", "")
ENV_URL = os.environ.get("ENV_URL", "http://localhost:7860")

MAX_STEPS = 3
DIFFICULTIES = ["easy", "medium", "hard"]


# ─── OpenAI Client ───────────────────────────────────────────────────────────

client = OpenAI(
    api_key=HF_TOKEN or "dummy",
    base_url=API_BASE_URL,
)


# ─── Logging (strict format required by evaluator) ───────────────────────────

def log_start(task_id: str, difficulty: str, episode: int):
    print(json.dumps({
        "type": "START",
        "episode": episode,
        "task_id": task_id,
        "difficulty": difficulty,
        "timestamp": time.time(),
    }), flush=True)


def log_step(task_id: str, step: int, action_summary: str, reward: float, done: bool):
    print(json.dumps({
        "type": "STEP",
        "task_id": task_id,
        "step": step,
        "action": action_summary,
        "reward": reward,
        "done": done,
        "timestamp": time.time(),
    }), flush=True)


def log_end(task_id: str, difficulty: str, final_reward: float, steps_taken: int, episode: int):
    print(json.dumps({
        "type": "END",
        "episode": episode,
        "task_id": task_id,
        "difficulty": difficulty,
        "final_reward": final_reward,
        "steps_taken": steps_taken,
        "timestamp": time.time(),
    }), flush=True)


# ─── Environment Client ───────────────────────────────────────────────────────

def env_reset(env_url: str, difficulty: str) -> dict:
    resp = requests.post(
        f"{env_url}/reset",
        json={"difficulty": difficulty},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def env_step(env_url: str, fixed_code: str, explanation: str = None) -> dict:
    payload = {"fixed_code": fixed_code}
    if explanation:
        payload["explanation"] = explanation
    resp = requests.post(
        f"{env_url}/step",
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def env_state(env_url: str) -> dict:
    resp = requests.get(f"{env_url}/state", timeout=10)
    resp.raise_for_status()
    return resp.json()


# ─── LLM Agent ───────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert Python debugging agent. 
You will be given buggy Python code and must fix it.

For easy tasks: fix the single bug.
For medium tasks: fix both bugs.
For hard tasks: fix the algorithmic bug AND explain your reasoning in the 'explanation' field.

You MUST respond ONLY with valid JSON in this exact format:
{
  "fixed_code": "<complete fixed Python function as a string>",
  "explanation": "<required for hard tasks; describe what was wrong and why your fix is correct>"
}

Rules:
- Return the COMPLETE function, not just the changed line.
- The fixed_code must be valid Python that can be exec'd.
- For hard tasks, explanation must discuss the algorithm, root cause, and fix.
- Do NOT include markdown fences or any text outside the JSON object.
"""


def call_llm(buggy_code: str, instructions: str, difficulty: str,
             feedback: str = None, attempt: int = 1) -> dict:
    """Call the LLM and return parsed {fixed_code, explanation}."""

    user_content = f"""Task difficulty: {difficulty}
Instructions: {instructions}

Buggy code:
```python
{buggy_code}
```
"""
    if feedback and attempt > 1:
        user_content += f"\nPrevious attempt feedback:\n{feedback}\n\nPlease fix the remaining issues."

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            max_tokens=1000,
            temperature=0.1,
        )
        content = response.choices[0].message.content.strip()

        # Strip markdown fences if present
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1]) if lines[-1] == "```" else "\n".join(lines[1:])

        parsed = json.loads(content)
        return {
            "fixed_code": parsed.get("fixed_code", ""),
            "explanation": parsed.get("explanation", None),
        }
    except json.JSONDecodeError:
        # Fallback: return original code if parsing fails
        return {"fixed_code": buggy_code, "explanation": None}
    except Exception as e:
        print(f"LLM call failed: {e}", file=sys.stderr)
        return {"fixed_code": buggy_code, "explanation": None}


# ─── Main Episode Loop ────────────────────────────────────────────────────────

def run_episode(env_url: str, difficulty: str, episode_num: int) -> float:
    """Run one full episode. Returns final reward."""

    # Reset
    reset_data = env_reset(env_url, difficulty)
    obs = reset_data["observation"]

    task_id = obs["task_id"]
    buggy_code = obs["buggy_code"]
    instructions = obs["instructions"]

    log_start(task_id, difficulty, episode_num)

    last_feedback = None
    final_reward = 0.0
    step_num = 0

    for attempt in range(1, MAX_STEPS + 1):
        step_num = attempt

        # Call LLM
        agent_action = call_llm(
            buggy_code=buggy_code,
            instructions=instructions,
            difficulty=difficulty,
            feedback=last_feedback,
            attempt=attempt,
        )

        # Submit to environment
        result = env_step(
            env_url,
            fixed_code=agent_action["fixed_code"],
            explanation=agent_action.get("explanation"),
        )

        reward = result.get("reward", 0.0)
        done = result.get("done", False)
        obs_result = result.get("observation", {})
        last_feedback = obs_result.get("feedback", "")

        log_step(
            task_id=task_id,
            step=attempt,
            action_summary=f"Submitted fix attempt {attempt} ({len(agent_action['fixed_code'])} chars)",
            reward=reward,
            done=done,
        )

        final_reward = reward

        if done:
            break

    log_end(task_id, difficulty, final_reward, step_num, episode_num)
    return final_reward


def main():
    parser = argparse.ArgumentParser(description="Code Debug Environment Baseline Agent")
    parser.add_argument("--url", default=ENV_URL, help="Environment base URL")
    parser.add_argument("--difficulty", default=None, choices=["easy", "medium", "hard", "all"],
                        help="Difficulty to run. 'all' runs one episode per difficulty.")
    args = parser.parse_args()

    env_url = args.url.rstrip("/")

    # Health check
    try:
        health = requests.get(f"{env_url}/health", timeout=10)
        health.raise_for_status()
        print(json.dumps({"type": "INFO", "message": f"Environment healthy at {env_url}"}), flush=True)
    except Exception as e:
        print(json.dumps({"type": "ERROR", "message": f"Health check failed: {e}"}), flush=True)
        sys.exit(1)

    # Determine episodes to run
    if args.difficulty == "all" or args.difficulty is None:
        episodes = [("easy", 1), ("medium", 2), ("hard", 3)]
    else:
        episodes = [(args.difficulty, 1)]

    all_rewards = []
    for episode_num, (difficulty, ep_id) in enumerate(episodes, start=1):
        reward = run_episode(env_url, difficulty, episode_num)  # use episode_num, not ep_id
        all_rewards.append({"difficulty": difficulty, "reward": reward})
        time.sleep(0.5)  # Small pause between episodes

    # Summary
    print(json.dumps({
        "type": "SUMMARY",
        "total_episodes": len(all_rewards),
        "results": all_rewards,
        "average_reward": round(sum(r["reward"] for r in all_rewards) / len(all_rewards), 3),
        "timestamp": time.time(),
    }), flush=True)


if __name__ == "__main__":
    main()
