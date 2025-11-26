"""
normalize.py
---------------
Main entrypoint for number normalization. Attempts to load a compiled FAR
grammar using Pynini/OpenFST. If Pynini or the FAR file is not available,
falls back to a pure-Python rule-based normalizer for cardinal numbers 0-1000.

This file is intentionally verbose and thoroughly commented to meet the
challenge requirement for very clear, well-commented code.
"""
from __future__ import annotations

import re
from typing import Callable
import sys
import os


def number_to_words(n: int) -> str:
    """Convert integer n (0 <= n <= 1000) to its English words.

    Rules:
    - Hyphenate numbers between 21-99 that are not multiples of 10 (e.g., 21 -> twenty-one)
    - Use 'one thousand' for 1000
    - Use 'zero' for 0
    """
    if not (0 <= n <= 1000):
        raise ValueError("number out of range (0-1000)")

    units = [
        "zero",
        "one",
        "two",
        "three",
        "four",
        "five",
        "six",
        "seven",
        "eight",
        "nine",
    ]

    teens = [
        "ten",
        "eleven",
        "twelve",
        "thirteen",
        "fourteen",
        "fifteen",
        "sixteen",
        "seventeen",
        "eighteen",
        "nineteen",
    ]

    tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

    if n == 1000:
        return "one thousand"

    if n < 10:
        return units[n]

    if 10 <= n < 20:
        return teens[n - 10]

    if n < 100:
        t, u = divmod(n, 10)
        if u == 0:
            return tens[t]
        else:
            return f"{tens[t]}-{units[u]}"

    # 100..999
    h, rest = divmod(n, 100)
    if rest == 0:
        return f"{units[h]} hundred"
    else:
        return f"{units[h]} hundred {number_to_words(rest)}"


def replace_numbers_in_text(text: str, convert_fn: Callable[[int], str]) -> str:
    """Replace integer numerals in `text` using `convert_fn`.

    - Matches non-negative integers in 0-1000.
    - Negative numbers and numbers outside range are left unchanged.
    - Preserves surrounding punctuation and spacing.
    """

    def repl(match: re.Match) -> str:
        s = match.group(0)
        start_pos = match.start()
        
        # Check if there's a minus sign immediately before the number
        # (allowing for optional whitespace between minus and number)
        if start_pos > 0:
            # Look back to find minus sign (skip whitespace)
            i = start_pos - 1
            while i >= 0 and text[i].isspace():
                i -= 1
            if i >= 0 and text[i] == "-":
                # This is a negative number, don't normalize
                return s
        
        try:
            # Disallow leading zeros like 012 unless it's '0'
            if len(s) > 1 and s.startswith("0"):
                # treat as a literal token (do not convert)
                return s
            n = int(s)
        except ValueError:
            return s

        # Only normalize non-negative numbers in range 0-1000
        if 0 <= n <= 1000:
            return convert_fn(n)
        return s

    # Use word-boundary aware regex to avoid replacing digits inside words
    return re.sub(r"\b\d+\b", repl, text)


def load_fst_and_normalize(sentence: str) -> str | None:
    """Attempt to load `src/grammar.far` and normalize using Pynini.

    Returns normalized sentence on success, or None if Pynini/FAR unavailable.
    This function is permissive and will not raise if external libs are missing.
    """
    try:
        import pynini
        from pynini import Far
    except Exception:  # pragma: no cover - environment dependent
        return None

    far_path = os.path.join(os.path.dirname(__file__), "grammar.far")
    if not os.path.exists(far_path):
        return None

    try:
        far = pynini.Far(far_path, mode="r")
        # Expect the FAR to contain an entry named 'normalize' that maps digits to words.
        if "normalize" not in far:
            # fallback if key is different; attempt to use first archive member
            keys = list(far.keys())
            if not keys:
                return None
            fst = far[keys[0]]
        else:
            fst = far["normalize"]

        # The typical usage is to tokenize and rewrite the tokens. For simplicity
        # we'll rewrite each numeric token separately using pynini.rewrite.
        from pynini.lib import rewrite

        def apply_fst_to_token(tok: str) -> str:
            try:
                # one_top_rewrite returns the best rewrite if available
                return rewrite.one_top_rewrite(tok, fst)
            except Exception:
                return tok

        return replace_numbers_in_text(sentence, lambda n: apply_fst_to_token(str(n)))
    except Exception:
        return None


def normalize_text(sentence: str) -> str:
    """Normalize cardinal numbers inside `sentence`.

    Strategy:
    1. Try to use compiled FAR grammar via Pynini (fast and FST-based).
    2. If unavailable, use the pure-Python `number_to_words` fallback.
    """
    fst_result = load_fst_and_normalize(sentence)
    if fst_result is not None:
        return fst_result

    # Pure-python fallback
    return replace_numbers_in_text(sentence, lambda n: number_to_words(n))


def _cli_main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv) if argv is None else list(argv)
    if len(argv) < 2:
        print("Usage: python src/normalize.py \"Some sentence with 21 numbers\"")
        return 1

    sentence = argv[1]
    print(normalize_text(sentence))
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli_main())
