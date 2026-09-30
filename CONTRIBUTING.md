# Contributing

The engine is deliberately small and knows nothing about any particular language.
Everything language-specific lives in `skills/slopcheck/scripts/lang/<code>.json`.

## Adding a language

You do not need to write Python. You need to be a fluent writer of the language and to
have read enough of its machine-generated text to know what it overproduces.

1. Copy the closest existing pack. `es.json` for Romance languages, `en.json` otherwise.
2. Rename it to the ISO 639-1 code and set `"code"` to match the filename.
3. Fill in each section:

| Field | What goes in it |
|---|---|
| `name` | The language's name, written in that language. |
| `detect_hints` | 10-15 of the most common function words. Used for auto-detection. |
| `sentence_split` | Regex splitting sentences. Adjust for languages that do not end sentences with `.!?`. |
| `copulas` | Forms of "to be". Models avoid them, so the rate is a signal. |
| `copula_floor` | Rate per 100 words below which the prose is suspiciously nominal. |
| `categories` | The patterns. Keep the `id` values identical across packs. |
| `ui` | Output strings. Keys must exist in `UI_DEFAULT` in `slopcheck.py`. |

4. Keep the eight category ids (`antithesis`, `tricolon`, `metadiscourse`,
   `inflated_lexicon`, `stacked_participles`, `vague_attribution`, `formulaic_opener`,
   `formulaic_closer`) so results stay comparable across languages. Add new ids only
   for a pattern that genuinely has no equivalent elsewhere, and say so in the PR.

5. Add two fixtures to `tests/fixtures/`: `slop_<code>.txt` and `human_<code>.txt`.
   Real text, not text you wrote to make the tool look good. A rejected draft is ideal.

6. Add a `Separation` test asserting the machine-like fixture is flagged and the human
   one comes back with no high-severity findings.

7. Run the suite:

```bash
python3 tests/run_tests.py
```

## Tuning patterns

Precision over recall. **A false positive costs more than a miss**, because a writer
who gets flagged for ordinary prose stops running the tool.

- Prefer a pattern that misses a construction to one that catches innocent sentences.
- Test against real human writing in your language before opening the PR. Literary
  prose, technical documentation and journalism all use these constructions on purpose.
- Set `budget` so a normal, well-written text passes. The budget is the number of
  occurrences allowed before the category is reported at all.
- If a word is common in ordinary usage in your language, raise the budget rather than
  removing the word. `clave` in Spanish is a good example: real but not rare.

## Reporting a false positive

Open an issue with the sentence, the language, and where it came from. Published human
writing that gets flagged is the most useful bug report this project can receive.

## Scope

In scope: patterns that machine writing overproduces, in any language.

Out of scope: grammar checking, spell checking, readability scores, house style rules,
and anything whose purpose is to help text evade an AI detector. Pull requests framed
as "humanizing" or "bypassing detection" will be closed.
