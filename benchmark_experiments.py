from __future__ import annotations

import csv
from pathlib import Path

from encoder import text_to_morseSimplify
from main import text_to_morse


DATASETS_DIR = Path(__file__).with_name("datasets")
OUTPUT_DIR = Path(__file__).with_name("output")
BASE_DATASET_PATH = DATASETS_DIR / "base" / "standard_samples.txt"
LONG_DATASET_PATH = DATASETS_DIR / "long" / "long_sentence_samples.txt"
PARAGRAPH_DATASET_PATH = DATASETS_DIR / "paragraph" / "paragraph_samples.txt"
GROUP_SUMMARY_CSV_PATH = OUTPUT_DIR / "experiment_group_summary.csv"
SAMPLE_DETAILS_CSV_PATH = OUTPUT_DIR / "experiment_sample_details.csv"


def load_dataset(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    return [line.strip() for line in lines if line.strip()]


def format_ratio(value: float) -> str:
    return f"{value:.2%}"


def sample_metrics(text: str) -> dict[str, object]:
    morse = text_to_morse(text)
    simplified = text_to_morseSimplify(morse)
    morse_len = len(morse)
    simplified_len = len(simplified)
    reduction = morse_len - simplified_len
    ratio = simplified_len / morse_len if morse_len else 0.0
    word_count = len(text.split())
    return {
        "text": text,
        "word_count": word_count,
        "morse_len": morse_len,
        "simplified_len": simplified_len,
        "reduction": reduction,
        "ratio": ratio,
    }


def contains_digit(text: str) -> bool:
    return any(ch.isdigit() for ch in text)


def contains_punctuation(text: str) -> bool:
    return any(not ch.isalnum() and not ch.isspace() for ch in text)


def select_samples(samples: list[str], predicate) -> list[str]:
    return [sample for sample in samples if predicate(sample)]


def print_group_report(name: str, samples: list[str]) -> None:
    print(f"[{name}]")
    if not samples:
        print("Samples: 0")
        print()
        return

    metrics = [sample_metrics(sample) for sample in samples]
    total_morse_len = sum(item["morse_len"] for item in metrics)
    total_simplified_len = sum(item["simplified_len"] for item in metrics)
    total_reduction = total_morse_len - total_simplified_len
    total_ratio = total_simplified_len / total_morse_len if total_morse_len else 0.0
    avg_reduction = total_reduction / len(metrics)

    best = max(metrics, key=lambda item: item["reduction"])
    worst = min(metrics, key=lambda item: item["reduction"])

    print(f"Samples: {len(metrics)}")
    print(f"Total Morse Length: {total_morse_len}")
    print(f"Total Simplified Length: {total_simplified_len}")
    print(f"Total Character Reduction: {total_reduction}")
    print(f"Average Character Reduction: {avg_reduction:.2f}")
    print(f"Overall Compression Ratio: {format_ratio(total_ratio)}")
    print(
        f"Best Sample: {best['text']} | reduction={best['reduction']} | "
        f"ratio={format_ratio(best['ratio'])}"
    )
    print(
        f"Worst Sample: {worst['text']} | reduction={worst['reduction']} | "
        f"ratio={format_ratio(worst['ratio'])}"
    )
    print()


def build_group_summary(name: str, samples: list[str]) -> dict[str, object]:
    if not samples:
        return {
            "group": name,
            "samples": 0,
            "total_morse_length": 0,
            "total_simplified_length": 0,
            "total_character_reduction": 0,
            "average_character_reduction": 0.0,
            "overall_compression_ratio": 0.0,
            "best_sample": "",
            "best_reduction": 0,
            "best_ratio": 0.0,
            "worst_sample": "",
            "worst_reduction": 0,
            "worst_ratio": 0.0,
        }

    metrics = [sample_metrics(sample) for sample in samples]
    total_morse_len = sum(item["morse_len"] for item in metrics)
    total_simplified_len = sum(item["simplified_len"] for item in metrics)
    total_reduction = total_morse_len - total_simplified_len
    total_ratio = total_simplified_len / total_morse_len if total_morse_len else 0.0
    avg_reduction = total_reduction / len(metrics)
    best = max(metrics, key=lambda item: item["reduction"])
    worst = min(metrics, key=lambda item: item["reduction"])

    return {
        "group": name,
        "samples": len(metrics),
        "total_morse_length": total_morse_len,
        "total_simplified_length": total_simplified_len,
        "total_character_reduction": total_reduction,
        "average_character_reduction": avg_reduction,
        "overall_compression_ratio": total_ratio,
        "best_sample": best["text"],
        "best_reduction": best["reduction"],
        "best_ratio": best["ratio"],
        "worst_sample": worst["text"],
        "worst_reduction": worst["reduction"],
        "worst_ratio": worst["ratio"],
    }


def write_group_summary_csv(rows: list[dict[str, object]]) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    with GROUP_SUMMARY_CSV_PATH.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "group",
                "samples",
                "total_morse_length",
                "total_simplified_length",
                "total_character_reduction",
                "average_character_reduction",
                "overall_compression_ratio",
                "best_sample",
                "best_reduction",
                "best_ratio",
                "worst_sample",
                "worst_reduction",
                "worst_ratio",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def write_sample_details_csv(groups: list[tuple[str, list[str]]]) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    with SAMPLE_DETAILS_CSV_PATH.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "group",
                "text",
                "word_count",
                "morse_length",
                "simplified_length",
                "character_reduction",
                "compression_ratio",
            ],
        )
        writer.writeheader()
        for group_name, samples in groups:
            for sample in samples:
                metrics = sample_metrics(sample)
                writer.writerow(
                    {
                        "group": group_name,
                        "text": metrics["text"],
                        "word_count": metrics["word_count"],
                        "morse_length": metrics["morse_len"],
                        "simplified_length": metrics["simplified_len"],
                        "character_reduction": metrics["reduction"],
                        "compression_ratio": metrics["ratio"],
                    }
                )


def main() -> None:
    base_samples = load_dataset(BASE_DATASET_PATH)
    long_samples = load_dataset(LONG_DATASET_PATH)
    paragraph_samples = load_dataset(PARAGRAPH_DATASET_PATH)

    experiment_groups = [
        ("single_word", select_samples(base_samples, lambda s: len(s.split()) == 1)),
        ("multi_word_phrase", select_samples(base_samples, lambda s: 2 <= len(s.split()) <= 5)),
        ("number_heavy", select_samples(base_samples, contains_digit)),
        ("punctuation_heavy", select_samples(base_samples, contains_punctuation)),
        (
            "mixed_digits_punctuation",
            select_samples(base_samples, lambda s: contains_digit(s) and contains_punctuation(s)),
        ),
        ("long_sentence_gt20_words", long_samples),
        ("paragraph_samples", paragraph_samples),
    ]

    group_rows: list[dict[str, object]] = []
    for name, samples in experiment_groups:
        print_group_report(name, samples)
        group_rows.append(build_group_summary(name, samples))

    write_group_summary_csv(group_rows)
    write_sample_details_csv(experiment_groups)
    print(f"CSV written: {GROUP_SUMMARY_CSV_PATH}")
    print(f"CSV written: {SAMPLE_DETAILS_CSV_PATH}")


if __name__ == "__main__":
    main()
