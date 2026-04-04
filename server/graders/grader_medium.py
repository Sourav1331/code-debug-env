# server/graders/grader_medium.py
# Grades medium tasks: 2 bugs, 3 test cases.
# Same proportional reward as easy but stricter — both bugs must be fixed for full score.

from .grader_easy import grade_easy  # reuse the same logic


def grade_medium(fixed_code: str, task: dict):
    """
    Grade a medium task. Same mechanics as easy — proportional reward by tests passed.
    Returns same tuple: reward, passed, total, feedback, results
    """
    reward, passed, total, feedback, results = grade_easy(fixed_code, task)

    # Add medium-specific feedback hint
    if passed < total:
        feedback += (
            "\n💡 Hint: Medium tasks have TWO bugs. "
            "Make sure you fixed both the primary logic bug AND the edge case."
        )

    return reward, passed, total, feedback, results
