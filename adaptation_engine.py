"""HanLevel v1.0 adaptation workflow.

Each AI generation produces three candidate rewrites in a single model call.
HanLevel scores all candidates locally and selects the one closest to the
requested readability band. Manual retry is available only when needed.
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
class CandidateResult:
    number: int
    generation: int
    adapted_text: str
    analysis: dict[str, Any]
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
    if target_level not in TARGET_BANDS:
        raise ValueError(f"Unknown target level: {target_level}")

    lower, upper = TARGET_BANDS[target_level]
    score = float(analysis["final_score"])

    if lower <= score < upper:
        return 0.0

    if score < lower:
        return lower - score

    return score - upper


def _best_candidate(
    candidates: list[CandidateResult],
    target_level: str,
) -> CandidateResult:
    successful = [
        candidate
        for candidate in candidates
        if target_reached(candidate.analysis, target_level)
    ]

    if successful:
        center = TARGET_CENTERS[target_level]
        return min(
            successful,
            key=lambda candidate: abs(candidate.score - center),
        )

    return min(
        candidates,
        key=lambda candidate: distance_to_target(
            candidate.analysis,
            target_level,
        ),
    )


def _serialize_candidate(candidate: CandidateResult) -> dict[str, Any]:
    return {
        "number": candidate.number,
        "generation": candidate.generation,
        "adapted_text": candidate.adapted_text,
        "analysis": candidate.analysis,
        "score": candidate.score,
        "level": candidate.level,
        "model": candidate.model,
        "latency_seconds": candidate.latency_seconds,
    }


def _difficult_word_count(analysis: dict[str, Any]) -> int:
    return sum(
        1
        for item in analysis["vocabulary"]["words"]
        if item.get("grade") in {"중급", "고급"}
    )


def _build_change_explanations(
    original_analysis: dict[str, Any],
    adapted_analysis: dict[str, Any],
) -> tuple[list[str], list[dict[str, str]]]:
    original_score = float(original_analysis["final_score"])
    adapted_score = float(adapted_analysis["final_score"])

    original_avg = float(
        original_analysis["sentence_length"]["average_eojeol"]
    )
    adapted_avg = float(
        adapted_analysis["sentence_length"]["average_eojeol"]
    )

    original_sentences = int(
        original_analysis["sentence_length"]["sentence_count"]
    )
    adapted_sentences = int(
        adapted_analysis["sentence_length"]["sentence_count"]
    )

    original_difficult = _difficult_word_count(original_analysis)
    adapted_difficult = _difficult_word_count(adapted_analysis)

    original_structures = len(original_analysis["grammar"]["structures"])
    adapted_structures = len(adapted_analysis["grammar"]["structures"])

    summaries = [
        (
            f"HanLevel score changed from {original_score:.1f} "
            f"to {adapted_score:.1f}."
        ),
        (
            f"Average sentence length changed from {original_avg:.1f} "
            f"to {adapted_avg:.1f} eojeol."
        ),
    ]

    notable_changes = [
        {
            "category": "Vocabulary",
            "original": f"{original_difficult} intermediate/advanced items detected",
            "adapted": f"{adapted_difficult} intermediate/advanced items detected",
            "explanation": (
                "This is computed directly from HanLevel's KRDICT-based "
                "vocabulary analysis."
            ),
        },
        {
            "category": "Sentence structure",
            "original": (
                f"{original_sentences} sentence(s), "
                f"{original_avg:.1f} eojeol on average"
            ),
            "adapted": (
                f"{adapted_sentences} sentence(s), "
                f"{adapted_avg:.1f} eojeol on average"
            ),
            "explanation": (
                "Shorter or more segmented sentences generally reduce the "
                "sentence-length component of HanLevel."
            ),
        },
        {
            "category": "Grammar",
            "original": f"{original_structures} weighted structures detected",
            "adapted": f"{adapted_structures} weighted structures detected",
            "explanation": (
                "This count reflects the grammar markers HanLevel currently "
                "uses in its rule-based complexity score."
            ),
        },
    ]

    return summaries, notable_changes


def _format_feedback(
    analysis: dict[str, Any],
    target_level: str,
) -> str:
    vocab_score = analysis["vocabulary"]["vocabulary_score"]
    vocab_text = (
        f"{vocab_score:.1f}"
        if vocab_score is not None
        else "unavailable"
    )

    grammar_score = float(analysis["grammar"]["grammar_score"])
    sentence_score = float(
        analysis["sentence_length"]["sentence_length_score"]
    )

    contributions = {
        "Grammar": grammar_score * 0.35,
        "Sentence length": sentence_score * 0.20,
    }

    if vocab_score is not None:
        contributions["Vocabulary"] = float(vocab_score) * 0.45

    blocker = max(contributions, key=contributions.get)

    if blocker == "Vocabulary":
        action = (
            "Replace or paraphrase the remaining intermediate/advanced words "
            "using common Korean. Preserve concepts, not difficult wording."
        )
    elif blocker == "Grammar":
        action = (
            "Use more independent sentences and fewer embedded, adnominal, "
            "nominalized, or heavily connected structures."
        )
    else:
        action = (
            "Split sentences more aggressively while preserving all important "
            "propositions."
        )

    return (
        f"Best candidate still scored {analysis['final_score']:.1f}/100 "
        f"({analysis['level']}). Target: {target_level}. "
        f"Vocabulary={vocab_text}, Grammar={grammar_score:.1f}, "
        f"Sentence={sentence_score:.1f}. "
        f"Main blocker: {blocker}. {action}"
    )


def _generate_and_score(
    *,
    text: str,
    original_text: str,
    target_level: str,
    style: str,
    current_analysis: dict[str, Any],
    generation: int,
    first_candidate_number: int,
    feedback: str | None,
    api_key: str | None,
    model: str | None,
) -> list[CandidateResult]:
    generated = adapt_text(
        text=text,
        target_level=target_level,
        style=style,
        original_analysis=current_analysis,
        feedback=feedback,
        api_key=api_key,
        model=model,
        original_text=original_text,
        attempt_number=generation,
    )

    results = []

    for offset, candidate_text in enumerate(generated["candidates"]):
        analysis = analyze_text(candidate_text)
        results.append(
            CandidateResult(
                number=first_candidate_number + offset,
                generation=generation,
                adapted_text=candidate_text,
                analysis=analysis,
                model=generated["model"],
                latency_seconds=float(
                    generated.get("latency_seconds", 0.0)
                ),
            )
        )

    return results


def adapt_with_evaluation(
    text: str,
    target_level: str,
    style: str,
    original_analysis: dict[str, Any] | None = None,
    *,
    api_key: str | None = None,
    model: str | None = None,
    max_automatic_attempts: int = 1,
) -> dict[str, Any]:
    """Generate three candidates once, score locally, and select the best.

    There is intentionally no automatic second API call. This keeps the
    interactive experience fast. If all three candidates miss the target, the
    UI offers a manual retry using HanLevel's diagnostics.
    """

    original_text = text.strip()

    if not original_text:
        raise ValueError("Text cannot be empty.")

    source_analysis = original_analysis or analyze_text(original_text)

    candidates = _generate_and_score(
        text=original_text,
        original_text=original_text,
        target_level=target_level,
        style=style,
        current_analysis=source_analysis,
        generation=1,
        first_candidate_number=1,
        feedback=None,
        api_key=api_key,
        model=model,
    )

    best = _best_candidate(candidates, target_level)
    reached = target_reached(best.analysis, target_level)

    change_summary, notable_changes = _build_change_explanations(
        source_analysis,
        best.analysis,
    )

    return {
        "original_text": original_text,
        "original_analysis": source_analysis,
        "target_level": target_level,
        "style": style,
        "target_reached": reached,
        "attempt_count": 1,
        "generation_count": 1,
        "best_attempt_number": best.number,
        "best_candidate_number": best.number,
        "final_text": best.adapted_text,
        "final_analysis": best.analysis,
        "change_summary": change_summary,
        "notable_changes": notable_changes,
        "model": best.model,
        "attempts": [
            _serialize_candidate(candidate)
            for candidate in candidates
        ],
    }


def retry_adaptation(
    previous_result: dict[str, Any],
    *,
    api_key: str | None = None,
    model: str | None = None,
) -> dict[str, Any]:
    """Generate three revised candidates only when the user asks to retry."""

    current_text = previous_result["final_text"]
    current_analysis = previous_result["final_analysis"]
    generation = int(previous_result.get("generation_count", 1)) + 1

    existing = list(previous_result.get("attempts", []))
    first_candidate_number = len(existing) + 1

    new_candidates = _generate_and_score(
        text=current_text,
        original_text=previous_result["original_text"],
        target_level=previous_result["target_level"],
        style=previous_result["style"],
        current_analysis=current_analysis,
        generation=generation,
        first_candidate_number=first_candidate_number,
        feedback=_format_feedback(
            current_analysis,
            previous_result["target_level"],
        ),
        api_key=api_key,
        model=model,
    )

    all_candidates = existing + [
        _serialize_candidate(candidate)
        for candidate in new_candidates
    ]

    # Reconstruct lightweight CandidateResult objects so the best candidate can
    # be selected across both generations.
    reconstructed = [
        CandidateResult(
            number=int(item["number"]),
            generation=int(item.get("generation", 1)),
            adapted_text=item["adapted_text"],
            analysis=item["analysis"],
            model=item.get("model", previous_result.get("model", "")),
            latency_seconds=float(item.get("latency_seconds", 0.0)),
        )
        for item in all_candidates
    ]

    best = _best_candidate(
        reconstructed,
        previous_result["target_level"],
    )

    reached = target_reached(
        best.analysis,
        previous_result["target_level"],
    )

    change_summary, notable_changes = _build_change_explanations(
        previous_result["original_analysis"],
        best.analysis,
    )

    return {
        **previous_result,
        "target_reached": reached,
        "attempt_count": generation,
        "generation_count": generation,
        "best_attempt_number": best.number,
        "best_candidate_number": best.number,
        "final_text": best.adapted_text,
        "final_analysis": best.analysis,
        "change_summary": change_summary,
        "notable_changes": notable_changes,
        "model": best.model,
        "attempts": all_candidates,
    }
