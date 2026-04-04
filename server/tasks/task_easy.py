# server/tasks/task_easy.py
# 15 single-bug tasks from real-world domains.
# Each bug is exactly ONE mistake: off-by-one, wrong operator, wrong return, etc.

import random

EASY_TASKS = [
    {
        "task_id": "easy_001",
        "domain": "data processing",
        "instructions": (
            "The function below is supposed to return the average of a list of numbers. "
            "It has exactly one bug. Fix it."
        ),
        "buggy_code": """\
def average(nums):
    total = 0
    for n in nums:
        total += n
    return total / len(nums) + 1
""",
        "fixed_code": """\
def average(nums):
    total = 0
    for n in nums:
        total += n
    return total / len(nums)
""",
        "test_cases": [
            {"input": [2, 4, 6], "expected": 4.0},
            {"input": [1, 1, 1, 1], "expected": 1.0},
            {"input": [10, 20], "expected": 15.0},
        ],
        "test_cases_description": "Checks that average([2,4,6])==4.0, average([1,1,1,1])==1.0, average([10,20])==15.0",
    },
    {
        "task_id": "easy_002",
        "domain": "string processing",
        "instructions": (
            "The function should count how many words are in a sentence. "
            "It has exactly one bug. Fix it."
        ),
        "buggy_code": """\
def count_words(sentence):
    words = sentence.split(' ')
    return len(words) - 1
""",
        "fixed_code": """\
def count_words(sentence):
    words = sentence.split()
    return len(words)
""",
        "test_cases": [
            {"input": "hello world", "expected": 2},
            {"input": "one two three four", "expected": 4},
            {"input": "single", "expected": 1},
        ],
        "test_cases_description": "Counts words in a sentence correctly",
    },
    {
        "task_id": "easy_003",
        "domain": "data processing",
        "instructions": (
            "The function should return the maximum value in a list. "
            "It has exactly one bug. Fix it."
        ),
        "buggy_code": """\
def find_max(nums):
    max_val = nums[0]
    for i in range(1, len(nums) + 1):
        if nums[i] > max_val:
            max_val = nums[i]
    return max_val
""",
        "fixed_code": """\
def find_max(nums):
    max_val = nums[0]
    for i in range(1, len(nums)):
        if nums[i] > max_val:
            max_val = nums[i]
    return max_val
""",
        "test_cases": [
            {"input": [3, 1, 4, 1, 5, 9], "expected": 9},
            {"input": [10, 2, 8], "expected": 10},
            {"input": [7], "expected": 7},
        ],
        "test_cases_description": "Finds max value in a list without IndexError",
    },
    {
        "task_id": "easy_004",
        "domain": "boolean logic",
        "instructions": (
            "The function checks if a number is even. "
            "It has exactly one bug. Fix it."
        ),
        "buggy_code": """\
def is_even(n):
    return n % 2 == 1
""",
        "fixed_code": """\
def is_even(n):
    return n % 2 == 0
""",
        "test_cases": [
            {"input": 4, "expected": True},
            {"input": 7, "expected": False},
            {"input": 0, "expected": True},
        ],
        "test_cases_description": "Correctly identifies even numbers",
    },
    {
        "task_id": "easy_005",
        "domain": "list operations",
        "instructions": (
            "The function should return the second element of a list. "
            "It has exactly one bug. Fix it."
        ),
        "buggy_code": """\
def second_element(lst):
    return lst[2]
""",
        "fixed_code": """\
def second_element(lst):
    return lst[1]
""",
        "test_cases": [
            {"input": [10, 20, 30], "expected": 20},
            {"input": ["a", "b", "c"], "expected": "b"},
            {"input": [99, 100], "expected": 100},
        ],
        "test_cases_description": "Returns correct second element (index 1)",
    },
    {
        "task_id": "easy_006",
        "domain": "math",
        "instructions": (
            "The function should compute the factorial of n. "
            "It has exactly one bug. Fix it."
        ),
        "buggy_code": """\
def factorial(n):
    if n == 0:
        return 0
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result
""",
        "fixed_code": """\
def factorial(n):
    if n == 0:
        return 1
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result
""",
        "test_cases": [
            {"input": 0, "expected": 1},
            {"input": 5, "expected": 120},
            {"input": 3, "expected": 6},
        ],
        "test_cases_description": "Correct factorial including base case factorial(0)==1",
    },
    {
        "task_id": "easy_007",
        "domain": "string processing",
        "instructions": (
            "The function should check if a string is a palindrome. "
            "It has exactly one bug. Fix it."
        ),
        "buggy_code": """\
def is_palindrome(s):
    return s == s[1:][::-1]
""",
        "fixed_code": """\
def is_palindrome(s):
    return s == s[::-1]
""",
        "test_cases": [
            {"input": "racecar", "expected": True},
            {"input": "hello", "expected": False},
            {"input": "madam", "expected": True},
        ],
        "test_cases_description": "Correctly identifies palindromes",
    },
    {
        "task_id": "easy_008",
        "domain": "data processing",
        "instructions": (
            "The function should sum all even numbers in a list. "
            "It has exactly one bug. Fix it."
        ),
        "buggy_code": """\
def sum_evens(nums):
    total = 0
    for n in nums:
        if n % 2 == 1:
            total += n
    return total
""",
        "fixed_code": """\
def sum_evens(nums):
    total = 0
    for n in nums:
        if n % 2 == 0:
            total += n
    return total
""",
        "test_cases": [
            {"input": [1, 2, 3, 4, 5, 6], "expected": 12},
            {"input": [1, 3, 5], "expected": 0},
            {"input": [2, 4], "expected": 6},
        ],
        "test_cases_description": "Sums only even numbers",
    },
    {
        "task_id": "easy_009",
        "domain": "list operations",
        "instructions": (
            "The function should reverse a string. "
            "It has exactly one bug. Fix it."
        ),
        "buggy_code": """\
def reverse_string(s):
    return s[1:][::-1]
""",
        "fixed_code": """\
def reverse_string(s):
    return s[::-1]
""",
        "test_cases": [
            {"input": "hello", "expected": "olleh"},
            {"input": "abc", "expected": "cba"},
            {"input": "x", "expected": "x"},
        ],
        "test_cases_description": "Reverses a string correctly",
    },
    {
        "task_id": "easy_010",
        "domain": "data processing",
        "instructions": (
            "The function should return the minimum value from a list. "
            "It has exactly one bug. Fix it."
        ),
        "buggy_code": """\
def find_min(nums):
    min_val = nums[0]
    for n in nums:
        if n > min_val:
            min_val = n
    return min_val
""",
        "fixed_code": """\
def find_min(nums):
    min_val = nums[0]
    for n in nums:
        if n < min_val:
            min_val = n
    return min_val
""",
        "test_cases": [
            {"input": [3, 1, 4, 1, 5], "expected": 1},
            {"input": [10, 2, 8], "expected": 2},
            {"input": [-5, 0, 5], "expected": -5},
        ],
        "test_cases_description": "Finds minimum value in a list",
    },
    {
        "task_id": "easy_011",
        "domain": "math",
        "instructions": (
            "The function should check if a number is prime. "
            "It has exactly one bug. Fix it."
        ),
        "buggy_code": """\
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, n):
        if n % i == 0:
            return True
    return False
""",
        "fixed_code": """\
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, n):
        if n % i == 0:
            return False
    return True
""",
        "test_cases": [
            {"input": 7, "expected": True},
            {"input": 4, "expected": False},
            {"input": 13, "expected": True},
        ],
        "test_cases_description": "Correctly identifies prime numbers",
    },
    {
        "task_id": "easy_012",
        "domain": "list operations",
        "instructions": (
            "The function should remove duplicates from a list while preserving order. "
            "It has exactly one bug. Fix it."
        ),
        "buggy_code": """\
def remove_duplicates(lst):
    seen = set()
    result = []
    for item in lst:
        if item in seen:
            result.append(item)
        seen.add(item)
    return result
""",
        "fixed_code": """\
def remove_duplicates(lst):
    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            result.append(item)
        seen.add(item)
    return result
""",
        "test_cases": [
            {"input": [1, 2, 2, 3, 3, 3], "expected": [1, 2, 3]},
            {"input": ["a", "b", "a"], "expected": ["a", "b"]},
            {"input": [1], "expected": [1]},
        ],
        "test_cases_description": "Removes duplicates while preserving order",
    },
    {
        "task_id": "easy_013",
        "domain": "string processing",
        "instructions": (
            "The function should capitalize the first letter of every word. "
            "It has exactly one bug. Fix it."
        ),
        "buggy_code": """\
def title_case(sentence):
    return sentence.lower()
""",
        "fixed_code": """\
def title_case(sentence):
    return sentence.title()
""",
        "test_cases": [
            {"input": "hello world", "expected": "Hello World"},
            {"input": "the quick brown fox", "expected": "The Quick Brown Fox"},
            {"input": "python", "expected": "Python"},
        ],
        "test_cases_description": "Converts sentence to title case",
    },
    {
        "task_id": "easy_014",
        "domain": "data processing",
        "instructions": (
            "The function should return the length of the longest word in a sentence. "
            "It has exactly one bug. Fix it."
        ),
        "buggy_code": """\
def longest_word_length(sentence):
    words = sentence.split()
    return min(len(w) for w in words)
""",
        "fixed_code": """\
def longest_word_length(sentence):
    words = sentence.split()
    return max(len(w) for w in words)
""",
        "test_cases": [
            {"input": "hello world", "expected": 5},
            {"input": "I am learning Python programming", "expected": 11},
            {"input": "cat", "expected": 3},
        ],
        "test_cases_description": "Returns length of the longest word",
    },
    {
        "task_id": "easy_015",
        "domain": "math",
        "instructions": (
            "The function should return n raised to the power of 2. "
            "It has exactly one bug. Fix it."
        ),
        "buggy_code": """\
def square(n):
    return n * 3
""",
        "fixed_code": """\
def square(n):
    return n * n
""",
        "test_cases": [
            {"input": 4, "expected": 16},
            {"input": 0, "expected": 0},
            {"input": -3, "expected": 9},
        ],
        "test_cases_description": "Returns n squared",
    },
]


def get_random_easy_task() -> dict:
    return random.choice(EASY_TASKS).copy()


def get_task_by_id(task_id: str) -> dict:
    for t in EASY_TASKS:
        if t["task_id"] == task_id:
            return t.copy()
    return random.choice(EASY_TASKS).copy()
