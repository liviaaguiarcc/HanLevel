"""Grounded AI tutor for HanLevel v1.0.

The tutor receives the user's Korean text plus HanLevel's rule-based analysis.
It does not replace the analyzer and must distinguish analyzer evidence from
general language-teaching explanations.
"""

import os
import time

from google import genai
from google.genai import types


DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
FALLBACK_MODELS = ("gemini-3.5-flash-lite",)


def _difficult_words(analysis: dict, limit: int = 16) -> list[str]:
    items = []
    seen = set()

    for item in analysis["vocabulary"]["words"]:
        word = item.get("word")
        grade = item.get("grade")

        if not word or grade not in {"중급", "고급"} or word in seen:
            continue

        seen.add(word)
        label = "Intermediate" if grade == "중급" else "Advanced"
        items.append(f"{word} — {label}")

        if len(items) >= limit:
            break

    return items


def _grammar_markers(analysis: dict, limit: int = 16) -> list[str]:
    items = []
    seen = set()

    for item in analysis["grammar"]["structures"]:
        form = item.get("form")
        tag = item.get("tag")
        key = (form, tag)

        if not form or key in seen:
            continue

        seen.add(key)
        items.append(f"{form} ({tag})")

        if len(items) >= limit:
            break

    return items


def _analysis_context(text: str, analysis: dict) -> str:
    vocab_score = analysis["vocabulary"]["vocabulary_score"]
    vocab_text = (
        f"{vocab_score:.1f}/100"
        if vocab_score is not None
        else "unavailable"
    )

    difficult = _difficult_words(analysis)
    grammar = _grammar_markers(analysis)

    difficult_text = (
        "\n".join(f"- {item}" for item in difficult)
        if difficult
        else "- none detected"
    )
    grammar_text = (
        "\n".join(f"- {item}" for item in grammar)
        if grammar
        else "- none detected"
    )

    return f"""
KOREAN TEXT
{text}

HANLEVEL RESULT
- Estimated level: {analysis['level']}
- Final score: {analysis['final_score']:.1f}/100
- Vocabulary difficulty: {vocab_text}
- Grammar complexity: {analysis['grammar']['grammar_score']:.1f}/100
- Sentence-length difficulty: {analysis['sentence_length']['sentence_length_score']:.1f}/100
- Average eojeol per sentence: {analysis['sentence_length']['average_eojeol']:.1f}
- Dictionary coverage: {analysis['vocabulary']['coverage']:.1f}%

INTERMEDIATE / ADVANCED VOCABULARY DETECTED
{difficult_text}

WEIGHTED STRUCTURAL MARKERS DETECTED BY HANLEVEL
{grammar_text}
""".strip()


def _history_context(history: list[dict] | None, limit: int = 4) -> str:
    if not history:
        return "No previous tutor conversation."

    recent = history[-limit:]
    lines = []

    for item in recent:
        role = item.get("role", "user")
        content = str(item.get("content", "")).strip()

        if content:
            lines.append(f"{role.upper()}: {content}")

    return "\n".join(lines) if lines else "No previous tutor conversation."


def build_tutor_prompt(
    text: str,
    analysis: dict,
    question: str,
    history: list[dict] | None = None,
) -> str:
    return f"""
You are HanLevel Tutor, a concise Korean-language learning assistant.

Your job is to help the learner understand ONLY the Korean text below, using
HanLevel's analysis as grounding evidence.

GROUNDING RULES
- Treat the supplied HanLevel result as the source of truth for what HanLevel
  detected and how it scored the text.
- Never invent a HanLevel score, vocabulary grade, or detected grammar marker.
- If you add general Korean-language knowledge beyond HanLevel's diagnostics,
  clearly frame it as a language explanation, not as something HanLevel
  detected.
- When explaining grammar, quote the relevant Korean expression from the text
  when possible and explain its function in context.
- When suggesting an easier or more advanced word/expression, label it as a
  suggestion. Do not claim an official learner grade unless that grade appears
  in the supplied HanLevel analysis.
- Preserve the meaning of the original sentence when proposing rewrites.
- If the learner asks for a rewrite, provide ONE useful rewrite first, then a
  short explanation of what changed. Do not run an optimization loop.
- Answer in the same language the learner used for the question unless they
  explicitly request another language.
- Sound warm, friendly, encouraging, and conversational, like a helpful study
  companion rather than a formal textbook or customer-service bot.
- Do not use pictographic emoji. You may occasionally use light text emoticons
  or simple typographic symbols such as :) ^^ -> * or + when they fit
  naturally. Use them sparingly, not in every sentence.
- Avoid overly formal openings, repetitive praise, or long disclaimers.
- Keep answers focused and educational. Usually 2-5 short paragraphs or a
  compact set of examples is enough.

ANALYZED MATERIAL
{_analysis_context(text, analysis)}

RECENT CONVERSATION
{_history_context(history)}

LEARNER QUESTION
{question}
""".strip()


def ask_tutor(
    text: str,
    analysis: dict,
    question: str,
    *,
    history: list[dict] | None = None,
    api_key: str | None = None,
    model: str | None = None,
) -> dict:
    """Answer one grounded tutor question with a single short model request."""

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

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

    prompt = build_tutor_prompt(
        text=text,
        analysis=analysis,
        question=question.strip(),
        history=history,
    )

    models = [selected_model]
    for fallback in FALLBACK_MODELS:
        if fallback not in models:
            models.append(fallback)

    started_at = time.perf_counter()
    response = None
    used_model = None
    last_error = None

    for candidate_model in models:
        try:
            response = client.models.generate_content(
                model=candidate_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=900,
                    temperature=0.25,
                    thinking_config=types.ThinkingConfig(
                        thinking_level="low",
                    ),
                ),
            )
            used_model = candidate_model
            break

        except Exception as exc:
            error_text = str(exc).lower()
            recoverable = any(
                marker in error_text
                for marker in (
                    "503",
                    "unavailable",
                    "high demand",
                    "429",
                    "resource_exhausted",
                    "404",
                    "not_found",
                )
            )

            if not recoverable:
                raise

            last_error = exc

    latency_seconds = time.perf_counter() - started_at

    if response is None:
        raise RuntimeError(
            "The tutor model is temporarily unavailable. Please try again."
        ) from last_error

    answer = (response.text or "").strip()

    if not answer:
        raise RuntimeError("The tutor returned an empty response.")

    return {
        "answer": answer,
        "model": used_model,
        "latency_seconds": latency_seconds,
    }
