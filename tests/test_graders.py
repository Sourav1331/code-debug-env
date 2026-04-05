# tests/test_graders.py
# Basic tests to verify all graders work correctly.
# Run: python -m pytest tests/ -v

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.graders.grader_easy import grade_easy
from server.graders.grader_medium import grade_medium
from server.graders.grader_hard import grade_hard
from server.tasks.task_easy import EASY_TASKS
from server.tasks.task_medium import MEDIUM_TASKS
from server.tasks.task_hard import HARD_TASKS


def test_easy_tasks_count():
    assert len(EASY_TASKS) == 15, f"Expected 15 easy tasks, got {len(EASY_TASKS)}"


def test_medium_tasks_count():
    assert len(MEDIUM_TASKS) == 15, f"Expected 15 medium tasks, got {len(MEDIUM_TASKS)}"


def test_hard_tasks_count():
    assert len(HARD_TASKS) == 15, f"Expected 15 hard tasks, got {len(HARD_TASKS)}"


def test_easy_correct_fix_scores_1():
    for task in EASY_TASKS:
        reward, passed, total, _, _ = grade_easy(task["fixed_code"], task)
        assert reward == 1.0, f"{task['task_id']} should score 1.0, got {reward}"


def test_medium_correct_fix_scores_1():
    for task in MEDIUM_TASKS:
        reward, passed, total, _, _ = grade_medium(task["fixed_code"], task)
        assert reward == 1.0, f"{task['task_id']} should score 1.0, got {reward}"


def test_hard_correct_fix_scores_high():
    for task in HARD_TASKS:
        keywords = task.get("explanation_keywords", [])
        explanation = " ".join(keywords)
        reward, passed, total, _, _ = grade_hard(task["fixed_code"], task, explanation)
        assert reward >= 0.9, f"{task['task_id']} should score >= 0.9, got {reward}"


def test_reward_range():
    for task in EASY_TASKS + MEDIUM_TASKS:
        reward, _, _, _, _ = grade_easy(task["buggy_code"], task)
        assert 0.0 <= reward <= 1.0, f"Reward out of range: {reward}"


def test_empty_code_returns_zero():
    task = EASY_TASKS[0]
    reward, passed, total, feedback, _ = grade_easy("", task)
    assert reward == 0.0


def test_buggy_code_scores_less_than_1():
    for task in EASY_TASKS[:5]:
        reward, _, _, _, _ = grade_easy(task["buggy_code"], task)
        assert reward < 1.0, f"{task['task_id']} buggy code should not score 1.0"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])