r"""
    original algorithm:
    The new encoding rules are as follows:
		ID -> Identifier -> position of the dot/dash in the Morse code/Morse code regularity
		RS -> Regular symbols 
            -> Consisting of two symbols.
            -> The number of patterns in Morse code represented by each character and regular expression
		/ -> space in the final encoded output
		ID\ID\..\ID%RS/ID\ID\..\ID%RS/...

	Perform the following operation on each word:
	  1. Convert spaces to '\'
   
      2. If the length of a Morse code is less than or equal to 2, keep it unchanged.

      3. Calculate the length of each Morse code
      For example, 'A' is '.-' which has a length of 2, and 'B' is '-...' which has a length of 4.
      
      If there are at least two consecutive Morse codes of length X.
        count the number of dots and dashes in each Morse code. 
        If the number of dashes is greater than the number of dots, mark it as 1
      	if the number of dots is greater than the number of dashes, mark it as 0
        If the number of dashes and dots is equal, mark it as 1 by default
       
       	Then compare the number of 1 and 0.
        If the number of 1 is greater than the number of 0, mark it as '-'
        if the number of 0 is greater than the number of 1, mark it as '.'
        
      According to the results above. 
        RS = "X-" or "X."
        
      3. Replace Morse code with position numbers according to second character of RS.
        If the second character of RS is '-', Replace Morse code with . in the position of it.
        If the second character of RS is '.', Replace Morse code with - in the position of it.
        If the quantity of the target symbol is 0, then replace it directly with N
        If Morse code is regular, Replace Morse code with +/-.
        Regular means the whole Morse code alternates from start to end with no adjacent repeated symbol.
            + -> like -.-.
            - -> like .-.-
      
      4. Add RS to the new code and separate it with %
      
    For example,
        "QC" is converted to "--.- -.-.".After the first step becomes "--.-\-.-." which has lengths of 4 and 4.
        
        For "--.-", there are 3 dashes and 1 dot, so it is marked as 1
    
        For "-.-.", there are 2 dashes and 2 dots, so it is marked as 1
            But we found that it fits the above + law, so it is marked +
        
        Since there are more 1s than 0s, RS is marked as '4-'.
        
        Because the second digit of RS is dash, the position of dot is recorded and replaced with dot position
        "--.-" is converted to "3" and "-.-." is converted to "+", then the final code is "3\+%4-"
"""

from functools import lru_cache


RS_TOKEN_TO_TEXT = {
    "A": "1-",
    "B": "1.",
    "C": "2-",
    "D": "2.",
    "E": "3-",
    "F": "3.",
    "G": "4-",
    "H": "4.",
    "I": "5-",
    "J": "5.",
    "K": "6-",
    "L": "6.",
    "M": "7-",
    "N": "7.",
}
RS_TEXT_TO_TOKEN = {value: key for key, value in RS_TOKEN_TO_TEXT.items()}
ID_TOKEN_ALPHABET = "abcdefghijklmnopqrstuvwxyz!#$&'()*?;"
ID_TEXT_SEQUENCE = (
    "",
    "+",
    "-",
    "1",
    "2",
    "3",
    "4",
    "5",
    "12",
    "14",
    "15",
    "16",
    "23",
    "24",
    "25",
    "34",
    "45",
    "47",
    "123",
    "124",
    "125",
    "134",
    "146",
    "234",
    "235",
    "345",
    "346",
    "456",
    "1234",
    "1256",
    "1345",
    "1346",
    "1356",
    "2345",
    "12345",
    "12356",
)
ID_TEXT_TO_TOKEN = {
    text: ID_TOKEN_ALPHABET[index] for index, text in enumerate(ID_TEXT_SEQUENCE)
}
ID_TOKEN_TO_TEXT = {value: key for key, value in ID_TEXT_TO_TOKEN.items()}


@lru_cache(maxsize=128)
def is_regular(code: str) -> str | None:
    if len(code) < 2:
        return None
    if any(code[i] == code[i - 1] for i in range(1, len(code))):
        return None
    return "+" if code[0] == "-" else "-"


@lru_cache(maxsize=128)
def build_position_ids(code: str) -> tuple[str, str]:
    mark = is_regular(code)
    if mark is not None:
        return mark, mark

    dot_positions: list[str] = []
    dash_positions: list[str] = []

    for index, ch in enumerate(code, start=1):
        if ch == ".":
            dot_positions.append(str(index))
        else:
            dash_positions.append(str(index))

    return "".join(dot_positions), "".join(dash_positions)


def pick_shorter_encoding(
    dash_segment: str,
    dot_segment: str,
    dash_suffix: str,
    dot_suffix: str,
) -> str:
    dash_encoded = dash_segment + dash_suffix
    dot_encoded = dot_segment + dot_suffix
    return min((dash_encoded, dot_encoded), key=lambda item: (len(item), item))


@lru_cache(maxsize=32768)
def optimize_same_length_run(codes: tuple[str, ...]) -> tuple[str, ...]:
    run_size = len(codes)
    if run_size == 0:
        return ()

    code_length = len(codes[0])

    ids_with_dash_rs: list[str] = []
    ids_with_dot_rs: list[str] = []
    dash_tokens: list[str] = []
    dot_tokens: list[str] = []
    for code in codes:
        dot_positions, dash_positions = build_position_ids(code)
        ids_with_dash_rs.append(dot_positions)
        ids_with_dot_rs.append(dash_positions)
        dash_tokens.append(ID_TEXT_TO_TOKEN[dot_positions])
        dot_tokens.append(ID_TEXT_TO_TOKEN[dash_positions])

    dash_suffix = RS_TEXT_TO_TOKEN[f"{code_length}-"]
    dot_suffix = RS_TEXT_TO_TOKEN[f"{code_length}."]
    best_cost = [0] * (run_size + 1)
    best_choice_end = [run_size] * run_size
    best_choice_segment = [""] * run_size

    # Dynamic programming picks the shortest mix of raw codes and encoded segments.
    for start in range(run_size - 1, -1, -1):
        raw_segment = codes[start]
        raw_cost = code_length + (1 if start + 1 < run_size else 0) + best_cost[start + 1]
        best_cost[start] = raw_cost
        best_choice_end[start] = start + 1
        best_choice_segment[start] = raw_segment

        dash_segment = dash_tokens[start]
        dot_segment = dot_tokens[start]
        raw_length = code_length

        for end in range(start + 2, run_size + 1):
            dash_segment += dash_tokens[end - 1]
            dot_segment += dot_tokens[end - 1]
            raw_length += 1 + code_length

            encoded_segment = pick_shorter_encoding(
                dash_segment,
                dot_segment,
                dash_suffix,
                dot_suffix,
            )
            if len(encoded_segment) >= raw_length:
                continue

            candidate_cost = len(encoded_segment) + (1 if end < run_size else 0) + best_cost[end]
            if candidate_cost < best_cost[start]:
                best_cost[start] = candidate_cost
                best_choice_end[start] = end
                best_choice_segment[start] = encoded_segment

    segments: list[str] = []
    index = 0
    while index < run_size:
        segments.append(best_choice_segment[index])
        index = best_choice_end[index]
    return tuple(segments)


def text_to_morseSimplify(text: str) -> str:
    r"""
    Convert Morse code to simplified output.
    
    The new encoding rules are as follows:
		ID -> Identifier -> position of the dot/dash in the Morse code/Morse code regularity
		RS -> Regular symbols 
            -> Consisting of two symbols.
            -> The number of patterns in Morse code represented by each character and regular expression
		/ -> space
        | -> separator between groups inside one word
        Any same-length run may be simplified if the encoded form is shorter.
        The simplified encoding is enabled only when there are at least two consecutive Morse codes with the same length.
		ID\ID\..\ID%RS|ID\ID\..\ID%RS/... 

    Optimization #1:
        For each same-length run inside a word, search for the shortest
        reversible representation instead of encoding the whole run only once.
        This keeps the decoder format unchanged while improving compression.

    Optimization #2:
        Cache repeated same-length runs and build candidate subsegments
        incrementally inside the dynamic program. This keeps the output
        unchanged while reducing repeated work.

    Optimization #3:
        Allow length-1 and length-2 same-length runs to participate in the
        same shortest-representation search. Short runs still fall back to
        raw Morse when compression is not profitable.

    Optimization #4:
        Replace the verbose `%<length><tail>` RS suffix with a single token
        character. The decoder keeps backward compatibility with the older
        suffix format.

    Optimization #5:
        Replace the high-frequency identifier strings with single-character
        tokens and omit intra-group backslash separators in the compact form.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a str")

    text = text.strip()
    if not text:
        return ""

    words: list[str] = []
    for word in text.split("/"):
        codes = [code for code in word.strip().split() if code]
        if not codes:
            continue

        segments: list[str] = []
        current = [codes[0]]
        for code in codes[1:]:
            if len(code) == len(current[-1]):
                current.append(code)
            else:
                segments.extend(optimize_same_length_run(tuple(current)))
                current = [code]
        segments.extend(optimize_same_length_run(tuple(current)))
        words.append("|".join(segments))

    return "/".join(words)
