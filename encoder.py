r"""
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
        Morse codes with length less than or equal to 2 are kept unchanged.
        The simplified encoding is enabled only when there are at least two consecutive Morse codes with the same length.
		ID\ID\..\ID%RS|ID\ID\..\ID%RS/... 
    """
    if not isinstance(text, str):
        raise TypeError("text must be a str")

    text = text.strip()
    if not text:
        return ""

    def is_regular(code: str) -> str | None:
        if len(code) < 2:
            return None
        if any(code[i] == code[i - 1] for i in range(1, len(code))):
            return None
        return "+" if code[0] == "-" else "-"

    def encode_group(codes: list[str]) -> str:
        length = len(codes[0])
        if length <= 2:
            return "\\".join(codes)
        if len(codes) < 2:
            return "\\".join(codes)

        flags: list[int] = []
        regular_marks: dict[str, str] = {}

        for code in codes:
            mark = is_regular(code)
            if mark is not None:
                regular_marks[code] = mark
                flags.append(1)
                continue
            dots = code.count(".")
            dashes = code.count("-")
            flags.append(1 if dashes >= dots else 0)

        rs_tail = "-" if flags.count(1) >= flags.count(0) else "."
        target = "." if rs_tail == "-" else "-"
        ids: list[str] = []

        for code in codes:
            mark = regular_marks.get(code)
            if mark is not None:
                ids.append(mark)
                continue
            positions = [str(i) for i, ch in enumerate(code, start=1) if ch == target]
            ids.append("".join(positions) or "")

        return "\\".join(ids) + f"%{length}{rs_tail}"

    words: list[str] = []
    for word in text.split(" / "):
        codes = [code for code in word.split() if code]
        if not codes:
            continue

        groups: list[list[str]] = []
        current = [codes[0]]
        for code in codes[1:]:
            if len(code) == len(current[-1]):
                current.append(code)
            else:
                groups.append(current)
                current = [code]
        groups.append(current)
        words.append("|".join(encode_group(group) for group in groups))

    return "/".join(words)
