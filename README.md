<div align="center">

# ✦ HanLevel ✦
### Korean Readability Profiler for learners and educators

**Know if a Korean text is right for your level — and understand why.**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-hanlevel.streamlit.app-8B7CF6?style=for-the-badge&logo=streamlit&logoColor=white)](https://hanlevel.streamlit.app/)
![Version](https://img.shields.io/badge/version-v0.1.0-C9B7F5?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.13-AEDCFF?style=for-the-badge&logo=python&logoColor=white)
![NLP](https://img.shields.io/badge/NLP-Korean-FFB7D5?style=for-the-badge)

</div>

---

## 🌸 Overview

**HanLevel** is an interpretable Korean readability profiler that estimates whether a Korean text is more suitable for a **Beginner**, **Intermediate**, or **Advanced** learner.

Instead of returning only a difficulty label, HanLevel explains *why* a text received that result by analyzing three transparent components:

| Indicator | Weight |
|---|---:|
| 📚 Vocabulary difficulty | **45%** |
| 🧩 Grammar & morphology | **35%** |
| ✦ Sentence length | **20%** |

The goal is simple:

> **Help learners and educators understand not only how difficult a Korean text may be, but what makes it difficult.**

### 🌐 Live demo

**Try HanLevel:**  
https://hanlevel.streamlit.app/

---

## 💗 Why HanLevel?

Choosing appropriate Korean reading material can be surprisingly difficult.

A text may look short or familiar while still containing:

- advanced vocabulary,
- dense grammatical structures,
- long sentences,
- or a combination of several difficulty signals.

HanLevel was created to answer two practical questions:

> **Is this Korean text appropriate for my level?**

> **What exactly is making it easy or difficult?**

Rather than acting as a black-box classifier, HanLevel exposes the signals behind its prediction.

---

## ✨ Features

### Difficulty estimation

HanLevel classifies a Korean text as:

- **Beginner**
- **Intermediate**
- **Advanced**

It also produces a continuous **HanLevel score from 0 to 100**.

### Interpretable analysis

For every analyzed text, HanLevel can show:

- vocabulary difficulty,
- grammar complexity,
- sentence-length complexity,
- weighted contribution of each component,
- dictionary coverage,
- vocabulary-level distribution,
- potentially challenging vocabulary,
- detected structural markers,
- average eojeol per sentence.

### Transparent explanation

The interface includes a **“Why this level?”** explanation that summarizes the main evidence contributing to the final estimate.

### Local lexical resource

HanLevel uses a compact local index derived from the **Korean Learners’ Dictionary (한국어기초사전)** rather than depending on a live API during runtime.

This makes the app faster, more stable, easier to deploy, and reproducible.

---

## 🫧 How it works

HanLevel combines three interpretable indicators.

### 1. 📚 Vocabulary difficulty — 45%

Korean lexical items are matched against learner-level information from the **Korean Learners’ Dictionary**.

| KRDICT level | HanLevel value |
|---|---:|
| 초급 | 0 |
| 중급 | 50 |
| 고급 | 100 |

When a lexical item cannot be assigned a learner level, it is left **unclassified** instead of automatically being treated as easy or difficult.

HanLevel also reports **dictionary coverage** so users can see how much of the lexical content could actually be scored.

### 2. 🧩 Grammar & morphology — 35%

HanLevel uses **Kiwi / kiwipiepy** for Korean morphological analysis.

The grammar component looks at structural markers such as connective endings, adnominal endings, nominalizing endings, auxiliary verbs, quotation particles, and prefinal endings. The model also considers morphological density.

This component estimates **structural complexity**. It is not intended to represent an official Korean grammar proficiency level.

### 3. ✦ Sentence length — 20%

Sentence complexity is partially estimated using the **average number of eojeol per sentence**.

Longer sentences provide an additional structural-complexity signal, especially when combined with more complex grammar.

---

## 🎀 Final HanLevel score

The three components are combined using the following weights:

```text
Vocabulary       45%
Grammar          35%
Sentence length  20%
```

The current provisional classification thresholds are:

| HanLevel score | Estimated level |
|---|---|
| `< 25` | Beginner |
| `25 – < 50` | Intermediate |
| `≥ 50` | Advanced |

> These thresholds are **project-specific and provisional**.  
> They should not be interpreted as official **TOPIK** or **CEFR** boundaries.

---

## 🌷 Example output

A result may look conceptually like this:

```text
Estimated level
ADVANCED

HanLevel score: 52.4 / 100
```

HanLevel then explains the estimate:

```text
Vocabulary difficulty: 33.3 / 100
Grammar complexity:    71.9 / 100
Sentence length:       60.9 / 100
```

And shows each weighted contribution:

```text
Vocabulary       +15.0 points
Grammar          +25.2 points
Sentence length  +12.2 points
```

This allows users to see **which component actually drove the final result**.

---

## 🌼 Vocabulary profile

HanLevel provides a lexical breakdown such as:

```text
Beginner       18
Intermediate   32
Advanced        1
Unclassified    1
```

It can also surface potentially challenging words and their learner levels.

Repeated lexical items are included in the profile counts, while the challenging-vocabulary list displays each word only once.

---

## 🪻 Grammar interpretability

HanLevel can display structural markers detected in the text.

```text
-게       — Connective ending
-고       — Connective ending
있다      — Auxiliary verb
-(으)ㄴ   — Adnominal ending
-기       — Nominalizing ending
-(으)ㄹ   — Adnominal ending
않다      — Auxiliary verb
```

These are used as **interpretable structural signals**, not as official pedagogical grammar-level labels.

---

## 🧁 Tech stack

| Technology | Purpose |
|---|---|
| **Python** | Core application logic |
| **Streamlit** | Web interface |
| **Kiwi / kiwipiepy** | Korean morphological analysis |
| **KRDICT-derived local index** | Learner-level lexical lookup |
| **GitHub** | Version control and source hosting |
| **Streamlit Community Cloud** | Deployment |

---

## 📖 Data source

HanLevel uses learner-level lexical information derived from:

**Korean Learners’ Dictionary (한국어기초사전)**  
**National Institute of Korean Language**

Only the fields required by HanLevel are kept in the deployed compact index:

- written form,
- part of speech,
- vocabulary level.

The original KRDICT export was approximately **969 MB** across 11 JSON files.

For deployment, HanLevel preprocesses this into a compact lexical index of approximately **1.79 MB** while preserving the lexical information used by the scoring pipeline.

> Please consult the Korean Learners’ Dictionary / National Institute of Korean Language terms for reuse and attribution requirements applicable to the source data.

---

## 🧪 Internal calibration

HanLevel v0.1 was internally calibrated using a small development set containing:

- **5 Beginner texts**
- **5 Intermediate texts**
- **5 Advanced texts**

The current version produced:

```text
15 / 15 matching classifications
```

on this constructed internal calibration set.

> This is **internal calibration agreement**, not a claim of 100% general accuracy.

A larger external evaluation is planned for future versions.

---

## 🗂️ Project structure

```text
HanLevel/
│
├── app.py
├── analyzer.py
├── krdict.py
├── calibration.py
├── build_krdict_index.py
├── calibration_results.csv
├── requirements.txt
├── .gitignore
│
├── .streamlit/
│   └── config.toml
│
└── data/
    └── krdict_index.json
```

---

## 💻 Run locally

### 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd HanLevel
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Install the dependencies

```bash
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 4. Run HanLevel

```bash
.venv\Scripts\python.exe -m streamlit run app.py
```

---

## 📦 Requirements

```txt
kiwipiepy
streamlit
```

---

## 🌙 Methodological principles

HanLevel v0.1 was intentionally designed as a **transparent rule-based NLP prototype**.

### HanLevel is

- an interpretable readability profiler,
- a Korean language-learning support tool,
- an educational NLP prototype,
- a foundation for future AI-assisted features.

### HanLevel is not

- an official proficiency assessment,
- an official TOPIK predictor,
- a CEFR mapping tool,
- a full pedagogical grammar evaluator,
- a validated large-scale readability benchmark.

---

## 🪞 Current limitations

HanLevel v0.1 currently has several important limitations:

- The calibration set is small and internally constructed.
- Classification thresholds are provisional.
- Proper nouns and foreign-language items may not have learner-level information.
- Some vocabulary may remain unclassified.
- Homonyms are not fully context-disambiguated in v0.1.
- Grammar complexity is based on structural indicators rather than complete pedagogical grammar analysis.
- Very short inputs provide less evidence than longer texts.
- Sentence length is only one aspect of syntactic complexity.
- The current model does not yet adapt or simplify the input text.

The interface exposes **dictionary coverage** to make one important source of uncertainty visible to the user.

---

## 🚀 Roadmap

### 🌱 HanLevel v0.1

**Interpretable Korean Readability Profiler**

Current focus:

- readability estimation,
- transparent scoring,
- Korean lexical-level analysis,
- grammar complexity,
- sentence length,
- explainable results.

### 🤖 HanLevel v1.0

Planned AI-assisted features include:

- level-aware text adaptation,
- Korean text simplification,
- learner-friendly explanations,
- vocabulary support,
- comprehension questions,
- reading recommendations,
- rule-based vs. AI-assisted comparison,
- broader evaluation.

---

## 💡 Why interpretability matters

A readability system becomes more useful when learners can understand its reasoning.

Instead of only saying:

> **Advanced**

HanLevel can show that the result came from moderate vocabulary, high grammar complexity, longer sentences, and a strong grammar contribution to the total score.

That transparency makes the output more actionable for learners, teachers, researchers, and language-technology developers.

---

## 🌸 Project motivation

HanLevel sits at the intersection of:

**Korean language learning × Linguistics × NLP × Educational technology**

The project explores how relatively simple and transparent NLP methods can create practical tools for learners while remaining inspectable enough for users to understand the system’s reasoning.

---

## 🔗 Try HanLevel

<div align="center">

### [🌷 Open the live HanLevel app](https://hanlevel.streamlit.app/)

**Beginner · Intermediate · Advanced**

*Korean readability, explained.*

</div>

---

## 🩷 Author

Developed by **Lívia Aguiar Cavalcanti**

Background and interests:

- Translation
- Korean language
- Natural Language Processing
- Corpus building
- Language technology
- Data analysis

---

<div align="center">

### ✦ HanLevel v0.1 ✦

**Korean Readability Profiler for learners and educators**

[Open HanLevel](https://hanlevel.streamlit.app/)

</div>
