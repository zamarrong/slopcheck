#!/usr/bin/env python3
"""slopcheck - audit prose for the patterns that make text read as machine-generated.

This is NOT an AI detector. It cannot tell you whether a text was written by a
model, and it will happily flag prose written by a careful human. It measures
stylistic habits that large language models overproduce, so that a writer can
decide, pattern by pattern, whether to keep them.

Dependency-free. Python 3.8+.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

VERSION = "1.0.0"
LANG_DIR = Path(__file__).resolve().parent / "lang"

SEVERITY_ORDER = {"high": 3, "medium": 2, "low": 1, "info": 0}

# Language-neutral typographic habits. Counted the same way in every language.
FORMATTING_CHECKS = [
    ("em_dash", "Em dash (—)", "—", 2, "medium"),
    ("arrow_bullets", "Arrow bullets (→)", "→", 0, "medium"),
    ("bold_runs", "Bold markers (**)", "**", 4, "low"),
    ("curly_quotes", "Curly quotes (“ ”)", "“", 6, "low"),
]

UI_DEFAULT = {
    "title": "slopcheck",
    "not_a_detector": "Signals, not a verdict. This is not an AI detector.",
    "findings": "FINDINGS",
    "clean": "No pattern exceeded its budget.",
    "rhythm": "RHYTHM",
    "formatting": "FORMATTING",
    "stats": "words/sentence: mean {mean}, sd {sd}, range {lo}-{hi}, variation {cv}",
    "flat": "Sentence lengths are uniform. Add one long sentence and one fragment.",
    "bursty": "Sentence length varies the way human prose does.",
    "budget": "budget",
    "read_aloud": "Now read it aloud. No script can do that part.",
    "copula": "copula rate: {rate} per 100 words",
    "copula_low": "Low copula rate. Models avoid plain 'to be' and pile up abstract nouns.",
}


def load_pack(code: str) -> dict:
    path = LANG_DIR / f"{code}.json"
    if not path.exists():
        available = ", ".join(sorted(p.stem for p in LANG_DIR.glob("*.json")))
        raise SystemExit(f"slopcheck: no language pack '{code}'. Available: {available}")
    return json.loads(path.read_text(encoding="utf-8"))


def available_langs() -> list:
    return sorted(p.stem for p in LANG_DIR.glob("*.json"))


def detect_language(text: str) -> str:
    """Pick the pack whose function words appear most often. Crude on purpose."""
    words = re.findall(r"[^\W\d_]+", text.lower(), re.UNICODE)
    if not words:
        return "en"
    counts = {}
    for code in available_langs():
        hints = set(load_pack(code).get("detect_hints", []))
        counts[code] = sum(1 for w in words if w in hints) / len(words)
    best = max(counts, key=counts.get)
    return best if counts[best] > 0.02 else "en"


def mask_quoted(text: str) -> str:
    """Blank out material the author is quoting rather than writing.

    Fenced code blocks, inline code and blockquote lines are replaced by spaces of
    equal length, so line and column numbers survive. Documentation about these
    patterns necessarily contains these patterns; auditing the examples is noise.
    """
    out = list(text)
    def blank(a: int, b: int) -> None:
        for i in range(a, min(b, len(out))):
            if out[i] != "\n":
                out[i] = " "
    for m in re.finditer(r"^[ \t]*```.*?^[ \t]*```[ \t]*$", text, re.S | re.M):
        blank(*m.span())
    for m in re.finditer(r"`[^`\n]+`", text):
        blank(*m.span())
    for m in re.finditer(r"^[ \t]*>.*$", text, re.M):
        blank(*m.span())
    return "".join(out)


def split_sentences(text: str, pattern: str) -> list:
    parts = re.split(pattern, text)
    return [p.strip() for p in parts if len(p.split()) > 1]


def line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def excerpt(text: str, start: int, end: int, width: int = 60) -> str:
    lo = max(0, start - 12)
    hi = min(len(text), end + 12)
    frag = " ".join(text[lo:hi].split())
    if len(frag) > width:
        frag = frag[: width - 1] + "…"
    return frag


def scan_categories(text: str, pack: dict) -> list:
    findings = []
    for cat in pack.get("categories", []):
        spans, hits = [], []
        for raw in cat.get("patterns", []):
            for m in re.finditer(raw, text, re.IGNORECASE | re.UNICODE):
                # Two patterns in the same category often match the same phrase.
                # Count it once: drop any hit overlapping one already recorded.
                if any(m.start() < e and s < m.end() for s, e in spans):
                    continue
                spans.append((m.start(), m.end()))
                hits.append({
                    "line": line_of(text, m.start()),
                    "match": " ".join(m.group(0).split())[:70],
                    "excerpt": excerpt(text, m.start(), m.end()),
                })
        hits.sort(key=lambda h: h["line"])
        budget = cat.get("budget", 0)
        if len(hits) > budget:
            findings.append({
                "id": cat["id"],
                "label": cat.get("label", cat["id"]),
                "severity": cat.get("severity", "medium"),
                "count": len(hits),
                "budget": budget,
                "why": cat.get("why", ""),
                "fix": cat.get("fix", ""),
                "hits": hits[:6],
            })
    return findings


def scan_formatting(text: str, words: int = 0) -> list:
    """Typographic budgets scale with length: a long document earns more of them."""
    scale = max(1.0, words / 500)
    findings = []
    for cid, label, token, base, severity in FORMATTING_CHECKS:
        n = text.count(token)
        if cid == "bold_runs":
            n //= 2
        budget = base if base == 0 else round(base * scale)
        if n > budget:
            findings.append({
                "id": cid, "label": label, "severity": severity,
                "count": n, "budget": budget, "why": "", "fix": "", "hits": [],
            })
    return findings


def rhythm(text: str, pack: dict) -> dict:
    sents = split_sentences(text, pack.get("sentence_split", r"(?<=[.!?…])\s+"))
    lengths = [len(s.split()) for s in sents]
    out = {"sentences": len(lengths)}
    if len(lengths) >= 3:
        mean = sum(lengths) / len(lengths)
        sd = math.sqrt(sum((x - mean) ** 2 for x in lengths) / len(lengths))
        out.update({
            "mean": round(mean, 1), "sd": round(sd, 1),
            "min": min(lengths), "max": max(lengths),
            "cv": round(sd / mean, 2) if mean else 0.0,
        })
    words = re.findall(r"[^\W\d_]+", text.lower(), re.UNICODE)
    cops = set(pack.get("copulas", []))
    if words and cops:
        out["copula_rate"] = round(100 * sum(1 for w in words if w in cops) / len(words), 2)
    return out


def analyze(text: str, pack: dict, include_quoted: bool = False) -> dict:
    scanned = text if include_quoted else mask_quoted(text)
    findings = scan_categories(scanned, pack) + scan_formatting(scanned, len(text.split()))
    findings.sort(key=lambda f: (-SEVERITY_ORDER.get(f["severity"], 0), -f["count"]))
    r = rhythm(text, pack)
    return {
        "version": VERSION,
        "language": pack["code"],
        "characters": len(text),
        "words": len(text.split()),
        "findings": findings,
        "rhythm": r,
    }


def render(result: dict, pack: dict, path: str) -> str:
    ui = {**UI_DEFAULT, **pack.get("ui", {})}
    L = []
    L.append(f"\n  {ui['title']} · {path} · {result['words']} words · {result['language']}")
    L.append(f"  {ui['not_a_detector']}\n")

    L.append(f"  {ui['findings']}")
    if not result["findings"]:
        L.append(f"    {ui['clean']}")
    for f in result["findings"]:
        mark = {"high": "!!", "medium": " !", "low": "  ", "info": "  "}[f["severity"]]
        L.append(f"    {mark} {f['label']}: {f['count']}  ({ui['budget']} {f['budget']})")
        if f.get("why"):
            L.append(f"         {f['why']}")
        for h in f["hits"]:
            L.append(f"         L{h['line']}: …{h['excerpt']}…")
        if f.get("fix"):
            L.append(f"         → {f['fix']}")
    L.append("")

    r = result["rhythm"]
    L.append(f"  {ui['rhythm']}")
    if "mean" in r:
        L.append("    " + ui["stats"].format(mean=r["mean"], sd=r["sd"], lo=r["min"], hi=r["max"], cv=r["cv"]))
        L.append(f"    {ui['flat'] if r['cv'] < 0.45 else ui['bursty']}")
    if "copula_rate" in r:
        L.append("    " + ui["copula"].format(rate=r["copula_rate"]))
        if r["copula_rate"] < pack.get("copula_floor", 1.0):
            L.append(f"    {ui['copula_low']}")
    L.append("")
    L.append(f"  {ui['read_aloud']}\n")
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="slopcheck",
        description="Audit prose for patterns that make it read as machine-generated. Not an AI detector.",
    )
    ap.add_argument("file", nargs="?", help="text file to audit; reads stdin when omitted")
    ap.add_argument("-l", "--lang", help=f"language pack ({', '.join(available_langs())}); auto-detected by default")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--strict", action="store_true", help="exit 1 on any finding, not only high-severity ones")
    ap.add_argument("--include-quoted", action="store_true",
                    help="also audit code blocks, inline code and blockquotes (skipped by default)")
    ap.add_argument("--list-langs", action="store_true", help="list installed language packs")
    ap.add_argument("--version", action="version", version=f"slopcheck {VERSION}")
    args = ap.parse_args(argv)

    if args.list_langs:
        for code in available_langs():
            print(f"{code}\t{load_pack(code).get('name', code)}")
        return 0

    if args.file:
        p = Path(args.file)
        if not p.exists():
            print(f"slopcheck: no such file: {args.file}", file=sys.stderr)
            return 2
        text, label = p.read_text(encoding="utf-8"), p.name
    else:
        text, label = sys.stdin.read(), "stdin"

    if not text.strip():
        print("slopcheck: empty input", file=sys.stderr)
        return 2

    pack = load_pack(args.lang or detect_language(text))
    result = analyze(text, pack, include_quoted=args.include_quoted)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render(result, pack, label))

    high = [f for f in result["findings"] if f["severity"] == "high"]
    if args.strict:
        return 1 if result["findings"] else 0
    return 1 if high else 0


if __name__ == "__main__":
    sys.exit(main())
