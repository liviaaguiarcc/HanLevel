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


/* =========================================================
   HERO
   ========================================================= */

.hero-card {
    position: relative;
    overflow: hidden;

    padding: 2.6rem 2.5rem;

    margin-bottom: 2rem;

    border-radius: 28px;

    border:
        1px solid
        rgba(210, 220, 240, 0.85);

    background:
        linear-gradient(
            135deg,
            rgba(238, 247, 255, 0.96),
            rgba(250, 245, 255, 0.96),
            rgba(255, 240, 244, 0.92)
        );

    box-shadow:
        0 14px 40px
        rgba(50, 65, 100, 0.08);

    text-align: center;
}


/* decorative circles */

.hero-card::before {
    content: "";

    position: absolute;

    width: 190px;
    height: 190px;

    border-radius: 50%;

    background:
        rgba(159, 220, 247, 0.25);

    top: -100px;
    right: -55px;
}

.hero-card::after {
    content: "";

    position: absolute;

    width: 150px;
    height: 150px;

    border-radius: 50%;

    background:
        rgba(243, 171, 196, 0.20);

    bottom: -85px;
    left: -35px;
}


.hero-content {
    position: relative;
    z-index: 2;

    display: flex;
    flex-direction: column;

    align-items: center;
    justify-content: center;
}


.hero-badge {
    display: inline-block;

    padding: 6px 11px;

    border-radius: 999px;

    background:
        rgba(255, 255, 255, 0.78);

    border:
        1px solid
        rgba(190, 200, 225, 0.8);

    color: #65708a;

    font-size: 0.75rem;
    font-weight: 700;

    letter-spacing: 0.07em;

    text-transform: uppercase;

    margin-bottom: 1rem;
}


.hero-title {
    font-size: 3.8rem;
    font-weight: 850;

    letter-spacing: -2px;

    color: #172033;

    line-height: 1;

    margin-bottom: 0.9rem;
}


.hero-description {
    max-width: 650px;

    margin-left: auto;
    margin-right: auto;

    color: #58657c;

    font-size: 1.05rem;
    line-height: 1.65;

    margin-bottom: 1.4rem;
}


.hero-highlight {
    color: #536dcc;
    font-weight: 700;
}


.hero-chips {
    display: flex;
    flex-wrap: wrap;

    justify-content: center;
    align-items: center;

    gap: 0.6rem;

    width: 100%;
}


.hero-chip {
    padding: 7px 13px;

    border-radius: 999px;

    background:
        rgba(255, 255, 255, 0.78);

    border:
        1px solid
        rgba(215, 222, 238, 0.9);

    color: #556078;

    font-size: 0.82rem;
    font-weight: 600;
}


/* ---------- TEXT AREA ---------- */

.stTextArea textarea {
    background-color: white;

    border:
        1.5px solid #d9e2f0;

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

    transform:
        translateY(-1px);
}


/* ---------- RESULT CARD ---------- */

.level-card {
    background:
        linear-gradient(
            135deg,
            rgba(255, 255, 255, 0.98),
            rgba(248, 249, 255, 0.98)
        );

    padding: 1.8rem;

    border-radius: 22px;

    border:
        1px solid #e2e8f0;

    margin-top: 1rem;
    margin-bottom: 1rem;

    box-shadow:
        0 8px 30px
        rgba(40, 55, 90, 0.07);

    text-align: center;

    overflow: hidden;
}


.level-kicker {
    font-size: 0.78rem;

    font-weight: 700;

    letter-spacing: 0.08em;

    text-transform: uppercase;

    color: #94a3b8;

    margin-bottom: 6px;
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

    width: 100%;
    height: 16px;

    border-radius: 999px;

    box-shadow:
        inset 0 1px 3px
        rgba(35, 48, 80, 0.10),

        0 3px 12px
        rgba(55, 70, 110, 0.10);
}


/* colored zones */

.difficulty-segment {
    position: absolute;

    top: 0;

    height: 100%;
}


.segment-beginner {
    left: 0;

    width: 25%;

    background-color: #9fdcf7;

    border-radius:
        999px 0 0 999px;
}


.segment-intermediate {
    left: 25%;

    width: 25%;

    background-color: #c3a9e7;
}


.segment-advanced {
    left: 50%;

    width: 50%;

    background-color: #f3abc4;

    border-radius:
        0 999px 999px 0;
}


/* threshold separators */

.difficulty-threshold {
    position: absolute;

    top: -3px;

    width: 2px;
    height: 22px;

    background:
        rgba(255, 255, 255, 0.65);

    border-radius: 2px;

    z-index: 3;
}


.threshold-one {
    left: 25%;
}


.threshold-two {
    left: 50%;
}


/* score marker */

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

    z-index: 5;
}


/* score bubble */

.difficulty-score {
    position: absolute;

    bottom: 25px;

    transform:
        translateX(-50%);

    background: #172033;

    color: white;

    padding: 4px 9px;

    border-radius: 999px;

    font-size: 0.78rem;
    font-weight: 700;

    white-space: nowrap;

    z-index: 6;
}


/* scale labels */

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


/* ---------- GENERAL ---------- */

h1,
h2,
h3 {
    color: #172033;
}

hr {
    border-color: #e8edf5;
}


/* ---------- RESPONSIVE ---------- */

@media (max-width: 700px) {

    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;

        padding-top: 1.2rem;
    }

    .hero-card {
        padding:
            2rem 1.4rem;
    }

    .hero-title {
        font-size: 2.9rem;
    }

    .hero-description {
        font-size: 0.95rem;
    }

    .hero-chip {
        font-size: 0.76rem;
    }

    .level-name {
        font-size: 2rem;
    }

    .difficulty-labels {
        font-size: 0.75rem;
    }

    [data-testid="stMetric"] {
        padding: 14px;
    }
}

</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# CONSTANTS
# =========================================================

LOW_COVERAGE_THRESHOLD = 60.0


GRAMMAR_TAG_LABELS = {
    "EP": "Prefinal ending",
    "EC": "Connective ending",
    "ETM": "Adnominal ending",
    "ETN": "Nominalizing ending",
    "VX": "Auxiliary verb",
    "JKQ": "Quotation particle",
}


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


# ---------------------------------------------------------
# Weighted contribution
# ---------------------------------------------------------

def calculate_contributions(result):

    vocabulary_score = (
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

    components = []

    if vocabulary_score is not None:

        components.append(
            (
                "Vocabulary",
                vocabulary_score,
                0.45,
            )
        )

    components.append(
        (
            "Grammar",
            grammar_score,
            0.35,
        )
    )

    components.append(
        (
            "Sentence length",
            sentence_score,
            0.20,
        )
    )

    total_weight = sum(
        weight
        for _, _, weight
        in components
    )

    contributions = {}

    for name, score, weight in components:

        contributions[name] = (
            score
            * weight
            / total_weight
        )

    return contributions


# ---------------------------------------------------------
# Vocabulary profile
# ---------------------------------------------------------

def get_vocabulary_profile(result):

    profile = {
        "Beginner": 0,
        "Intermediate": 0,
        "Advanced": 0,
        "Unclassified": 0,
    }

    words = (
        result["vocabulary"][
            "words"
        ]
    )

    for item in words:

        grade = item["grade"]

        if grade == "초급":

            profile["Beginner"] += 1

        elif grade == "중급":

            profile["Intermediate"] += 1

        elif grade == "고급":

            profile["Advanced"] += 1

        else:

            profile["Unclassified"] += 1

    return profile


def get_dominant_vocabulary_level(
    profile
):

    classified = {
        "Beginner":
            profile["Beginner"],

        "Intermediate":
            profile["Intermediate"],

        "Advanced":
            profile["Advanced"],
    }

    if sum(
        classified.values()
    ) == 0:

        return None

    return max(
        classified,
        key=classified.get,
    )


# ---------------------------------------------------------
# Explanation
# ---------------------------------------------------------

def generate_explanation(result):

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

    average_eojeol = (
        result["sentence_length"][
            "average_eojeol"
        ]
    )

    coverage = (
        result["vocabulary"][
            "coverage"
        ]
    )

    contributions = (
        calculate_contributions(
            result
        )
    )

    strongest = max(
        contributions,
        key=contributions.get,
    )

    profile = (
        get_vocabulary_profile(
            result
        )
    )

    dominant_vocab = (
        get_dominant_vocabulary_level(
            profile
        )
    )

    vocab_description = (
        describe_score(
            vocab_score
        )
    )

    grammar_description = (
        describe_score(
            grammar_score
        )
    )

    sentence_description = (
        describe_score(
            sentence_score
        )
    )

    explanation = (
        f"The text has "
        f"{vocab_description} vocabulary difficulty, "
        f"{grammar_description} grammatical complexity, "
        f"and {sentence_description} "
        f"sentence-length difficulty. "
    )

    explanation += (
        f"{strongest} contributes the most "
        f"to the final score "
        f"(+{contributions[strongest]:.1f} points). "
    )

    if dominant_vocab is not None:

        explanation += (
            f"Most classified lexical items are "
            f"{dominant_vocab.lower()} level. "
        )

    explanation += (
        f"Sentences average "
        f"{average_eojeol:.1f} eojeol."
    )

    if (
        coverage
        < LOW_COVERAGE_THRESHOLD
    ):

        explanation += (
            " Vocabulary coverage is limited, "
            "so the lexical estimate should be "
            "interpreted cautiously."
        )

    return explanation


# ---------------------------------------------------------
# Challenging vocabulary
# ---------------------------------------------------------

def get_difficult_words(result):

    words = (
        result["vocabulary"][
            "words"
        ]
    )

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


# ---------------------------------------------------------
# Grammar structures
# ---------------------------------------------------------

def format_grammar_structure(
    item
):

    form = None
    tag = None

    if isinstance(
        item,
        dict
    ):

        form = (
            item.get("form")
            or item.get("word")
            or item.get("lemma")
        )

        tag = (
            item.get("tag")
            or item.get("pos")
        )

    else:

        form = getattr(
            item,
            "form",
            None,
        )

        tag = getattr(
            item,
            "tag",
            None,
        )

        if form is None:

            form = str(item)

    if not form:

        form = "Unknown"

    display_form = form

    if (
        tag
        and tag.startswith("E")
        and not form.startswith("-")
    ):

        display_form = (
            f"-{form}"
        )

    display_normalization = {

        ("ᆫ", "ETM"):
            "-(으)ㄴ",

        ("ㄴ", "ETM"):
            "-(으)ㄴ",

        ("ᆯ", "ETM"):
            "-(으)ㄹ",

        ("ㄹ", "ETM"):
            "-(으)ㄹ",

        ("있", "VX"):
            "있다",

        ("않", "VX"):
            "않다",
    }

    display_form = (
        display_normalization.get(
            (
                form,
                tag,
            ),
            display_form,
        )
    )

    label = (
        GRAMMAR_TAG_LABELS.get(
            tag,
            tag or "Structural marker",
        )
    )

    return (
        display_form,
        tag,
        label,
    )


def get_unique_grammar_structures(
    result
):

    structures = (
        result["grammar"][
            "structures"
        ]
    )

    unique = []

    seen = set()

    for item in structures:

        form, tag, label = (
            format_grammar_structure(
                item
            )
        )

        key = (
            form,
            tag,
        )

        if key in seen:

            continue

        seen.add(key)

        unique.append(
            {
                "form": form,
                "tag": tag,
                "label": label,
            }
        )

    return unique


# =========================================================
# HERO
# =========================================================

hero_html = (
    '<div class="hero-card">'

        '<div class="hero-content">'

            '<div class="hero-badge">'
                'Korean Readability Profiler'
            '</div>'

            '<div class="hero-title">'
                'HanLevel'
            '</div>'

            '<div class="hero-description">'

                '<span class="hero-highlight">'
                    'Know if a Korean text is right for your level'
                '</span>'

                ' — and understand why. '

                'HanLevel analyzes vocabulary, grammar, '
                'and sentence length to estimate how challenging '
                'a Korean text may be.'

            '</div>'

            '<div class="hero-chips">'

                '<span class="hero-chip">'
                    'Vocabulary · 45%'
                '</span>'

                '<span class="hero-chip">'
                    'Grammar · 35%'
                '</span>'

                '<span class="hero-chip">'
                    'Sentence length · 20%'
                '</span>'

            '</div>'

        '</div>'

    '</div>'
)


st.markdown(
    hero_html,
    unsafe_allow_html=True,
)


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

            result = (
                analyze_text(
                    text
                )
            )


        # -------------------------------------------------
        # Extract results
        # -------------------------------------------------

        final_score = (
            result["final_score"]
        )

        level = (
            result["level"]
        )

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
            generate_explanation(
                result
            )
        )

        difficult_words = (
            get_difficult_words(
                result
            )
        )

        vocabulary_profile = (
            get_vocabulary_profile(
                result
            )
        )

        contributions = (
            calculate_contributions(
                result
            )
        )

        grammar_structures = (
            get_unique_grammar_structures(
                result
            )
        )


        # -------------------------------------------------
        # Colors
        # -------------------------------------------------

        level_colors = {

            "Beginner":
                "#62a9d8",

            "Intermediate":
                "#786ed7",

            "Advanced":
                "#d66f9e",
        }

        level_color = (
            level_colors.get(
                level,
                "#786ed7",
            )
        )


        # =================================================
        # MAIN RESULT
        # =================================================

        st.subheader(
            "Estimated difficulty"
        )


        result_card_html = (
            f'<div class="level-card">'

            f'<div class="level-kicker">'
            f'Estimated level'
            f'</div>'

            f'<div class="level-name" '
            f'style="color:{level_color};">'
            f'{level}'
            f'</div>'

            f'<div class="score-text">'
            f'HanLevel score: '
            f'{final_score:.1f} / 100'
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

            f'<div class="difficulty-segment '
            f'segment-beginner"></div>'

            f'<div class="difficulty-segment '
            f'segment-intermediate"></div>'

            f'<div class="difficulty-segment '
            f'segment-advanced"></div>'

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

            f'<strong>'
            f'Why {level}?'
            f'</strong>'

            f'<br>'

            f'{explanation}'

            f'</div>'
        )


        st.markdown(
            explanation_html,
            unsafe_allow_html=True,
        )


        # =================================================
        # LOW COVERAGE WARNING
        # =================================================

        if (
            coverage
            < LOW_COVERAGE_THRESHOLD
        ):

            st.warning(
                f"Limited vocabulary coverage "
                f"({coverage:.1f}%). "
                "The difficulty estimate may be less reliable "
                "because many lexical items could not be "
                "assigned a learner level."
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
            "Higher scores indicate greater "
            "estimated difficulty."
        )


        # =================================================
        # CONTRIBUTION BREAKDOWN
        # =================================================

        st.markdown(
            "#### Contribution to HanLevel score"
        )


        contribution_columns = (
            st.columns(3)
        )


        with contribution_columns[0]:

            st.metric(
                "Vocabulary",
                (
                    f"+"
                    f"{contributions.get('Vocabulary', 0):.1f}"
                    f" points"
                ),
            )


        with contribution_columns[1]:

            st.metric(
                "Grammar",
                (
                    f"+"
                    f"{contributions.get('Grammar', 0):.1f}"
                    f" points"
                ),
            )


        with contribution_columns[2]:

            st.metric(
                "Sentence length",
                (
                    f"+"
                    f"{contributions.get('Sentence length', 0):.1f}"
                    f" points"
                ),
            )


        st.caption(
            "Weighted contributions add up "
            "to the final HanLevel score."
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


            # ---------------------------------------------
            # Vocabulary profile
            # ---------------------------------------------

            st.markdown(
                "#### Vocabulary profile"
            )


            vocab_cols = (
                st.columns(4)
            )


            with vocab_cols[0]:

                st.metric(
                    "Beginner",
                    vocabulary_profile[
                        "Beginner"
                    ],
                )


            with vocab_cols[1]:

                st.metric(
                    "Intermediate",
                    vocabulary_profile[
                        "Intermediate"
                    ],
                )


            with vocab_cols[2]:

                st.metric(
                    "Advanced",
                    vocabulary_profile[
                        "Advanced"
                    ],
                )


            with vocab_cols[3]:

                st.metric(
                    "Unclassified",
                    vocabulary_profile[
                        "Unclassified"
                    ],
                )


            st.caption(
                "Counts include repeated lexical items. "
                "The challenging-vocabulary list below "
                "shows each word only once."
            )


            # ---------------------------------------------
            # Challenging vocabulary
            # ---------------------------------------------

            if difficult_words:

                st.markdown(
                    "#### Potentially challenging vocabulary"
                )


                for item in difficult_words:

                    label = (
                        "Intermediate"
                        if item["grade"] == "중급"
                        else "Advanced"
                    )

                    st.write(
                        f"- **{item['word']}** "
                        f"— {label}"
                    )


            else:

                st.write(
                    "No intermediate or advanced vocabulary "
                    "was identified in the graded "
                    "dictionary entries."
                )


            # ---------------------------------------------
            # Grammar structures
            # ---------------------------------------------

            st.markdown(
                "#### Detected structural markers"
            )


            st.write(
                f"HanLevel detected "
                f"**{len(result['grammar']['structures'])}** "
                f"structural markers in total."
            )


            if grammar_structures:

                for structure in grammar_structures:

                    tag_text = (
                        f" ({structure['tag']})"
                        if structure["tag"]
                        else ""
                    )

                    st.write(
                        f"- **{structure['form']}** "
                        f"— {structure['label']}"
                        f"{tag_text}"
                    )


            else:

                st.write(
                    "No weighted structural markers "
                    "were detected."
                )


            st.caption(
                "These markers are used by HanLevel's "
                "rule-based grammar-complexity component. "
                "They are structural indicators, not official "
                "learner-level grammar classifications."
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

Beginner entries receive a lower difficulty value, while intermediate and advanced entries contribute progressively more to the vocabulary score. Unclassified items do not automatically count as difficult.

**Grammar & morphology — 35%**

Korean morphological analysis is performed with Kiwi. Selected structural markers and morphological density contribute to the grammar-complexity score.

The grammar score represents structural complexity. It should not be interpreted as an official grammar proficiency level.

**Sentence length — 20%**

Average eojeol per sentence is used as an additional structural-complexity indicator.

**Final classification**

The three components are combined into the HanLevel score.

Current provisional thresholds are:

- **Beginner:** below 25
- **Intermediate:** 25 to below 50
- **Advanced:** 50 and above

These thresholds were calibrated on a small internally constructed development set. They are not official TOPIK or CEFR boundaries.

HanLevel v0.1 uses a rule-based model designed to make its difficulty estimate transparent and inspectable.
"""
            )