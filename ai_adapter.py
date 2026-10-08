"""AI text adaptation layer for HanLevel v1.0.

One Gemini call generates several meaning-preserving candidates. HanLevel then
scores those candidates locally and selects the one closest to the requested
readability band.
"""

import os
import time

from google import genai
from google.genai import types
from pydantic import BaseModel, Field


DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
FALLBACK_MODELS = ("gemini-3.5-flash-lite",)

VALID_LEVELS = {"Beginner", "Intermediate", "Advanced"}
VALID_STYLES = {"Natural", "Casual", "Learning-friendly"}


class AdaptationResponse(BaseModel):
    candidates: list[str] = Field(
        min_length=3,
        max_length=3,
        description=(
            "Exactly three complete Korean adaptations with the same meaning, "
            "ordered from moderate to strongest movement toward the target."
        ),
    )


def _analysis_summary(analysis: dict) -> str:
    vocab = analysis["vocabulary"]["vocabulary_score"]
    vocab_text = f"{vocab:.1f}" if vocab is not None else "unavailable"

    return (
        f"score={analysis['final_score']:.1f}; "
        f"level={analysis['level']}; "
        f"vocabulary={vocab_text}; "
        f"grammar={analysis['grammar']['grammar_score']:.1f}; "
        f"sentence={analysis['sentence_length']['sentence_length_score']:.1f}; "
        f"avg_eojeol={analysis['sentence_length']['average_eojeol']:.1f}"
    )


def _difficult_words(analysis: dict, limit: int = 10) -> str:
    words = []
    seen = set()

    for item in analysis["vocabulary"]["words"]:
        if item.get("grade") not in {"중급", "고급"}:
            continue

        word = item.get("word")
        if not word or word in seen:
            continue

        seen.add(word)
        words.append(word)

        if len(words) >= limit:
            break

    return ", ".join(words) if words else "none detected"


def _complex_structures(analysis: dict, limit: int = 8) -> str:
    structures = []
    seen = set()

    for item in analysis["grammar"]["structures"]:
        form = item.get("form")
        tag = item.get("tag")
        key = (form, tag)

        if not form or key in seen:
            continue

        seen.add(key)
        structures.append(f"{form}({tag})")

        if len(structures) >= limit:
            break

    return ", ".join(structures) if structures else "none detected"


def _target_instructions(target_level: str) -> str:
    if target_level == "Beginner":
        return (
            "BEGINNER TARGET: HanLevel must score below 25; aim around 10-20. "
            "Generate three increasingly strong simplifications. Candidate 3 "
            "must be genuinely beginner-safe: use very common vocabulary, "
            "paraphrase technical/abstract nouns with simple Korean, split "
            "ideas into short independent sentences, and avoid nested clauses. "
            "For short source texts, 3-7 eojeol per sentence is a useful goal. "
            "Do not preserve difficult wording just because it appears in the "
            "source; preserve the concept instead."
        )

    if target_level == "Intermediate":
        return (
            "INTERMEDIATE TARGET: HanLevel must score from 25 to below 50; aim "
            "near the middle of the band. Generate three alternatives with "
            "moderate vocabulary and grammar, avoiding both oversimplification "
            "and dense advanced prose."
        )

    return (
        "ADVANCED TARGET: HanLevel must score 50 or above. Generate three "
        "natural alternatives with increasing lexical and grammatical "
        "sophistication, but never add facts or artificial verbosity."
    )


def _style_instructions(style: str) -> str:
    if style == "Casual":
        return "Use natural everyday conversational Korean."
    if style == "Learning-friendly":
        return "Prioritize transparent structure and learner-accessible wording."
    return (
        "Keep the source tone where possible, but target difficulty takes "
        "priority over preserving the original surface style."
    )


def build_adaptation_prompt(
    text: str,
    target_level: str,
    style: str,
    current_analysis: dict,
    feedback: str | None = None,
    original_text: str | None = None,
) -> str:
    if target_level not in VALID_LEVELS:
        raise ValueError(f"Invalid target level: {target_level}")

    if style not in VALID_STYLES:
        raise ValueError(f"Invalid style: {style}")

    original = (original_text or text).strip()

    feedback_block = ""
    if feedback:
        feedback_block = f"\nEvaluator feedback:\n{feedback}\n"

    return f"""
Adapt this Korean text for HanLevel.

PRIORITY ORDER
1. Preserve every important proposition, fact, number, name, relationship,
   stance, and conclusion from the original.
2. Reach the requested HanLevel difficulty.
3. Apply the requested style.

{_target_instructions(target_level)}

STYLE
{style}: {_style_instructions(style)}

CURRENT HANLEVEL ANALYSIS
{_analysis_summary(current_analysis)}

DIFFICULT WORDS TO ADDRESS
{_difficult_words(current_analysis)}

COMPLEX STRUCTURES TO ADDRESS
{_complex_structures(current_analysis)}

ORIGINAL MEANING ANCHOR
{original}

TEXT TO REWRITE
{text}
{feedback_block}
RULES
- Produce exactly 3 complete Korean candidates.
- All 3 must preserve the same meaning.
- Do not summarize away information.
- Do not invent examples or facts.
- Candidates must differ meaningfully in how strongly they move toward the
  target, especially for Beginner.
- For downward adaptation, replace difficult terms with plain-language
  paraphrases when possible instead of retaining the difficult term.
- Return only the structured response requested by the schema.
""".strip()


def adapt_text(
    text: str,
    target_level: str,
    style: str,
    original_analysis: dict,
    feedback: str | None = None,
    api_key: str | None = None,
    model: str | None = None,
    original_text: str | None = None,
    attempt_number: int = 1,
) -> dict:
    """Generate three candidate adaptations in one bounded Gemini request."""

    if not text or not text.strip():
        raise ValueError("Text cannot be empty.")

    selected_model = model or DEFAULT_MODEL

    http_options = types.HttpOptions(
        retry_options=types.HttpRetryOptions(
            attempts=1,
            http_status_codes=[408, 429, 500, 502, 503, 504],
        ),
    )

    if api_key:
        client = genai.Client(
            api_key=api_key,
            http_options=http_options,
        )
    else:
        client = genai.Client(http_options=http_options)

    prompt = build_adaptation_prompt(
        text=text.strip(),
        target_level=target_level,
        style=style,
        current_analysis=original_analysis,
        feedback=feedback,
        original_text=original_text,
    )

    candidate_models = [selected_model]
    for fallback in FALLBACK_MODELS:
        if fallback not in candidate_models:
            candidate_models.append(fallback)

    started_at = time.perf_counter()
    response = None
    used_model = None
    last_error = None

    for candidate_model in candidate_models:
        try:
            response = client.models.generate_content(
                model=candidate_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=1200,
                    response_mime_type="application/json",
                    response_schema=AdaptationResponse,
                    thinking_config=types.ThinkingConfig(
                        thinking_level="low",
                    ),
                ),
            )
            used_model = candidate_model
            break

        except Exception as exc:
            error_text = str(exc)
            lowered = error_text.lower()

            recoverable = (
                "503" in error_text
                or "unavailable" in lowered
                or "high demand" in lowered
                or "429" in error_text
                or "resource_exhausted" in lowered
                or "404" in error_text
                or "not_found" in lowered
            )

            if not recoverable:
                raise

            last_error = exc

    latency_seconds = time.perf_counter() - started_at

    if response is None:
        raise RuntimeError(
            "Gemini is temporarily unavailable on the configured models. "
            "Please try again shortly."
        ) from last_error

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    parsed = AdaptationResponse.model_validate_json(response.text)

    clean_candidates = [
        candidate.strip()
        for candidate in parsed.candidates
        if candidate and candidate.strip()
    ]

    if len(clean_candidates) != 3:
        raise RuntimeError("Gemini did not return exactly three valid candidates.")

    return {
        "candidates": clean_candidates,
        "model": used_model,
        "latency_seconds": latency_seconds,
    }
