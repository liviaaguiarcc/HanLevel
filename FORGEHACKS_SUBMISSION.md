# 🏗️ HanLevel v1.0 — ForgeHacks Submission Notes

This file is a ready-to-use reference for the Devpost submission, demo video, and judging explanation.

---

## 🌸 One-line pitch

**HanLevel tells Korean learners how difficult a text is, shows why, and gives them a grounded AI tutor to explore the exact vocabulary and grammar that made it challenging.**

Short alternative:

> **Analyze first. Ask why. Learn from the text.**

---

## 💗 Problem

Korean learners often find a text online and have no reliable way to answer two basic questions:

1. **Is this text appropriate for my level?**
2. **What exactly is making it difficult?**

A general chatbot can explain Korean, but it does not automatically know what a linguistic readability system actually measured.

A readability classifier can return a label, but a label alone does not help the learner understand the text.

HanLevel combines those two needs.

---

## ✨ Solution

HanLevel first analyzes the Korean text using an interpretable NLP pipeline.

It evaluates:

- vocabulary difficulty,
- grammar / morphology complexity,
- sentence length.

The learner receives a transparent Beginner / Intermediate / Advanced estimate plus the evidence behind it.

Then **Mongle (몽글)**, the AI tutor, receives the original text together with HanLevel's structured diagnostics.

The learner can ask:

- what the text means,
- why it received that difficulty level,
- which words are difficult,
- how the grammar works,
- how to express the same idea more simply,
- how to make it more advanced,
- or any free-form follow-up question.

---

## 🧠 Why the AI integration is technically meaningful

Mongle is not responsible for the readability classification.

The pipeline is:

```text
Korean text
   ↓
Kiwi + KRDICT-derived lexical data
   ↓
HanLevel deterministic readability analysis
   ↓
structured diagnostics
   ↓
Mongle / Gemini grounded context
   ↓
learner-facing explanation
```

The AI receives:
- the original text,
- final score,
- estimated difficulty level,
- vocabulary score,
- grammar score,
- sentence-length score,
- dictionary coverage,
- challenging vocabulary detected by the analyzer,
- weighted structural markers,
- recent conversation context.

This lets the generative model explain and teach from the analyzer output without allowing it to redefine the score.

---

## 🎯 Impact

HanLevel is designed for:
- independent Korean learners,
- teachers choosing reading material,
- learners trying to understand why a sentence feels difficult,
- anyone who wants a bridge between an NLP score and an actual learning experience.

The educational value comes from turning a static difficulty label into a guided exploration of the text.

---

## 🌍 Accessibility / learner experience

HanLevel v1.0 supports:
- English,
- Brazilian Portuguese,
- Spanish.

The UI includes:
- localized suggested questions,
- localized chat bubbles,
- multilingual tutor responses,
- a friendly study-companion persona,
- bounded scrollable chat,
- feedback flow for incorrect or hallucinated AI explanations.

---

## 🧪 Validation

### Readability analyzer

Internal calibration set:
- 5 Beginner texts,
- 5 Intermediate texts,
- 5 Advanced texts.

Result:

```text
15 / 15 matching classifications
```

This is **internal calibration agreement**, not a claim of general 100% accuracy.

### AI tutor

Mongle is manually tested for:
- grounding,
- grammar explanation,
- vocabulary support,
- rewrite usefulness,
- multilingual behavior,
- conversational follow-up,
- resistance to inventing analyzer facts.

See `TESTING.md`.

---

## 🪞 Limitations

Be explicit with judges:

- the calibration set is small,
- thresholds are project-specific,
- HanLevel is not an official TOPIK / CEFR predictor,
- grammar complexity is structural rather than a complete pedagogical grammar analysis,
- homonym disambiguation is limited,
- Gemini answers can still be imperfect,
- grounding reduces but does not eliminate hallucination,
- model availability and latency depend on the external Gemini API.

---

## 🌱 Pre-existing work vs. ForgeHacks work

HanLevel is an extension of a pre-existing project.

### Before ForgeHacks — v0.1

Already existed:
- rule-based Korean readability analyzer,
- Kiwi morphological analysis,
- KRDICT-derived lexical resource,
- vocabulary / grammar / sentence-length scoring,
- original Streamlit UI,
- internal calibration set.

The original version remains preserved on the repository's `main` branch.

### Built for ForgeHacks — v1.0

Added during the Forge version:
- Mongle (몽글), the grounded AI tutor,
- Gemini integration,
- structured analyzer-to-tutor grounding,
- suggested learner questions,
- free-form conversational tutoring,
- conversation history,
- easier / more advanced rewrites,
- multilingual interface,
- localized suggested-question bubbles,
- tutor avatar/personality,
- hallucination/problem feedback dialog,
- Forge-specific UI and documentation.

---

## 🎥 Recommended 2–4 minute demo flow

### 0:00–0:25 — Problem

Say:

> Korean learners often find a text but don't know whether it's appropriate for their level — or why it feels difficult. HanLevel first analyzes that difficulty transparently, then lets the learner ask a grounded AI tutor about the exact text.

### 0:25–1:10 — Analyze

Paste:

```text
연구 결과를 해석할 때에는 통계적 유의성뿐만 아니라 연구 설계와 자료 수집 과정의 한계도 함께 고려해야 한다.
```

Show:
- estimated level,
- HanLevel score,
- vocabulary,
- grammar,
- sentence length,
- weighted contribution.

Mention:

> The AI did not produce this score. This is the deterministic analyzer.

### 1:10–2:15 — Mongle

Click:
- **Explain the grammar**
- **Which words are difficult?**

Then ask manually:

```text
Is there an easier word for 고려하다?
```

Show a follow-up.

Explain:

> Mongle receives the analyzer output as structured context, so it can teach from what the system actually detected.

### 2:15–2:40 — Multilingual

Switch to Portuguese or Spanish.

Show that:
- the UI changes,
- suggested question is localized,
- the tutor answers in that language.

### 2:40–3:10 — Architecture / impact

Summarize:

> HanLevel combines an interpretable Korean NLP pipeline with grounded generative AI. The analyzer measures difficulty; the tutor helps the learner understand it.

End with:

> Analyze first. Ask why. Learn from the text.

---

## 📸 Recommended submission screenshots

Use at least:

1. **Full result screen**
   - source text,
   - difficulty card,
   - readability profile.

2. **Mongle conversation**
   - one grammar or vocabulary answer visible,
   - tutor avatar visible.

3. Optional:
   - multilingual interface,
   - detailed vocabulary / grammar breakdown.

Avoid screenshots that are mostly empty states.

---

## 🔗 Submission links

Repository:

```text
https://github.com/liviaaguiarcc/HanLevel
```

Forge branch:

```text
https://github.com/liviaaguiarcc/HanLevel/tree/forge-v1.0
```

Live app:

```text
https://hanlevel-v1.streamlit.app/
```

Original v0.1:

```text
https://hanlevel.streamlit.app/
```

---

## 🌷 Short Devpost description

**HanLevel is an interpretable Korean readability profiler with a grounded AI tutor.**

It first evaluates Korean text using learner-level vocabulary data, Kiwi morphological analysis, and sentence-length signals to produce a transparent Beginner / Intermediate / Advanced estimate.

Then Mongle (몽글), the AI tutor, receives the original text plus HanLevel's diagnostics and helps the learner understand meaning, grammar, difficult vocabulary, and alternative expressions through contextual follow-up questions.

The key design choice is separation: **the rule-based NLP analyzer decides the readability result; the generative AI explains and teaches from that result.**

---

## 💡 What makes HanLevel different

For judges, emphasize three points:

**1. Interpretable before generative**  
The AI does not invent the readability classification.

**2. Grounded tutoring**  
The model receives concrete linguistic diagnostics from the analyzer.

**3. Designed around a real learner workflow**  
Paste text → understand difficulty → ask why → learn from the text.

---

## ✦ Final tagline

> **Korean readability, explained — now with Mongle.**
