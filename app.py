import os

import streamlit as st

from adaptation_engine import adapt_with_evaluation, retry_adaptation
from analyzer import analyze_text


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="HanLevel v1.0",
    page_icon="🇰🇷",
    layout="centered",
)


# =========================================================
# STYLING
# =========================================================

st.markdown(
    """
<style>
[data-testid="stHeader"],
[data-testid="stDecoration"] {
    display: none;
}

.stApp {
    background:
        radial-gradient(circle at top left, #eef7ff 0%, transparent 34%),
        radial-gradient(circle at top right, #fff0f4 0%, transparent 34%),
        #fbfcff;
}

.block-container {
    max-width: 940px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

.hero-card {
    position: relative;
    overflow: hidden;
    padding: 2.5rem 2.2rem;
    margin-bottom: 1.6rem;
    border-radius: 28px;
    border: 1px solid rgba(210, 220, 240, 0.85);
    background:
        linear-gradient(
            135deg,
            rgba(238, 247, 255, 0.96),
            rgba(250, 245, 255, 0.96),
            rgba(255, 240, 244, 0.92)
        );
    box-shadow: 0 14px 40px rgba(50, 65, 100, 0.08);
    text-align: center;
}

.hero-card::before,
.hero-card::after {
    content: "";
    position: absolute;
    border-radius: 50%;
}

.hero-card::before {
    width: 190px;
    height: 190px;
    background: rgba(159, 220, 247, 0.25);
    top: -100px;
    right: -55px;
}

.hero-card::after {
    width: 150px;
    height: 150px;
    background: rgba(243, 171, 196, 0.20);
    bottom: -85px;
    left: -35px;
}

.hero-content {
    position: relative;
    z-index: 2;
}

.hero-badge {
    display: inline-block;
    padding: 6px 11px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.78);
    border: 1px solid rgba(190, 200, 225, 0.8);
    color: #65708a;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    margin-bottom: 0.9rem;
}

.hero-title {
    font-size: 3.7rem;
    font-weight: 850;
    letter-spacing: -2px;
    color: #172033;
    line-height: 1;
    margin-bottom: 0.7rem;
}

.hero-description {
    max-width: 690px;
    margin: 0 auto 1.25rem auto;
    color: #58657c;
    font-size: 1.02rem;
    line-height: 1.65;
}

.hero-highlight {
    color: #536dcc;
    font-weight: 700;
}

.hero-chips {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 0.6rem;
}

.hero-chip {
    padding: 7px 13px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.78);
    border: 1px solid rgba(215, 222, 238, 0.9);
    color: #556078;
    font-size: 0.82rem;
    font-weight: 600;
}

.section-card {
    background: rgba(255, 255, 255, 0.86);
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    padding: 1.25rem 1.35rem;
    box-shadow: 0 6px 24px rgba(40, 55, 90, 0.05);
    margin: 0.7rem 0 1.2rem 0;
}

.level-card {
    background:
        linear-gradient(
            135deg,
            rgba(255, 255, 255, 0.98),
            rgba(248, 249, 255, 0.98)
        );
    padding: 1.45rem;
    border-radius: 20px;
    border: 1px solid #e2e8f0;
    margin: 0.7rem 0 0.8rem 0;
    box-shadow: 0 8px 30px rgba(40, 55, 90, 0.06);
    text-align: center;
}

.level-kicker {
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #94a3b8;
    margin-bottom: 4px;
}

.level-name {
    font-size: 2.25rem;
    font-weight: 800;
}

.score-text {
    color: #64748b;
    font-size: 0.96rem;
    margin-top: 3px;
}

.difficulty-wrapper {
    margin-top: 1.55rem;
    margin-bottom: 1.15rem;
    padding-top: 1.65rem;
}

.difficulty-track {
    position: relative;
    width: 100%;
    height: 16px;
    border-radius: 999px;
    box-shadow:
        inset 0 1px 3px rgba(35, 48, 80, 0.10),
        0 3px 12px rgba(55, 70, 110, 0.10);
}

.difficulty-segment {
    position: absolute;
    top: 0;
    height: 100%;
}

.segment-beginner {
    left: 0;
    width: 25%;
    background-color: #9fdcf7;
    border-radius: 999px 0 0 999px;
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
    border-radius: 0 999px 999px 0;
}

.difficulty-threshold {
    position: absolute;
    top: -3px;
    width: 2px;
    height: 22px;
    background: rgba(255, 255, 255, 0.65);
    border-radius: 2px;
    z-index: 3;
}

.threshold-one { left: 25%; }
.threshold-two { left: 50%; }

.difficulty-marker {
    position: absolute;
    top: 50%;
    width: 28px;
    height: 28px;
    transform: translate(-50%, -50%);
    border-radius: 50%;
    background: white;
    border: 6px solid #786ed7;
    box-shadow: 0 4px 14px rgba(57, 67, 120, 0.22);
    z-index: 5;
}

.difficulty-score {
    position: absolute;
    bottom: 25px;
    transform: translateX(-50%);
    background: #172033;
    color: white;
    padding: 4px 9px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 700;
    white-space: nowrap;
    z-index: 6;
}

.difficulty-labels {
    display: grid;
    grid-template-columns: 1fr 1fr 2fr;
    margin-top: 12px;
    color: #64748b;
    font-size: 0.85rem;
    font-weight: 600;
    text-align: center;
}

.compare-heading {
    color: #172033;
    font-weight: 800;
    font-size: 1.05rem;
    margin-bottom: 0.2rem;
}

.compare-level {
    font-size: 1.55rem;
    font-weight: 800;
    margin-bottom: 0.15rem;
}

.compare-score {
    color: #64748b;
    font-size: 0.93rem;
}

.change-card {
    padding: 0.9rem 1rem;
    border-radius: 15px;
    background: linear-gradient(135deg, #f5f8ff, #fbf6ff);
    border: 1px solid #e1e7f3;
    margin-bottom: 0.65rem;
}

.status-success {
    padding: 0.95rem 1.05rem;
    border-radius: 15px;
    background: #eefbf4;
    border: 1px solid #ccebd9;
    color: #24633d;
    font-weight: 650;
}

.status-warning {
    padding: 0.95rem 1.05rem;
    border-radius: 15px;
    background: #fff8ed;
    border: 1px solid #f1dfbd;
    color: #7d5a1f;
    font-weight: 650;
}

.stTextArea textarea {
    background-color: white;
    border: 1.5px solid #d9e2f0;
    border-radius: 16px;
    padding: 16px;
    color: #172033;
}

.stTextArea textarea:focus {
    border-color: #7c9ee8;
    box-shadow: 0 0 0 2px rgba(124, 158, 232, 0.15);
}

.stButton > button,
.stDownloadButton > button {
    border-radius: 14px;
    font-weight: 700;
    min-height: 3rem;
}

.stButton > button[kind="primary"] {
    border: none;
    background: linear-gradient(90deg, #6587dd, #8f79d8);
    color: white;
}

[data-testid="stMetric"] {
    background-color: white;
    border: 1px solid #e2e8f0;
    padding: 16px;
    border-radius: 18px;
    box-shadow: 0 5px 20px rgba(40, 55, 90, 0.05);
}

[data-testid="stExpander"] {
    background-color: rgba(255, 255, 255, 0.76);
    border: 1px solid #e3e8f2;
    border-radius: 14px;
}

h1, h2, h3 {
    color: #172033;
}

hr {
    border-color: #e8edf5;
}

@media (max-width: 700px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
        padding-top: 1.2rem;
    }

    .hero-card {
        padding: 2rem 1.25rem;
    }

    .hero-title {
        font-size: 2.9rem;
    }

    .hero-description {
        font-size: 0.95rem;
    }

    .compare-level {
        font-size: 1.25rem;
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

LEVEL_COLORS = {
    "Beginner": "#62a9d8",
    "Intermediate": "#786ed7",
    "Advanced": "#d66f9e",
}

LEVELS = ["Beginner", "Intermediate", "Advanced"]
STYLES = ["Natural", "Casual", "Learning-friendly"]

GRAMMAR_TAG_LABELS = {
    "EP": "Prefinal ending",
    "EC": "Connective ending",
    "ETM": "Adnominal ending",
    "ETN": "Nominalizing ending",
    "VX": "Auxiliary verb",
    "JKQ": "Quotation particle",
}


# =========================================================
# SESSION STATE
# =========================================================

DEFAULT_STATE = {
    "input_text": "",
    "source_text": None,
    "source_analysis": None,
    "adaptation_result": None,
    "uploaded_fingerprint": None,
}

for state_key, default_value in DEFAULT_STATE.items():
    if state_key not in st.session_state:
        st.session_state[state_key] = default_value


# =========================================================
# HELPERS
# =========================================================

def safe_score(value):
    return 0.0 if value is None else float(value)


def get_gemini_api_key():
    env_key = os.getenv("GEMINI_API_KEY")
    if env_key:
        return env_key

    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return None


def clear_adaptation():
    st.session_state.adaptation_result = None


def clear_analysis():
    st.session_state.source_text = None
    st.session_state.source_analysis = None
    clear_adaptation()


def calculate_contributions(result):
    vocabulary_score = result["vocabulary"]["vocabulary_score"]
    grammar_score = result["grammar"]["grammar_score"]
    sentence_score = result["sentence_length"]["sentence_length_score"]

    components = []

    if vocabulary_score is not None:
        components.append(("Vocabulary", vocabulary_score, 0.45))

    components.append(("Grammar", grammar_score, 0.35))
    components.append(("Sentence length", sentence_score, 0.20))

    total_weight = sum(weight for _, _, weight in components)

    return {
        name: score * weight / total_weight
        for name, score, weight in components
    }


def get_vocabulary_profile(result):
    profile = {
        "Beginner": 0,
        "Intermediate": 0,
        "Advanced": 0,
        "Unclassified": 0,
    }

    for item in result["vocabulary"]["words"]:
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


def get_difficult_words(result):
    difficult = []
    seen = set()

    for item in result["vocabulary"]["words"]:
        word = item["word"]
        grade = item["grade"]

        if grade not in {"중급", "고급"}:
            continue

        key = (word, grade)
        if key in seen:
            continue

        seen.add(key)
        difficult.append({"word": word, "grade": grade})

    return difficult


def format_grammar_structure(item):
    form = item.get("form") or item.get("word") or item.get("lemma") or "Unknown"
    tag = item.get("tag") or item.get("pos")

    display_form = form

    if tag and tag.startswith("E") and not form.startswith("-"):
        display_form = f"-{form}"

    display_normalization = {
        ("ᆫ", "ETM"): "-(으)ㄴ",
        ("ㄴ", "ETM"): "-(으)ㄴ",
        ("ᆯ", "ETM"): "-(으)ㄹ",
        ("ㄹ", "ETM"): "-(으)ㄹ",
        ("있", "VX"): "있다",
        ("않", "VX"): "않다",
    }

    display_form = display_normalization.get((form, tag), display_form)
    label = GRAMMAR_TAG_LABELS.get(tag, tag or "Structural marker")

    return display_form, tag, label


def get_unique_grammar_structures(result):
    unique = []
    seen = set()

    for item in result["grammar"]["structures"]:
        form, tag, label = format_grammar_structure(item)
        key = (form, tag)

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


def render_level_card(result, kicker="Estimated level"):
    level = result["level"]
    score = result["final_score"]
    level_color = LEVEL_COLORS.get(level, "#786ed7")

    st.markdown(
        f"""
        <div class="level-card">
            <div class="level-kicker">{kicker}</div>
            <div class="level-name" style="color:{level_color};">{level}</div>
            <div class="score-text">HanLevel score: {score:.1f} / 100</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_difficulty_scale(result):
    score = min(max(float(result["final_score"]), 0), 100)
    level_color = LEVEL_COLORS.get(result["level"], "#786ed7")

    st.markdown(
        f"""
        <div class="difficulty-wrapper">
            <div class="difficulty-track">
                <div class="difficulty-segment segment-beginner"></div>
                <div class="difficulty-segment segment-intermediate"></div>
                <div class="difficulty-segment segment-advanced"></div>
                <div class="difficulty-threshold threshold-one"></div>
                <div class="difficulty-threshold threshold-two"></div>
                <div class="difficulty-score" style="left:{score}%;">{score:.1f}</div>
                <div class="difficulty-marker"
                     style="left:{score}%; border-color:{level_color};"></div>
            </div>
            <div class="difficulty-labels">
                <span>Beginner</span>
                <span>Intermediate</span>
                <span>Advanced</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_analysis_details(result):
    vocabulary_score = safe_score(result["vocabulary"]["vocabulary_score"])
    grammar_score = result["grammar"]["grammar_score"]
    sentence_score = result["sentence_length"]["sentence_length_score"]
    coverage = result["vocabulary"]["coverage"]
    average_eojeol = result["sentence_length"]["average_eojeol"]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Vocabulary difficulty", f"{vocabulary_score:.1f}/100")
    with col2:
        st.metric("Grammar complexity", f"{grammar_score:.1f}/100")
    with col3:
        st.metric("Sentence length", f"{sentence_score:.1f}/100")

    st.caption(
        f"Dictionary coverage: {coverage:.1f}% · "
        f"Average sentence length: {average_eojeol:.1f} eojeol"
    )

    if coverage < LOW_COVERAGE_THRESHOLD:
        st.warning(
            "Vocabulary coverage is limited, so the lexical estimate "
            "should be interpreted cautiously."
        )

    contributions = calculate_contributions(result)

    st.markdown("#### Contribution to HanLevel score")
    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Vocabulary",
            f"+{contributions.get('Vocabulary', 0):.1f} points",
        )
    with c2:
        st.metric(
            "Grammar",
            f"+{contributions.get('Grammar', 0):.1f} points",
        )
    with c3:
        st.metric(
            "Sentence length",
            f"+{contributions.get('Sentence length', 0):.1f} points",
        )

    profile = get_vocabulary_profile(result)

    st.markdown("#### Vocabulary profile")
    p1, p2, p3, p4 = st.columns(4)

    with p1:
        st.metric("Beginner", profile["Beginner"])
    with p2:
        st.metric("Intermediate", profile["Intermediate"])
    with p3:
        st.metric("Advanced", profile["Advanced"])
    with p4:
        st.metric("Unclassified", profile["Unclassified"])

    difficult_words = get_difficult_words(result)

    if difficult_words:
        st.markdown("#### Potentially challenging vocabulary")
        for item in difficult_words:
            level_name = "Intermediate" if item["grade"] == "중급" else "Advanced"
            st.write(f"• **{item['word']}** — {level_name}")

    grammar_structures = get_unique_grammar_structures(result)

    if grammar_structures:
        st.markdown("#### Detected structural markers")
        for item in grammar_structures:
            st.write(f"• **{item['form']}** — {item['label']}")

        st.caption(
            "These markers are structural indicators used by HanLevel, "
            "not official learner-level grammar classifications."
        )


def metric_change(original_result, adapted_result, key):
    if key == "Vocabulary":
        original = safe_score(original_result["vocabulary"]["vocabulary_score"])
        adapted = safe_score(adapted_result["vocabulary"]["vocabulary_score"])
    elif key == "Grammar":
        original = float(original_result["grammar"]["grammar_score"])
        adapted = float(adapted_result["grammar"]["grammar_score"])
    elif key == "Sentence length":
        original = float(
            original_result["sentence_length"]["sentence_length_score"]
        )
        adapted = float(
            adapted_result["sentence_length"]["sentence_length_score"]
        )
    elif key == "Average eojeol":
        original = float(
            original_result["sentence_length"]["average_eojeol"]
        )
        adapted = float(
            adapted_result["sentence_length"]["average_eojeol"]
        )
    else:
        raise ValueError(f"Unknown comparison metric: {key}")

    return original, adapted, adapted - original


def render_comparison(original_result, adapted_result):
    original_level = original_result["level"]
    adapted_level = adapted_result["level"]

    left, right = st.columns(2)

    with left:
        st.markdown(
            f"""
            <div class="section-card">
                <div class="compare-heading">Original</div>
                <div class="compare-level"
                     style="color:{LEVEL_COLORS.get(original_level, '#786ed7')};">
                    {original_level}
                </div>
                <div class="compare-score">
                    {original_result['final_score']:.1f} / 100
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            f"""
            <div class="section-card">
                <div class="compare-heading">Adapted</div>
                <div class="compare-level"
                     style="color:{LEVEL_COLORS.get(adapted_level, '#786ed7')};">
                    {adapted_level}
                </div>
                <div class="compare-score">
                    {adapted_result['final_score']:.1f} / 100
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    overall_delta = (
        adapted_result["final_score"]
        - original_result["final_score"]
    )

    st.metric(
        "HanLevel score change",
        f"{adapted_result['final_score']:.1f}",
        f"{overall_delta:+.1f} points",
        delta_color="off",
    )

    st.markdown("#### Component changes")
    columns = st.columns(3)

    for column, metric_name in zip(
        columns,
        ["Vocabulary", "Grammar", "Sentence length"],
    ):
        original, adapted, delta = metric_change(
            original_result,
            adapted_result,
            metric_name,
        )

        with column:
            st.metric(
                metric_name,
                f"{original:.1f} → {adapted:.1f}",
                f"{delta:+.1f}",
                delta_color="off",
            )

    original_eojeol, adapted_eojeol, eojeol_delta = metric_change(
        original_result,
        adapted_result,
        "Average eojeol",
    )

    st.caption(
        "Average sentence length: "
        f"{original_eojeol:.1f} → {adapted_eojeol:.1f} eojeol "
        f"({eojeol_delta:+.1f})"
    )


def render_what_changed(adaptation_result):
    st.subheader("④ Learn — What changed?")

    final_analysis = adaptation_result["final_analysis"]
    original_analysis = adaptation_result["original_analysis"]

    render_comparison(original_analysis, final_analysis)

    change_summary = adaptation_result.get("change_summary", [])
    notable_changes = adaptation_result.get("notable_changes", [])

    if change_summary:
        st.markdown("#### Main changes")
        for summary in change_summary:
            st.markdown(
                f'<div class="change-card">{summary}</div>',
                unsafe_allow_html=True,
            )

    if notable_changes:
        st.markdown("#### Examples from the adaptation")

        for change in notable_changes:
            category = change.get("category", "Change")
            original = change.get("original", "")
            adapted = change.get("adapted", "")
            explanation = change.get("explanation", "")

            with st.container(border=True):
                st.caption(category)
                if original or adapted:
                    st.write(f"**{original}** → **{adapted}**")
                if explanation:
                    st.write(explanation)


# =========================================================
# HERO
# =========================================================

st.markdown(
    """
    <div class="hero-card">
        <div class="hero-content">
            <div class="hero-badge">HanLevel v1.0 · AI + Education</div>
            <div class="hero-title">HanLevel</div>
            <div class="hero-description">
                <span class="hero-highlight">
                    Analyze, adapt, compare, and learn.
                </span>
                HanLevel measures Korean readability with an interpretable
                rule-based NLP engine, then uses AI to adapt the text to
                your chosen difficulty and style.
            </div>
            <div class="hero-chips">
                <span class="hero-chip">Analyze</span>
                <span class="hero-chip">Adapt</span>
                <span class="hero-chip">Verify</span>
                <span class="hero-chip">Learn</span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ① INPUT + ANALYZE
# =========================================================

st.subheader("① Analyze")

uploaded_file = st.file_uploader(
    "Import a Korean .txt file",
    type=["txt"],
    help="UTF-8 text files are supported.",
)

if uploaded_file is not None:
    raw_bytes = uploaded_file.getvalue()
    fingerprint = (
        uploaded_file.name,
        len(raw_bytes),
        hash(raw_bytes),
    )

    if fingerprint != st.session_state.uploaded_fingerprint:
        try:
            imported_text = raw_bytes.decode("utf-8-sig")
        except UnicodeDecodeError:
            st.error(
                "This file could not be read as UTF-8 text. "
                "Please save it as UTF-8 and try again."
            )
        else:
            st.session_state.input_text = imported_text
            st.session_state.uploaded_fingerprint = fingerprint
            clear_analysis()

text = st.text_area(
    "Korean text",
    key="input_text",
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

if analyze_button:
    if not text.strip():
        st.warning("Please enter some Korean text first.")
    else:
        with st.spinner("Analyzing Korean text..."):
            st.session_state.source_text = text.strip()
            st.session_state.source_analysis = analyze_text(text.strip())
            st.session_state.adaptation_result = None


# =========================================================
# ORIGINAL RESULT
# =========================================================

if st.session_state.source_analysis is not None:
    source_result = st.session_state.source_analysis

    st.markdown("---")
    render_level_card(source_result, kicker="Current readability")
    render_difficulty_scale(source_result)

    with st.expander("See original analysis details"):
        render_analysis_details(source_result)


    # =====================================================
    # ② ADAPT
    # =====================================================

    st.markdown("---")
    st.subheader("② Adapt")

    st.write(
        "Choose the difficulty and style you want. "
        "The target can be easier, harder, or the same level as the original."
    )

    current_level = source_result["level"]
    default_level_index = LEVELS.index(current_level)

    target_level = st.radio(
        "Target difficulty",
        LEVELS,
        index=default_level_index,
        horizontal=True,
    )

    style = st.radio(
        "Adaptation style",
        STYLES,
        index=0,
        horizontal=True,
        help=(
            "Natural preserves the source register when possible. "
            "Casual uses everyday conversational Korean. "
            "Learning-friendly prioritizes clarity and explicit connections."
        ),
    )

    gemini_api_key = get_gemini_api_key()

    if gemini_api_key is None:
        st.info(
            "AI adaptation is ready, but this deployment does not have a "
            "Gemini API key configured yet."
        )

    adapt_button = st.button(
        "✨ Adapt with AI",
        type="primary",
        use_container_width=True,
        disabled=(gemini_api_key is None),
    )

    if adapt_button:
        with st.spinner(
            "Adapting the text and checking the result with HanLevel..."
        ):
            try:
                st.session_state.adaptation_result = adapt_with_evaluation(
                    text=st.session_state.source_text,
                    target_level=target_level,
                    style=style,
                    original_analysis=source_result,
                    api_key=gemini_api_key,
                )
            except Exception as exc:
                st.error(
                    "The AI adaptation could not be completed. "
                    "Please try again in a moment."
                )
                with st.expander("Technical details"):
                    st.code(str(exc))


# =========================================================
# ③ COMPARE + STATUS
# =========================================================

if st.session_state.adaptation_result is not None:
    adaptation_result = st.session_state.adaptation_result
    adapted_text = adaptation_result["final_text"]
    adapted_result = adaptation_result["final_analysis"]

    st.markdown("---")
    st.subheader("③ Compare")

    st.write(
        "Compare the original and adapted versions side by side."
    )

    original_col, adapted_col = st.columns(2)

    with original_col:
        st.text_area(
            "Original text",
            value=adaptation_result["original_text"],
            height=220,
            disabled=True,
            key="compare_original_text",
        )

    with adapted_col:
        st.text_area(
            "Adapted text",
            value=adapted_text,
            height=220,
            disabled=True,
            key="compare_adapted_text",
        )

    if adaptation_result["target_reached"]:
        generation_count = adaptation_result.get("generation_count", 1)
        generation_word = (
            "generation" if generation_count == 1 else "generations"
        )

        st.markdown(
            f"""
            <div class="status-success">
                ✓ Target reached in {generation_count} {generation_word}.
                HanLevel independently selected candidate
                {adaptation_result.get('best_candidate_number', 1)}
                as {adapted_result['level']}
                ({adapted_result['final_score']:.1f}/100).
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="status-warning">
                Target not reached in the current generation.
                Requested: {adaptation_result['target_level']}.
                Best candidate so far: {adapted_result['level']}
                ({adapted_result['final_score']:.1f}/100),
                candidate {adaptation_result.get('best_candidate_number', 1)}.
            </div>
            """,
            unsafe_allow_html=True,
        )

        retry_button = st.button(
            "Try again",
            use_container_width=True,
        )

        if retry_button:
            gemini_api_key = get_gemini_api_key()

            if gemini_api_key is None:
                st.error("Gemini API key is not configured.")
            else:
                with st.spinner(
                    "Trying another adaptation using HanLevel feedback..."
                ):
                    try:
                        st.session_state.adaptation_result = retry_adaptation(
                            adaptation_result,
                            api_key=gemini_api_key,
                        )
                        st.rerun()
                    except Exception as exc:
                        st.error(
                            "The retry could not be completed. "
                            "Please try again."
                        )
                        with st.expander("Technical details"):
                            st.code(str(exc))

    st.download_button(
        "Download adapted .txt",
        data=adapted_text.encode("utf-8"),
        file_name="hanlevel_adapted.txt",
        mime="text/plain",
        use_container_width=True,
    )

    attempts = adaptation_result.get("attempts", [])
    if attempts:
        with st.expander("See generated candidates"):
            for attempt in attempts:
                status = (
                    "✓ target"
                    if attempt["level"] == adaptation_result["target_level"]
                    else "→"
                )
                analysis = attempt["analysis"]
                vocab = safe_score(
                    analysis["vocabulary"]["vocabulary_score"]
                )
                grammar = analysis["grammar"]["grammar_score"]
                sentence = (
                    analysis["sentence_length"]["sentence_length_score"]
                )

                latency = float(attempt.get("latency_seconds", 0.0))
                latency_text = (
                    f" · {latency:.1f}s"
                    if latency > 0
                    else ""
                )

                st.write(
                    f"**Candidate {attempt['number']}** {status} "
                    f"{attempt['level']} · {attempt['score']:.1f}/100 "
                    f"· {attempt.get('model', 'Gemini')}{latency_text}"
                )
                st.caption(
                    f"Vocabulary {vocab:.1f} · "
                    f"Grammar {grammar:.1f} · "
                    f"Sentence length {sentence:.1f}"
                )

    render_what_changed(adaptation_result)

    with st.expander("See adapted-text analysis details"):
        render_analysis_details(adapted_result)


# =========================================================
# METHODOLOGY
# =========================================================

st.markdown("---")

with st.expander("How HanLevel v1.0 works"):
    st.markdown(
        """
        **HanLevel's readability score remains rule-based and interpretable.**

        The original and adapted texts are independently analyzed using:

        - **Vocabulary difficulty — 45%**
        - **Grammar & morphology — 35%**
        - **Sentence length — 20%**

        Current project-specific bands:

        - **Beginner:** score below 25
        - **Intermediate:** 25 to below 50
        - **Advanced:** 50 or above

        For AI adaptation, HanLevel sends the source text, requested target,
        style, and readability diagnostics to Gemini. The generated text is
        then scored again by HanLevel's independent rule-based analyzer.

        If the first generation misses the requested band, HanLevel sends its
        diagnostic feedback back to the AI for **one automatic corrective
        retry**. If that second attempt still misses the target, the user can
        choose **Try again** manually.

        The AI is instructed to preserve meaning, facts, names, numbers,
        relationships, speaker position, and conclusions as closely as
        possible. Adaptation is not intended to be summarization.

        HanLevel scores and thresholds are project-specific and should not be
        interpreted as official TOPIK or CEFR proficiency boundaries.
        """
    )
