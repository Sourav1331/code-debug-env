# tests/test_graders.py — Run: python -m pytest tests/ -v
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.graders.grader_easy import grade_easy
from server.graders.grader_medium import grade_medium
from server.graders.grader_hard import grade_hard
from server.tasks.task_easy import EASY_TASKS
from server.tasks.task_medium import MEDIUM_TASKS
from server.tasks.task_hard import HARD_TASKS


def test_task_counts():
    assert len(EASY_TASKS) == 15
    assert len(MEDIUM_TASKS) == 15
    assert len(HARD_TASKS) == 15

def test_easy_correct_scores_1():
    for t in EASY_TASKS:
        r, _, _, _, _ = grade_easy(t["fixed_code"], t)
        assert r == 1.0, f"{t['task_id']} expected 1.0 got {r}"

def test_medium_correct_scores_1():
    for t in MEDIUM_TASKS:
        r, _, _, _, _ = grade_medium(t["fixed_code"], t)
        assert r == 1.0, f"{t['task_id']} expected 1.0 got {r}"

def test_hard_correct_scores_high():
    for t in HARD_TASKS:
        keywords = t.get("explanation_keywords", [])
        r, _, _, _, _ = grade_hard(t["fixed_code"], t, " ".join(keywords))
        assert r >= 0.9, f"{t['task_id']} expected >=0.9 got {r}"

def test_reward_in_range():
    for t in EASY_TASKS:
        r, _, _, _, _ = grade_easy(t["buggy_code"], t)
        assert 0.0 <= r <= 1.0

def test_buggy_scores_less_than_1():
    for t in EASY_TASKS[:5]:
        r, _, _, _, _ = grade_easy(t["buggy_code"], t)
        assert r < 1.0, f"{t['task_id']} buggy code should not score 1.0"

def test_empty_code_returns_zero():
    r, _, _, _, _ = grade_easy("", EASY_TASKS[0])
    assert r == 0.0

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
