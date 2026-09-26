## turns the linguistic labels into numbers
## calculates HanLevel's difficulty scores

from kiwipiepy import Kiwi
from krdict import lookup_word

kiwi = Kiwi()

GRADE_SCORES  = {
    "초급": 0,
    "중급": 50,
    "고급": 100
}

# Kiwi POS → Korean Learners' Dictionary POS code
KIWI_TO_KRDICT_POS = {
    "NNG": 1,   # common noun → 명사
    "NNB": 11,  # dependent noun → 의존 명사
    "NP": 2,    # pronoun → 대명사
    "NR": 3,    # numeral → 수사

    "VV": 5,    # verb → 동사
    "VA": 6,    # adjective → 형용사

    "MM": 7,    # determiner → 관형사
    "MAG": 8,   # adverb → 부사
    "MAJ": 8,   # conjunctive adverb → 부사
    "IC": 9,    # interjection → 감탄사
}

# Convert Kiwi output into kr dictionary citation forms.
def normalize_lemma(form, tag):
    if tag in {"VV", "VA"}:
        return form + "다"

    return form

# Extract lexical vocabulary from Korean text.
# Grammar markers, particles and endings are excluded because     they will belong to HanLevel's grammar component.
def extract_vocabulary(text):
    tokens = kiwi.tokenize(text)
    vocabulary = []

    for token in tokens:
        tag = token.tag

        if tag == "NNP":
            continue
        if tag not in KIWI_TO_KRDICT_POS:
            continue

        lemma = normalize_lemma(token.form, tag)

        vocabulary.append(
            {
                "lemma": lemma,
                "kiwi_pos":tag,
                "krdict_pos": KIWI_TO_KRDICT_POS[tag],
            }
        )

    return vocabulary

# Choose a grade when the dictionary return one or more entries.
def choose_grade(results):
    grades = [
        result["grade"]
        for result in results
        if result["grade"] in GRADE_SCORES
    ]

    if not grades:
        return None

    return min(
        grades,
        key=lambda grade: GRADE_SCORES[grade]
    )


def analyze_vocabulary(text):
    vocabulary = extract_vocabulary(text)

    analyzed_words = []

    for item in vocabulary:
        results = lookup_word(
            item["lemma"],
            item["krdict_pos"]
        )

        grade = choose_grade(results)

        analyzed_words.append(
            {
                "word": item["lemma"],
                "pos": item["kiwi_pos"],
                "grade": grade,
                "score": (
                    GRADE_SCORES[grade]
                    if grade is not None
                    else None
                ),
            }
        )

    scored_words = [
        item
        for item in analyzed_words
        if item["score"] is not None
    ]

    if scored_words:
        vocabulary_score = sum(
            item["score"] for item in scored_words
        ) / len(scored_words)
    else:
        vocabulary_score = None

    coverage = (
        len(scored_words) / len(analyzed_words) * 100
        if analyzed_words
        else 0
    )

    return {
        "words": analyzed_words,
        "vocabulary_score": vocabulary_score,
        "coverage": coverage,
    }


#####################################################################


GRAMMAR_WEIGHTS = {
    "EP": 0.75,   # pre-final ending: tense/honorific etc.
    "EC": 1.25,   # connective ending
    "ETM": 2.0,   # adnominal ending
    "ETN": 2.0,   # nominalizing ending
    "VX": 1.0,    # auxiliary predicate
    "JKQ": 1.0,   # quotation particle
}

# Kiwi may return tags such as VV-I or VA-R. Only the base POS tag is needed.
def base_tag(tag):
    return tag.split("-")[0]

# Convert a measurement into 0-100 score.
def scale_score(value, minimum, maximum):
    if value <= minimum:
        return 0.0
    if value >= maximum:
        return 100.0

    return (
        (value - minimum)
        / (maximum - minimum)
        * 100
    )

# Estimate korean grammatical/morphological complexity.
def analyze_grammar(text):
    tokens = kiwi.tokenize(text,split_complex=True)
    sentences = kiwi.split_into_sents(text)
    sentence_count = max(len(sentences), 1)

    # 1. structural complexity

    structural_points = 0.0
    structures = []

    for token in tokens:
        tag = base_tag(token.tag)

        if tag in GRAMMAR_WEIGHTS:
            weight = GRAMMAR_WEIGHTS[tag]
            structural_points += weight

            structures.append(
                {
                     "form": token.form,
                    "tag": tag,
                    "weight": weight,
                }
            )

    structure_density = (structural_points / sentence_count)

    # Initial calibration:
    # 0 structural points/sentence → 0
    # 4+ structural points/sentence → 100
    structure_score = scale_score(structure_density, 0, 4)

    # 2. Morphology density
    morphological_tokens = []

    for token in tokens:
        tag = base_tag(token.tag)

        if not tag.startswith("S") and not tag.startswith("W"):
            morphological_tokens.append(token)

    eojeol_count = len(text.split())

    if eojeol_count:
        morphology_density = (
            len(morphological_tokens)
            / eojeol_count
        )
    else:
        morphology_density = 0

    # Initial calibration:
    # ~2 morphemes/eojeol → simple
    # ~4+ morphemes/eojeol → complex
    morphology_score = scale_score(
        morphology_density,
        2,
        4
    )

    #3. Final grammar score
    grammar_score = (
        structure_score * 0.70
        + morphology_score * 0.30
    )

    return {
        "grammar_score": grammar_score,
        "structure_score": structure_score,
        "morphology_score": morphology_score,
        "structure_density": structure_density,
        "morphology_density": morphology_density,
        "sentence_count": sentence_count,
        "structures": structures,
    }


########################################################


# Estimate sentence-length complexity using average eojeol per sentence.
def analyze_sentence_length(text):
    sentences = kiwi.split_into_sents(text)

    if not sentences:
        return {
            "sentence_length_score": 0.0,
            "average_eojeol": 0.0,
            "sentence_count": 0,
        }

    eojeol_counts = []

    for sentence in sentences:
        eojeol_count = len(sentence.text.split())
        eojeol_counts.append(eojeol_count)

    average_eojeol = (
        sum(eojeol_counts) / len(eojeol_counts)
    )

    # Initial calibration:
    # 4 or fewer eojeol/sentence → very simple
    # 20+ eojeol/sentence → very complex
    sentence_length_score = scale_score(
        average_eojeol,
        4,
        20
    )

    return {
        "sentence_length_score": sentence_length_score,
        "average_eojeol": average_eojeol,
        "sentence_count": len(sentences),
    }


#####################################################################


def classify_level(final_score):
    if final_score < 25:
        return "Beginner"
    elif final_score < 55:
        return "Intermediate"
    else:
        return "Advanced"


def analyze_text(text):
    vocabulary = analyze_vocabulary(text)
    grammar = analyze_grammar(text)
    sentence_length = analyze_sentence_length(text)

    vocabulary_score = vocabulary["vocabulary_score"]

    if vocabulary_score is None:
        vocabulary_score = 0.0

    final_score = (
        vocabulary_score * 0.45
        + grammar["grammar_score"] * 0.35
        + sentence_length["sentence_length_score"] * 0.20
    )

    level = classify_level(final_score)

    return {
        "final_score": final_score,
        "level": level,
        "vocabulary": vocabulary,
        "grammar": grammar,
        "sentence_length": sentence_length,
    }


#####################################################################


if __name__ == "__main__":
    text = input("Enter Korean text: ")

    print("\n========================")
    print("VOCABULARY")
    print("========================\n")

    vocab = analyze_vocabulary(text)

    for word in vocab["words"]:
        grade = word["grade"] or "Unclassified"

        print(
            f"{word['word']:15} "
            f"{word['pos']:5} "
            f"{grade}"
        )

    print(
        f"\nVocabulary coverage: "
        f"{vocab['coverage']:.1f}%"
    )

    if vocab["vocabulary_score"] is not None:
        print(
            f"Vocabulary difficulty: "
            f"{vocab['vocabulary_score']:.1f} / 100"
        )


    print("\n========================")
    print("GRAMMAR / MORPHOLOGY")
    print("========================\n")

    grammar = analyze_grammar(text)

    print("Detected structures:")

    for structure in grammar["structures"]:
        print(
            f"{structure['form']:10} "
            f"{structure['tag']:5} "
            f"+{structure['weight']}"
        )

    print(
        f"\nStructural density: "
        f"{grammar['structure_density']:.2f}"
    )

    print(
        f"Morphological density: "
        f"{grammar['morphology_density']:.2f}"
    )

    print(
        f"\nStructure score: "
        f"{grammar['structure_score']:.1f} / 100"
    )

    print(
        f"Morphology score: "
        f"{grammar['morphology_score']:.1f} / 100"
    )

    print(
        f"\nGrammar complexity score: "
        f"{grammar['grammar_score']:.1f} / 100"
    )

    print("\n========================")
print("SENTENCE LENGTH")
print("========================\n")

length = analyze_sentence_length(text)

print(
    f"Average eojeol per sentence: "
    f"{length['average_eojeol']:.2f}"
)

print(
    f"Sentence length score: "
    f"{length['sentence_length_score']:.1f} / 100"
)

print("\n========================")
print("HANLEVEL RESULT")
print("========================\n")

result = analyze_text(text)

print(
    f"Vocabulary: "
    f"{result['vocabulary']['vocabulary_score']:.1f} / 100"
)

print(
    f"Grammar: "
    f"{result['grammar']['grammar_score']:.1f} / 100"
)

print(
    f"Sentence length: "
    f"{result['sentence_length']['sentence_length_score']:.1f} / 100"
)

print("\n------------------------")

print(
    f"Final HanLevel score: "
    f"{result['final_score']:.1f} / 100"
)

print(
    f"Estimated level: "
    f"{result['level']}"
)