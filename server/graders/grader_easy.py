# server/graders/grader_easy.py
# Grades easy tasks: 1 bug, 3 test cases.
# Reward is proportional to tests passed (0.33, 0.66, 1.0).

import traceback
from typing import Tuple, List


def _run_code_safely(code: str, func_name: str, test_input):
    """
    Executes the submitted code in an isolated namespace and calls the function.
    Returns (output, error_message).
    """
    namespace = {}
    try:
        exec(compile(code, "<submitted>", "exec"), namespace)
    except SyntaxError as e:
        return None, f"SyntaxError: {e}"
    except Exception as e:
        return None, f"Compile error: {e}"

    func = namespace.get(func_name)
    if func is None:
        # Try to find any callable
        funcs = [v for v in namespace.values() if callable(v) and not v.__name__.startswith("_")]
        if not funcs:
            return None, "No callable function found in submitted code."
        func = funcs[0]

    try:
        if isinstance(test_input, list):
            result = func(*test_input)
        else:
            result = func(test_input)
        return result, None
    except Exception as e:
        return None, f"RuntimeError: {traceback.format_exc(limit=2)}"


def _extract_func_name(code: str) -> str:
    """Extract the first function name defined in the code."""
    for line in code.splitlines():
        line = line.strip()
        if line.startswith("def "):
            return line.split("(")[0].replace("def ", "").strip()
    return "unknown"


def grade_easy(fixed_code: str, task: dict) -> Tuple[float, int, int, str, List[dict]]:
    """
    Grade an easy task submission.

    Returns:
        reward (float): 0.0 to 1.0
        passed (int): number of tests passed
        total (int): total test cases
        feedback (str): detailed feedback message
        results (list): per-test results
    """
    test_cases = task["test_cases"]
    total = len(test_cases)
    passed = 0
    results = []
    func_name = _extract_func_name(fixed_code)
    feedback_lines = []

    for i, tc in enumerate(test_cases):
        inp = tc["input"]
        expected = tc["expected"]
        got, error = _run_code_safely(fixed_code, func_name, inp)

        if error:
            results.append({"test_id": i + 1, "passed": False, "expected": str(expected), "got": f"ERROR: {error}"})
            feedback_lines.append(f"Test {i+1}: ❌ Error — {error}")
        elif got == expected:
            passed += 1
            results.append({"test_id": i + 1, "passed": True, "expected": str(expected), "got": str(got)})
            feedback_lines.append(f"Test {i+1}: ✅ Passed — got {got!r}")
        else:
            results.append({"test_id": i + 1, "passed": False, "expected": str(expected), "got": str(got)})
            feedback_lines.append(f"Test {i+1}: ❌ Failed — expected {expected!r}, got {got!r}")

    reward = round(passed / total, 2)
    feedback = "\n".join(feedback_lines)
    if passed == total:
        feedback += "\n🎉 All tests passed! Full reward."
    else:
        feedback += f"\n{passed}/{total} tests passed. Review the failing cases."

    return reward, passed, total, feedback, results
