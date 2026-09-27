import csv
from analyzer import analyze_text

CALIBRATION_TEXTS = [
    # -------------------------
    # BEGINNER
    # -------------------------
    {
        "id": "B1",
        "expected": "Beginner",
        "text": "저는 학생이에요. 매일 학교에 가요.",
    },
    {
        "id": "B2",
        "expected": "Beginner",
        "text": "오늘 날씨가 좋아요. 친구하고 공원에 가요.",
    },
    {
        "id": "B3",
        "expected": "Beginner",
        "text": "어제 시장에서 사과하고 우유를 샀어요.",
    },
    {
        "id": "B4",
        "expected": "Beginner",
        "text": "저는 한국 음식을 좋아해요. 김치찌개를 자주 먹어요.",
    },
    {
        "id": "B5",
        "expected": "Beginner",
        "text": "주말에 가족과 영화를 봤어요. 영화가 아주 재미있었어요.",
    },

    # -------------------------
    # INTERMEDIATE
    # -------------------------
    {
        "id": "I1",
        "expected": "Intermediate",
        "text": "제가 어렸을 때 자주 방문했던 도시는 시간이 지나면서 많이 변했습니다.",
    },
    {
        "id": "I2",
        "expected": "Intermediate",
        "text": "한국어를 공부한 지 일 년이 되었지만 아직 모르는 표현이 많습니다.",
    },
    {
        "id": "I3",
        "expected": "Intermediate",
        "text": "비가 많이 왔기 때문에 계획했던 여행을 다음 주로 미루기로 했습니다.",
    },
    {
        "id": "I4",
        "expected": "Intermediate",
        "text": "친구가 추천해 준 책을 읽어 보았는데 생각보다 내용이 어려웠습니다.",
    },
    {
        "id": "I5",
        "expected": "Intermediate",
        "text": "새로운 환경에 적응하려면 사람들과 적극적으로 이야기하는 것이 도움이 됩니다.",
    },

    # -------------------------
    # ADVANCED
    # -------------------------
    {
        "id": "A1",
        "expected": "Advanced",
        "text": "기술의 급속한 발전은 생활의 편리함을 높이는 반면 새로운 사회적 문제를 초래하기도 한다.",
    },
    {
        "id": "A2",
        "expected": "Advanced",
        "text": "개인의 선택을 존중해야 한다는 주장에도 불구하고 사회 전체에 미치는 영향을 간과해서는 안 된다.",
    },
    {
        "id": "A3",
        "expected": "Advanced",
        "text": "문화적 차이를 단순한 오해의 원인으로만 간주하는 것은 복잡한 사회적 맥락을 지나치게 단순화할 가능성이 있다.",
    },
    {
        "id": "A4",
        "expected": "Advanced",
        "text": "연구 결과를 해석할 때에는 통계적 유의성뿐만 아니라 연구 설계와 자료 수집 과정의 한계도 함께 고려해야 한다.",
    },
    {
        "id": "A5",
        "expected": "Advanced",
        "text": "언어 사용의 변화는 단순히 새로운 표현이 등장하는 현상에 그치지 않고 사회 구성원의 가치관과 정체성이 변화하는 양상을 반영한다고 볼 수 있다.",
    },
]

def safe_score(value):
    if value is None:
        return 0.0
    return value

def main():
    results = []

    for sample in CALIBRATION_TEXTS:
        print(f"Analyzing {sample['id']}...")

        result = analyze_text(sample["text"])

        vocabulary_score = safe_score(
            result["vocabulary"]["vocabulary_score"]
        )

        grammar_score = result["grammar"]["grammar_score"]

        sentence_score = (
            result["sentence_length"]["sentence_length_score"]
        )

        row = {
            "id": sample["id"],
            "expected": sample["expected"],
            "predicted": result["level"],
            "final_score": round(result["final_score"], 1),
            "vocabulary_score": round(vocabulary_score, 1),
            "grammar_score": round(grammar_score, 1),
            "sentence_score": round(sentence_score, 1),
            "coverage": round(
                result["vocabulary"]["coverage"], 1
            ),
            "text": sample["text"],
        }

        results.append(row)

    print("\nHANLEVEL CALIBRATION")
    print("=" * 90)

    for row in results:
        status = (
            "✓"
            if row["expected"] == row["predicted"]
            else "✗"
        )

        print(
            f"{row['id']:3} | "
            f"Expected: {row['expected']:12} | "
            f"Predicted: {row['predicted']:12} | "
            f"Score: {row['final_score']:5.1f} | "
            f"{status}"
        )

    correct = sum(
        1
        for row in results
        if row["expected"] == row["predicted"]
    )

    accuracy = correct / len(results) * 100

    print("\n" + "=" * 90)
    print(
        f"Correct: {correct}/{len(results)} "
        f"({accuracy:.1f}%)"
    )

    with open(
        "calibration_results.csv",
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:

        fieldnames = [
            "id",
            "expected",
            "predicted",
            "final_score",
            "vocabulary_score",
            "grammar_score",
            "sentence_score",
            "coverage",
            "text",
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(results)

    print("\nResults saved to calibration_results.csv")


if __name__ == "__main__":
    main()