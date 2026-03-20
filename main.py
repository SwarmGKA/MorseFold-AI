"""Morse code generator (text -> morse).

Usage:
  - Run and follow the prompt, then it prints Morse code.

Output format:
  - Letters are separated by a single space.
  - Words are separated by " / ".
"""

from __future__ import annotations
from encoder import text_to_morseSimplify


MORSE_CODE: dict[str, str] = {
	"A": ".-",
	"B": "-...",
	"C": "-.-.",
	"D": "-..",
	"E": ".",
	"F": "..-.",
	"G": "--.",
	"H": "....",
	"I": "..",
	"J": ".---",
	"K": "-.-",
	"L": ".-..",
	"M": "--",
	"N": "-.",
	"O": "---",
	"P": ".--.",
	"Q": "--.-",
	"R": ".-.",
	"S": "...",
	"T": "-",
	"U": "..-",
	"V": "...-",
	"W": ".--",
	"X": "-..-",
	"Y": "-.--",
	"Z": "--..",
	"0": "-----",
	"1": ".----",
	"2": "..---",
	"3": "...--",
	"4": "....-",
	"5": ".....",
	"6": "-....",
	"7": "--...",
	"8": "---..",
	"9": "----.",
	".": ".-.-.-",
	",": "--..--",
	"?": "..--..",
	"'": ".----.",
	"!": "-.-.--",
	"/": "-..-.",
	"(": "-.--.",
	")": "-.--.-",
	"&": ".-...",
	":": "---...",
	";": "-.-.-.",
	"=": "-...-",
	"+": ".-.-.",
	"-": "-....-",
	"_": "..--.-",
	'"': ".-..-.",
	"$": "...-..-",
	"@": ".--.-.",
}


def text_to_morse(text: str, *, letter_sep: str = " ", word_sep: str = " / ") -> str:
	"""Convert plain text to Morse code.

	- Collapses any whitespace into word boundaries.
	- Raises ValueError if any character is not supported.
	"""

	if not isinstance(text, str):
		raise TypeError("text must be a str")

	text = text.strip()
	if not text:
		return ""

	words = text.split()
	encoded_words: list[str] = []
	for word in words:
		letters: list[str] = []
		for ch in word:
			key = ch.upper()
			code = MORSE_CODE.get(key)
			if code is None:
				raise ValueError(
					f"Unsupported character: {ch!r} (U+{ord(ch):04X}). "
					"Only English letters, digits, and common English punctuation are supported."
				)
			letters.append(code)
		encoded_words.append(letter_sep.join(letters))
	return word_sep.join(encoded_words)


def main() -> None:
	text = input("Enter the text to convert: ").strip()
	try:
		morse = text_to_morse(text)
		new_code = text_to_morseSimplify(morse)
	except (TypeError, ValueError) as exc:
		print(f"Conversion failed: {exc}")
		return

	print(f"Morse Code: {morse}")
	print(f"Simplified Code: {new_code}")
	print(f"Length: Morse: {len(morse)}, Simplified Code: {len(new_code)}")
	print(f"Character reduction: {len(morse) - len(new_code)} characters")
	print(f"Compression Ratio: {len(new_code) / len(morse):.2%}")

if __name__ == "__main__":
	main()
