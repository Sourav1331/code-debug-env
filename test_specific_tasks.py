#!/usr/bin/env python3
"""Test medium_005 and hard_011 specifically"""

from server.tasks.task_medium import get_task_by_id as get_medium_task
from server.tasks.task_hard import get_task_by_id as get_hard_task
from server.graders.grader_medium import grade_medium
from server.graders.grader_hard import grade_hard

print("="*70)
print("Testing MEDIUM_005")
print("="*70)
task = get_medium_task('medium_005')
print(f"Task ID: {task['task_id']}")
print(f"Instructions: {task['instructions']}")
print(f"\nBuggy code:")
print(task['buggy_code'])
print(f"\nFixed code:")
print(task['fixed_code'])
print(f"\nTest cases: {task['test_cases']}")

# Test with buggy code
print("\n--- Testing BUGGY code ---")
try:
    reward, passed, total, feedback, results = grade_medium(task['buggy_code'], task)
    print(f"Result: {passed}/{total}, reward={reward:.2f}")
    print(f"Feedback:\n{feedback}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# Test with fixed code
print("\n--- Testing FIXED code ---")
try:
    reward, passed, total, feedback, results = grade_medium(task['fixed_code'], task)
    print(f"Result: {passed}/{total}, reward={reward:.2f}")
    for r in results:
        print(f"  Test {r['test_id']}: {'✅' if r['passed'] else '❌'}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("Testing HARD_011")
print("="*70)
task = get_hard_task('hard_011')
print(f"Task ID: {task['task_id']}")
print(f"Instructions: {task['instructions']}")
print(f"\nBuggy code:")
print(task['buggy_code'])
print(f"\nFixed code:")
print(task['fixed_code'])
print(f"\nTest cases: {task['test_cases']}")
print(f"\nExplanation keywords: {task['explanation_keywords']}")

# Test with buggy code (no explanation)
print("\n--- Testing BUGGY code (no explanation) ---")
try:
    reward, passed, total, feedback, results = grade_hard(task['buggy_code'], task, explanation=None)
    print(f"Result: {passed}/{total}, reward={reward:.2f}")
    print(f"Feedback:\n{feedback[:300]}...")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# Test with fixed code and good explanation
print("\n--- Testing FIXED code (with good explanation) ---")
explanation = "The bug was in the iteration order. The inner loop must iterate backward (from capacity down to weights[i]) to prevent using the same item multiple times, which would turn this into an unbounded knapsack instead of 0/1 knapsack."
try:
    reward, passed, total, feedback, results = grade_hard(task['fixed_code'], task, explanation=explanation)
    print(f"Result: {passed}/{total}, reward={reward:.2f}")
    for r in results:
        print(f"  Test {r['test_id']}: {'✅' if r['passed'] else '❌'}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# Test some potentially problematic LLM-generated code
print("\n" + "="*70)
print("Testing POTENTIALLY BAD LLM CODE for medium_005")
print("="*70)

bad_code_1 = """
def count_frequency(lst):
    freq = {}
    for item in lst:
        freq[item] = freq.get(item, 0) + 1
    return freq
"""
print("Testing: Using .get() method (should work)")
try:
    reward, passed, total, feedback, results = grade_medium(bad_code_1, get_medium_task('medium_005'))
    print(f"Result: {passed}/{total}, reward={reward:.2f}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")

bad_code_2 = """
def count_frequency(lst):
    from collections import Counter
    return dict(Counter(lst))
"""
print("\nTesting: Using Counter (should work)")
try:
    reward, passed, total, feedback, results = grade_medium(bad_code_2, get_medium_task('medium_005'))
    print(f"Result: {passed}/{total}, reward={reward:.2f}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")

bad_code_3 = """
def count_frequency(lst):
    freq = {}
    for item in lst:
        if item in freq:
            freq[item] = freq[item] + 1  # Still wrong - should be +=
        else:
            freq[item] = freq[item] + 1  # This will cause KeyError!
    return freq
"""
print("\nTesting: Code with KeyError (should fail gracefully)")
try:
    reward, passed, total, feedback, results = grade_medium(bad_code_3, get_medium_task('medium_005'))
    print(f"Result: {passed}/{total}, reward={reward:.2f}")
    print(f"Feedback: {feedback[:200]}...")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
