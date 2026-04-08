#!/usr/bin/env python3
"""
inference.py - Code Debug Environment Baseline Agent

Required env vars: API_BASE_URL, MODEL_NAME, and one of API_KEY/GROQ_API_KEY/OPENAI_API_KEY/HF_TOKEN
Usage:
  python inference.py
  python inference.py --url https://Souravdanyal-code-debug-env.hf.space
  python inference.py --difficulty easy

STDOUT FORMAT (strictly required by evaluator - JSON):
  {"type": "START", "task": "<id>", "env": "<benchmark>", "model": "<model>"}
  {"type": "STEP", "step": <n>, "action": "<str>", "reward": <0.00>, "done": <bool>, "error": <msg|null>}
  {"type": "END", "success": <bool>, "steps": <n>, "score": <0.000>, "rewards": [<r1>, <r2>, ...]}
"""

import os, sys, json, time, argparse, requests, re
from openai import OpenAI
from typing import List, Optional


def _read_env(*names: str) -> tuple[str, Optional[str]]:
    """Return first non-empty env value and the matched variable name."""
    for name in names:
        for candidate in (name, name.lower()):
            val = os.environ.get(candidate)
            if val and val.strip():
                return val.strip(), candidate
    return "", None

# ── Config ────────────────────────────────────────────────────────────────────
API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.groq.com/openai/v1")
MODEL_NAME   = os.environ.get("MODEL_NAME",   "llama-3.1-8b-instant")

# Accept common provider key names, including lowercase variants.
API_KEY, API_KEY_SOURCE = _read_env("API_KEY", "GROQ_API_KEY", "OPENAI_API_KEY", "HF_TOKEN")
ENV_URL      = os.environ.get("ENV_URL",      "http://localhost:7860")
BENCHMARK    = "code-debug-env"
MAX_STEPS    = 5
SUCCESS_SCORE_THRESHOLD = 0.5

client = OpenAI(api_key=API_KEY or "dummy", base_url=API_BASE_URL)

# ── Logging — STRICT JSON FORMAT ─────────────────────────────────────────────
def log_start(task_id: str, env: str, model: str) -> None:
    log_entry = {
        "type": "START",
        "task": task_id,
        "env": env,
        "model": model
    }
    print(json.dumps(log_entry), flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    log_entry = {
        "type": "STEP",
        "step": step,
        "action": action,
        "reward": round(reward, 2),
        "done": done,
        "error": error
    }
    print(json.dumps(log_entry), flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    log_entry = {
        "type": "END",
        "success": success,
        "steps": steps,
        "score": round(score, 3),
        "rewards": [round(r, 2) for r in rewards]
    }
    print(json.dumps(log_entry), flush=True)

# ── Env client ────────────────────────────────────────────────────────────────
def env_reset(url: str, difficulty: str) -> dict:
    r = requests.post(f"{url}/reset", json={"difficulty": difficulty}, timeout=30)
    r.raise_for_status()
    return r.json()

def env_step(url: str, fixed_code: str, explanation: Optional[str] = None) -> dict:
    payload = {"fixed_code": fixed_code}
    if explanation:
        payload["explanation"] = explanation
    r = requests.post(f"{url}/step", json=payload, timeout=30)
    r.raise_for_status()
    return r.json()

# ── LLM ──────────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert Python debugging agent.

RESPONSE FORMAT — JSON only, no markdown fences, no extra text:
{"fixed_code": "<complete Python function with all imports>", "explanation": "<for hard tasks only>"}

RULES:
- Return the COMPLETE function including all imports (e.g. from collections import deque)
- fixed_code must be valid, executable Python
- For hard tasks: explanation MUST mention the algorithmic concepts from the instructions

COMMON BUG PATTERNS — memorize these:
- RIGHT rotate list by k: lst[-k:] + lst[:-k]   (NOT lst[k:] + lst[:k] which is LEFT rotate)
- LEFT rotate list by k: lst[k:] + lst[:k]
- BFS/graph missing visited: add visited=set([start]) before queue, check before appending
- 0/1 Knapsack: iterate BACKWARD range(capacity, weight-1, -1) NOT forward
- Binary search boundary: often return high not low, or initial high=n//2 not n
- Wrong operator: target-n not target+n for complement
- Off-by-one: lst[1] for second element not lst[2]

IMPORTANT: If feedback shows TimeoutError → you have infinite loop → add visited set.
IMPORTANT: If Expected shows right-rotated list → use lst[-k:] + lst[:-k].
"""

def _parse_llm_response(raw: str, buggy_code: str) -> dict:
    """Robustly parse LLM response handling control chars and malformed JSON."""
    # Remove markdown fences
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        parts = raw.split("```")
        if len(parts) >= 2:
            raw = parts[1].strip()
            if raw.startswith("json"):
                raw = raw[4:].strip()

    # Find JSON boundaries
    start = raw.find("{")
    end   = raw.rfind("}") + 1
    if start >= 0 and end > start:
        raw = raw[start:end]

    # Try direct parse
    try:
        parsed = json.loads(raw)
        return {
            "fixed_code": parsed.get("fixed_code", ""),
            "explanation": parsed.get("explanation"),
        }
    except json.JSONDecodeError:
        pass

    # Fix literal control characters inside JSON strings
    try:
        fixed  = re.sub(r'(?<!\\)\n', r'\\n', raw)
        fixed  = re.sub(r'(?<!\\)\t', r'\\t', fixed)
        fixed  = re.sub(r'(?<!\\)\r', r'\\r', fixed)
        parsed = json.loads(fixed)
        code   = parsed.get("fixed_code", "")
        if "\\n" in code:
            code = code.replace("\\n", "\n").replace("\\t", "\t")
        return {"fixed_code": code, "explanation": parsed.get("explanation")}
    except json.JSONDecodeError:
        pass

    # Last resort: regex extraction
    code_match = re.search(r'"fixed_code"\s*:\s*"((?:[^"\\]|\\.)*)"', raw, re.DOTALL)
    exp_match  = re.search(r'"explanation"\s*:\s*"((?:[^"\\]|\\.)*)"', raw, re.DOTALL)

    if code_match:
        code = code_match.group(1).replace("\\n", "\n").replace("\\t", "\t")
        exp  = exp_match.group(1).replace("\\n", "\n") if exp_match else None
        return {"fixed_code": code, "explanation": exp}

    # Complete fallback — return buggy code unchanged
    return {"fixed_code": buggy_code, "explanation": None}


def call_llm(
    buggy_code: str,
    instructions: str,
    difficulty: str,
    feedback: Optional[str] = None,
    attempt: int = 1,
    prev_code: Optional[str] = None,
) -> dict:
    content = (
        f"Difficulty: {difficulty}\n"
        f"Instructions: {instructions}\n\n"
        f"Buggy code:\n```python\n{buggy_code}\n```\n"
    )

    if feedback and attempt > 1:
        content += (
            f"\nPREVIOUS FIX FAILED. Feedback:\n{feedback}\n\n"
            f"Your previous code:\n```python\n{prev_code or ''}\n```\n"
            "ANALYZE THE FEEDBACK CAREFULLY:\n"
            "- Look at Input/Expected/Got for each failing test\n"
            "- If Got shows wrong rotation direction: use lst[-k:] + lst[:-k] for RIGHT rotate\n"
            "- If TimeoutError: add visited=set([start]) before queue in graph code\n"
            "- Try a COMPLETELY DIFFERENT fix.\n"
        )

    if difficulty == "hard":
        hint_match = re.search(r'[Mm]ention[:\s]+([^.]+?)(?:\.|$)', instructions)
        if hint_match:
            hints = hint_match.group(1).strip()
            content += f"\nFor explanation, you MUST mention these concepts: {hints}\n"
        content += "Explanation counts for 30% of reward — make it detailed and specific.\n"

    try:
        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": content},
            ],
            max_tokens=1500,
            temperature=0.1 if attempt == 1 else 0.4,
        )
        raw = resp.choices[0].message.content.strip()
        return _parse_llm_response(raw, buggy_code)
    except Exception as e:
        print(f"# LLM error: {e}", file=sys.stderr)
        return {"fixed_code": buggy_code, "explanation": None}


# ── Episode ───────────────────────────────────────────────────────────────────
def run_episode(env_url: str, difficulty: str) -> tuple:
    """Run one full episode. Returns (success, steps_taken, rewards)."""
    data         = env_reset(env_url, difficulty)
    obs          = data["observation"]
    task_id      = obs["task_id"]
    buggy_code   = obs["buggy_code"]
    instructions = obs["instructions"]

    log_start(task_id, BENCHMARK, MODEL_NAME)

    rewards: List[float] = []
    steps_taken          = 0
    success              = False
    last_feedback        = None
    last_code            = None

    for attempt in range(1, MAX_STEPS + 1):
        steps_taken = attempt
        action      = call_llm(buggy_code, instructions, difficulty, last_feedback, attempt, last_code)
        code        = action["fixed_code"]
        last_code   = code

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

        reward        = result.get("reward", 0.0)
        done          = result.get("done", False)
        obs_r         = result.get("observation", {})
        last_feedback = obs_r.get("feedback", "")

        log_step(attempt, f"fix_{difficulty}_attempt{attempt}", reward, done, None)
        rewards.append(reward)

        if reward >= 1.0:
            success = True
        if done:
            break

    # Compute normalised score for this episode (best reward achieved)
    score = max(rewards) if rewards else 0.0
    score = min(max(score, 0.0), 1.0)
    success = success or (score >= SUCCESS_SCORE_THRESHOLD)

    log_end(success, steps_taken, score, rewards)
    return success, steps_taken, rewards


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Code Debug Environment Baseline Agent")
    parser.add_argument("--url",        default=ENV_URL)
    parser.add_argument("--difficulty", default=None, choices=["easy", "medium", "hard", "all"])
    args = parser.parse_args()
    url  = args.url.rstrip("/")

    if not API_KEY:
        print(
            "# Missing API key. Set one of: API_KEY, GROQ_API_KEY, OPENAI_API_KEY, HF_TOKEN (or lowercase variants)",
            file=sys.stderr,
            flush=True,
        )
        sys.exit(1)
    print(f"# Using API key from {API_KEY_SOURCE}", file=sys.stderr, flush=True)

    # Health check
    try:
        requests.get(f"{url}/health", timeout=10).raise_for_status()
        print(f"# Environment healthy at {url}", file=sys.stderr, flush=True)
    except Exception as e:
        print(f"# Health check failed: {e}", file=sys.stderr)
        sys.exit(1)

    diffs = ["easy", "medium", "hard"] if args.difficulty in (None, "all") else [args.difficulty]

    all_rewards: List[float] = []
    successes:   List[bool]  = []

    for d in diffs:
        ok, _, rewards = run_episode(url, d)
        all_rewards.extend(rewards)
        successes.append(ok)
        time.sleep(0.5)

    avg = round(sum(all_rewards) / len(all_rewards), 3) if all_rewards else 0.0
    print(
        f"# SUMMARY: {sum(successes)}/{len(diffs)} tasks solved | avg_reward={avg}",
        file=sys.stderr, flush=True,
    )


if __name__ == "__main__":
    main()