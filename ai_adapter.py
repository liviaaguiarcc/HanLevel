"""AI text adaptation layer for HanLevel v1.0.

The generative model adapts text. HanLevel's rule-based analyzer independently
scores every candidate, so generation and evaluation remain separate.
"""

import os
from typing import Literal

from google import genai
from google.genai import types
from pydantic import BaseModel, Field


DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
FALLBACK_MODELS = ("gemini-3.7-flash", "gemini-3.5-flash-lite")

VALID_LEVELS = {"Beginner", "Intermediate", "Advanced"}
VALID_STYLES = {"Natural", "Casual", "Learning-friendly"}

LEVEL_GUIDANCE = {
    "Beginner": (
        "Use very common learner-friendly vocabulary and short, direct "
        "sentences. Prefer simple clause structures and explicit connections. "
        "Paraphrase difficult technical or abstract terms into simpler Korean "
        "when possible instead of preserving the difficult wording itself. "
        "Avoid dense nominalization, long adnominal chains, and nested clauses. "
        "Preserve the propositions and essential information; do not summarize "
        "them away."
    ),
    "Intermediate": (
        "Use natural intermediate-level Korean with moderately varied "
        "vocabulary and grammar. Keep sentences readable while allowing some "
        "connected and embedded structures. Avoid unnecessary advanced lexical "
        "choices."
    ),
    "Advanced": (
        "Use natural Korean appropriate for proficient readers. Increase "
        "lexical and grammatical sophistication only when it sounds natural. "
        "Do not add information or make the text artificially verbose."
    ),
}

STYLE_GUIDANCE = {
    "Natural": (
        "Preserve the source register and tone where they are compatible with "
        "the requested difficulty. If register and target difficulty conflict, "
        "prioritize the target difficulty."
    ),
    "Casual": (
        "Use natural everyday conversational Korean while preserving meaning. "
        "Difficulty control still takes priority over stylistic flourish."
    ),
    "Learning-friendly": (
        "Prioritize clarity, explicit connections between ideas, and "
        "learner-accessible wording while preserving the requested level."
    ),
}

# These are control hints derived from HanLevel v0.1's internal calibration.
# They are not external proficiency standards and are intentionally described
# as soft targets rather than hard linguistic rules.
TARGET_CONTROL = {
    "Beginner": (
        "Aim comfortably below the Beginner cutoff, not barely under it. "
        "As a practical control target: prefer mostly beginner-graded lexical "
        "items; keep sentences around 4-7 eojeol when possible; prefer separate "
        "sentences over clause chains; avoid ETM/ETN-style embedding where a "
        "simple independent sentence can express the same proposition; use "
        "simple connectives sparingly. A final score around 10-20 is safer "
        "than aiming for 24."
    ),
    "Intermediate": (
        "Aim near the middle of the Intermediate band rather than a boundary. "
        "Use a mix of beginner and intermediate vocabulary, readable connected "
        "sentences, and moderate structural complexity."
    ),
    "Advanced": (
        "Aim clearly inside the Advanced band. Use naturally sophisticated "
        "lexical choices, longer connected discourse, and varied grammatical "
        "structure without padding the text or inventing detail."
    ),
}

LEVEL_EXAMPLES = {
    "Beginner": (
        "Difficulty references only (do not copy their content):\n"
        "저는 학생이에요. 매일 학교에 가요.\n"
        "주말에 가족과 영화를 봤어요. 영화가 아주 재미있었어요."
    ),
    "Intermediate": (
        "Difficulty references only (do not copy their content):\n"
        "한국어를 공부한 지 일 년이 되었지만 아직 모르는 표현이 많습니다.\n"
        "친구가 추천해 준 책을 읽어 보았는데 생각보다 내용이 어려웠습니다."
    ),
    "Advanced": (
        "Difficulty references only (do not copy their content):\n"
        "기술의 급속한 발전은 생활의 편리함을 높이는 반면 새로운 사회적 문제를 초래하기도 한다.\n"
        "연구 결과를 해석할 때에는 통계적 유의성뿐만 아니라 연구 설계와 자료 수집 과정의 한계도 함께 고려해야 한다."
    ),
}


class ChangeExample(BaseModel):
    category: Literal["Vocabulary", "Grammar", "Sentence structure", "Style"]
    original: str = Field(
        description="Short source expression or structural description."
    )
    adapted: str = Field(
        description="Short adapted expression or structural description."
    )
    explanation: str = Field(
        description="Concise learner-facing explanation of the change."
    )


class AdaptationResponse(BaseModel):
    adapted_text: str = Field(
        description="The complete adapted Korean text and nothing else."
    )
    change_summary: list[str] = Field(
        description="Two or three concise explanations of the main changes."
    )
    notable_changes: list[ChangeExample] = Field(
        description="Concrete examples of vocabulary, grammar, sentence, or style changes."
    )


def _analysis_summary(analysis: dict) -> str:
    vocabulary_score = analysis["vocabulary"]["vocabulary_score"]
    vocabulary_text = (
        f"{vocabulary_score:.1f}"
        if vocabulary_score is not None
        else "unavailable"
    )

    return (
        f"HanLevel score: {analysis['final_score']:.1f}/100\n"
        f"Estimated level: {analysis['level']}\n"
        f"Vocabulary difficulty: {vocabulary_text}/100\n"
        f"Grammar complexity: "
        f"{analysis['grammar']['grammar_score']:.1f}/100\n"
        f"Sentence-length difficulty: "
        f"{analysis['sentence_length']['sentence_length_score']:.1f}/100\n"
        f"Average eojeol per sentence: "
        f"{analysis['sentence_length']['average_eojeol']:.1f}\n"
        f"Dictionary coverage: {analysis['vocabulary']['coverage']:.1f}%"
    )


def _diagnostic_items(analysis: dict) -> str:
    difficult_words = []
    seen_words = set()

    for item in analysis["vocabulary"]["words"]:
        grade = item.get("grade")
        word = item.get("word")

        if grade not in {"중급", "고급"} or not word or word in seen_words:
            continue

        seen_words.add(word)
        label = "Intermediate" if grade == "중급" else "Advanced"
        difficult_words.append(f"{word} ({label})")

        if len(difficult_words) >= 16:
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

    blocks = []

    if difficult_words:
        blocks.append(
            "Lexical items currently contributing difficulty:\n- "
            + "\n- ".join(difficult_words)
        )

    if structures:
        blocks.append(
            "Structural markers currently contributing complexity:\n- "
            + "\n- ".join(structures)
        )

    return "\n\n".join(blocks) if blocks else "No extra diagnostic items."


def build_adaptation_prompt(
    text: str,
    target_level: str,
    style: str,
    current_analysis: dict,
    feedback: str | None = None,
    original_text: str | None = None,
    attempt_number: int = 1,
) -> str:
    """Build the controlled Korean text-adaptation prompt."""

    if target_level not in VALID_LEVELS:
        raise ValueError(
            f"Invalid target level: {target_level}. "
            f"Choose one of {sorted(VALID_LEVELS)}."
        )

    if style not in VALID_STYLES:
        raise ValueError(
            f"Invalid style: {style}. "
            f"Choose one of {sorted(VALID_STYLES)}."
        )

    semantic_anchor = (original_text or text).strip()

    retry_context = ""
    if feedback:
        retry_context = (
            "\n\nEVALUATOR FEEDBACK FROM THE PREVIOUS CANDIDATE\n"
            f"{feedback}"
        )

    return f"""
You are the generative adaptation component of HanLevel, a Korean readability
tool for language learners.

PRIORITIES — FOLLOW IN THIS ORDER
1. Preserve the original propositions, facts, names, numbers, relationships,
   speaker position, and conclusion.
2. Hit the requested HanLevel difficulty band.
3. Apply the requested style.
If style conflicts with the target difficulty, relax the style before missing
the target. Preserve meaning, but you may paraphrase difficult terminology into
simpler explanations when adapting downward.

ATTEMPT
{attempt_number}

TARGET DIFFICULTY
{target_level}

TARGET-LEVEL GUIDANCE
{LEVEL_GUIDANCE[target_level]}

HANLEVEL CONTROL HINTS
{TARGET_CONTROL[target_level]}

REFERENCE EXAMPLES
{LEVEL_EXAMPLES[target_level]}

STYLE
{style}

STYLE GUIDANCE
{STYLE_GUIDANCE[style]}

CURRENT CANDIDATE HANLEVEL ANALYSIS
{_analysis_summary(current_analysis)}

CURRENT DIAGNOSTIC ITEMS
{_diagnostic_items(current_analysis)}

ORIGINAL MEANING ANCHOR
This is the original text whose meaning must remain represented:
{semantic_anchor}

CURRENT TEXT TO ADAPT OR REVISE
{text}

MEANING-PRESERVATION RULES
- Do not invent facts or examples.
- Do not change names, numbers, relationships, stance, or conclusions.
- Do not turn the text into a summary.
- Preserve each important proposition, even if it must be unpacked into several
  shorter sentences.
- You may replace terminology with plain-language paraphrases, restructure
  clauses, split or combine sentences, make implicit links explicit, and adjust
  grammar/register.
- When adapting upward, sophistication must be natural rather than verbose.
- When adapting downward, simple wording and sentence structure matter more
  than preserving the original surface form.
- Return coherent, natural Korean rather than disconnected textbook fragments.
{retry_context}

OUTPUT
Adaptation quality is the highest priority. Return the complete adapted Korean
text plus concise educational change notes. The notes must describe changes
that actually appear in the adapted text.
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
    """Adapt Korean text with Gemini and return structured output."""

    if not text or not text.strip():
        raise ValueError("Text cannot be empty.")

    selected_model = model or DEFAULT_MODEL

    if api_key:
        client = genai.Client(api_key=api_key)
    else:
        client = genai.Client()

    prompt = build_adaptation_prompt(
        text=text.strip(),
        target_level=target_level,
        style=style,
        current_analysis=original_analysis,
        feedback=feedback,
        original_text=original_text,
        attempt_number=attempt_number,
    )

    candidate_models = [selected_model]

    for fallback_model in FALLBACK_MODELS:
        if fallback_model not in candidate_models:
            candidate_models.append(fallback_model)

    last_error = None
    response = None
    used_model = None

    for candidate_model in candidate_models:
        try:
            response = client.models.generate_content(
                model=candidate_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=4096,
                    response_mime_type="application/json",
                    response_schema=AdaptationResponse,
                    thinking_config=types.ThinkingConfig(
                        thinking_level="medium",
                    ),
                ),
            )
            used_model = candidate_model
            break

        except Exception as exc:
            error_text = str(exc)
            is_capacity_error = (
                "503" in error_text
                or "UNAVAILABLE" in error_text
                or "high demand" in error_text.lower()
            )

            if not is_capacity_error:
                raise

            last_error = exc

    if response is None:
        raise RuntimeError(
            "Gemini is temporarily unavailable across the configured "
            "fallback models. Please try again shortly."
        ) from last_error

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    parsed = AdaptationResponse.model_validate_json(response.text)

    return {
        **parsed.model_dump(),
        "model": used_model,
    }
