#!/usr/bin/env python3
"""GSM8K reliability experiment for the semantic-reduction framework.

Measures the four quantities defined in Section 6 of the paper:

    a        accuracy          final answer matches the reference
    nu       verifiability     output yields a well-formed IR object
    kappa    consistency       the IR's rendering matches the model's own claim
    alpha    certified acc.    verifiable AND verified AND consistent

Two conditions:

    baseline  free-form chain-of-thought, answer marked with "#### <num>"
    ir        structured typed IR (JSON) that is parsed and checked locally

The local checker -- not the model -- decides nu and kappa.  That is the point:
the whole experiment is about whether a machine, not the model, can warrant
the answer.

Usage
-----
    # no key needed: verifies parsing / checking logic on 5 items
    python3 run_experiment.py --dry-run

    # real run, 200 problems, DeepSeek
    DEEPSEEK_API_KEY=sk-... python3 run_experiment.py --limit 200

    # OpenAI-compatible endpoint
    OPENAI_API_KEY=sk-... python3 run_experiment.py --base-url https://api.openai.com/v1 --model gpt-4o-mini --limit 200

Outputs: results/<run-id>/{raw.jsonl,summary.md,table.tex}
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "gsm8k_test.jsonl"
RESULTS = ROOT / "results"

BASELINE_PROMPT = """Solve the following grade-school math problem.
Think step by step, then give the final answer on its own last line in the
exact form:

#### <number>

Problem: {q}
"""

IR_PROMPT = """Solve the following grade-school math problem by emitting a typed
intermediate representation, then a final answer.

Reply with EXACTLY ONE JSON object and nothing else, with this schema:

{{"vars": [{{"name": "x", "type": "Nat|Int|Rat|Real", "unit": "<string or null>",
            "def": "<arithmetic expression in earlier vars and literals>"}}],
  "claims": ["<informal statement each var is supposed to capture>"],
  "goal": "<the quantity the problem asks for, as an expression over vars>",
  "answer": <number>}}

Rules: every var must be defined only from literals or previously declared vars;
every division must be accompanied by a "nonzero" field proving the divisor is
non-zero; "goal" must be an expression over declared vars.  No prose, no markdown
fences.

Problem: {q}
"""


# --------------------------------------------------------------------------
# data
# --------------------------------------------------------------------------
def load_problems(limit, offset=0):
    rows = [json.loads(l) for l in DATA.read_text().splitlines() if l.strip()]
    rows = rows[offset:]
    if limit:
        rows = rows[:limit]
    out = []
    for r in rows:
        m = re.search(r"####\s*([-\d,\.]+)", r["answer"])
        if not m:
            continue
        out.append({
            "question": r["question"],
            "ref": float(m.group(1).replace(",", "")),
        })
    return out


# --------------------------------------------------------------------------
# model access
# --------------------------------------------------------------------------
def call_model(base_url, api_key, model, prompt, temperature=0.0, retries=3):
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
    }
    req = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + api_key,
        },
    )
    last = None
    for i in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                body = json.loads(resp.read().decode())
            return body["choices"][0]["message"]["content"]
        except (urllib.error.URLError, urllib.error.HTTPError, KeyError, TimeoutError) as e:
            last = e
            time.sleep(2 ** i)
    raise RuntimeError(f"model call failed after {retries} retries: {last}")


# --------------------------------------------------------------------------
# extraction + checking
# --------------------------------------------------------------------------
NUM = r"[-+]?\d[\d,]*(?:\.\d+)?"


def extract_baseline_answer(text):
    m = re.findall(r"####\s*(" + NUM + ")", text or "")
    if not m:
        return None
    try:
        return float(m[-1].replace(",", ""))
    except ValueError:
        return None


def strip_fences(text):
    t = (text or "").strip()
    t = re.sub(r"^```(?:json)?", "", t).strip()
    t = re.sub(r"```$", "", t).strip()
    return t


def parse_ir(text):
    """Return (obj, None) if well-formed, else (None, reason). Failure classes
    follow the taxonomy in Section 4: A ambiguity / T type omission /
    R referential drift / N non-invertible."""
    t = strip_fences(text)
    try:
        obj = json.loads(t)
    except json.JSONDecodeError as e:
        return None, f"A:malformed-json({e.msg[:40]})"
    if not isinstance(obj, dict):
        return None, "A:not-an-object"
    for k in ("vars", "goal", "answer"):
        if k not in obj:
            return None, f"T:missing-field:{k}"
    if not isinstance(obj["vars"], list) or not obj["vars"]:
        return None, "T:empty-vars"
    declared, order = set(), []
    for v in obj["vars"]:
        if not isinstance(v, dict):
            return None, "A:bad-var"
        name = v.get("name")
        if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z_]\w*", name):
            return None, "T:bad-var-name"
        if v.get("type") not in ("Nat", "Int", "Rat", "Real"):
            return None, "T:missing-or-unknown-type"
        d = v.get("def")
        if not isinstance(d, str) or not d.strip():
            return None, "T:missing-def"
        names = re.findall(r"[A-Za-z_]\w*", d)
        unknown = [n for n in names if n not in declared]
        if unknown:
            return None, f"R:forward-or-unbound-ref:{unknown[0]}"
        if "/" in d and "nonzero" not in v:
            return None, "T:division-without-nonzero-proof"
        declared.add(name)
        order.append(name)
    goal = obj.get("goal")
    if not isinstance(goal, str) or not goal.strip():
        return None, "T:missing-goal"
    gnames = re.findall(r"[A-Za-z_]\w*", goal)
    gunknown = [n for n in gnames if n not in declared]
    if gunknown:
        return None, f"R:goal-refs-undeclared:{gunknown[0]}"
    if not isinstance(obj.get("answer"), (int, float)):
        return None, "T:answer-not-numeric"
    return obj, None


def eval_expr(expr, env):
    """Evaluate an arithmetic expression over already-bound vars. Returns
    (value, None) or (None, reason). No eval(): whitelisted parser only."""
    e = expr.strip()
    if re.fullmatch(NUM, e.replace(",", "")):
        return float(e.replace(",", "")), None
    for name, val in env.items():
        e = re.sub(r"\b" + re.escape(name) + r"\b", repr(val), e)
    if not re.fullmatch(r"[-+*/().\d\s]+", e):
        return None, "N:non-arithmetic-residue"
    try:
        return float(eval(e, {"__builtins__": {}}, {})), None  # noqa: S307
    except ZeroDivisionError:
        return None, "N:division-by-zero"
    except Exception:
        return None, "N:unevaluable"


def check_ir(obj):
    """Evaluate the IR and compare its rendering with the model's own answer.
    Returns (verified, consistent, ir_value, reason)."""
    env = {}
    for v in obj["vars"]:
        val, err = eval_expr(v["def"], env)
        if err:
            return False, False, None, err
        env[v["name"]] = val
    goal_val, err = eval_expr(obj["goal"], env)
    if err:
        return False, False, None, err
    consistent = abs(goal_val - float(obj["answer"])) < 1e-6
    return True, consistent, goal_val, (None if consistent else "N:goal!=answer")


# --------------------------------------------------------------------------
# per-condition scoring
# --------------------------------------------------------------------------
def score(records):
    n = len(records) or 1
    a = sum(r["correct"] for r in records) / n
    nu = sum(r["verifiable"] for r in records) / n
    ver = [r for r in records if r["verifiable"] and r["verified"]]
    kappa = (sum(r["consistent"] for r in ver) / len(ver)) if ver else 0.0
    # alpha counts only outputs that are ALSO correct; without the correctness
    # conjunct the identity a = alpha + (1-nu)u cannot hold (a measured alpha can
    # exceed a).  This was found by running the harness, not by inspection.
    alpha = sum(r["verifiable"] and r["verified"] and r["consistent"]
                and r["correct"] for r in records) / n
    return {"n": len(records), "a": a, "nu": nu, "kappa": kappa, "alpha": alpha,
            "errors": sum(1 for r in records if r.get("error"))}


def run_condition(problems, cond, base_url, api_key, model, dry, log, workers=8):
    prompt_tpl = BASELINE_PROMPT if cond == "baseline" else IR_PROMPT
    prompts = [prompt_tpl.format(q=p["question"]) for p in problems]

    if dry:
        texts = [None] * len(prompts)
    else:
        def job(pr):
            try:
                return call_model(base_url, api_key, model, pr)
            except Exception as e:                      # noqa: BLE001
                return "__CALL_ERROR__:" + type(e).__name__
        with ThreadPoolExecutor(max_workers=workers) as ex:
            texts = list(ex.map(job, prompts))

    records = []
    for i, (p, text) in enumerate(zip(problems, texts), 1):
        rec = {"i": i, "ref": p["ref"], "raw": text,
               "error": isinstance(text, str) and text.startswith("__CALL_ERROR__")}

        if cond == "baseline":
            ans = extract_baseline_answer(text)
            rec.update(verifiable=False, verified=False, consistent=False,
                       predicted=ans, fail="A:no-structured-object")
            rec["correct"] = ans is not None and abs(ans - p["ref"]) < 1e-6
        else:
            obj, ferr = parse_ir(text)
            if obj is None:
                rec.update(verifiable=False, verified=False, consistent=False,
                           predicted=None, fail=ferr, correct=False)
            else:
                ok, cons, val, reason = check_ir(obj)
                rec.update(verifiable=True, verified=ok, consistent=cons,
                           predicted=float(obj["answer"]), fail=reason,
                           ir_value=val)
                rec["correct"] = abs(float(obj["answer"]) - p["ref"]) < 1e-6
        records.append(rec)
        log.write(json.dumps({k: v for k, v in rec.items() if k != "raw"},
                             ensure_ascii=False) + "\n")
        print(f"  [{cond}] {i}/{len(problems)} "
              f"correct={rec['correct']} nu={rec['verifiable']}", flush=True)
    return records


# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=200)
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("--conditions", default="baseline,ir")
    ap.add_argument("--base-url", default=os.getenv("BASE_URL", "https://api.deepseek.com"))
    ap.add_argument("--model", default=os.getenv("MODEL", "deepseek-chat"))
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--rescore", metavar="RAW_JSONL",
                    help="re-score a previous run from its raw.jsonl, no model calls")
    args = ap.parse_args()

    if args.rescore:
        from collections import Counter
        rows = [json.loads(l) for l in Path(args.rescore).read_text().splitlines() if l.strip()]
        half = len(rows) // 2
        out = Path(args.rescore).parent / "rescore.md"
        lines = ["# rescore of " + str(args.rescore), "",
                 "| condition | a | nu | kappa | alpha | errors |", "|---|---|---|---|---|---|"]
        tex = []
        for cond, chunk in (("baseline", rows[:half]), ("ir", rows[half:])):
            s = score(chunk)
            lines.append(f"| {cond} | {s['a']:.3f} | {s['nu']:.3f} | {s['kappa']:.3f} "
                         f"| {s['alpha']:.3f} | {s['errors']} |")
            tex.append(f"{cond} & {s['a']:.3f} & {s['nu']:.3f} & {s['kappa']:.3f} "
                       f"& {s['alpha']:.3f} \\\\")
            fails = Counter(r.get("fail") for r in chunk
                            if r.get("fail") and not r.get("verifiable"))
            if fails:
                lines.append("")
                lines.append(f"  rejection reasons ({cond}): "
                             + ", ".join(f"{k}={v}" for k, v in fails.most_common()))
        out.write_text("\n".join(lines) + "\n")
        (Path(args.rescore).parent / "table.tex").write_text("\n".join(tex) + "\n")
        print("\n".join(lines))
        print("\nwrote: " + str(out))
        return

    key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not args.dry_run and not key:
        sys.exit("ERROR: set DEEPSEEK_API_KEY or OPENAI_API_KEY "
                 "(or run with --dry-run to check the harness only).")

    problems = load_problems(args.limit, args.offset)
    print(f"problems: {len(problems)}  conditions: {args.conditions}  "
          f"dry-run: {args.dry_run}")

    rid = datetime.now().strftime("%Y%m%d-%H%M%S") + ("-dry" if args.dry_run else "")
    out = RESULTS / rid
    out.mkdir(parents=True, exist_ok=True)

    summary, tables = {}, []
    with (out / "raw.jsonl").open("w") as log:
        for cond in args.conditions.split(","):
            recs = run_condition(problems, cond.strip(), args.base_url, key,
                                 args.model, args.dry_run, log, args.workers)
            s = score(recs)
            summary[cond] = s
            print(f"{cond}: " + "  ".join(f"{k}={v:.3f}" if isinstance(v, float)
                                          else f"{k}={v}" for k, v in s.items()))
            tables.append(f"{cond.replace('_', ' ')} & {s['a']:.3f} & "
                          f"{s['nu']:.3f} & {s['kappa']:.3f} & {s['alpha']:.3f} \\\\")

    (out / "summary.md").write_text(
        "# run " + rid + "\n\n"
        + f"- problems: {len(problems)} (offset {args.offset})\n"
        + f"- model: {args.model} @ {args.base_url}\n"
        + f"- dry-run: {args.dry_run}   workers: {args.workers}\n"
        + "".join(f"- {c}: call errors = {s['errors']}\n" for c, s in summary.items())
        + "\n"
        + "| condition | a | nu | kappa | alpha |\n|---|---|---|---|---|\n"
        + "".join(f"| {c} | {s['a']:.3f} | {s['nu']:.3f} | "
                  f"{s['kappa']:.3f} | {s['alpha']:.3f} |\n"
                  for c, s in summary.items())
    )
    (out / "table.tex").write_text("\n".join(tables) + "\n")
    print("\nwrote: " + str(out))


if __name__ == "__main__":
    main()
