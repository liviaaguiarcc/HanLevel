##talks to the Korean Learners' Dictionary
##returns 초급 / 중급 / 고급

import os
import xml.etree.ElementTree as ET
from functools import lru_cache

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("KRDICT_API_KEY")
API_URL = "https://krdict.korean.go.kr/api/search"

@lru_cache(maxsize=2048)
def lookup_word(word, pos_code=None):
    if not API_KEY:
        raise RuntimeError(
            "KRDICT_API_KEY was not found. Check your .env file."
        )
    
    params = {
        "key": API_KEY,
        "q": word,
        "part": "word",
        "advanced": "y",
        "target": 1,
        "method": "exact",
        "num": 10,
    }

    if pos_code is not None:
        params["pos"] = pos_code

    response = requests.get(API_URL, params=params, timeout=10)
    response.raise_for_status()

    root = ET.fromstring(response.text)


    #API error handling
    if root.tag == "error":
        error_code = root.findtext("error_code")
        message = root.findtext("message")
        raise RuntimeError(
            f"KRDICT API error {error_code}: {message}"
        )

    results = []

    for item in root.findall("item"):
        dictionary_word = item.findtext("word")
        grade = item.findtext("word_grade")
        pos = item.findtext("pos")

        if dictionary_word == word:
            results.append(
                {
                    "word": dictionary_word,
                    "grade": grade,
                    "pos": pos,
                }
            )

    return results

if __name__ == "__main__":
    print(lookup_word("나무"))
