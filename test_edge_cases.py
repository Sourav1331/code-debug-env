#!/usr/bin/env python3
"""Test edge cases that might cause 500 errors"""

from server.tasks.task_easy import get_task_by_id
from server.graders.grader_easy import grade_easy

# Test easy_014 with potentially bad code
task = get_task_by_id('easy_014')

print("="*60)
print("Testing easy_014 with various bad codes")
print("="*60)

# Test 1: Code with infinite loop
print("\n1. Testing with infinite loop code:")
bad_code1 = """
def longest_word_length(sentence):
    while True:
        pass
"""
try:
    reward, passed, total, feedback, results = grade_easy(bad_code1, task)
    print(f"Result: {passed}/{total}, reward={reward}")
    print(f"Feedback: {feedback[:200]}...")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")

# Test 2: Code that doesn't return anything
print("\n2. Testing with code that returns None:")
bad_code2 = """
def longest_word_length(sentence):
    words = sentence.split()
    # forgot to return
"""
try:
    reward, passed, total, feedback, results = grade_easy(bad_code2, task)
    print(f"Result: {passed}/{total}, reward={reward}")
    print(f"Feedback: {feedback[:200]}...")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")

# Test 3: Code with syntax error
print("\n3. Testing with syntax error:")
bad_code3 = """
def longest_word_length(sentence:
    return max(len(w) for w in sentence.split())
"""
try:
    reward, passed, total, feedback, results = grade_easy(bad_code3, task)
    print(f"Result: {passed}/{total}, reward={reward}")
    print(f"Feedback: {feedback[:200]}...")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")

# Test 4: Code with empty string input handling issue
print("\n4. Testing with code that might fail on empty string:")
bad_code4 = """
def longest_word_length(sentence):
    words = sentence.split()
    return max(len(w) for w in words)  # This will fail if words is empty!
"""
try:
    # Temporarily add an empty string test
    task_copy = task.copy()
    task_copy['test_cases'] = [{"input": "", "expected": 0}]
    reward, passed, total, feedback, results = grade_easy(bad_code4, task_copy)
    print(f"Result: {passed}/{total}, reward={reward}")
    print(f"Feedback: {feedback[:200]}...")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")

# Test 5: Normal test cases
print("\n5. Testing with normal test cases:")
try:
    reward, passed, total, feedback, results = grade_easy(bad_code4, task)
    print(f"Result: {passed}/{total}, reward={reward}")
    for result in results:
        print(f"  Test {result['test_id']}: {'✅' if result['passed'] else '❌'} - expected={result['expected']}, got={result['got']}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
