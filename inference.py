#!/usr/bin/env python3
# inference.py — Code Debug Environment Baseline Agent
# Log format strictly follows [START] [STEP] [END] as required by evaluator.
#
# Required env vars: API_BASE_URL, MODEL_NAME, HF_TOKEN
# Usage:
#   python inference.py
#   python inference.py --url https://Souravdanyal-code-debug-env.hf.space
#   python inference.py --difficulty easy

import os
import sys
import json
import time
import argparse
import requests
from openai import OpenAI
from typing import List, Optional

# ─── Configuration ────────────────────────────────────────────────────────────
API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME   = os.environ.get("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN     = os.environ.get("HF_TOKEN", "")
ENV_URL      = os.environ.get("ENV_URL", "http://localhost:7860")
BENCHMARK    = "code-debug-env"
MAX_STEPS    = 5

# ─── OpenAI Client ───────────────────────────────────────────────────────────
client = OpenAI(api_key=HF_TOKEN or "dummy", base_url=API_BASE_URL)

# ─── Logging — STRICT FORMAT REQUIRED BY EVALUATOR ───────────────────────────
# [START] task=<task_id> env=<benchmark> model=<model_name>
# [STEP] step=<n> action=<str> reward=<0.00> done=<true|false> error=<msg|null>
# [END] success=<true|false> steps=<n> rewards=<r1,r2,...,rn>

def log_start(task_id: str, env: str, model: str) -> None:
    print(f"[START] task={task_id} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}", flush=True)

def log_end(success: bool, steps: int, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} rewards={rewards_str}", flush=True)

# ─── Environment Client ───────────────────────────────────────────────────────
def env_reset(env_url: str, difficulty: str) -> dict:
    resp = requests.post(f"{env_url}/reset", json={"difficulty": difficulty}, timeout=30)
    resp.raise_for_status()
    return resp.json()

def env_step(env_url: str, fixed_code: str, explanation: str = None) -> dict:
    payload = {"fixed_code": fixed_code}
    if explanation:
        payload["explanation"] = explanation
    resp = requests.post(f"{env_url}/step", json=payload, timeout=30)
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
            model=MODEL_NAME, messages=messages, max_tokens=1000, temperature=0.1,
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1]) if lines[-1] == "```" else "\n".join(lines[1:])
        parsed = json.loads(content)
        return {"fixed_code": parsed.get("fixed_code", ""), "explanation": parsed.get("explanation", None)}
    except json.JSONDecodeError:
        return {"fixed_code": buggy_code, "explanation": None}
    except Exception as e:
        print(f"# LLM call failed: {e}", file=sys.stderr)
        return {"fixed_code": buggy_code, "explanation": None}

# ─── Main Episode Loop ────────────────────────────────────────────────────────
def run_episode(env_url: str, difficulty: str) -> tuple:
    reset_data = env_reset(env_url, difficulty)
    obs = reset_data["observation"]
    task_id      = obs["task_id"]
    buggy_code   = obs["buggy_code"]
    instructions = obs["instructions"]

    log_start(task_id=task_id, env=BENCHMARK, model=MODEL_NAME)

    last_feedback = None
    rewards: List[float] = []
    steps_taken = 0
    success = False

    for attempt in range(1, MAX_STEPS + 1):
        steps_taken = attempt
        agent_action = call_llm(
            buggy_code=buggy_code, instructions=instructions,
            difficulty=difficulty, feedback=last_feedback, attempt=attempt,
        )
        fixed_code = agent_action["fixed_code"]

        if not fixed_code or not fixed_code.strip():
            log_step(step=attempt, action="empty_submission", reward=0.0, done=False, error="empty_code")
            rewards.append(0.0)
            continue

        try:
            result = env_step(env_url, fixed_code=fixed_code, explanation=agent_action.get("explanation"))
        except Exception as e:
            log_step(step=attempt, action="step_failed", reward=0.0, done=False, error=str(e)[:60])
            rewards.append(0.0)
            continue

        reward = result.get("reward", 0.0)
        done   = result.get("done", False)
        obs_r  = result.get("observation", {})
        last_feedback = obs_r.get("feedback", "")

        log_step(step=attempt, action=f"fix_{difficulty}_attempt{attempt}", reward=reward, done=done, error=None)
        rewards.append(reward)

        if reward >= 1.0:
            success = True
        if done:
            break

    log_end(success=success, steps=steps_taken, rewards=rewards)
    return success, steps_taken, rewards

def main():
    parser = argparse.ArgumentParser(description="Code Debug Environment Baseline Agent")
    parser.add_argument("--url", default=ENV_URL, help="Environment base URL")
    parser.add_argument("--difficulty", default=None, choices=["easy", "medium", "hard", "all"])
    args = parser.parse_args()
    env_url = args.url.rstrip("/")

    try:
        health = requests.get(f"{env_url}/health", timeout=10)
        health.raise_for_status()
        print(f"# Environment healthy at {env_url}", flush=True)
    except Exception as e:
        print(f"# Health check failed: {e}", file=sys.stderr)
        sys.exit(1)

    difficulties = ["easy", "medium", "hard"] if (args.difficulty in ("all", None)) else [args.difficulty]

    all_rewards = []
    all_successes = []
    for difficulty in difficulties:
        success, steps, rewards = run_episode(env_url, difficulty)
        all_rewards.extend(rewards)
        all_successes.append(success)
        time.sleep(0.5)

    avg = round(sum(all_rewards) / len(all_rewards), 3) if all_rewards else 0.0
    print(f"# SUMMARY: {sum(all_successes)}/{len(difficulties)} tasks solved | avg_reward={avg}", flush=True)

if __name__ == "__main__":
    main()