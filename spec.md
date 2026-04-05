# Code Debug Environment — API Specification

## Overview
OpenEnv-compatible RL environment where LLM agents fix buggy Python code.
- 45 tasks: 15 easy + 15 medium + 15 hard
- Partial rewards: 0.33, 0.67, 1.0 based on test cases passed
- Hard tasks: reward = 0.7×code + 0.3×explanation

## Endpoints

### GET /health
```json
{"status": "ok", "environment": "code-debug-env", "version": "1.0.0"}
```

### POST /reset
```json
// Request
{"difficulty": "easy"}  // or "medium", "hard", omit for random

// Response
{
  "observation": {
    "task_id": "easy_003",
    "difficulty": "easy",
    "buggy_code": "def find_max(nums):\n    return min(nums)",
    "instructions": "The function has exactly one bug. Fix it.",
    "test_cases_description": "Finds max value in a list",
    "reward": null, "passed_tests": null, "total_tests": 3,
    "feedback": null, "done": false
  },
  "reward": 0.0, "done": false
}
```

### POST /step
```json
// Request
{"fixed_code": "def find_max(nums):\n    return max(nums)", "explanation": "optional for hard"}

// Response
{
  "observation": {
    "task_id": "easy_003", "reward": 1.0,
    "passed_tests": 3, "total_tests": 3,
    "feedback": "Test 1: ✅ Passed\n   Input: [1,2,3]\n   Expected: 3\n   Got: 3",
    "done": true
  },
  "reward": 1.0, "done": true
}
```

### GET /state
```json
{"episode_id": "uuid", "task_id": "easy_003", "difficulty": "easy",
 "step_count": 1, "max_steps": 5, "current_reward": 1.0, "best_reward": 1.0, "done": true}
```

### GET /tasks
```json
{"easy": ["easy_001",...], "medium": ["medium_001",...], "hard": ["hard_001",...], "total": 45}
```

## Reward Design
| Task | Formula |
|------|---------|
| Easy | passed/3 |
| Medium | passed/3 |
| Hard | 0.7×code_score + 0.3×explanation_score |

## Invalid Actions
- Empty code → reward=0.0 + penalty feedback
- Infinite loop → TimeoutError → reward=0.0 + hint to add visited set

## Episode Rules
- Max 5 steps per episode
- Ends when reward=1.0 OR max steps reached
- 3 deterministic test cases per task
