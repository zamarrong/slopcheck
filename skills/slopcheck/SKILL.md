---
name: slopcheck
description: Audit prose for the habits that make writing read as machine-generated, then rewrite it. Use before delivering any text a human will sign or publish - posts, essays, docs, emails, landing copy, proposals, release notes - and when someone says a draft "sounds like AI", "sounds generic", or asks to "make it sound human". Works in English, Spanish, Portuguese and French. Also useful when reviewing someone else's text to understand why it feels machine-made.
---

# slopcheck

Large language models write in a recognizable dialect. Not wrong, not ungrammatical:
recognizable. Antithesis every third line, lists of three, a tidy bow at the end, and
sentences that all land at the same length. Readers notice, even when they cannot name
what they noticed, and the writing loses the authority it was supposed to carry.

This skill audits a draft against those habits and rewrites what it finds.

## Rule zero: never fabricate

This comes before style, and it is the failure that matters most.

Never invent anecdotes, clients, numbers, quotes, dates, or personal experience for a
text a human will sign. If the draft would be better with a specific fact you do not have:

- mark it `[YOUR DATA: what is needed]` and leave the gap visible, **or**
- ask the author before writing, **or**
- rebuild the argument so it does not depend on that fact.

Specificity is the most human quality in prose and the most tempting thing to
counterfeit. A fabricated detail that reads beautifully is worse than an obvious gap,
because the author cannot defend it and does not know they need to.

## Procedure

1. Draft.
2. Run the audit:
   ```bash
   python3 scripts/slopcheck.py draft.txt
   ```
   It auto-detects the language. Force one with `--lang es`. Add `--json` for structured
   output, `--strict` to fail on medium-severity findings too.
3. Fix what it reports. Each finding carries a `why` and a `fix`.
4. Read the result aloud. If it sounds like a corporate narrator, it is still wrong.
5. Deliver **with the counts reported**. Never hand back a silent pass.

Exit codes: `0` clean, `1` findings, `2` usage error. Useful in CI and pre-commit hooks.

## What it checks

| Category | Why it matters |
|---|---|
| Negative parallelism | `Not X, but Y.` The most reliable single tell. Budget: one per text. |
| Rule of three | Three parallel items. Fine once; mechanical when it becomes the default cadence. |
| Signposting | `It's important to note that...` Talking about the text instead of saying the thing. |
| Inflated vocabulary | `delve`, `pivotal`, `robust`, `testament`, `unlock`, `landscape`. Importance claimed, never shown. |
| Trailing participles | `, highlighting the growing need for...` Causation implied but never argued. |
| Vague attribution | `Experts say`, `Studies show`. Authority with no source behind it. |
| Formulaic openers | `In today's rapidly evolving landscape...` |
| Formulaic closers | `In conclusion`, `At the end of the day`, the symmetrical bow. |
| Formatting | Em dashes, arrow bullets, bold everywhere, curly quotes. |
| Rhythm | Sentence-length variation. Human prose is bursty; generated prose is even. |

The rhythm check reports a coefficient of variation. Below about 0.45 the prose is
metronomic and needs one long winding sentence and one fragment. It also reports the
copula rate, because models avoid plain "to be" and stack abstract nouns instead.

## What to do instead

**Be specific.** One odd, checkable detail beats three well-turned sentences. This is
the hardest thing to fake and the easiest thing to notice.

**Vary the rhythm on purpose.** Let one sentence run long and get slightly tangled. Let
another be four words. Let a paragraph end without resolving.

**Say the idea once.** Restating it three ways in new clothes is padding that reads as
depth.

**Admit what you do not know.** "Where I get stuck is..." cannot be mistaken for model
output, and it draws better responses than a rhetorical question.

**Ask real questions.** If you do not want the answer, cut the question.

## Adding a language

Language packs are JSON in `scripts/lang/`. Nothing in the engine is
English-specific; a new language is a data file, not a code change. See
`CONTRIBUTING.md` in the repository.

## Thesis first

Before writing a line, say what the text argues in one sentence. Everything else is
evidence for it or it is cut.

Skipping this is how a draft dies by a thousand edits: each fix is sound on its own, and
after fifteen of them the piece is a list of topics with no spine. If a reader says "I
don't know what this is trying to say", stop patching sentences and go back to the
thesis. That is a rewrite, not an edit.

## Where emotion comes from

A text can clear every check in this skill and still be dead on the page.

The fix is never adjectives. It is **scene and stakes**:

- Put the reader inside a moment. "You open the console, the account is frozen, there is
  nobody to call, and your whole team is waiting to work" beats "we have experienced
  service interruptions".
- Name what is at risk, in the subject's own terms.
- Give the strongest line its own paragraph. Buried in a clause, it dies.
- Resolve the tension you opened. A scene with no landing is just noise.

Specificity is also what makes prose feel alive. "When Meta marks the line red" is better
than "when it detects risk signals" — not because it is prettier, but because only
someone who has lived it writes the first one.

## What the script cannot see

Every item below was caught by a human reading a draft that the audit had passed clean.
Each one would have shipped.

**Broken referents.** A cut removed a clause and "exactly this" began pointing at the
wrong antecedent; the text ended up saying someone had asked to be blocked. After any
deletion, re-read every sentence that opens with a pronoun or a demonstrative.

**Unwanted presupposition.** "A year ago we operated much worse" tells the reader you
operate badly today. "Either a person has that conversation or nobody does" told the
reader you would leave a customer unattended. Comparatives and absolutes smuggle in
claims you never meant to make.

**Claims the system cannot back.** A draft said the product computed return on ad spend.
It imports no ad spend, and every deal in the database carried a value of zero. Verify
against the running system, not against the brand document, not against memory, and not
against what the product roadmap says it will do.

**Context that is not yours to publish.** The author explained, as background, how his
product related to the company in the story. It went into the draft and would have
exposed him to his own board. Background given to you so you understand is not material
to publish. Ask.

**Hedging something true.** Flagging that a working feature shipped recently reads as
inexperience. Removing a false claim is mandatory; putting an asterisk on a true one only
costs the author authority.

**Regional vocabulary.** Language packs do not catch dialect. "Pizarra" is Spain,
"pizarrón" is Mexico. Know which variety the author writes.

**Ornamental filler.** Clauses that sound like craft and carry nothing: "which is what
really moves the needle", "one by one", "and I would rather say it than sell it". Test:
delete the clause. If the paragraph says the same thing, it was filler.

## What this is not

Not an AI detector. It cannot tell you whether a model wrote something, and it will
flag careful human prose that happens to use these constructions. Do not use it to
accuse anyone of anything.

Not a tool for disguising undisclosed AI use. If a person or a policy is owed a
disclosure, this skill does not discharge it. See `references/disclosure.md` for what
ICMJE, COPE and the EU AI Act actually require.

The counts are signals, not a verdict. A text can score clean and still read like a
machine, and one well-placed antithesis can be the best line in the paragraph.

In the session that produced this skill, three antithesis forms and every single problem
in the list above were found by a person reading aloud, not by the script. The script
narrows what you have to look for. It does not look for you.
