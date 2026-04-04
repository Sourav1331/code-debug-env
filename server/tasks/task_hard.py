# server/tasks/task_hard.py
# 15 hard tasks: algorithmic bugs + agent must explain what was wrong.
# Reward is based on test pass rate PLUS explanation quality.

import random

HARD_TASKS = [
    {
        "task_id": "hard_001",
        "domain": "sorting algorithm",
        "instructions": (
            "The function implements bubble sort but is broken. "
            "Fix the algorithm AND explain what was wrong in your 'explanation' field. "
            "Explanation must mention: loop range, boundary, or swap logic."
        ),
        "buggy_code": """\
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(n - i):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
""",
        "fixed_code": """\
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
""",
        "explanation_keywords": ["boundary", "index", "range", "n - i - 1", "out of bounds", "last element"],
        "test_cases": [
            {"input": [64, 34, 25, 12, 22, 11, 90], "expected": [11, 12, 22, 25, 34, 64, 90]},
            {"input": [5, 1, 4, 2, 8], "expected": [1, 2, 4, 5, 8]},
            {"input": [1], "expected": [1]},
        ],
        "test_cases_description": "Bubble sort with correct inner loop boundary (n - i - 1)",
    },
    {
        "task_id": "hard_002",
        "domain": "dynamic programming",
        "instructions": (
            "The function computes the longest increasing subsequence (LIS) length. "
            "Fix the algorithm AND explain what was wrong. "
            "Explanation must mention: initialization, dp transition, or base case."
        ),
        "buggy_code": """\
def lis_length(nums):
    if not nums:
        return 0
    dp = [0] * len(nums)
    for i in range(len(nums)):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)
""",
        "fixed_code": """\
def lis_length(nums):
    if not nums:
        return 0
    dp = [1] * len(nums)
    for i in range(len(nums)):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)
""",
        "explanation_keywords": ["initialization", "base case", "dp[i]", "1", "zero", "initial value"],
        "test_cases": [
            {"input": [10, 9, 2, 5, 3, 7, 101, 18], "expected": 4},
            {"input": [0, 1, 0, 3, 2, 3], "expected": 4},
            {"input": [7, 7, 7, 7], "expected": 1},
        ],
        "test_cases_description": "LIS with dp initialized to 1 (not 0)",
    },
    {
        "task_id": "hard_003",
        "domain": "binary search",
        "instructions": (
            "The function does binary search on a sorted list. "
            "Fix the algorithm AND explain what was wrong. "
            "Explanation must mention: mid calculation, overflow, boundary, or infinite loop."
        ),
        "buggy_code": """\
def binary_search(arr, target):
    low, high = 0, len(arr)
    while low < high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid
        else:
            high = mid - 1
    return -1
""",
        "fixed_code": """\
def binary_search(arr, target):
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
""",
        "explanation_keywords": ["high", "len - 1", "low = mid", "infinite loop", "boundary", "off-by-one"],
        "test_cases": [
            {"input": [[1, 3, 5, 7, 9], 7], "expected": 3},
            {"input": [[1, 3, 5, 7, 9], 1], "expected": 0},
            {"input": [[1, 3, 5, 7, 9], 6], "expected": -1},
        ],
        "test_cases_description": "Binary search: high = len-1, low = mid+1, while low <= high",
    },
    {
        "task_id": "hard_004",
        "domain": "dynamic programming",
        "instructions": (
            "The function computes the minimum number of coins to make 'amount'. "
            "Fix the algorithm AND explain what was wrong. "
            "Explanation must mention: initialization, infinity, dp table, or base case."
        ),
        "buggy_code": """\
def coin_change(coins, amount):
    dp = [0] * (amount + 1)
    dp[0] = 0
    for i in range(1, amount + 1):
        for coin in coins:
            if coin <= i:
                dp[i] = min(dp[i], dp[i - coin] + 1)
    return dp[amount] if dp[amount] != 0 else -1
""",
        "fixed_code": """\
def coin_change(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for i in range(1, amount + 1):
        for coin in coins:
            if coin <= i:
                dp[i] = min(dp[i], dp[i - coin] + 1)
    return dp[amount] if dp[amount] != float('inf') else -1
""",
        "explanation_keywords": ["infinity", "inf", "initialization", "0 instead of inf", "unreachable", "base"],
        "test_cases": [
            {"input": [[1, 5, 6, 9], 11], "expected": 2},
            {"input": [[2], 3], "expected": -1},
            {"input": [[1, 2, 5], 11], "expected": 3},
        ],
        "test_cases_description": "Coin change DP: initialized to inf, not 0",
    },
    {
        "task_id": "hard_005",
        "domain": "graph algorithm",
        "instructions": (
            "The function checks if a directed graph has a cycle using DFS. "
            "Fix it AND explain what was wrong. "
            "Explanation must mention: visited, recursion stack, back edge, or state."
        ),
        "buggy_code": """\
def has_cycle(graph):
    visited = set()

    def dfs(node):
        visited.add(node)
        for neighbor in graph.get(node, []):
            if neighbor in visited:
                return True
            if dfs(neighbor):
                return True
        return False

    for node in graph:
        if node not in visited:
            if dfs(node):
                return True
    return False
""",
        "fixed_code": """\
def has_cycle(graph):
    visited = set()
    rec_stack = set()

    def dfs(node):
        visited.add(node)
        rec_stack.add(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor):
                    return True
            elif neighbor in rec_stack:
                return True
        rec_stack.remove(node)
        return False

    for node in graph:
        if node not in visited:
            if dfs(node):
                return True
    return False
""",
        "explanation_keywords": ["recursion stack", "rec_stack", "back edge", "visited", "false positive", "path"],
        "test_cases": [
            {"input": {"A": ["B"], "B": ["C"], "C": ["A"]}, "expected": True},
            {"input": {"A": ["B"], "B": ["C"], "C": []}, "expected": False},
            {"input": {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}, "expected": False},
        ],
        "test_cases_description": "Cycle detection in directed graph using recursion stack",
    },
    {
        "task_id": "hard_006",
        "domain": "dynamic programming",
        "instructions": (
            "The function computes the maximum subarray sum (Kadane's algorithm). "
            "Fix it AND explain what was wrong. "
            "Explanation must mention: initialization, negative numbers, current_sum, or reset."
        ),
        "buggy_code": """\
def max_subarray(nums):
    max_sum = 0
    current_sum = 0
    for n in nums:
        current_sum = max(n, current_sum + n)
        max_sum = max(max_sum, current_sum)
    return max_sum
""",
        "fixed_code": """\
def max_subarray(nums):
    max_sum = nums[0]
    current_sum = nums[0]
    for n in nums[1:]:
        current_sum = max(n, current_sum + n)
        max_sum = max(max_sum, current_sum)
    return max_sum
""",
        "explanation_keywords": ["initialization", "negative", "nums[0]", "all negative", "zero", "initial"],
        "test_cases": [
            {"input": [-2, 1, -3, 4, -1, 2, 1, -5, 4], "expected": 6},
            {"input": [-1, -2, -3, -4], "expected": -1},
            {"input": [1], "expected": 1},
        ],
        "test_cases_description": "Kadane's algorithm handles all-negative arrays",
    },
    {
        "task_id": "hard_007",
        "domain": "string algorithm",
        "instructions": (
            "The function checks if a string has balanced brackets. "
            "Fix it AND explain what was wrong. "
            "Explanation must mention: stack, matching, empty stack, or closing bracket."
        ),
        "buggy_code": """\
def is_balanced(s):
    stack = []
    matching = {')': '(', ']': '[', '}': '{'}
    for ch in s:
        if ch in '([{':
            stack.append(ch)
        elif ch in ')]}':
            if stack and stack[-1] == matching[ch]:
                stack.pop()
    return len(stack) == 0
""",
        "fixed_code": """\
def is_balanced(s):
    stack = []
    matching = {')': '(', ']': '[', '}': '{'}
    for ch in s:
        if ch in '([{':
            stack.append(ch)
        elif ch in ')]}':
            if not stack or stack[-1] != matching[ch]:
                return False
            stack.pop()
    return len(stack) == 0
""",
        "explanation_keywords": ["stack", "empty stack", "mismatch", "not stack", "early return", "closing"],
        "test_cases": [
            {"input": "([{}])", "expected": True},
            {"input": "([)]", "expected": False},
            {"input": "]", "expected": False},
        ],
        "test_cases_description": "Balanced brackets: early return False on mismatch or empty stack",
    },
    {
        "task_id": "hard_008",
        "domain": "dynamic programming",
        "instructions": (
            "The function computes the number of ways to climb n stairs (1 or 2 steps at a time). "
            "Fix it AND explain what was wrong. "
            "Explanation must mention: base case, dp, index, or off-by-one."
        ),
        "buggy_code": """\
def climb_stairs(n):
    if n <= 0:
        return 0
    dp = [0] * (n + 1)
    dp[0] = 1
    dp[1] = 1
    for i in range(3, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    return dp[n]
""",
        "fixed_code": """\
def climb_stairs(n):
    if n <= 0:
        return 0
    dp = [0] * (n + 1)
    dp[0] = 1
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    return dp[n]
""",
        "explanation_keywords": ["range", "starts at 3", "range(2", "off-by-one", "dp[2]", "skipped"],
        "test_cases": [
            {"input": 2, "expected": 2},
            {"input": 3, "expected": 3},
            {"input": 5, "expected": 8},
        ],
        "test_cases_description": "Climb stairs DP: loop starts at range(2, ...) not range(3, ...)",
    },
    {
        "task_id": "hard_009",
        "domain": "data processing",
        "instructions": (
            "The function implements quicksort. "
            "Fix it AND explain what was wrong. "
            "Explanation must mention: pivot, partition, recursion, or base case."
        ),
        "buggy_code": """\
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[0]
    left = [x for x in arr if x < pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + [pivot] + quicksort(right)
""",
        "fixed_code": """\
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[0]
    left = [x for x in arr[1:] if x <= pivot]
    right = [x for x in arr[1:] if x > pivot]
    return quicksort(left) + [pivot] + quicksort(right)
""",
        "explanation_keywords": ["duplicate", "arr[1:]", "pivot included", "equal", "lost", "missing"],
        "test_cases": [
            {"input": [3, 6, 8, 10, 1, 2, 1], "expected": [1, 1, 2, 3, 6, 8, 10]},
            {"input": [5, 5, 5], "expected": [5, 5, 5]},
            {"input": [1], "expected": [1]},
        ],
        "test_cases_description": "Quicksort handles duplicates: arr[1:] and x <= pivot",
    },
    {
        "task_id": "hard_010",
        "domain": "graph algorithm",
        "instructions": (
            "The function finds the shortest path length in an unweighted graph using BFS. "
            "Fix it AND explain what was wrong. "
            "Explanation must mention: visited, queue, infinite loop, or distance tracking."
        ),
        "buggy_code": """\
from collections import deque

def bfs_shortest_path(graph, start, end):
    queue = deque([(start, 0)])
    while queue:
        node, dist = queue.popleft()
        if node == end:
            return dist
        for neighbor in graph.get(node, []):
            queue.append((neighbor, dist + 1))
    return -1
""",
        "fixed_code": """\
from collections import deque

def bfs_shortest_path(graph, start, end):
    visited = set([start])
    queue = deque([(start, 0)])
    while queue:
        node, dist = queue.popleft()
        if node == end:
            return dist
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, dist + 1))
    return -1
""",
        "explanation_keywords": ["visited", "infinite loop", "revisit", "cycle", "set", "already visited"],
        "test_cases": [
            {"input": [{"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}, "A", "D"], "expected": 2},
            {"input": [{"A": ["B"], "B": ["A"]}, "A", "B"], "expected": 1},
            {"input": [{"A": ["B"]}, "A", "C"], "expected": -1},
        ],
        "test_cases_description": "BFS shortest path with visited set to prevent revisiting",
    },
    {
        "task_id": "hard_011",
        "domain": "dynamic programming",
        "instructions": (
            "The function computes the 0/1 knapsack maximum value. "
            "Fix it AND explain what was wrong. "
            "Explanation must mention: capacity, dp table, iteration order, or overwrite."
        ),
        "buggy_code": """\
def knapsack(weights, values, capacity):
    n = len(weights)
    dp = [0] * (capacity + 1)
    for i in range(n):
        for w in range(weights[i], capacity + 1):
            dp[w] = max(dp[w], dp[w - weights[i]] + values[i])
    return dp[capacity]
""",
        "fixed_code": """\
def knapsack(weights, values, capacity):
    n = len(weights)
    dp = [0] * (capacity + 1)
    for i in range(n):
        for w in range(capacity, weights[i] - 1, -1):
            dp[w] = max(dp[w], dp[w - weights[i]] + values[i])
    return dp[capacity]
""",
        "explanation_keywords": ["reverse", "backward", "overwrite", "0/1", "unbounded", "iteration order", "right to left"],
        "test_cases": [
            {"input": [[2, 3, 4, 5], [3, 4, 5, 6], 5], "expected": 7},
            {"input": [[1, 2, 3], [6, 10, 12], 5], "expected": 22},
            {"input": [[5], [10], 3], "expected": 0},
        ],
        "test_cases_description": "0/1 Knapsack: inner loop must go backward to avoid using item twice",
    },
    {
        "task_id": "hard_012",
        "domain": "string algorithm",
        "instructions": (
            "The function finds the length of the longest substring without repeating characters. "
            "Fix it AND explain what was wrong. "
            "Explanation must mention: window, pointer, index, or update."
        ),
        "buggy_code": """\
def length_of_longest_substring(s):
    char_index = {}
    left = 0
    max_len = 0
    for right, ch in enumerate(s):
        if ch in char_index:
            left = char_index[ch] + 1
        char_index[ch] = right
        max_len = max(max_len, right - left + 1)
    return max_len
""",
        "fixed_code": """\
def length_of_longest_substring(s):
    char_index = {}
    left = 0
    max_len = 0
    for right, ch in enumerate(s):
        if ch in char_index and char_index[ch] >= left:
            left = char_index[ch] + 1
        char_index[ch] = right
        max_len = max(max_len, right - left + 1)
    return max_len
""",
        "explanation_keywords": ["left pointer", "stale", "char_index[ch] >= left", "window", "shrink", "old index"],
        "test_cases": [
            {"input": "abcabcbb", "expected": 3},
            {"input": "bbbbb", "expected": 1},
            {"input": "pwwkew", "expected": 3},
        ],
        "test_cases_description": "Longest substring without repeating: only update left if char is within current window",
    },
    {
        "task_id": "hard_013",
        "domain": "data processing",
        "instructions": (
            "The function merges overlapping intervals. "
            "Fix it AND explain what was wrong. "
            "Explanation must mention: sort, overlap, merge condition, or end index."
        ),
        "buggy_code": """\
def merge_intervals(intervals):
    if not intervals:
        return []
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]
    for start, end in intervals[1:]:
        if start <= merged[-1][0]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged
""",
        "fixed_code": """\
def merge_intervals(intervals):
    if not intervals:
        return []
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]
    for start, end in intervals[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged
""",
        "explanation_keywords": ["merged[-1][1]", "end", "start", "overlap", "last interval", "index 1 vs 0"],
        "test_cases": [
            {"input": [[[1, 3], [2, 6], [8, 10]]], "expected": [[1, 6], [8, 10]]},
            {"input": [[[1, 4], [4, 5]]], "expected": [[1, 5]]},
            {"input": [[[1, 2]]], "expected": [[1, 2]]},
        ],
        "test_cases_description": "Merge intervals: compare start with merged[-1][1] (end), not [0] (start)",
    },
    {
        "task_id": "hard_014",
        "domain": "math",
        "instructions": (
            "The function does integer square root (floor) without using sqrt(). "
            "Fix it AND explain what was wrong. "
            "Explanation must mention: binary search, convergence, mid, or boundary."
        ),
        "buggy_code": """\
def integer_sqrt(n):
    if n < 2:
        return n
    low, high = 1, n
    while low <= high:
        mid = (low + high) // 2
        if mid * mid == n:
            return mid
        elif mid * mid < n:
            low = mid + 1
        else:
            high = mid - 1
    return low
""",
        "fixed_code": """\
def integer_sqrt(n):
    if n < 2:
        return n
    low, high = 1, n // 2
    while low <= high:
        mid = (low + high) // 2
        if mid * mid == n:
            return mid
        elif mid * mid < n:
            low = mid + 1
        else:
            high = mid - 1
    return high
""",
        "explanation_keywords": ["high", "n // 2", "return high", "return low", "floor", "boundary", "last valid"],
        "test_cases": [
            {"input": 16, "expected": 4},
            {"input": 8, "expected": 2},
            {"input": 1, "expected": 1},
        ],
        "test_cases_description": "Integer square root: high=n//2, return high (floor result)",
    },
    {
        "task_id": "hard_015",
        "domain": "string algorithm",
        "instructions": (
            "The function implements the Z-algorithm to count pattern occurrences in text. "
            "Fix it AND explain what was wrong. "
            "Explanation must mention: concatenation, Z-array, separator, or index offset."
        ),
        "buggy_code": """\
def count_occurrences(text, pattern):
    concat = pattern + text
    n = len(concat)
    z = [0] * n
    l, r = 0, 0
    for i in range(1, n):
        if i < r:
            z[i] = min(r - i, z[i - l])
        while i + z[i] < n and concat[z[i]] == concat[i + z[i]]:
            z[i] += 1
        if i + z[i] > r:
            l, r = i, i + z[i]
    return sum(1 for i in range(len(pattern), n) if z[i] == len(pattern))
""",
        "fixed_code": """\
def count_occurrences(text, pattern):
    concat = pattern + '#' + text
    n = len(concat)
    z = [0] * n
    l, r = 0, 0
    for i in range(1, n):
        if i < r:
            z[i] = min(r - i, z[i - l])
        while i + z[i] < n and concat[z[i]] == concat[i + z[i]]:
            z[i] += 1
        if i + z[i] > r:
            l, r = i, i + z[i]
    p_len = len(pattern)
    return sum(1 for i in range(p_len + 1, n) if z[i] == p_len)
""",
        "explanation_keywords": ["separator", "#", "without separator", "bleed", "p_len + 1", "offset", "boundary"],
        "test_cases": [
            {"input": ["aabxaabaab", "aab"], "expected": 3},
            {"input": ["hello world", "world"], "expected": 1},
            {"input": ["aaaa", "aa"], "expected": 3},
        ],
        "test_cases_description": "Z-algorithm with '#' separator and corrected offset p_len+1",
    },
]


def get_random_hard_task() -> dict:
    return random.choice(HARD_TASKS).copy()


def get_task_by_id(task_id: str) -> dict:
    for t in HARD_TASKS:
        if t["task_id"] == task_id:
            return t.copy()
    return random.choice(HARD_TASKS).copy()