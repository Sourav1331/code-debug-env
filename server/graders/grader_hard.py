# server/graders/grader_hard.py
# Grades hard tasks: algorithmic bug + explanation required.
# Reward = 0.7 * test_score + 0.3 * explanation_score

from typing import Tuple, List, Optional
from .grader_easy import grade_easy


def _score_explanation(explanation: Optional[str], keywords: List[str]) -> Tuple[float, str]:
    """
    Scores the explanation by checking for required conceptual keywords.
    Returns (score 0.0-1.0, feedback string).
    """
    if not explanation or len(explanation.strip()) < 10:
        return 0.0, "❌ No explanation provided. Hard tasks require an explanation field."

    explanation_lower = explanation.lower()
    hits = [kw for kw in keywords if kw.lower() in explanation_lower]
    score = min(1.0, len(hits) / max(1, len(keywords) // 2))  # need at least half the keywords

    if score == 1.0:
        feedback = f"✅ Explanation excellent! Mentioned key concepts: {', '.join(hits)}"
    elif score > 0:
        feedback = (
            f"⚠️ Partial explanation. Mentioned: {', '.join(hits) if hits else 'none'}. "
            f"Consider discussing: {', '.join(kw for kw in keywords if kw.lower() not in explanation_lower)[:3]}"
        )
    else:
        feedback = (
            f"❌ Explanation missing key concepts. "
            f"Try to explain: {', '.join(keywords[:3])} in your analysis."
        )

    return round(score, 2), feedback


def grade_hard(fixed_code: str, task: dict, explanation: Optional[str] = None) -> Tuple[float, int, int, str, List[dict]]:
    """
    Grade a hard task submission.
    Reward = 0.7 * test_score + 0.3 * explanation_score

    Returns:
        reward (float): 0.0 to 1.0
        passed (int)
        total (int)
        feedback (str)
        results (list)
    """
    # Grade code
    test_reward, passed, total, code_feedback, results = grade_easy(fixed_code, task)

    # Grade explanation
    keywords = task.get("explanation_keywords", [])
    exp_score, exp_feedback = _score_explanation(explanation, keywords)

    # Combined reward
    final_reward = round(0.7 * test_reward + 0.3 * exp_score, 2)

    feedback = (
        f"--- Code Score (70% weight): {test_reward:.2f} ---\n"
        f"{code_feedback}\n\n"
        f"--- Explanation Score (30% weight): {exp_score:.2f} ---\n"
        f"{exp_feedback}\n\n"
        f"=== Final Reward: {final_reward:.2f} ==="
    )

    if passed < total and not explanation:
        feedback += "\n💡 Tip: Fix the code bugs AND provide a clear explanation for max reward."

    return final_reward, passed, total, feedback, results
