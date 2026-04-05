#!/usr/bin/env python3
"""
inference.py - Code Debug Environment Baseline Agent

Required env vars: API_BASE_URL, MODEL_NAME, HF_TOKEN
Usage:
  python inference.py
  python inference.py --url https://Souravdanyal-code-debug-env.hf.space
  python inference.py --difficulty easy

STDOUT FORMAT (required by evaluator):
  [START] task=<id> env=<benchmark> model=<model>
  [STEP] step=<n> action=<str> reward=<0.00> done=<true|false> error=<msg|null>
  [END] success=<true|false> steps=<n> rewards=<r1,r2,...>
"""

import os, sys, json, time, argparse, requests
from openai import OpenAI
from typing import List, Optional

# ── Config ────────────────────────────────────────────────────────────────────
API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME   = os.environ.get("MODEL_NAME",   "gpt-4o-mini")
HF_TOKEN     = os.environ.get("HF_TOKEN",     "")
ENV_URL      = os.environ.get("ENV_URL",      "http://localhost:7860")
BENCHMARK    = "code-debug-env"
MAX_STEPS    = 5

client = OpenAI(api_key=HF_TOKEN or "dummy", base_url=API_BASE_URL)

# ── Logging ───────────────────────────────────────────────────────────────────
def log_start(task_id, env, model):
    print(f"[START] task={task_id} env={env} model={model}", flush=True)

def log_step(step, action, reward, done, error):
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={error or 'null'}", flush=True)

def log_end(success, steps, rewards):
    print(f"[END] success={str(success).lower()} steps={steps} rewards={','.join(f'{r:.2f}' for r in rewards)}", flush=True)

# ── Env client ────────────────────────────────────────────────────────────────
def env_reset(url, difficulty):
    r = requests.post(f"{url}/reset", json={"difficulty": difficulty}, timeout=30)
    r.raise_for_status()
    return r.json()

def env_step(url, fixed_code, explanation=None):
    payload = {"fixed_code": fixed_code}
    if explanation:
        payload["explanation"] = explanation
    r = requests.post(f"{url}/step", json=payload, timeout=30)
    r.raise_for_status()
    return r.json()

# ── LLM ──────────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert Python debugging agent. Fix bugs in Python functions.

RESPONSE FORMAT — strictly JSON only, no markdown:
{
  "fixed_code": "<complete corrected Python function including imports>",
  "explanation": "<for hard tasks: explain the bug, root cause, and fix>"
}

RULES:
- Return COMPLETE function with all imports (e.g. from collections import deque)
- fixed_code must be valid Python
- For hard tasks explanation MUST mention the algorithmic concept

COMMON BUGS:
- Graph/BFS: missing visited set → infinite loop on cycles → add visited=set()
- Knapsack DP: wrong loop order (forward=unbounded, backward=0/1 knapsack)
- Binary search: wrong boundary → return high not low, or high=n//2 not n
- Off-by-one: lst[2] should be lst[1] for second element
- Wrong operator: + instead of -, * instead of /

IF PREVIOUS ATTEMPT FAILED:
- Read the Input/Expected/Got carefully
- Try a completely different fix
- For TimeoutError: you have an infinite loop, add a visited set
"""

def call_llm(buggy_code, instructions, difficulty, feedback=None, attempt=1, prev_code=None):
    content = f"Difficulty: {difficulty}\nInstructions: {instructions}\n\nBuggy code:\n```python\n{buggy_code}\n```\n"

    if feedback and attempt > 1:
        content += f"\nPREVIOUS FIX FAILED. Feedback:\n{feedback}\n\nYour previous code:\n```python\n{prev_code or ''}\n```\nTry a different approach.\n"

    if difficulty == "hard":
        content += "\nIMPORTANT: Include a detailed explanation field mentioning the algorithmic concept.\n"

    try:
        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": content}],
            max_tokens=1500,
            temperature=0.1 if attempt == 1 else 0.4,
        )
        raw = resp.choices[0].message.content.strip()
        # Clean markdown fences
        if "```" in raw:
            raw = raw.split("```")[1] if raw.startswith("```") else raw
            if raw.startswith("json\n"):
                raw = raw[5:]
        # Find JSON object
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            raw = raw[start:end]
        parsed = json.loads(raw)
        return {"fixed_code": parsed.get("fixed_code", ""), "explanation": parsed.get("explanation")}
    except Exception as e:
        print(f"# LLM error: {e}", file=sys.stderr)
        return {"fixed_code": buggy_code, "explanation": None}

# ── Episode ───────────────────────────────────────────────────────────────────
def run_episode(env_url, difficulty):
    data = env_reset(env_url, difficulty)
    obs  = data["observation"]
    task_id      = obs["task_id"]
    buggy_code   = obs["buggy_code"]
    instructions = obs["instructions"]

    log_start(task_id, BENCHMARK, MODEL_NAME)

    rewards, steps_taken, success = [], 0, False
    last_feedback, last_code = None, None

    for attempt in range(1, MAX_STEPS + 1):
        steps_taken = attempt
        action = call_llm(buggy_code, instructions, difficulty, last_feedback, attempt, last_code)
        code = action["fixed_code"]
        last_code = code

        if not code or not code.strip():
            log_step(attempt, "empty_submission", 0.0, False, "empty_code")
            rewards.append(0.0)
            continue

        try:
            result = env_step(env_url, code, action.get("explanation"))
        except Exception as e:
            log_step(attempt, "step_failed", 0.0, False, str(e)[:60])
            rewards.append(0.0)
            continue

        reward = result.get("reward", 0.0)
        done   = result.get("done", False)
        last_feedback = result.get("observation", {}).get("feedback", "")

        log_step(attempt, f"fix_{difficulty}_attempt{attempt}", reward, done, None)
        rewards.append(reward)

        if reward >= 1.0:
            success = True
        if done:
            break

    log_end(success, steps_taken, rewards)
    return success, steps_taken, rewards

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=ENV_URL)
    parser.add_argument("--difficulty", default=None, choices=["easy","medium","hard","all"])
    args = parser.parse_args()
    url = args.url.rstrip("/")

    try:
        requests.get(f"{url}/health", timeout=10).raise_for_status()
        print(f"# Environment healthy at {url}", flush=True)
    except Exception as e:
        print(f"# Health check failed: {e}", file=sys.stderr)
        sys.exit(1)

    diffs = ["easy","medium","hard"] if args.difficulty in (None,"all") else [args.difficulty]
    all_rewards, successes = [], []

    for d in diffs:
        ok, _, rewards = run_episode(url, d)
        all_rewards.extend(rewards)
        successes.append(ok)
        time.sleep(0.5)

    avg = round(sum(all_rewards)/len(all_rewards), 3) if all_rewards else 0.0
    print(f"# SUMMARY: {sum(successes)}/{len(diffs)} tasks solved | avg_reward={avg}", flush=True)

if __name__ == "__main__":
    main()
