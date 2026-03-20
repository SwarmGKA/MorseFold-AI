from __future__ import annotations

from main import MORSE_CODE


REVERSE_MORSE_CODE = {value: key for key, value in MORSE_CODE.items()}


def simplified_to_morse(text: str) -> str:
    """Decode simplified Morse output back to standard Morse code.

    Note:
    - "/" is treated as a word separator.
    - "|" is treated as an intra-word group separator.
    - This decoder restores the Morse letters and word boundaries.
    """

    if not isinstance(text, str):
        raise TypeError("text must be a str")

    text = text.strip()
    if not text:
        return ""

    def alternating_code(length: int, first: str) -> str:
        chars: list[str] = []
        current = first
        for _ in range(length):
            chars.append(current)
            current = "-" if current == "." else "."
        return "".join(chars)

    def decode_identifier(identifier: str, length: int, rs_tail: str) -> str:
        if identifier == "+":
            return alternating_code(length, "-")
        if identifier == "-":
            return alternating_code(length, ".")

        target = "." if rs_tail == "-" else "-"
        other = "-" if target == "." else "."
        code = [other] * length

        if identifier in {"", "N"}:
            return "".join(code)

        for ch in identifier:
            if not ch.isdigit():
                raise ValueError(f"invalid identifier: {identifier!r}")
            pos = int(ch)
            if pos < 1 or pos > length:
                raise ValueError(f"identifier out of range: {identifier!r}")
            code[pos - 1] = target

        return "".join(code)

    decoded_words: list[str] = []
    for word in text.split("/"):
        word = word.strip()
        if not word:
            continue

        decoded_codes: list[str] = []
        for segment in word.split("|"):
            segment = segment.strip()
            if not segment:
                continue

            if "%" not in segment:
                decoded_codes.extend(part for part in segment.split("\\") if part)
                continue

            ids_part, rs = segment.rsplit("%", 1)
            if len(rs) < 2 or rs[-1] not in ".-":
                raise ValueError(f"invalid RS: {rs!r}")

            length_text = rs[:-1]
            if not length_text.isdigit():
                raise ValueError(f"invalid Morse length: {rs!r}")

            length = int(length_text)
            rs_tail = rs[-1]
            identifiers = ids_part.split("\\")
            decoded_codes.extend(
                decode_identifier(identifier, length, rs_tail)
                for identifier in identifiers
            )

        if decoded_codes:
            decoded_words.append(" ".join(decoded_codes))

    return " / ".join(decoded_words)


def morse_to_text(text: str) -> str:
    """Decode standard Morse code to plain text.

    Note:
    - Morse letters must be separated by spaces.
    - "/" is treated as a word separator when present in the Morse input.
    """

    if not isinstance(text, str):
        raise TypeError("text must be a str")

    text = text.strip()
    if not text:
        return ""

    words: list[str] = []
    for word in text.split(" / "):
        letters: list[str] = []
        for code in word.split():
            letter = REVERSE_MORSE_CODE.get(code)
            if letter is None:
                raise ValueError(f"unsupported Morse code: {code!r}")
            letters.append(letter)
        if letters:
            words.append("".join(letters))

    return " ".join(words)


def simplified_to_text(text: str) -> str:
    """Decode simplified Morse output to plain text.

    Note:
    - Characters and word boundaries are restored from the current encoder format.
    """

    return morse_to_text(simplified_to_morse(text))


def main() -> None:
    text = input("请输入要解码的简化代码: ").strip()
    try:
        morse = simplified_to_morse(text)
        plain_text = simplified_to_text(text)
    except (TypeError, ValueError) as exc:
        print(f"解码失败: {exc}")
        return

    print(f"Decoded Morse Code: {morse}")
    print(f"Decoded Text: {plain_text}")


if __name__ == "__main__":
    main()
