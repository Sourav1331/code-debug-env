# server/graders/grader_easy.py
# Grades easy and medium tasks: runs code against test cases.
# Reward is proportional to tests passed (0.33, 0.67, 1.0).

import traceback
import signal
from typing import Tuple, List


def _timeout_handler(signum, frame):
    raise TimeoutError("Code timed out — likely infinite loop. Check for missing visited set in graph traversal.")


def _run_code_safely(code: str, func_name: str, test_input):
    """Run submitted code safely with 5s timeout. Returns (result, error)."""
    namespace = {}
    try:
        exec(compile(code, "<submitted>", "exec"), namespace)
    except SyntaxError as e:
        return None, f"SyntaxError: {e}"
    except Exception as e:
        return None, f"CompileError: {e}"

    func = namespace.get(func_name)
    if func is None:
        funcs = [v for v in namespace.values() if callable(v) and not str(v.__name__).startswith("_")]
        if not funcs:
            return None, "No callable function found in submitted code."
        func = funcs[0]

    try:
        try:
            signal.signal(signal.SIGALRM, _timeout_handler)
            signal.alarm(5)
        except (AttributeError, OSError):
            pass  # Windows has no SIGALRM

        if isinstance(test_input, list) and len(test_input) > 0 and isinstance(test_input[0], list):
            result = func(*test_input)
        elif isinstance(test_input, list):
            try:
                result = func(test_input)
            except TypeError:
                result = func(*test_input)
        else:
            result = func(test_input)

        try:
            signal.alarm(0)
        except (AttributeError, OSError):
            pass

        return result, None

    except TimeoutError as e:
        return None, str(e)
    except Exception as e:
        try:
            signal.alarm(0)
        except (AttributeError, OSError):
            pass
        return None, f"RuntimeError: {traceback.format_exc(limit=2)}"


def _extract_func_name(code: str) -> str:
    for line in code.splitlines():
        line = line.strip()
        if line.startswith("def "):
            return line.split("(")[0].replace("def ", "").strip()
    return "unknown"


def grade_easy(fixed_code: str, task: dict) -> Tuple[float, int, int, str, List[dict]]:
    """
    Grade submission against test cases.
    Returns: (reward, passed, total, feedback, results)
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
            results.append({"test_id": i+1, "passed": False, "expected": str(expected), "got": f"ERROR"})
            feedback_lines.append(f"Test {i+1}: ❌ Error\n   Input    : {inp!r}\n   Expected : {expected!r}\n   Error    : {error}")
        elif got == expected:
            passed += 1
            results.append({"test_id": i+1, "passed": True, "expected": str(expected), "got": str(got)})
            feedback_lines.append(f"Test {i+1}: ✅ Passed\n   Input    : {inp!r}\n   Expected : {expected!r}\n   Got      : {got!r}")
        else:
            results.append({"test_id": i+1, "passed": False, "expected": str(expected), "got": str(got)})
            feedback_lines.append(f"Test {i+1}: ❌ Failed\n   Input    : {inp!r}\n   Expected : {expected!r}\n   Got      : {got!r}")

    reward = round(passed / total, 2)
    feedback = "\n".join(feedback_lines)
    feedback += "\n🎉 All tests passed! Full reward." if passed == total else f"\n{passed}/{total} tests passed."

    return reward, passed, total, feedback, results
