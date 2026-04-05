# server/graders/grader_hard.py
# Grades hard tasks: algorithmic bug + explanation required.
# Reward = 0.7 * test_score + 0.3 * explanation_score

from typing import Tuple, List, Optional
from .grader_easy import grade_easy


def _score_explanation(explanation: Optional[str], keywords: List[str]) -> Tuple[float, str]:
    """
    Score explanation by checking for required conceptual keywords.
    - No explanation → 0.0
    - 1+ keyword hit → partial credit proportional to hits
    - Half or more keywords → 1.0
    """
    if not explanation or len(explanation.strip()) < 10:
        return 0.0, "❌ No explanation provided. Hard tasks require an explanation field."

    explanation_lower = explanation.lower()
    hits = [kw for kw in keywords if kw.lower() in explanation_lower]

    if not keywords:
        score = 1.0 if len(explanation.strip()) > 20 else 0.5
    else:
        needed = max(1, len(keywords) // 2)
        if len(hits) == 0:
            score = 0.0
        elif len(hits) >= needed:
            score = 1.0
        else:
            score = round(len(hits) / needed, 2)

    if score == 1.0:
        feedback = f"✅ Explanation excellent! Mentioned: {', '.join(hits)}"
    elif score > 0:
        missing = [kw for kw in keywords if kw.lower() not in explanation_lower]
        feedback = (
            f"⚠️ Partial explanation (score={score}). Mentioned: {', '.join(hits) or 'none'}. "
            f"Also discuss: {', '.join(missing[:3])}"
        )
    else:
        feedback = (
            f"❌ Explanation missing key concepts. "
            f"Explain: {', '.join(keywords[:3])}"
        )

    return round(score, 2), feedback


def grade_hard(fixed_code: str, task: dict, explanation: Optional[str] = None) -> Tuple[float, int, int, str, List[dict]]:
    """
    Grade a hard task submission.
    Reward = 0.7 × test_score + 0.3 × explanation_score
    """
    test_reward, passed, total, code_feedback, results = grade_easy(fixed_code, task)
    keywords = task.get("explanation_keywords", [])
    exp_score, exp_feedback = _score_explanation(explanation, keywords)
    final_reward = round(0.7 * test_reward + 0.3 * exp_score, 2)

    feedback = (
        f"--- Code Score (70% weight): {test_reward:.2f} ---\n"
        f"{code_feedback}\n\n"
        f"--- Explanation Score (30% weight): {exp_score:.2f} ---\n"
        f"{exp_feedback}\n\n"
        f"=== Final Reward: {final_reward:.2f} ==="
    )

    if passed == total and exp_score < 1.0:
        feedback += f"\n💡 Code is correct! Improve explanation by mentioning: {', '.join(keywords[:3])}"
    elif passed < total and not explanation:
        feedback += "\n💡 Fix the code AND provide a clear explanation for max reward."

    return final_reward, passed, total, feedback, results
