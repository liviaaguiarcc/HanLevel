"""HanLevel v1.0 adaptation workflow.

Gemini generates a candidate, HanLevel independently evaluates it, and failed
candidates are revised iteratively. Generation and evaluation remain separate.
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

TARGET_CENTERS = {
    "Beginner": 15.0,
    "Intermediate": 37.5,
    "Advanced": 65.0,
}


@dataclass
class AdaptationAttempt:
    number: int
    adapted_text: str
    analysis: dict[str, Any]
    change_summary: list[str]
    notable_changes: list[dict[str, Any]]
    model: str
    latency_seconds: float = 0.0

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


def distance_to_target(analysis: dict[str, Any], target_level: str) -> float:
    """Distance from a score to the requested band.

    Inside the band, distance is zero. Outside it, smaller is better.
    """
    if target_level not in TARGET_BANDS:
        raise ValueError(f"Unknown target level: {target_level}")

    lower, upper = TARGET_BANDS[target_level]
    score = float(analysis["final_score"])

    if lower <= score < upper:
        return 0.0

    if score < lower:
        return lower - score

    return score - upper


def _format_feedback(
    analysis: dict[str, Any],
    target_level: str,
    previous_text: str | None = None,
) -> str:
    """Create actionable evaluator feedback for a corrective revision."""

    vocab_score = analysis["vocabulary"]["vocabulary_score"]
    vocab_text = (
        f"{vocab_score:.1f}/100"
        if vocab_score is not None
        else "unavailable"
    )

    grammar_score = analysis["grammar"]["grammar_score"]
    sentence_score = analysis["sentence_length"]["sentence_length_score"]
    avg_eojeol = analysis["sentence_length"]["average_eojeol"]

    # Mirror HanLevel's actual weighting so the corrective prompt attacks the
    # component that is contributing the most to the current score.
    contributions = {
        "Grammar": grammar_score * 0.35,
        "Sentence length": sentence_score * 0.20,
    }

    if vocab_score is not None:
        contributions["Vocabulary"] = vocab_score * 0.45

    strongest_component = max(contributions, key=contributions.get)

    if strongest_component == "Vocabulary":
        blocker_advice = (
            "The largest weighted blocker is VOCABULARY. Replace or paraphrase "
            "the listed intermediate/advanced lexical items with common words "
            "or simple explanatory phrases. Preserve the concept, not the "
            "original difficult term."
        )
    elif strongest_component == "Grammar":
        blocker_advice = (
            "The largest weighted blocker is GRAMMAR. Break embedded clauses "
            "into independent sentences, reduce nominalization and adnominal "
            "chains, and prefer direct predicate structures."
        )
    else:
        blocker_advice = (
            "The largest weighted blocker is SENTENCE LENGTH. Split long "
            "sentences aggressively while preserving every proposition."
        )

    challenging_words = []
    seen_words = set()

    for item in analysis["vocabulary"]["words"]:
        if item.get("grade") not in {"중급", "고급"}:
            continue

        word = item.get("word")

        if not word or word in seen_words:
            continue

        seen_words.add(word)
        challenging_words.append(word)

        if len(challenging_words) >= 16:
            break

    structures = []
    seen_structures = set()

    for item in analysis["grammar"]["structures"]:
        form = item.get("form")
        tag = item.get("tag")
        key = (form, tag)

        if not form or key in seen_structures:
            continue

        seen_structures.add(key)
        structures.append(f"{form} ({tag})")

        if len(structures) >= 16:
            break

    if target_level == "Beginner":
        target_text = (
            "below 25; aim around 10-20 rather than barely below 25"
        )
        directional_advice = (
            "Revise the CURRENT CANDIDATE, not the original wording. "
            "Reduce difficult lexical items one by one. Split long clauses "
            "into short independent sentences. Replace abstract nouns with "
            "plain-language paraphrases where possible. Avoid ETM/ETN-style "
            "embedding and long connective chains when the same proposition "
            "can be expressed directly."
        )

    elif target_level == "Intermediate":
        target_text = (
            "from 25 up to, but not including, 50; aim around 32-42"
        )
        directional_advice = (
            "Revise the CURRENT CANDIDATE toward moderate vocabulary and "
            "grammar. Avoid both beginner-like oversimplification and dense "
            "advanced structures."
        )

    else:
        target_text = "50 or higher; aim around 55-70"
        directional_advice = (
            "Revise the CURRENT CANDIDATE with natural lexical and grammatical "
            "sophistication. Do not add irrelevant facts or artificial padding."
        )

    previous_block = ""

    if previous_text:
        previous_block = (
            "\n\nCURRENT CANDIDATE TO REVISE\n"
            f"{previous_text[:6000]}"
        )

    vocab_block = (
        "\n- Difficult lexical items still detected: "
        + ", ".join(challenging_words)
        if challenging_words
        else ""
    )

    structure_block = (
        "\n- Complexity markers still detected: "
        + ", ".join(structures)
        if structures
        else ""
    )

    return (
        f"Independent HanLevel evaluation of the current candidate:\n"
        f"- Result: {analysis['level']}\n"
        f"- HanLevel score: {analysis['final_score']:.1f}/100\n"
        f"- Vocabulary difficulty: {vocab_text}\n"
        f"- Grammar complexity: {grammar_score:.1f}/100\n"
        f"- Sentence-length difficulty: {sentence_score:.1f}/100\n"
        f"- Average eojeol per sentence: {avg_eojeol:.1f}\n"
        f"- Strongest weighted blocker: {strongest_component}\n"
        f"- Priority action: {blocker_advice}"
        f"{vocab_block}{structure_block}\n"
        f"The requested target is {target_level}, which requires a score "
        f"{target_text}. {directional_advice} Preserve the original meaning, "
        f"facts, names, numbers, relationships, stance, and conclusions."
        f"{previous_block}"
    )


def _run_attempt(
    *,
    number: int,
    candidate_text: str,
    target_level: str,
    style: str,
    current_analysis: dict[str, Any],
    original_text: str,
    feedback: str | None,
    api_key: str | None,
    model: str | None,
) -> AdaptationAttempt:
    """Generate one revision of the current candidate and evaluate it."""

    generated = adapt_text(
        text=candidate_text,
        target_level=target_level,
        style=style,
        original_analysis=current_analysis,
        feedback=feedback,
        api_key=api_key,
        model=model,
        original_text=original_text,
        attempt_number=number,
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
        latency_seconds=float(generated.get("latency_seconds", 0.0)),
    )


def _serialize_attempt(attempt: AdaptationAttempt) -> dict[str, Any]:
    return {
        "number": attempt.number,
        "adapted_text": attempt.adapted_text,
        "analysis": attempt.analysis,
        "score": attempt.score,
        "level": attempt.level,
        "change_summary": attempt.change_summary,
        "notable_changes": attempt.notable_changes,
        "model": attempt.model,
        "latency_seconds": attempt.latency_seconds,
    }


def _best_attempt(
    attempts: list[AdaptationAttempt],
    target_level: str,
) -> AdaptationAttempt:
    """Return the candidate closest to the requested target band."""

    successful = [
        attempt
        for attempt in attempts
        if target_reached(attempt.analysis, target_level)
    ]

    if successful:
        target_center = TARGET_CENTERS[target_level]
        return min(
            successful,
            key=lambda attempt: abs(attempt.score - target_center),
        )

    return min(
        attempts,
        key=lambda attempt: distance_to_target(
            attempt.analysis,
            target_level,
        ),
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
    """Adapt, evaluate, and automatically revise once when needed.

    The important behavior is iterative:
    attempt 1 adapts the original;
    attempt 2 revises attempt 1 using HanLevel's diagnostics.
    """

    if max_automatic_attempts < 1:
        raise ValueError("max_automatic_attempts must be at least 1.")

    max_automatic_attempts = min(max_automatic_attempts, 2)

    original_text = text.strip()
    source_analysis = original_analysis or analyze_text(original_text)

    attempts: list[AdaptationAttempt] = []
    candidate_text = original_text
    current_analysis = source_analysis
    feedback = None

    for attempt_number in range(1, max_automatic_attempts + 1):
        attempt = _run_attempt(
            number=attempt_number,
            candidate_text=candidate_text,
            target_level=target_level,
            style=style,
            current_analysis=current_analysis,
            original_text=original_text,
            feedback=feedback,
            api_key=api_key,
            model=model,
        )

        attempts.append(attempt)

        if target_reached(attempt.analysis, target_level):
            break

        # Critical: the next pass revises the generated candidate itself.
        candidate_text = attempt.adapted_text
        current_analysis = attempt.analysis
        feedback = _format_feedback(
            attempt.analysis,
            target_level,
            previous_text=attempt.adapted_text,
        )

    best_attempt = _best_attempt(attempts, target_level)
    reached = target_reached(best_attempt.analysis, target_level)

    return {
        "original_text": original_text,
        "original_analysis": source_analysis,
        "target_level": target_level,
        "style": style,
        "target_reached": reached,
        "attempt_count": len(attempts),
        "best_attempt_number": best_attempt.number,
        "final_text": best_attempt.adapted_text,
        "final_analysis": best_attempt.analysis,
        "change_summary": best_attempt.change_summary,
        "notable_changes": best_attempt.notable_changes,
        "model": best_attempt.model,
        "attempts": [
            _serialize_attempt(attempt)
            for attempt in attempts
        ],
    }


def retry_adaptation(
    previous_result: dict[str, Any],
    *,
    api_key: str | None = None,
    model: str | None = None,
) -> dict[str, Any]:
    """Run one manual revision of the best current candidate."""

    current_text = previous_result["final_text"]
    current_analysis = previous_result["final_analysis"]

    feedback = _format_feedback(
        current_analysis,
        previous_result["target_level"],
        previous_text=current_text,
    )

    attempt_number = int(previous_result.get("attempt_count", 0)) + 1

    new_attempt = _run_attempt(
        number=attempt_number,
        candidate_text=current_text,
        target_level=previous_result["target_level"],
        style=previous_result["style"],
        current_analysis=current_analysis,
        original_text=previous_result["original_text"],
        feedback=feedback,
        api_key=api_key,
        model=model,
    )

    existing_attempts = list(previous_result.get("attempts", []))
    existing_attempts.append(_serialize_attempt(new_attempt))

    # Compare the new candidate with the previous best instead of assuming
    # later automatically means better.
    previous_best = AdaptationAttempt(
        number=int(previous_result.get("best_attempt_number", 1)),
        adapted_text=previous_result["final_text"],
        analysis=previous_result["final_analysis"],
        change_summary=previous_result.get("change_summary", []),
        notable_changes=previous_result.get("notable_changes", []),
        model=previous_result.get("model", new_attempt.model),
        latency_seconds=0.0,
    )

    best_attempt = _best_attempt(
        [previous_best, new_attempt],
        previous_result["target_level"],
    )

    reached = target_reached(
        best_attempt.analysis,
        previous_result["target_level"],
    )

    return {
        **previous_result,
        "target_reached": reached,
        "attempt_count": attempt_number,
        "best_attempt_number": best_attempt.number,
        "final_text": best_attempt.adapted_text,
        "final_analysis": best_attempt.analysis,
        "change_summary": best_attempt.change_summary,
        "notable_changes": best_attempt.notable_changes,
        "model": best_attempt.model,
        "attempts": existing_attempts,
    }
