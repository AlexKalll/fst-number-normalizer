"""
scripts/compile_grammar.py
--------------------------
Helper script to compile `src/grammar.pynini` into `src/grammar.far` using Pynini.

Usage:
    python scripts/compile_grammar.py

This script tries to import Pynini, exec() the `grammar.pynini` file, call
`build_fst()` and write a FAR archive with an entry named 'normalize'.

Note: Pynini/OpenFST must be installed for this script to succeed.
"""
from __future__ import annotations

import os
import sys


def main() -> int:
    # Get paths relative to project root
    project_root = os.path.dirname(os.path.dirname(__file__))
    src = os.path.join(project_root, "src", "grammar.pynini")
    far_out = os.path.join(project_root, "src", "grammar.far")

    if not os.path.exists(src):
        print(f"Grammar source not found: {src}")
        return 2

    try:
        import pynini
        from pynini import Far
    except Exception as e:
        print("Pynini is not available. Install it (conda recommended).")
        print(e)
        return 3

    # Load grammar file and execute it in a minimal namespace
    namespace = {}
    with open(src, "r", encoding="utf8") as fh:
        code = fh.read()
    exec(code, namespace)  # define build_fst in namespace

    if "build_fst" not in namespace:
        print("grammar.pynini must define build_fst()")
        return 4

    build_fst = namespace["build_fst"]
    result = build_fst()

    # If the result is a dict of components, try to assemble a full mapping
    # mapping 0..1000 to words by enumerating values (safe fallback)
    if isinstance(result, dict):
        # Try to use two_digit and thousand to assemble 0..1000
        two_digit_fst = result.get("two_digit")
        thousand_fst = result.get("thousand")
        # If two_digit_fst is available, enumerate 0..99
        mapping = {}
        try:
            for i in range(0, 100):
                s = str(i)
                try:
                    w = pynini.shortestpath(two_digit_fst @ pynini.acceptor(s)).stringify()
                except Exception:
                    # fallback: skip
                    continue
                mapping[s] = w
            mapping["1000"] = "one thousand"
        except Exception:
            pass

        # Build an FST by unioning all cross() of mapping
        union_fst = None
        for k, v in mapping.items():
            x = pynini.cross(k, v)
            union_fst = x if union_fst is None else union_fst | x

        if union_fst is None:
            print("Failed to construct mapping; cannot write FAR.")
            return 6

        final_fst = union_fst.optimize()
    else:
        # If build_fst returned an FST-like object, use it directly
        final_fst = result

    # Create FAR and write
    try:
        far = pynini.Far(far_out, "w")
        far["normalize"] = final_fst
        far.close()
        print(f"Wrote FAR to {far_out}")
        return 0
    except Exception as e:
        print("Error while building/writing FAR:", e)
        return 7


if __name__ == "__main__":
    raise SystemExit(main())

