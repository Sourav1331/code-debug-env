# Code Debug Environment

An [OpenEnv](https://github.com/meta-pytorch/OpenEnv)-compatible RL environment where an LLM agent diagnoses and fixes buggy Python code across three difficulty levels.

---

## Overview

| Property | Value |
|---|---|
| Domain | Real-world Python code debugging |
| Tasks | 45 total (15 easy + 15 medium + 15 hard) |
| Difficulties | easy → medium → hard |
| Reward Range | 0.0 – 1.0 (partial, proportional) |
| Max Steps/Episode | 3 |
| API | OpenEnv standard: `/reset`, `/step`, `/state` |

---

## Environment Description

The agent receives a buggy Python function and must fix it. Tasks come from real-world domains: data processing, string algorithms, API validation, sorting, dynamic programming, and graph algorithms.

- **Easy**: One bug (wrong operator, off-by-one, incorrect return). Reward proportional to test pass rate.
- **Medium**: Two bugs (logic bug + edge case). Reward proportional to test pass rate.
- **Hard**: One algorithmic bug + agent must explain what was wrong. Reward = 0.7 × test score + 0.3 × explanation quality.

---

## Action Space

```json
{
  "fixed_code": "string — the corrected Python function (required)",
  "explanation": "string — explanation of what was wrong (required for hard tasks)"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `fixed_code` | `str` | Always | Complete corrected Python function as a string |
| `explanation` | `str` | Hard tasks | Describe the bug and why your fix is correct |

---

## Observation Space

Returned by `/reset` and `/step`:

```json
{
  "task_id": "easy_003",
  "difficulty": "easy",
  "buggy_code": "def find_max(nums):\n    ...",
  "instructions": "The function has exactly one bug. Fix it.",
  "test_cases_description": "Finds max value in a list without IndexError",
  "reward": 0.67,
  "passed_tests": 2,
  "total_tests": 3,
  "feedback": "Test 1: ✅ ...\nTest 2: ✅ ...\nTest 3: ❌ ...",
  "done": false
}
```

| Field | Type | Description |
|---|---|---|
| `task_id` | `str` | Unique task identifier |
| `difficulty` | `str` | `easy` / `medium` / `hard` |
| `buggy_code` | `str` | Buggy Python function to fix |
| `instructions` | `str` | Task instructions |
| `test_cases_description` | `str` | What the test cases check |
| `reward` | `float\|null` | Score from last step (null on reset) |
| `passed_tests` | `int\|null` | Tests passed (null on reset) |
| `total_tests` | `int` | Total number of test cases |
| `feedback` | `str\|null` | Detailed per-test feedback |
| `done` | `bool` | True when episode is complete |

---

## Reward Function

### Easy & Medium
```
reward = passed_tests / total_tests
```
- 3/3 tests → 1.0
- 2/3 tests → 0.67
- 1/3 tests → 0.33
- 0/3 tests → 0.0

### Hard
```
reward = 0.7 × test_score + 0.3 × explanation_score
```
Explanation is scored by matching key algorithmic concepts. Partial credit is given.

---

## Setup & Local Run

### Prerequisites
- Python 3.10+
- Docker
- Hugging Face CLI

### Install
```bash
git clone https://github.com/YOUR_USERNAME/code-debug-env
cd code-debug-env
pip install -e .
# Also clone OpenEnv for PYTHONPATH
git clone https://github.com/meta-pytorch/OpenEnv.git
export PYTHONPATH=$PYTHONPATH:OpenEnv:OpenEnv/src:.
```

### Run locally
```bash
uvicorn server.app:app --host 0.0.0.0 --port 7860 --reload
```

### Run with Docker
```bash
docker build -f server/Dockerfile -t code-debug-env .
docker run -p 7860:7860 code-debug-env
```

### Test the API
```bash
# Health check
curl http://localhost:7860/health

# Reset (easy task)
curl -X POST http://localhost:7860/reset \
  -H "Content-Type: application/json" \
  -d '{"difficulty": "easy"}'

# Submit a fix
curl -X POST http://localhost:7860/step \
  -H "Content-Type: application/json" \
  -d '{"fixed_code": "def find_max(nums):\n    return max(nums)"}'

# Check state
curl http://localhost:7860/state
```

---

## Run Baseline Inference

```bash
export API_BASE_URL="https://api.openai.com/v1"
export MODEL_NAME="gpt-4o-mini"
export HF_TOKEN="your-api-key"

# Run all 3 difficulties
python inference.py --url http://localhost:7860

# Run specific difficulty
python inference.py --url http://localhost:7860 --difficulty hard
```

---

## Pre-Submission Validation

Run before submitting to catch any disqualifying issues:

```bash
# Start the environment first, then:
python validator/pre_submit_check.py --url http://localhost:7860

# Or against your HF Space:
python validator/pre_submit_check.py --url https://YOUR_SPACE.hf.space
```

---

## Deploy to Hugging Face Spaces

```bash
# Login
huggingface-cli login

# Create space and push
huggingface-cli repo create code-debug-env --type space --space_sdk docker
cd code-debug-env
git init
git remote add origin https://huggingface.co/spaces/YOUR_USERNAME/code-debug-env
git add .
git commit -m "Initial commit"
git push origin main
```

---

## Project Structure

```
code-debug-env/
├── openenv.yaml          ← OpenEnv manifest
├── inference.py          ← Baseline agent (root, required)
├── pyproject.toml        ← Dependencies
├── README.md
├── models.py             ← Pydantic Action/Observation/State
├── client.py             ← EnvClient for training loops
├── __init__.py
├── server/
│   ├── app.py            ← FastAPI: /reset /step /state /health
│   ├── environment.py    ← Core episode logic
│   ├── tasks/
│   │   ├── task_easy.py  ← 15 single-bug tasks
│   │   ├── task_medium.py← 15 two-bug tasks
│   │   └── task_hard.py  ← 15 algorithmic tasks
│   ├── graders/
│   │   ├── grader_easy.py
│   │   ├── grader_medium.py
│   │   └── grader_hard.py
│   ├── requirements.txt
│   └── Dockerfile
└── validator/
    └── pre_submit_check.py
```
