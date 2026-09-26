#!/usr/bin/env python3
"""Convert MATH (Hendrycks et al., 2021) parquet subsets into the same JSONL
shape the GSM8K harness consumes.

Only problems whose boxed reference answer is a *number* are kept, because the
IR schema of the harness is arithmetic and its ``answer`` field is numeric.
The conversion is deliberately conservative: anything we cannot parse into a
float is dropped and counted, never guessed.

Usage
-----
    python3 prepare_math.py            # reads /tmp/math_*.parquet, writes data/
    python3 prepare_math.py --src DIR

Outputs: data/math_<subset>.jsonl  with fields
    question, ref, level, subject, raw_answer
"""
import argparse
import json
import re
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
SUBSETS = ["prealgebra", "number_theory"]


def find_boxed(solution):
    """Return the content of the last \\boxed{...} in the solution, or None."""
    idx = solution.rfind("\\boxed")
    if idx < 0:
        return None
    i = solution.find("{", idx)
    if i < 0:
        return None
    depth, j = 0, i
    while j < len(solution):
        if solution[j] == "{":
            depth += 1
        elif solution[j] == "}":
            depth -= 1
            if depth == 0:
                return solution[i + 1:j]
        j += 1
    return None


def to_number(s):
    """Parse a boxed LaTeX answer into a float, or None if not a plain number.

    Handles: integers, decimals, signed numbers, a/b, \\frac{a}{b}, \\dfrac,
    and a trailing percent sign.  Anything else -- matrices, intervals,
    expressions in a free variable, \\text{...} -- is rejected.
    """
    if s is None:
        return None
    t = s.strip()
    t = t.replace("\\!", "").replace("\\,", "").replace("\\;", "")
    t = t.replace("$", "").replace("\\left", "").replace("\\right", "")
    t = t.replace("\\%", "").replace("%", "")
    t = t.replace("{,}", "").replace(",", "")          # 1{,}000 -> 1000
    t = t.replace("\\dfrac", "\\frac").replace("\\tfrac", "\\frac")
    t = t.strip()
    if not t:
        return None

    # \frac{a}{b} possibly nested inside nothing else
    m = re.fullmatch(r"\\frac\{(-?[\d.]+)\}\{(-?[\d.]+)\}", t)
    if m:
        try:
            den = float(m.group(2))
            return float(m.group(1)) / den if den else None
        except ValueError:
            return None

    # bare fraction a/b
    m = re.fullmatch(r"(-?[\d.]+)\s*/\s*(-?[\d.]+)", t)
    if m:
        try:
            den = float(m.group(2))
            return float(m.group(1)) / den if den else None
        except ValueError:
            return None

    # plain number, possibly with a sign or trailing \text unit stripped already
    if re.fullmatch(r"[-+]?\d*\.?\d+", t):
        try:
            return float(t)
        except ValueError:
            return None
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="/tmp", help="directory holding math_<subset>.parquet")
    args = ap.parse_args()
    import pyarrow.parquet as pq  # imported late: only needed for conversion

    if not DATA.exists():
        DATA.mkdir(parents=True)
    for sub in SUBSETS:
        src = Path(args.src) / f"math_{sub}.parquet"
        if not src.exists():
            print(f"skip {sub}: {src} not found")
            continue
        rows = pq.read_table(src).to_pylist()
        kept, dropped = [], 0
        for r in rows:
            boxed = find_boxed(r["solution"] or "")
            val = to_number(boxed)
            if val is None:
                dropped += 1
                continue
            kept.append({
                "question": r["problem"],
                "ref": val,
                "level": r.get("level"),
                "subject": r.get("type"),
                "raw_answer": boxed,
            })
        out = DATA / f"math_{sub}.jsonl"
        out.write_text("\n".join(json.dumps(k, ensure_ascii=False) for k in kept) + "\n")
        print(f"{sub}: total={len(rows)}  numeric={len(kept)}  "
              f"dropped={dropped} ({dropped/len(rows):.1%})  -> {out}")


if __name__ == "__main__":
    main()
