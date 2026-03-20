from __future__ import annotations

import sys
from pathlib import Path



ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from encoder import text_to_morseSimplify
from main import text_to_morse

DATASET_PATH = ROOT_DIR / "datasets" / "base" / "standard_samples.txt"


def load_dataset(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    return [line.strip() for line in lines if line.strip()]


def format_ratio(value: float) -> str:
    return f"{value:.2%}"


def main() -> None:
    samples = load_dataset(DATASET_PATH)
    total_morse_len = 0
    total_simplified_len = 0

    print("Text | Morse Len | Simplified Len | Character Reduction | Compression Ratio")
    print("-" * 78)

    for text in samples:
        morse = text_to_morse(text, word_sep=" / ")
        simplified = text_to_morseSimplify(morse)
        morse_len = len(morse)
        simplified_len = len(simplified)
        reduction = morse_len - simplified_len
        ratio = simplified_len / morse_len if morse_len else 0.0

        total_morse_len += morse_len
        total_simplified_len += simplified_len

        print(
            f"{text} | {morse_len} | {simplified_len} | "
            f"{reduction} | {format_ratio(ratio)}"
        )

    total_reduction = total_morse_len - total_simplified_len
    total_ratio = total_simplified_len / total_morse_len if total_morse_len else 0.0

    print(f"{'-' * 78}")
    print(f"Samples: {len(samples)}")
    print(f"Total Morse Length: {total_morse_len}")
    print(f"Total Simplified Length: {total_simplified_len}")
    print(f"Total Character Reduction: {total_reduction}")
    print(f"Overall Compression Ratio: {format_ratio(total_ratio)}")


if __name__ == "__main__":
    main()

