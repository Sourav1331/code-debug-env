# server/tasks/task_medium.py
# 15 medium tasks: each function has TWO bugs (logic + edge case).
# Agent must fix both to get full reward.

import random

MEDIUM_TASKS = [
    {
        "task_id": "medium_001",
        "domain": "data processing",
        "instructions": (
            "The function should return the average of a list, returning 0.0 for an empty list. "
            "It has TWO bugs. Fix both."
        ),
        "buggy_code": """\
def safe_average(nums):
    if len(nums) == 0:
        return -1
    total = 0
    for n in nums:
        total += n
    return total / len(nums) + 1
""",
        "fixed_code": """\
def safe_average(nums):
    if len(nums) == 0:
        return 0.0
    total = 0
    for n in nums:
        total += n
    return total / len(nums)
""",
        "test_cases": [
            {"input": [2, 4, 6], "expected": 4.0},
            {"input": [], "expected": 0.0},
            {"input": [10], "expected": 10.0},
        ],
        "test_cases_description": "Average of list; empty list returns 0.0, not -1; no +1 added to result",
    },
    {
        "task_id": "medium_002",
        "domain": "string processing",
        "instructions": (
            "The function should count vowels in a string (case-insensitive). "
            "It has TWO bugs. Fix both."
        ),
        "buggy_code": """\
def count_vowels(s):
    vowels = 'aeiou'
    count = 0
    for ch in s:
        if ch in vowels:
            count += 1
    return count + 1
""",
        "fixed_code": """\
def count_vowels(s):
    vowels = 'aeiouAEIOU'
    count = 0
    for ch in s:
        if ch in vowels:
            count += 1
    return count
""",
        "test_cases": [
            {"input": "hello", "expected": 2},
            {"input": "HELLO", "expected": 2},
            {"input": "rhythm", "expected": 0},
        ],
        "test_cases_description": "Counts vowels case-insensitively without off-by-one",
    },
    {
        "task_id": "medium_003",
        "domain": "list operations",
        "instructions": (
            "The function should flatten a list of lists into one list. "
            "It has TWO bugs. Fix both."
        ),
        "buggy_code": """\
def flatten(lists):
    result = []
    for sublist in lists:
        for item in sublist:
            result.append(item)
    return result[1:]
""",
        "fixed_code": """\
def flatten(lists):
    result = []
    for sublist in lists:
        for item in sublist:
            result.append(item)
    return result
""",
        "test_cases": [
            {"input": [[[1, 2], [3, 4]]], "expected": [1, 2, 3, 4]},
            {"input": [[[1]]], "expected": [1]},
            {"input": [[[], [5, 6]]], "expected": [5, 6]},
        ],
        "test_cases_description": "Flattens nested lists correctly without slicing off first element",
    },
    {
        "task_id": "medium_004",
        "domain": "math",
        "instructions": (
            "The function should return the GCD of two numbers. "
            "It has TWO bugs. Fix both."
        ),
        "buggy_code": """\
def gcd(a, b):
    while b != 0:
        a = b
        b = a % b
    return b
""",
        "fixed_code": """\
def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a
""",
        "test_cases": [
            {"input": [12, 8], "expected": 4},
            {"input": [100, 75], "expected": 25},
            {"input": [7, 3], "expected": 1},
        ],
        "test_cases_description": "Correct GCD using Euclidean algorithm",
    },
    {
        "task_id": "medium_005",
        "domain": "data processing",
        "instructions": (
            "The function should count frequency of each element in a list and return a dict. "
            "It has TWO bugs. Fix both."
        ),
        "buggy_code": """\
def count_frequency(lst):
    freq = {}
    for item in lst:
        if item in freq:
            freq[item] = 1
        else:
            freq[item] = freq[item] + 1
    return freq
""",
        "fixed_code": """\
def count_frequency(lst):
    freq = {}
    for item in lst:
        if item in freq:
            freq[item] += 1
        else:
            freq[item] = 1
    return freq
""",
        "test_cases": [
            {"input": [1, 2, 2, 3, 3, 3], "expected": {1: 1, 2: 2, 3: 3}},
            {"input": ["a", "b", "a"], "expected": {"a": 2, "b": 1}},
            {"input": [5], "expected": {5: 1}},
        ],
        "test_cases_description": "Correctly counts frequency; swapped if/else logic fixed",
    },
    {
        "task_id": "medium_006",
        "domain": "string processing",
        "instructions": (
            "The function should check if two strings are anagrams (case-insensitive). "
            "It has TWO bugs. Fix both."
        ),
        "buggy_code": """\
def are_anagrams(s1, s2):
    if len(s1) != len(s2):
        return True
    return sorted(s1) == sorted(s2)
""",
        "fixed_code": """\
def are_anagrams(s1, s2):
    if len(s1) != len(s2):
        return False
    return sorted(s1.lower()) == sorted(s2.lower())
""",
        "test_cases": [
            {"input": ["listen", "silent"], "expected": True},
            {"input": ["hello", "world"], "expected": False},
            {"input": ["Listen", "Silent"], "expected": True},
        ],
        "test_cases_description": "Anagram check with case-insensitivity and correct early-return logic",
    },
    {
        "task_id": "medium_007",
        "domain": "data processing",
        "instructions": (
            "The function should merge two sorted lists into one sorted list. "
            "It has TWO bugs. Fix both."
        ),
        "buggy_code": """\
def merge_sorted(a, b):
    result = []
    i, j = 0, 0
    while i < len(a) and j < len(b):
        if a[i] < b[j]:
            result.append(b[j])
            i += 1
        else:
            result.append(a[i])
            j += 1
    result.extend(a[i:])
    result.extend(b[j:])
    return result
""",
        "fixed_code": """\
def merge_sorted(a, b):
    result = []
    i, j = 0, 0
    while i < len(a) and j < len(b):
        if a[i] < b[j]:
            result.append(a[i])
            i += 1
        else:
            result.append(b[j])
            j += 1
    result.extend(a[i:])
    result.extend(b[j:])
    return result
""",
        "test_cases": [
            {"input": [[1, 3, 5], [2, 4, 6]], "expected": [1, 2, 3, 4, 5, 6]},
            {"input": [[1, 2], [3, 4]], "expected": [1, 2, 3, 4]},
            {"input": [[], [1, 2]], "expected": [1, 2]},
        ],
        "test_cases_description": "Merges two sorted lists correctly",
    },
    {
        "task_id": "medium_008",
        "domain": "API handler",
        "instructions": (
            "The function validates a user registration dict. "
            "It should return True only if 'email' and 'password' are present and password >= 8 chars. "
            "It has TWO bugs. Fix both."
        ),
        "buggy_code": """\
def validate_registration(data):
    if 'email' not in data:
        return False
    if len(data.get('password', '')) > 8:
        return False
    return True
""",
        "fixed_code": """\
def validate_registration(data):
    if 'email' not in data:
        return False
    if len(data.get('password', '')) < 8:
        return False
    return True
""",
        "test_cases": [
            {"input": {"email": "a@b.com", "password": "strongpass"}, "expected": True},
            {"input": {"email": "a@b.com", "password": "short"}, "expected": False},
            {"input": {"password": "strongpass"}, "expected": False},
        ],
        "test_cases_description": "Validates registration with correct password length check",
    },
    {
        "task_id": "medium_009",
        "domain": "math",
        "instructions": (
            "The function should return True if a number is a perfect square. "
            "It has TWO bugs. Fix both."
        ),
        "buggy_code": """\
def is_perfect_square(n):
    if n < 0:
        return True
    root = int(n ** 0.5)
    return root * root != n
""",
        "fixed_code": """\
def is_perfect_square(n):
    if n < 0:
        return False
    root = int(n ** 0.5)
    return root * root == n
""",
        "test_cases": [
            {"input": 16, "expected": True},
            {"input": 15, "expected": False},
            {"input": -4, "expected": False},
        ],
        "test_cases_description": "Correctly identifies perfect squares including negative number check",
    },
    {
        "task_id": "medium_010",
        "domain": "data processing",
        "instructions": (
            "The function should return the top-k most frequent elements in a list. "
            "It has TWO bugs. Fix both."
        ),
        "buggy_code": """\
def top_k_frequent(nums, k):
    freq = {}
    for n in nums:
        freq[n] = freq.get(n, 0) + 1
    sorted_items = sorted(freq.items(), key=lambda x: x[1])
    return [item[0] for item in sorted_items[:k]]
""",
        "fixed_code": """\
def top_k_frequent(nums, k):
    freq = {}
    for n in nums:
        freq[n] = freq.get(n, 0) + 1
    sorted_items = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [item[0] for item in sorted_items[:k]]
""",
        "test_cases": [
            {"input": [[1, 1, 1, 2, 2, 3], 2], "expected": [1, 2]},
            {"input": [[4, 4, 5, 5, 5], 1], "expected": [5]},
            {"input": [[1, 2, 3], 3], "expected": [1, 2, 3]},
        ],
        "test_cases_description": "Returns top-k frequent elements in descending frequency order",
    },
    {
        "task_id": "medium_011",
        "domain": "string processing",
        "instructions": (
            "The function should return the longest common prefix of a list of strings. "
            "It has TWO bugs. Fix both."
        ),
        "buggy_code": """\
def longest_common_prefix(strs):
    if not strs:
        return ''
    prefix = strs[1]
    for s in strs:
        while not s.startswith(prefix):
            prefix = prefix[:-1]
            if not prefix:
                return ''
    return prefix
""",
        "fixed_code": """\
def longest_common_prefix(strs):
    if not strs:
        return ''
    prefix = strs[0]
    for s in strs:
        while not s.startswith(prefix):
            prefix = prefix[:-1]
            if not prefix:
                return ''
    return prefix
""",
        "test_cases": [
            {"input": ["flower", "flow", "flight"], "expected": "fl"},
            {"input": ["dog", "racecar", "car"], "expected": ""},
            {"input": ["interview", "interact", "interface"], "expected": "inter"},
        ],
        "test_cases_description": "Correct longest common prefix starting from index 0",
    },
    {
        "task_id": "medium_012",
        "domain": "list operations",
        "instructions": (
            "The function should rotate a list to the right by k positions. "
            "It has TWO bugs. Fix both."
        ),
        "buggy_code": """\
def rotate_right(lst, k):
    if not lst:
        return lst
    k = k % len(lst)
    return lst[k:] + lst[:k]
""",
        "fixed_code": """\
def rotate_right(lst, k):
    if not lst:
        return lst
    k = k % len(lst)
    return lst[-k:] + lst[:-k]
""",
        "test_cases": [
            {"input": [[1, 2, 3, 4, 5], 2], "expected": [4, 5, 1, 2, 3]},
            {"input": [[1, 2, 3], 1], "expected": [3, 1, 2]},
            {"input": [[], 3], "expected": []},
        ],
        "test_cases_description": "Rotates list to the right correctly",
    },
    {
        "task_id": "medium_013",
        "domain": "API handler",
        "instructions": (
            "The function parses a query string into a dict. "
            "It has TWO bugs. Fix both."
        ),
        "buggy_code": """\
def parse_query_string(query):
    if not query:
        return None
    result = {}
    for pair in query.split('&'):
        if '=' in pair:
            key, value = pair.split('=')
            result[value] = key
    return result
""",
        "fixed_code": """\
def parse_query_string(query):
    if not query:
        return {}
    result = {}
    for pair in query.split('&'):
        if '=' in pair:
            key, value = pair.split('=', 1)
            result[key] = value
    return result
""",
        "test_cases": [
            {"input": "name=Alice&age=30", "expected": {"name": "Alice", "age": "30"}},
            {"input": "", "expected": {}},
            {"input": "key=value=extra", "expected": {"key": "value=extra"}},
        ],
        "test_cases_description": "Parses query string; empty returns {}; key=value order correct; split on first = only",
    },
    {
        "task_id": "medium_014",
        "domain": "data processing",
        "instructions": (
            "The function should return all pairs of numbers in a list that sum to target. "
            "It has TWO bugs. Fix both."
        ),
        "buggy_code": """\
def find_pairs(nums, target):
    pairs = []
    seen = set()
    for n in nums:
        complement = target + n
        if complement in seen:
            pairs.append((complement, n))
        seen.add(n)
    return pairs
""",
        "fixed_code": """\
def find_pairs(nums, target):
    pairs = []
    seen = set()
    for n in nums:
        complement = target - n
        if complement in seen:
            pairs.append((complement, n))
        seen.add(n)
    return pairs
""",
        "test_cases": [
            {"input": [[2, 7, 11, 15], 9], "expected": [(2, 7)]},
            {"input": [[1, 2, 3, 4], 5], "expected": [(2, 3), (1, 4)]},
            {"input": [[1, 2], 10], "expected": []},
        ],
        "test_cases_description": "Finds all pairs summing to target using complement = target - n",
    },
    {
        "task_id": "medium_015",
        "domain": "math",
        "instructions": (
            "The function should return the nth Fibonacci number (0-indexed). "
            "It has TWO bugs. Fix both."
        ),
        "buggy_code": """\
def fibonacci(n):
    if n == 0:
        return 1
    if n == 1:
        return 1
    a, b = 0, 1
    for _ in range(2, n):
        a, b = b, a + b
    return b
""",
        "fixed_code": """\
def fibonacci(n):
    if n == 0:
        return 0
    if n == 1:
        return 1
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
""",
        "test_cases": [
            {"input": 0, "expected": 0},
            {"input": 1, "expected": 1},
            {"input": 6, "expected": 8},
        ],
        "test_cases_description": "Correct Fibonacci: fib(0)=0, fib(1)=1, fib(6)=8",
    },
]


def get_random_medium_task() -> dict:
    return random.choice(MEDIUM_TASKS).copy()


def get_task_by_id(task_id: str) -> dict:
    for t in MEDIUM_TASKS:
        if t["task_id"] == task_id:
            return t.copy()
    return random.choice(MEDIUM_TASKS).copy()
