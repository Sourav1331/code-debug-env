#!/usr/bin/env python3
# validator/pre_submit_check.py
# Run this BEFORE submitting to catch any disqualifying issues.
#
# Usage:
#   python validator/pre_submit_check.py
#   python validator/pre_submit_check.py --url https://your-space.hf.space

import os
import sys
import json
import argparse
import requests

PASS = "✅"
FAIL = "❌"
WARN = "⚠️"

results = []


def check(name: str, passed: bool, detail: str = ""):
    status = PASS if passed else FAIL
    results.append({"check": name, "passed": passed, "detail": detail})
    print(f"  {status} {name}" + (f": {detail}" if detail else ""))
    return passed


def run_checks(base_url: str):
    print(f"\n{'='*60}")
    print(f"  Code Debug Environment — Pre-Submission Validator")
    print(f"  Target: {base_url}")
    print(f"{'='*60}\n")

    all_passed = True

    # ── 1. Health check ───────────────────────────────────────────
    print("[ CHECK 1 ] Health endpoint")
    try:
        r = requests.get(f"{base_url}/health", timeout=10)
        passed = r.status_code == 200 and r.json().get("status") == "ok"
        check("GET /health returns 200 with status=ok", passed, f"HTTP {r.status_code}")
        all_passed &= passed
    except Exception as e:
        check("GET /health", False, str(e))
        all_passed = False

    # ── 2. Reset responds ─────────────────────────────────────────
    print("\n[ CHECK 2 ] POST /reset")
    obs = None
    for difficulty in ["easy", "medium", "hard"]:
        try:
            r = requests.post(f"{base_url}/reset", json={"difficulty": difficulty}, timeout=15)
            data = r.json()
            obs = data.get("observation", {})
            has_fields = all(k in obs for k in ["task_id", "difficulty", "buggy_code", "instructions"])
            passed = r.status_code == 200 and has_fields
            check(f"reset(difficulty='{difficulty}') returns valid observation", passed,
                  f"task_id={obs.get('task_id', 'MISSING')}")
            all_passed &= passed
        except Exception as e:
            check(f"reset(difficulty='{difficulty}')", False, str(e))
            all_passed = False

    # ── 3. Step responds ──────────────────────────────────────────
    print("\n[ CHECK 3 ] POST /step")
    try:
        # Reset first to get a fresh task
        r = requests.post(f"{base_url}/reset", json={"difficulty": "easy"}, timeout=15)
        buggy_code = r.json()["observation"]["buggy_code"]

        # Submit the buggy code as-is (reward may be 0, that's fine)
        r = requests.post(f"{base_url}/step", json={"fixed_code": buggy_code}, timeout=15)
        data = r.json()
        has_reward = "reward" in data and isinstance(data["reward"], (int, float))
        has_done = "done" in data and isinstance(data["done"], bool)
        reward_in_range = 0.0 <= data.get("reward", -1) <= 1.0
        passed = r.status_code == 200 and has_reward and has_done and reward_in_range
        check("step() returns reward in [0.0, 1.0] and done flag", passed,
              f"reward={data.get('reward')}, done={data.get('done')}")
        all_passed &= passed
    except Exception as e:
        check("POST /step", False, str(e))
        all_passed = False

    # ── 4. State responds ─────────────────────────────────────────
    print("\n[ CHECK 4 ] GET /state")
    try:
        r = requests.get(f"{base_url}/state", timeout=10)
        data = r.json()
        has_fields = all(k in data for k in ["episode_id", "step_count", "difficulty"])
        passed = r.status_code == 200 and has_fields
        check("GET /state returns episode_id, step_count, difficulty", passed)
        all_passed &= passed
    except Exception as e:
        check("GET /state", False, str(e))
        all_passed = False

    # ── 5. 3 difficulties all work ────────────────────────────────
    print("\n[ CHECK 5 ] All 3 task difficulties functional")
    for difficulty in ["easy", "medium", "hard"]:
        try:
            r = requests.post(f"{base_url}/reset", json={"difficulty": difficulty}, timeout=15)
            obs = r.json()["observation"]
            passed = obs.get("difficulty") == difficulty
            check(f"difficulty='{difficulty}' task loads correctly",
                  passed, f"got difficulty={obs.get('difficulty')}")
            all_passed &= passed
        except Exception as e:
            check(f"difficulty='{difficulty}'", False, str(e))
            all_passed = False

    # ── 6. Reward range on perfect answer ─────────────────────────
    print("\n[ CHECK 6 ] Reward range validation (correct fix)")
    try:
        from server.tasks.task_easy import EASY_TASKS
        task = EASY_TASKS[0]
        # Reset with the first easy task
        r = requests.post(f"{base_url}/reset", json={"difficulty": "easy"}, timeout=15)
        # Submit the known correct fix
        r = requests.post(f"{base_url}/step",
                          json={"fixed_code": task["fixed_code"]}, timeout=15)
        data = r.json()
        reward = data.get("reward", -1)
        passed = 0.0 <= reward <= 1.0
        check(f"Submitting correct fix yields reward in [0.0, 1.0]", passed,
              f"reward={reward}")
        all_passed &= passed
    except Exception as e:
        check("Reward range check", False, str(e))
        all_passed = False

    # ── 7. openenv.yaml exists ────────────────────────────────────
    print("\n[ CHECK 7 ] Project structure")
    required_files = [
        "openenv.yaml",
        "inference.py",
        "models.py",
        "server/app.py",
        "server/environment.py",
        "server/Dockerfile",
        "server/requirements.txt",
        "pyproject.toml",
        "README.md",
    ]
    for fname in required_files:
        exists = os.path.exists(fname)
        check(f"File exists: {fname}", exists)
        all_passed &= exists

    # ── 8. inference.py has required log format ───────────────────
    print("\n[ CHECK 8 ] inference.py log format")
    try:
        with open("inference.py") as f:
            content = f.read()
        has_start = '"type": "START"' in content
        has_step = '"type": "STEP"' in content
        has_end = '"type": "END"' in content
        check("inference.py emits [START] logs", has_start)
        check("inference.py emits [STEP] logs", has_step)
        check("inference.py emits [END] logs", has_end)
        all_passed &= has_start and has_step and has_end
    except Exception as e:
        check("inference.py log format", False, str(e))
        all_passed = False

    # ── Final summary ─────────────────────────────────────────────
    total = len(results)
    passed_count = sum(1 for r in results if r["passed"])

    print(f"\n{'='*60}")
    print(f"  Results: {passed_count}/{total} checks passed")
    if all_passed:
        print(f"  {PASS} ALL CHECKS PASSED — you are safe to submit!")
    else:
        failed = [r["check"] for r in results if not r["passed"]]
        print(f"  {FAIL} FAILED CHECKS — fix these before submitting:")
        for f in failed:
            print(f"     • {f}")
    print(f"{'='*60}\n")

    return all_passed


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:7860",
                        help="Base URL of the running environment")
    args = parser.parse_args()

    success = run_checks(args.url.rstrip("/"))
    sys.exit(0 if success else 1)
