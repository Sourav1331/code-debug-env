# Code Debug Environment — Specification

## Overview

The Code Debug Environment is an OpenEnv-compatible RL environment where an LLM agent diagnoses and fixes buggy Python code across three difficulty levels.

---

## API Specification

### POST /reset
Start a new episode.

**Request:**
```json
{"difficulty": "easy"}
```

**Response:**
```json
{
  "observation": {
    "task_id": "easy_003",
    "difficulty": "easy",
    "buggy_code": "def find_max(nums):\n    return min(nums)",
    "instructions": "The function has exactly one bug. Fix it.",
    "test_cases_description": "Finds max value in a list",
    "reward": null,
    "passed_tests": null,
    "total_tests": 3,
    "feedback": null,
    "done": false
  },
  "reward": 0.0,
  "done": false
}
```

---

### POST /step
Submit a code fix.

**Request:**
```json
{
  "fixed_code": "def find_max(nums):\n    return max(nums)",
  "explanation": "Optional for hard tasks"
}
```

**Response:**
```json
{
  "observation": {
    "task_id": "easy_003",
    "reward": 1.0,
    "passed_tests": 3,
    "total_tests": 3,
    "feedback": "Test 1: ✅ Passed\n   Input: [1,2,3]\n   Expected: 3\n   Got: 3",
    "done": true
  },
  "reward": 1.0,
  "done": true
}
```

---

### GET /state
Returns current episode state.

```json
{
  "episode_id": "uuid",
  "task_id": "easy_003",
  "difficulty": "easy",
  "step_count": 1,
  "max_steps": 5,
  "current_reward": 1.0,
  "best_reward": 1.0,
  "done": true
}
```

---

### GET /health
```json
{"status": "ok", "environment": "code-debug-env", "version": "1.0.0"}
```

---

## Reward Function

### Easy & Medium
```
reward = passed_tests / total_tests
```
- 3/3 → 1.00
- 2/3 → 0.67
- 1/3 → 0.33
- 0/3 → 0.00

### Hard
```
reward = 0.7 × test_score + 0.3 × explanation_score
```

### Invalid Actions
- Empty code → reward = 0.0 + feedback message
- Non-Python code → reward = 0.0 + feedback message

---

## Episode Rules

- Max 5 steps per episode
- Episode ends when reward = 1.0 OR max steps reached
- Each step runs fixed_code against 3 deterministic test cases
- Feedback shows Input, Expected, Got for each test

---

## Task Domains

| Domain | Examples |
|---|---|
| List operations | second element, max, flatten |
| String algorithms | palindrome, reverse, word count |
| Math | fibonacci, factorial, square root |
| Sorting | bubble sort, binary search |
| Data processing | JSON parsing, API validation |
| Graph algorithms | BFS, cycle detection |
| Dynamic programming | knapsack, longest subsequence |