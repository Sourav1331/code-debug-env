#!/usr/bin/env python3
"""Test script to debug failing tasks"""

from server.tasks.task_easy import get_task_by_id
from server.tasks.task_hard import get_task_by_id as get_hard_task_by_id
from server.graders.grader_easy import grade_easy
from server.graders.grader_hard import grade_hard

# Test easy_014
print("="*60)
print("Testing easy_014")
print("="*60)
task_easy = get_task_by_id('easy_014')
print(f"Task ID: {task_easy['task_id']}")
print(f"Test cases: {task_easy['test_cases']}")

try:
    buggy_code = task_easy['buggy_code']
    reward, passed, total, feedback, results = grade_easy(buggy_code, task_easy)
    print(f"\nBuggy code result: {passed}/{total}, reward={reward}")
except Exception as e:
    print(f"\nERROR with buggy code: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

try:
    fixed_code = task_easy['fixed_code']
    reward, passed, total, feedback, results = grade_easy(fixed_code, task_easy)
    print(f"\nFixed code result: {passed}/{total}, reward={reward}")
    print(f"Feedback:\n{feedback}")
except Exception as e:
    print(f"\nERROR with fixed code: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# Test hard_010
print("\n" + "="*60)
print("Testing hard_010")
print("="*60)
task_hard = get_hard_task_by_id('hard_010')
print(f"Task ID: {task_hard['task_id']}")
print(f"Test cases: {task_hard['test_cases']}")

try:
    buggy_code = task_hard['buggy_code']
    reward, passed, total, feedback, results = grade_hard(buggy_code, task_hard, explanation=None)
    print(f"\nBuggy code result (no explanation): {passed}/{total}, reward={reward}")
except Exception as e:
    print(f"\nERROR with buggy code: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

try:
    fixed_code = task_hard['fixed_code']
    explanation = "The bug was that there was no visited set to track already visited nodes, which caused infinite loops in graphs with cycles."
    reward, passed, total, feedback, results = grade_hard(fixed_code, task_hard, explanation=explanation)
    print(f"\nFixed code result (with explanation): {passed}/{total}, reward={reward}")
    print(f"Feedback:\n{feedback}")
except Exception as e:
    print(f"\nERROR with fixed code: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
