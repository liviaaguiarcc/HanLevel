import streamlit as st

from analyzer import analyze_text


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="HanLevel",
    page_icon="🇰🇷",
    layout="centered",
)


# =========================================================
# STYLING
# =========================================================

st.markdown(
    """
<style>

/* ---------- STREAMLIT ---------- */

[data-testid="stHeader"] {
    display: none;
}

[data-testid="stDecoration"] {
    display: none;
}


/* ---------- PAGE ---------- */

.stApp {
    background:
        radial-gradient(
            circle at top left,
            #eef7ff 0%,
            transparent 35%
        ),
        radial-gradient(
            circle at top right,
            #fff0f4 0%,
            transparent 35%
        ),
        #fbfcff;
}

.block-container {
    max-width: 900px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}


/* ---------- HEADER ---------- */

.hanlevel-title {
    font-size: 3.5rem;
    font-weight: 800;
    letter-spacing: -2px;
    color: #172033;
    margin-bottom: 0;
}

.hanlevel-subtitle {
    font-size: 1.15rem;
    color: #64748b;
    margin-top: -0.3rem;
    margin-bottom: 1.2rem;
}


/* ---------- TEXT AREA ---------- */

.stTextArea textarea {
    background-color: white;
    border: 1.5px solid #d9e2f0;
    border-radius: 16px;
    padding: 16px;
    color: #172033;
}

.stTextArea textarea:focus {
    border-color: #7c9ee8;
    box-shadow:
        0 0 0 2px
        rgba(124, 158, 232, 0.15);
}


/* ---------- BUTTON ---------- */

.stButton > button {
    border-radius: 14px;
    font-weight: 700;
    height: 3rem;
    border: none;

    background:
        linear-gradient(
            90deg,
            #6587dd,
            #8f79d8
        );

    color: white;
}

.stButton > button:hover {
    border: none;
    color: white;
    transform: translateY(-1px);
}


/* ---------- RESULT CARD ---------- */

.level-card {
    background: white;

    padding: 1.8rem;

    border-radius: 22px;
    border: 1px solid #e2e8f0;

    margin-top: 1rem;
    margin-bottom: 1rem;

    box-shadow:
        0 8px 30px
        rgba(40, 55, 90, 0.07);

    text-align: center;
}

.level-name {
    font-size: 2.4rem;
    font-weight: 800;
}

.score-text {
    color: #64748b;
    font-size: 1rem;
    margin-top: 4px;
}


/* ---------- DIFFICULTY SCALE ---------- */

.difficulty-wrapper {
    margin-top: 1.8rem;
    margin-bottom: 2rem;
    padding-top: 1.8rem;
}

.difficulty-track {
    position: relative;

    height: 14px;
    border-radius: 999px;

    background:
        linear-gradient(
            90deg,

            #a9dcf7 0%,
            #a9dcf7 25%,

            #b9a8ee 25%,
            #b9a8ee 50%,

            #f2aac8 50%,
            #f2aac8 100%
        );

    box-shadow:
        inset 0 1px 3px
        rgba(35, 48, 80, 0.12),

        0 3px 12px
        rgba(55, 70, 110, 0.08);
}


/* threshold separators */

.difficulty-threshold {
    position: absolute;

    top: -4px;

    width: 2px;
    height: 22px;

    background:
        rgba(255, 255, 255, 0.95);

    border-radius: 2px;
}

.threshold-one {
    left: 25%;
}

.threshold-two {
    left: 50%;
}


/* movable marker */

.difficulty-marker {
    position: absolute;

    top: 50%;

    width: 28px;
    height: 28px;

    transform:
        translate(-50%, -50%);

    border-radius: 50%;

    background: white;

    border:
        6px solid #786ed7;

    box-shadow:
        0 4px 14px
        rgba(57, 67, 120, 0.22);
}


/* score bubble */

.difficulty-score {
    position: absolute;

    bottom: 25px;

    transform:
        translateX(-50%);

    background: #172033;
    color: white;

    padding:
        4px 9px;

    border-radius: 999px;

    font-size: 0.78rem;
    font-weight: 700;

    white-space: nowrap;
}


/* labels */

.difficulty-labels {
    display: grid;

    grid-template-columns:
        1fr 1fr 2fr;

    margin-top: 12px;

    color: #64748b;

    font-size: 0.85rem;
    font-weight: 600;

    text-align: center;
}


/* ---------- EXPLANATION ---------- */

.reason-box {
    padding:
        1.2rem 1.4rem;

    border-radius: 16px;

    background:
        linear-gradient(
            135deg,
            #f1f6ff,
            #faf5ff
        );

    border:
        1px solid #dde5f4;

    margin-top: 1.2rem;
    margin-bottom: 2rem;

    color: #263248;
}


/* ---------- METRICS ---------- */

[data-testid="stMetric"] {
    background-color: white;

    border:
        1px solid #e2e8f0;

    padding: 18px;

    border-radius: 18px;

    box-shadow:
        0 5px 20px
        rgba(40, 55, 90, 0.05);
}


/* ---------- EXPANDERS ---------- */

[data-testid="stExpander"] {
    background-color:
        rgba(255, 255, 255, 0.75);

    border:
        1px solid #e3e8f2;

    border-radius: 14px;
}


/* ---------- TEXT ---------- */

h1,
h2,
h3 {
    color: #172033;
}

hr {
    border-color: #e8edf5;
}

</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# HELPERS
# =========================================================

def safe_score(value):
    if value is None:
        return 0.0

    return value


def describe_score(score):
    if score < 25:
        return "low"

    if score < 50:
        return "moderate"

    return "high"


def generate_explanation(result):

    vocab = safe_score(
        result["vocabulary"]["vocabulary_score"]
    )

    grammar = (
        result["grammar"]["grammar_score"]
    )

    sentence = (
        result["sentence_length"][
            "sentence_length_score"
        ]
    )

    scores = {
        "Vocabulary": vocab,
        "Grammar": grammar,
        "Sentence length": sentence,
    }

    strongest = max(
        scores,
        key=scores.get,
    )

    vocab_description = describe_score(vocab)
    grammar_description = describe_score(grammar)
    sentence_description = describe_score(sentence)

    explanation = (
        f"The text has {vocab_description} vocabulary difficulty, "
        f"{grammar_description} grammatical complexity, and "
        f"{sentence_description} sentence-length complexity. "
    )

    if strongest == "Vocabulary":
        explanation += (
            "Vocabulary is the main contributor "
            "to the estimated difficulty."
        )

    elif strongest == "Grammar":
        explanation += (
            "Grammar is the main contributor "
            "to the estimated difficulty."
        )

    else:
        explanation += (
            "Sentence length is the main contributor "
            "to the estimated difficulty."
        )

    return explanation


def get_difficult_words(result):

    words = result["vocabulary"]["words"]

    difficult = []

    seen = set()

    for item in words:

        word = item["word"]
        grade = item["grade"]

        if grade not in {
            "중급",
            "고급",
        }:
            continue

        key = (
            word,
            grade,
        )

        if key in seen:
            continue

        seen.add(key)

        difficult.append(
            {
                "word": word,
                "grade": grade,
            }
        )

    return difficult


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="hanlevel-title">HanLevel</div>',
    unsafe_allow_html=True,
)

st.markdown(
    (
        '<div class="hanlevel-subtitle">'
        'Korean Readability Profiler for learners and educators'
        '</div>'
    ),
    unsafe_allow_html=True,
)

st.markdown(
    "**Know if a Korean text is right for your level — "
    "and understand why.**"
)

st.write(
    "HanLevel estimates Korean text difficulty using vocabulary, "
    "grammatical complexity, and sentence length."
)

st.divider()


# =========================================================
# INPUT
# =========================================================

text = st.text_area(
    "Korean text",
    height=180,
    placeholder=(
        "예: 오늘은 날씨가 정말 좋네요. "
        "친구와 함께 공원에 갔어요."
    ),
)

analyze_button = st.button(
    "Analyze difficulty",
    type="primary",
    use_container_width=True,
)


# =========================================================
# ANALYSIS
# =========================================================

if analyze_button:

    if not text.strip():

        st.warning(
            "Please enter some Korean text first."
        )

    else:

        with st.spinner(
            "Analyzing Korean text..."
        ):

            result = analyze_text(text)


        # -----------------------------------------
        # Extract scores
        # -----------------------------------------

        final_score = result["final_score"]

        level = result["level"]

        vocab_score = safe_score(
            result["vocabulary"][
                "vocabulary_score"
            ]
        )

        grammar_score = (
            result["grammar"][
                "grammar_score"
            ]
        )

        sentence_score = (
            result["sentence_length"][
                "sentence_length_score"
            ]
        )

        coverage = (
            result["vocabulary"][
                "coverage"
            ]
        )

        average_eojeol = (
            result["sentence_length"][
                "average_eojeol"
            ]
        )

        explanation = (
            generate_explanation(result)
        )

        difficult_words = (
            get_difficult_words(result)
        )


        # -----------------------------------------
        # Level-specific colors
        # -----------------------------------------

        level_colors = {
            "Beginner": "#62a9d8",
            "Intermediate": "#786ed7",
            "Advanced": "#d66f9e",
        }

        level_color = level_colors.get(
            level,
            "#786ed7",
        )


        # =================================================
        # MAIN RESULT
        # =================================================

        st.subheader(
            "Estimated difficulty"
        )

        result_card_html = (
            f'<div class="level-card">'
            f'<div class="level-name" '
            f'style="color:{level_color};">'
            f'{level}'
            f'</div>'
            f'<div class="score-text">'
            f'HanLevel score: {final_score:.1f} / 100'
            f'</div>'
            f'</div>'
        )

        st.markdown(
            result_card_html,
            unsafe_allow_html=True,
        )


        # =================================================
        # DIFFICULTY SCALE
        # =================================================

        marker_position = min(
            max(
                final_score,
                0,
            ),
            100,
        )

        difficulty_html = (
            f'<div class="difficulty-wrapper">'

            f'<div class="difficulty-track">'

            f'<div class="difficulty-threshold '
            f'threshold-one"></div>'

            f'<div class="difficulty-threshold '
            f'threshold-two"></div>'

            f'<div class="difficulty-score" '
            f'style="left:{marker_position}%;">'
            f'{final_score:.1f}'
            f'</div>'

            f'<div class="difficulty-marker" '
            f'style="left:{marker_position}%; '
            f'border-color:{level_color};">'
            f'</div>'

            f'</div>'

            f'<div class="difficulty-labels">'
            f'<span>Beginner</span>'
            f'<span>Intermediate</span>'
            f'<span>Advanced</span>'
            f'</div>'

            f'</div>'
        )

        st.markdown(
            difficulty_html,
            unsafe_allow_html=True,
        )


        # =================================================
        # EXPLANATION
        # =================================================

        explanation_html = (
            f'<div class="reason-box">'
            f'<strong>Why {level}?</strong>'
            f'<br>'
            f'{explanation}'
            f'</div>'
        )

        st.markdown(
            explanation_html,
            unsafe_allow_html=True,
        )


        # =================================================
        # READABILITY PROFILE
        # =================================================

        st.subheader(
            "Readability profile"
        )

        col1, col2, col3 = (
            st.columns(3)
        )

        with col1:

            st.metric(
                "Vocabulary difficulty",
                f"{vocab_score:.1f}/100",
            )

        with col2:

            st.metric(
                "Grammar complexity",
                f"{grammar_score:.1f}/100",
            )

        with col3:

            st.metric(
                "Sentence length",
                f"{sentence_score:.1f}/100",
            )

        st.caption(
            "Higher scores indicate greater estimated difficulty."
        )


        # =================================================
        # DETAILS
        # =================================================

        with st.expander(
            "See analysis details"
        ):

            st.write(
                f"**Dictionary coverage:** "
                f"{coverage:.1f}%"
            )

            st.write(
                f"**Average eojeol per sentence:** "
                f"{average_eojeol:.1f}"
            )

            st.write(
                f"**Detected grammatical structures:** "
                f"{len(result['grammar']['structures'])}"
            )

            if difficult_words:

                st.write(
                    "**Potentially challenging vocabulary:**"
                )

                for item in difficult_words:

                    label = (
                        "Intermediate"
                        if item["grade"] == "중급"
                        else "Advanced"
                    )

                    st.write(
                        f"- {item['word']} — {label}"
                    )

            else:

                st.write(
                    "No intermediate or advanced vocabulary "
                    "was identified in the graded dictionary entries."
                )


        # =================================================
        # METHODOLOGY
        # =================================================

        with st.expander(
            "How HanLevel calculates difficulty"
        ):

            st.markdown(
                """
HanLevel combines three interpretable indicators:

**Vocabulary difficulty — 45%**

Vocabulary is matched against learner-level information from the Korean Learners' Dictionary (한국어기초사전).

**Grammar & morphology — 35%**

Korean morphological analysis is performed with Kiwi. Structural endings and morphological density contribute to the grammar-complexity score.

**Sentence length — 20%**

Average eojeol per sentence is used as an additional structural-complexity indicator.

The current version uses a rule-based scoring model designed for transparent readability assessment.
"""
            )