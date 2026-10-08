"""HanLevel v1.0 adaptation workflow.

Runs generative adaptation, evaluates each output with HanLevel's
independent rule-based analyzer, and performs at most one automatic retry.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ai_adapter import adapt_text
from analyzer import analyze_text


TARGET_BANDS = {
    "Beginner": (0.0, 25.0),
    "Intermediate": (25.0, 50.0),
    "Advanced": (50.0, 100.000001),
}


@dataclass
class AdaptationAttempt:
    number: int
    adapted_text: str
    analysis: dict[str, Any]
    change_summary: list[str]
    notable_changes: list[dict[str, Any]]
    model: str

    @property
    def score(self) -> float:
        return float(self.analysis["final_score"])

    @property
    def level(self) -> str:
        return str(self.analysis["level"])


def target_reached(analysis: dict[str, Any], target_level: str) -> bool:
    if target_level not in TARGET_BANDS:
        raise ValueError(f"Unknown target level: {target_level}")

    lower, upper = TARGET_BANDS[target_level]
    score = float(analysis["final_score"])
    return lower <= score < upper


def _format_feedback(
    analysis: dict[str, Any],
    target_level: str,
) -> str:
    """Create compact evaluator feedback for the corrective retry."""

    vocab_score = analysis["vocabulary"]["vocabulary_score"]
    vocab_text = (
        f"{vocab_score:.1f}/100"
        if vocab_score is not None
        else "unavailable"
    )

    grammar_score = analysis["grammar"]["grammar_score"]
    sentence_score = analysis["sentence_length"]["sentence_length_score"]
    avg_eojeol = analysis["sentence_length"]["average_eojeol"]

    lower, upper = TARGET_BANDS[target_level]
    if target_level == "Beginner":
        target_text = "below 25"
    elif target_level == "Intermediate":
        target_text = "from 25 up to, but not including, 50"
    else:
        target_text = "50 or higher"

    return (
        f"Independent HanLevel evaluation of the previous adaptation:\n"
        f"- Result: {analysis['level']}\n"
        f"- HanLevel score: {analysis['final_score']:.1f}/100\n"
        f"- Vocabulary difficulty: {vocab_text}\n"
        f"- Grammar complexity: {grammar_score:.1f}/100\n"
        f"- Sentence-length difficulty: {sentence_score:.1f}/100\n"
        f"- Average eojeol per sentence: {avg_eojeol:.1f}\n"
        f"The requested target is {target_level}, which requires a HanLevel "
        f"score {target_text}. Revise the text more decisively toward the "
        f"target while preserving meaning, facts, relationships, names, "
        f"numbers, and the requested style."
    )


def _run_attempt(
    *,
    number: int,
    source_text: str,
    target_level: str,
    style: str,
    source_analysis: dict[str, Any],
    feedback: str | None,
    api_key: str | None,
    model: str | None,
) -> AdaptationAttempt:
    generated = adapt_text(
        text=source_text,
        target_level=target_level,
        style=style,
        original_analysis=source_analysis,
        feedback=feedback,
        api_key=api_key,
        model=model,
    )

    adapted_text = generated["adapted_text"].strip()
    adapted_analysis = analyze_text(adapted_text)

    return AdaptationAttempt(
        number=number,
        adapted_text=adapted_text,
        analysis=adapted_analysis,
        change_summary=generated.get("change_summary", []),
        notable_changes=generated.get("notable_changes", []),
        model=generated["model"],
    )


def adapt_with_evaluation(
    text: str,
    target_level: str,
    style: str,
    original_analysis: dict[str, Any] | None = None,
    *,
    api_key: str | None = None,
    model: str | None = None,
    max_automatic_attempts: int = 2,
) -> dict[str, Any]:
    """Adapt, evaluate, and automatically retry once when needed.

    max_automatic_attempts is intentionally capped at 2 for HanLevel v1.0.
    After that, the UI can offer a manual "Try again" action.
    """

    if max_automatic_attempts < 1:
        raise ValueError("max_automatic_attempts must be at least 1.")

    max_automatic_attempts = min(max_automatic_attempts, 2)

    source_analysis = original_analysis or analyze_text(text)
    attempts: list[AdaptationAttempt] = []

    feedback = None

    for attempt_number in range(1, max_automatic_attempts + 1):
        attempt = _run_attempt(
            number=attempt_number,
            source_text=text,
            target_level=target_level,
            style=style,
            source_analysis=source_analysis,
            feedback=feedback,
            api_key=api_key,
            model=model,
        )
        attempts.append(attempt)

        if target_reached(attempt.analysis, target_level):
            break

        feedback = _format_feedback(attempt.analysis, target_level)

    final_attempt = attempts[-1]
    reached = target_reached(final_attempt.analysis, target_level)

    return {
        "original_text": text,
        "original_analysis": source_analysis,
        "target_level": target_level,
        "style": style,
        "target_reached": reached,
        "attempt_count": len(attempts),
        "final_text": final_attempt.adapted_text,
        "final_analysis": final_attempt.analysis,
        "change_summary": final_attempt.change_summary,
        "notable_changes": final_attempt.notable_changes,
        "model": final_attempt.model,
        "attempts": [
            {
                "number": attempt.number,
                "adapted_text": attempt.adapted_text,
                "analysis": attempt.analysis,
                "score": attempt.score,
                "level": attempt.level,
                "change_summary": attempt.change_summary,
                "notable_changes": attempt.notable_changes,
                "model": attempt.model,
            }
            for attempt in attempts
        ],
    }


def retry_adaptation(
    previous_result: dict[str, Any],
    *,
    api_key: str | None = None,
    model: str | None = None,
) -> dict[str, Any]:
    """Manual retry after the automatic two-attempt cycle has failed.

    This runs one fresh generation using the latest evaluator feedback.
    It does not recursively trigger another automatic retry.
    """

    latest_analysis = previous_result["final_analysis"]
    feedback = _format_feedback(
        latest_analysis,
        previous_result["target_level"],
    )

    attempt = _run_attempt(
        number=int(previous_result.get("attempt_count", 0)) + 1,
        source_text=previous_result["original_text"],
        target_level=previous_result["target_level"],
        style=previous_result["style"],
        source_analysis=previous_result["original_analysis"],
        feedback=feedback,
        api_key=api_key,
        model=model,
    )

    reached = target_reached(
        attempt.analysis,
        previous_result["target_level"],
    )

    attempts = list(previous_result.get("attempts", []))
    attempts.append(
        {
            "number": attempt.number,
            "adapted_text": attempt.adapted_text,
            "analysis": attempt.analysis,
            "score": attempt.score,
            "level": attempt.level,
            "change_summary": attempt.change_summary,
            "notable_changes": attempt.notable_changes,
            "model": attempt.model,
        }
    )

    return {
        **previous_result,
        "target_reached": reached,
        "attempt_count": attempt.number,
        "final_text": attempt.adapted_text,
        "final_analysis": attempt.analysis,
        "change_summary": attempt.change_summary,
        "notable_changes": attempt.notable_changes,
        "model": attempt.model,
        "attempts": attempts,
    }
