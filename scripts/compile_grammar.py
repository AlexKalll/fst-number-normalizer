"""
Helper script to compile `src/grammar.pynini` into `src/grammar.far` using Pynini.
"""
from __future__ import annotations
import os

def main() -> int:
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
        print("Pynini is not available")
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

    # mapping 0..1000 to words by enumerating values
    if isinstance(result, dict):
        two_digit_fst = result.get("two_digit")
        _ = result.get("thousand")
        # If two_digit_fst is available, enumerate 0..99
        mapping = {}
        try:
            for i in range(0, 100):
                s = str(i)
                try:
                    w = pynini.shortestpath(two_digit_fst @ pynini.acceptor(s)).stringify()
                except Exception:
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
