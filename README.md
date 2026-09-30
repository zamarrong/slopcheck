# slopcheck

A Claude Code skill that audits prose for the habits that make writing read as
machine-generated, and helps you rewrite it.

English · Español · Português · Français. Adding a language is a JSON file, not a code
change.

```
  slopcheck · draft.txt · 138 words · en
  Signals, not a verdict. This is not an AI detector.

  FINDINGS
    !! Negative parallelism: 3  (budget 1)
         The single most reliable tell. Models reach for it to sound profound
         without adding information.
         L1: …this shift is not just a technological change, but a fundament…
         L5: …productivity. Rather than replacing w…
         → Keep at most one, and only where the contrast carries the argument.
    !! Signposting: 1  (budget 0)
         L1: …they operate. It's important to note that this s…
     ! Vague attribution: 2  (budget 0)
         L3: …work itself. Experts say that compan…
         L3: …efficiency. Studies show that the im…

  RHYTHM
    words/sentence: mean 15.3, sd 4.2, range 7-20, variation 0.28
    Sentence lengths are uniform. Add one long sentence and one fragment.

  Now read it aloud. No script can do that part.
```

## Why

Language models write in a recognizable dialect. Antithesis every third line, lists of
three, a tidy symmetrical closing, and sentences that all land at the same length.
None of it is wrong. All of it is recognizable, and a reader who half-notices it stops
trusting the page.

The cost is not aesthetic. A document used to be evidence that somebody thought: you
found the hole in your own argument at the paragraph where you had to explain it.
When the draft arrives already shaped, that moment can be skipped and nobody can tell
from the artifact.

slopcheck does not restore the thinking. It makes the skipping visible.

## Install

**As a Claude Code plugin**

```
/plugin marketplace add zamarrong/slopcheck
/plugin install slopcheck
```

**As a personal skill**

```bash
git clone https://github.com/zamarrong/slopcheck.git
cp -r slopcheck/skills/slopcheck ~/.claude/skills/
```

**As a plain command line tool** — no Claude required, no dependencies, Python 3.8+

```bash
python3 skills/slopcheck/scripts/slopcheck.py draft.md
cat draft.md | python3 skills/slopcheck/scripts/slopcheck.py --lang es
```

## Usage

```
slopcheck [file] [-l LANG] [--json] [--strict] [--list-langs]
```

| Flag | Effect |
|---|---|
| `-l, --lang` | Force a language pack. Auto-detected otherwise. |
| `--json` | Structured output for editors, CI and other tools. |
| `--strict` | Exit non-zero on medium findings too, not only high ones. |
| `--list-langs` | Print installed packs. |

Exit codes: `0` clean, `1` findings, `2` usage error. Drop it in a pre-commit hook or a
docs pipeline.

## What it checks

Negative parallelism · rule of three · signposting · inflated vocabulary · trailing
participles · vague attribution · formulaic openers and closers · em dashes, arrow
bullets and bold runs · sentence-length variation · copula rate.

Every finding carries a budget, an explanation of why it matters, and a concrete fix.
Some patterns are allowed once. One antithesis can be the best line in a paragraph;
seven is a signature.

## The fixtures are real

`tests/fixtures/slop_es.txt` is a genuine first draft, written by a model, that its
author rejected with "your writing is very AI style". `human_es.txt` is the version
that shipped after the rewrite. The test suite asserts the tool can tell them apart:
five findings against zero.

That is the bar. A tool that flags everything is as useless as one that flags nothing.

## What this is not

**Not an AI detector.** It cannot tell you who or what wrote a text. It flags
constructions, and careful human writers use every one of them. Do not use it to accuse
a student, a colleague, or a job applicant of anything. There is no threshold at which
it becomes evidence.

**Not a way to hide undisclosed AI use.** If a journal, a professor, a client or a
reader is owed a disclosure, cleaning up the prose does not discharge it.
`skills/slopcheck/references/disclosure.md` collects what ICMJE, COPE and the EU AI Act
actually require. The goal here is writing worth signing, not writing that slips past
a filter.

**Not a style guide.** It has opinions about machine habits, not about the Oxford comma.

## Contributing

New language packs are the most valuable contribution and the easiest to review. The
engine has nothing English-specific in it; a language is a JSON data file with patterns,
labels and UI strings. See [CONTRIBUTING.md](CONTRIBUTING.md).

Wanted: German, Italian, Dutch, Polish, Japanese, Korean, Hindi, Arabic, Turkish,
Indonesian.

## Prior art

The most complete public catalogue of these patterns is
[Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing),
maintained by WikiProject AI Cleanup from thousands of flagged submissions. It is
descriptive, not prescriptive, and this project follows that stance. Full sources in
[`references/sources.md`](skills/slopcheck/references/sources.md).

## License

MIT. See [LICENSE](LICENSE).

Documentación en español: [docs/es.md](docs/es.md).
