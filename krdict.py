##talks to the Korean Learners' Dictionary
##returns 초급 / 중급 / 고급

import json
from functools import lru_cache
from pathlib import Path


# =========================================================
# PATH
# =========================================================

DATA_FILE = (
    Path(__file__).resolve().parent
    / "data"
    / "krdict_index.json"
)


# =========================================================
# LOAD COMPACT INDEX
# =========================================================

def load_dictionary():

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Compact KRDICT index was not found: {DATA_FILE}"
        )

    with open(
        DATA_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


DICTIONARY = load_dictionary()


# =========================================================
# LOOKUP
# =========================================================

@lru_cache(maxsize=10000)
def lookup_word(word, pos=None):

    entries = DICTIONARY.get(
        word,
        [],
    )

    results = []

    for entry in entries:

        entry_pos = entry[0]
        grade = entry[1]

        result = {
            "word": word,
            "pos": entry_pos,
            "grade": grade,
        }

        results.append(result)


    if pos is not None:

        results = [
            result
            for result in results
            if result["pos"] == pos
        ]


    return results