"""Main entrypoint for number normalization. It Tries to load a compiled FAR grammar via Pynini; otherwise uses a pure-Python rule-based fallback for cardinal numbers 0–1000.
"""
from __future__ import annotations

import re
from typing import Callable
import sys
import os


def number_to_words(n: int) -> str:
    """Return English words for 0 <= n <= 1000.
    Hyphenates values like 21 -> "twenty-one" and uses "one thousand"
    for 1000.
    """
    if not (0 <= n <= 1000):
        raise ValueError("number out of range (0-1000)")

    units = [ "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine" ]

    teens = ["ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]

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
    Preserves tokens that are negative, have leading zeros, or lie outside
    the 0–1000 range.
    """

    def repl(match: re.Match) -> str:
        s = match.group(0)
        start_pos = match.start()

        # If a minus sign precedes the token (possibly with whitespace), skip it.
        if start_pos > 0:
            i = start_pos - 1
            while i >= 0 and text[i].isspace():
                i -= 1
            if i >= 0 and text[i] == "-":
                return s

        try:
            if len(s) > 1 and s.startswith("0"):
                return s
            n = int(s)
        except ValueError:
            return s

        if 0 <= n <= 1000:
            return convert_fn(n)
        return s

    return re.sub(r"\b\d+\b", repl, text)


def load_fst_and_normalize(sentence: str) -> str | None:
    """Try to normalize using a compiled FAR (`src/grammar.far`).
    Returns the normalized sentence or ``None`` when Pynini/FAR is not
    available.
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
        fst = far.get("normalize") if "normalize" in far else None
        if fst is None:
            keys = list(far.keys())
            if not keys:
                return None
            fst = far[keys[0]]

        from pynini.lib import rewrite

        def apply_fst_to_token(tok: str) -> str:
            try:
                return rewrite.one_top_rewrite(tok, fst)
            except Exception:
                return tok
        # python fallback
        return replace_numbers_in_text(sentence, lambda n: apply_fst_to_token(str(n)))
    except Exception:
        return None


def normalize_text(sentence: str) -> str:
    """
    Normalize cardinal numbers in `sentence`.It Uses the FAR-based FST when available, otherwise the Python fallback.
    """
    fst_result = load_fst_and_normalize(sentence)
    if fst_result is not None:
        return fst_result

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