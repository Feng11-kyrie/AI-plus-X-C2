#!/usr/bin/env python3
"""Cross-task analysis over one or more runs of run_experiment.py.

Produces the two tables the paper needs:

  1. a per-task table of a / nu / kappa / alpha,
  2. a *paired* table that isolates the reduction bottleneck.

The paired measure is the one that matters.  A low nu can mean two different
things -- the problem is hard, or the model can solve it but cannot express the
solution in a checkable form.  These are not distinguishable from nu alone.
Restricting the IR condition to the subset of problems the *baseline* already
answered correctly removes task difficulty as an explanation: on that subset
the model demonstrably knows the answer, so any remaining failure to produce a
well-formed IR is a reduction failure and nothing else.

    nu | baseline-correct   =   fraction of IR outputs that are verifiable,
                                computed only over problems whose baseline
                                answer was correct

Usage
-----
    python3 analyze.py results/<run1> results/<run2> ...
    python3 analyze.py --raw results/<run1>/raw.jsonl:gsm8k results/<run2>/raw.jsonl:MATH-Pre
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_raw(path):
    rows = [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]
    if rows and "cond" in rows[0]:
        base = [r for r in rows if r["cond"] == "baseline"]
        ir = [r for r in rows if r["cond"] == "ir"]
    else:                      # runs recorded before the cond field existed
        half = len(rows) // 2
        base, ir = rows[:half], rows[half:]
    return base, ir


def rate(rows, key):
    return (sum(bool(r.get(key)) for r in rows) / len(rows)) if rows else float("nan")


def task_stats(base, ir):
    n = len(ir)
    ver = [r for r in ir if r.get("verifiable") and r.get("verified")]
    kappa = (sum(bool(r.get("consistent")) for r in ver) / len(ver)) if ver else float("nan")
    alpha = (sum(bool(r.get("verifiable")) and bool(r.get("verified"))
                 and bool(r.get("consistent")) and bool(r.get("correct"))
                 for r in ir) / n) if n else float("nan")
    return {
        "n": n,
        "a_base": rate(base, "correct"),
        "a_ir": rate(ir, "correct"),
        "nu": rate(ir, "verifiable"),
        "kappa": kappa,
        "alpha": alpha,
    }


def paired(base, ir):
    """Restrict both conditions to problems the baseline got right."""
    bmap = {r["i"]: bool(r.get("correct")) for r in base}
    keep = [r for r in ir if bmap.get(r["i"])]
    if not keep:
        return {"n_solved": 0}
    return {
        "n_solved": len(keep),
        "nu_given_solved": rate(keep, "verifiable"),
        "a_ir_given_solved": rate(keep, "correct"),
        "alpha_given_solved": (
            sum(bool(r.get("verifiable")) and bool(r.get("verified"))
                and bool(r.get("consistent")) and bool(r.get("correct"))
                for r in keep) / len(keep)),
    }


def fail_classes(ir):
    """Aggregate failure reasons into the A/T/R/N taxonomy of Section 4.

    Two distinct things are counted here and must not be conflated:
      *parse* failures (the output never became a checkable object, so
      verifiable is False), and *post-parse* failures (the object parsed but
      either would not evaluate or its goal disagreed with its own answer).
    Both are reduction failures; only the first lowers nu.
    """
    parse_c, post_c = Counter(), Counter()
    for r in ir:
        f = r.get("fail")
        if not f:
            continue
        m = re.match(r"([ATRN]):", str(f))
        cls = m.group(1) if m else "other"
        (parse_c if not r.get("verifiable") else post_c)[cls] += 1
    return parse_c, post_c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("specs", nargs="+", metavar="LABEL=PATH",
                    help="e.g. GSM8K=results/20260926-170715/raw.jsonl  "
                         "(a bare path uses the parent directory as label)")
    args = ap.parse_args()

    items = []
    for spec in args.specs:
        if "=" in spec:
            label, _, p = spec.partition("=")
        else:
            p, label = spec, None
        path = Path(p)
        if path.is_dir():
            path = path / "raw.jsonl"
        items.append((label or path.parent.name, path))
    if not items:
        sys.exit("give at least one LABEL=PATH")

    print("\n== per-task ==\n")
    print("| task | n | a_base | a_ir | nu | kappa | alpha |")
    print("|---|---|---|---|---|---|---|")
    tex_rows, paired_rows = [], []
    for label, p in items:
        base, ir = load_raw(p)
        s = task_stats(base, ir)
        print(f"| {label} | {s['n']} | {s['a_base']:.3f} | {s['a_ir']:.3f} | "
              f"{s['nu']:.3f} | {s['kappa']:.3f} | {s['alpha']:.3f} |")
        tex_rows.append(f"{label} & {s['n']} & {s['a_base']:.3f} & {s['a_ir']:.3f} & "
                        f"{s['nu']:.3f} & {s['kappa']:.3f} & {s['alpha']:.3f} \\\\")
        paired_rows.append((label, s, paired(base, ir), fail_classes(ir)))

    print("\n== paired: restricted to problems the baseline solved ==\n")
    print("| task | n_solved | nu\\|solved | a_ir\\|solved | alpha\\|solved |")
    print("|---|---|---|---|---|")
    tex_paired = []
    for label, s, pr, _ in paired_rows:
        if not pr.get("n_solved"):
            continue
        print(f"| {label} | {pr['n_solved']} | {pr['nu_given_solved']:.3f} | "
              f"{pr['a_ir_given_solved']:.3f} | {pr['alpha_given_solved']:.3f} |")
        tex_paired.append(
            f"{label} & {pr['n_solved']} & {pr['nu_given_solved']:.3f} & "
            f"{pr['a_ir_given_solved']:.3f} & {pr['alpha_given_solved']:.3f} \\\\")

    print("\n== IR failure classes (Section 4 taxonomy) ==\n")
    print("   parse-fail = never became a checkable object (lowers nu)")
    print("   post-parse = parsed but unevaluable, or goal != own answer\n")
    for label, s, pr, fc in paired_rows:
        pc, qc = fc
        print(f"{label}: parse-fail={sum(pc.values())}/{s['n']} "
              + (", ".join(f"{k}={v}" for k, v in sorted(pc.items())) or "none"))
        print(f"{' ' * len(label)}  post-parse={sum(qc.values())}/{s['n']} "
              + (", ".join(f"{k}={v}" for k, v in sorted(qc.items())) or "none"))

    out = ROOT / "results" / "cross_task.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        "| task | n | a_base | a_ir | nu | kappa | alpha |\n|---|---|---|---|---|---|---|\n"
        + "\n".join(tex_rows) + "\n\n"
        + "| task | n_solved | nu|solved | a_ir|solved | alpha|solved |\n"
          "|---|---|---|---|---|\n"
        + "\n".join(tex_paired) + "\n"
    )
    (ROOT / "results" / "cross_task.tex").write_text("\n".join(tex_rows) + "\n\n%\n"
                                                     + "\n".join(tex_paired) + "\n")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
