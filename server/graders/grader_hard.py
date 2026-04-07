# server/graders/grader_hard.py
# Grades hard tasks: algorithmic bug + explanation required.
# Reward = 0.7 * test_score + 0.3 * explanation_score

from typing import Tuple, List, Optional
from .grader_easy import grade_easy


def _score_explanation(explanation: Optional[str], keywords: List[str], instructions: str) -> Tuple[float, str]:
    """
    Score explanation semantically:
    - Length check (must be meaningful)
    - Keyword matching (concept coverage)
    - Partial credit for any relevant mention
    """
    if not explanation or len(explanation.strip()) < 15:
        return 0.0, "❌ No explanation provided. Hard tasks require explanation field."

    exp_lower = explanation.lower()
    hits = [kw for kw in keywords if kw.lower() in exp_lower]

    # Also check for common synonyms
    synonym_map = {
        "visited": ["seen", "visited", "track", "memo"],
        "iteration order": ["order", "direction", "forward", "backward", "reverse"],
        "overwrite": ["overwrite", "override", "update", "modify"],
        "reverse": ["reverse", "backward", "right to left", "descending"],
        "0/1": ["0/1", "zero one", "binary", "knapsack"],
        "high": ["high", "upper", "boundary", "bound"],
        "return high": ["return high", "high boundary"],
        "floor": ["floor", "integer", "truncat"],
    }

    synonym_hits = set(hits)
    for kw in keywords:
        kw_lower = kw.lower()
        if kw_lower in synonym_map:
            for syn in synonym_map[kw_lower]:
                if syn in exp_lower:
                    synonym_hits.add(kw)
                    break

    total_hits = len(synonym_hits)
    needed = max(1, len(keywords) // 2)

    if total_hits == 0:
        score = 0.1 if len(explanation.strip()) > 50 else 0.0  # minimal credit for any long attempt
    elif total_hits >= needed:
        score = 1.0
    else:
        score = round(total_hits / needed, 2)

    if score >= 1.0:
        feedback = f"✅ Explanation excellent! Covered: {', '.join(synonym_hits)}"
    elif score > 0:
        missing = [kw for kw in keywords if kw.lower() not in exp_lower]
        feedback = (
            f"⚠️ Partial explanation (score={score}). Covered: {', '.join(synonym_hits) or 'none'}. "
            f"Also mention: {', '.join(missing[:3])}"
        )
    else:
        feedback = f"❌ Explanation too vague. Explain: {', '.join(keywords[:3])}"

    return round(score, 2), feedback


def grade_hard(fixed_code: str, task: dict, explanation: Optional[str] = None) -> Tuple[float, int, int, str, List[dict]]:
    """
    Grade hard task: Reward = 0.7 × test_score + 0.3 × explanation_score
    """
    test_reward, passed, total, code_feedback, results = grade_easy(fixed_code, task)
    keywords = task.get("explanation_keywords", [])
    instructions = task.get("instructions", "")
    exp_score, exp_feedback = _score_explanation(explanation, keywords, instructions)
    final_reward = round(0.7 * test_reward + 0.3 * exp_score, 2)

    feedback = (
        f"--- Code Score (70%): {test_reward:.2f} ---\n"
        f"{code_feedback}\n\n"
        f"--- Explanation Score (30%): {exp_score:.2f} ---\n"
        f"{exp_feedback}\n\n"
        f"=== Final Reward: {final_reward:.2f} ==="
    )

    if passed == total and exp_score < 1.0:
        feedback += f"\n💡 Code correct! Boost score by mentioning: {', '.join(keywords[:3])}"
    elif passed < total and not explanation:
        feedback += "\n💡 Fix the code AND add explanation for max reward."

    return final_reward, passed, total, feedback, results
