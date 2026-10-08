"""AI text adaptation layer for HanLevel v1.0.

This module is intentionally separate from HanLevel's rule-based analyzer.
The generative model adapts text; HanLevel independently evaluates the result.
"""

import os
from typing import Literal

from google import genai
from google.genai import types
from pydantic import BaseModel, Field


DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

VALID_LEVELS = {"Beginner", "Intermediate", "Advanced"}
VALID_STYLES = {"Natural", "Casual", "Learning-friendly"}

LEVEL_GUIDANCE = {
    "Beginner": (
        "Use common learner-friendly vocabulary, short and clear sentences, "
        "and simple grammatical connections. Preserve essential information "
        "instead of summarizing it away."
    ),
    "Intermediate": (
        "Use natural intermediate-level Korean with moderately varied "
        "vocabulary and grammar. Keep sentences readable while allowing "
        "some connected and embedded structures."
    ),
    "Advanced": (
        "Use natural Korean appropriate for proficient readers. Increase "
        "lexical and grammatical sophistication only when it sounds natural; "
        "do not make the text artificially verbose or obscure."
    ),
}

STYLE_GUIDANCE = {
    "Natural": (
        "Preserve the source text's register and tone as closely as possible."
    ),
    "Casual": (
        "Use natural everyday conversational Korean while preserving meaning."
    ),
    "Learning-friendly": (
        "Prioritize clarity, explicit connections between ideas, and "
        "learner-accessible wording while preserving the requested level."
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


def build_adaptation_prompt(
    text: str,
    target_level: str,
    style: str,
    original_analysis: dict,
    feedback: str | None = None,
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

    retry_context = ""
    if feedback:
        retry_context = (
            "\n\nA previous adaptation missed the target. "
            "Use the independent HanLevel feedback below to revise more "
            "precisely. Do not mention this retry in the adapted text.\n"
            f"{feedback}"
        )

    return f"""
You are the generative adaptation component of HanLevel, a Korean readability
tool for language learners.

TASK
Adapt the Korean source text to the requested HanLevel target difficulty and
style.

TARGET DIFFICULTY
{target_level}

TARGET-LEVEL GUIDANCE
{LEVEL_GUIDANCE[target_level]}

STYLE
{style}

STYLE GUIDANCE
{STYLE_GUIDANCE[style]}

SOURCE HANLEVEL ANALYSIS
{_analysis_summary(original_analysis)}

MEANING-PRESERVATION RULES
- Preserve the original meaning, facts, named entities, numbers, relationships,
  speaker position, and conclusion as closely as possible.
- Do not invent facts or examples.
- Do not remove essential information.
- Do not turn the text into a summary.
- You may replace vocabulary, restructure clauses, split or combine sentences,
  make connections more explicit, and adjust grammar/register when needed.
- If adapting upward, increase sophistication naturally rather than adding
  unnecessary verbosity.
- If adapting downward, simplify language and structure without flattening the
  core meaning.
- Return natural Korean, not textbook-like fragments.
- The target level and style are independent: a text may remain at the same
  level while its style changes.

SOURCE TEXT
{text}
{retry_context}

OUTPUT
Return the complete adapted Korean text plus concise educational change notes.
The change notes must describe changes that actually appear in the output.
""".strip()


def adapt_text(
    text: str,
    target_level: str,
    style: str,
    original_analysis: dict,
    feedback: str | None = None,
    api_key: str | None = None,
    model: str | None = None,
) -> dict:
    """Adapt Korean text with Gemini and return structured output."""

    if not text or not text.strip():
        raise ValueError("Text cannot be empty.")

    selected_model = model or DEFAULT_MODEL

    if api_key:
        client = genai.Client(api_key=api_key)
    else:
        # The Google SDK automatically reads GEMINI_API_KEY when available.
        client = genai.Client()

    prompt = build_adaptation_prompt(
        text=text.strip(),
        target_level=target_level,
        style=style,
        original_analysis=original_analysis,
        feedback=feedback,
    )

    response = client.models.generate_content(
        model=selected_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.35,
            max_output_tokens=2500,
            response_mime_type="application/json",
            response_schema=AdaptationResponse,
            thinking_config=types.ThinkingConfig(
                thinking_budget=0,
            ),
        ),
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    parsed = AdaptationResponse.model_validate_json(response.text)

    return {
        **parsed.model_dump(),
        "model": selected_model,
    }
