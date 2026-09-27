import json
from collections import defaultdict
from pathlib import Path


# =========================================================
# PATHS
# =========================================================

PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"

OUTPUT_FILE = DATA_DIR / "krdict_index.json"


# =========================================================
# HELPERS
# =========================================================

def as_list(value):
    """
    KRDICT sometimes stores one item as a dictionary
    and multiple items as a list.
    Normalize both cases into a list.
    """

    if value is None:
        return []

    if isinstance(value, list):
        return value

    return [value]


def get_feature(features, attribute):
    """
    Find one KRDICT feature by its 'att' value.
    """

    for feature in as_list(features):

        if not isinstance(feature, dict):
            continue

        if feature.get("att") == attribute:
            return feature.get("val")

    return None


def get_written_form(entry):
    """
    Extract the dictionary written form from Lemma.
    """

    lemmas = as_list(
        entry.get("Lemma")
    )

    for lemma in lemmas:

        if not isinstance(lemma, dict):
            continue

        written_form = get_feature(
            lemma.get("feat"),
            "writtenForm",
        )

        if written_form:
            return written_form

    return None


# =========================================================
# BUILD INDEX
# =========================================================

def build_compact_index():

    files = sorted(
        DATA_DIR.glob(
            "krdict_*_5000.json"
        )
    )

    if not files:

        raise FileNotFoundError(
            f"No KRDICT source files were found in {DATA_DIR}"
        )

    index = defaultdict(list)

    total_entries = 0
    kept_entries = 0

    print(
        f"Found {len(files)} KRDICT source files."
    )

    print()

    for number, file_path in enumerate(
        files,
        start=1,
    ):

        print(
            f"[{number}/{len(files)}] "
            f"Reading {file_path.name}..."
        )

        with open(
            file_path,
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        entries = (
            data.get(
                "LexicalResource",
                {}
            )
            .get(
                "Lexicon",
                {}
            )
            .get(
                "LexicalEntry",
                []
            )
        )

        entries = as_list(entries)

        for entry in entries:

            if not isinstance(entry, dict):
                continue

            total_entries += 1

            word = get_written_form(
                entry
            )

            if not word:
                continue

            features = (
                entry.get("feat")
            )

            pos = get_feature(
                features,
                "partOfSpeech",
            )

            grade = get_feature(
                features,
                "vocabularyLevel",
            )

            # KRDICT uses 없음 for entries
            # without a learner vocabulary level.
            if grade == "없음":
                grade = None

            # HanLevel only needs:
            # written form + POS + learner level
            compact_entry = [
                pos,
                grade,
            ]

            # Avoid exact duplicates
            if compact_entry not in index[word]:

                index[word].append(
                    compact_entry
                )

                kept_entries += 1


    # -----------------------------------------------------
    # Deterministic order
    # -----------------------------------------------------

    compact_index = {
        word: index[word]
        for word in sorted(index)
    }


    # -----------------------------------------------------
    # Save compact JSON
    # -----------------------------------------------------

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            compact_index,
            file,
            ensure_ascii=False,
            separators=(",", ":"),
        )


    # -----------------------------------------------------
    # Report
    # -----------------------------------------------------

    size_mb = (
        OUTPUT_FILE.stat().st_size
        / (1024 * 1024)
    )

    print()
    print("Finished.")
    print(
        f"Source lexical entries: {total_entries:,}"
    )

    print(
        f"Compact entries kept: {kept_entries:,}"
    )

    print(
        f"Unique written forms: {len(compact_index):,}"
    )

    print(
        f"Output: {OUTPUT_FILE}"
    )

    print(
        f"Compact file size: {size_mb:.2f} MB"
    )


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":
    build_compact_index()