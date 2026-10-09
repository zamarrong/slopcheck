# Changelog

## 1.1.0

- Catch two more antithesis forms in Spanish: "tampoco ... sino" and "X y no Y"
  (plus the equivalent in English, Portuguese and French). Both were found by a reader
  in drafts the audit had already passed.
- Report findings that fired but stayed inside their budget, so the writer can see what
  the tool decided to allow.
- Restrict tricolon detection to single-word series; the broader pattern flagged ordinary
  conditionals and appositions.
- Skip quoted material (fenced code, inline code, blockquotes) by default, with
  `--include-quoted` to audit it. Documentation about these patterns contains them.
- Typographic budgets now scale with document length.
- SKILL.md: thesis-first procedure, where emotion comes from, and a checklist of the
  failures no script can detect.

## 1.0.0

First release.

- Audit engine, dependency-free, Python 3.8+.
- Eight pattern categories plus formatting, rhythm and copula-rate analysis.
- Language packs for English, Spanish, Portuguese and French.
- Automatic language detection; `--lang` to override.
- `--json` output and exit codes for CI and pre-commit hooks.
- Claude Code skill and plugin manifest.
- 17 tests, including separation tests against real rejected and published drafts.
