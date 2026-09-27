##talks to the Korean Learners' Dictionary
##returns 초급 / 중급 / 고급

import json
from functools import lru_cache
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent / "data"

# KRDICT JSON sometimes stores one item as a dictionary and multiple items as a list. Normalize both cases.
def as_list(value):
    if value is None:
        return []

    if isinstance(value, list):
        return value

    return [value]


# Extract a value such as: partOfSpeech,vocabularyLevel, writtenForm
def get_feature(features, attribute):
    for feature in as_list(features):
        if not isinstance(feature, dict):
            continue

        if feature.get("att") == attribute:
            return feature.get("val")

    return None


# Extract the main dictionary lemma. 
def get_written_form(entry):
    lemmas = as_list(entry.get("Lemma"))

    for lemma in lemmas:
        if not isinstance(lemma, dict):
            continue

        written_form = get_feature(
            lemma.get("feat"),
            "writtenForm"
        )

        if written_form:
            return written_form

    return None


# Load all KRDICT JSON chunks and create an index: word -> list of dictionary entries
def build_dictionary_index():
    index = {}

    files = sorted(
        DATA_DIR.glob("krdict_*_5000.json")
    )

    if not files:
        raise FileNotFoundError(
            f"No KRDICT JSON files were found in {DATA_DIR}"
        )

    for file_path in files:

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        entries = (
            data
            .get("LexicalResource", {})
            .get("Lexicon", {})
            .get("LexicalEntry", [])
        )

        for entry in entries:

            word = get_written_form(entry)

            if not word:
                continue

            features = entry.get("feat")

            pos = get_feature(
                features,
                "partOfSpeech"
            )

            grade = get_feature(
                features,
                "vocabularyLevel"
            )

            # "없음" means the dictionary does not assign a learner level to this entry.
            if grade == "없음":
                grade = None

            result = {
                "word": word,
                "grade": grade,
                "pos": pos,
            }

            index.setdefault(
                word,
                []
            ).append(result)

    return index


# Load once when HanLevel starts.
DICTIONARY = build_dictionary_index()


# Look up a Korean word locally. Optional POS filtering to reduce problmes caused by homonyms.
@lru_cache(maxsize=10000)
def lookup_word(word, pos=None):
    results = DICTIONARY.get(
        word,
        []
    )

    if pos is not None:

        results = [
            result
            for result in results
            if result["pos"] == pos
        ]

    return results


if __name__ == "__main__":

    print(
        f"Loaded {len(DICTIONARY):,} unique dictionary forms."
    )

    print("\nTest lookup: 나무")

    print(
        lookup_word(
            "나무",
            "명사"
        )
    )