#!/usr/bin/env python3
"""slopcheck test suite. Standard library only: python3 tests/run_tests.py"""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills" / "slopcheck" / "scripts" / "slopcheck.py"
FIXTURES = ROOT / "tests" / "fixtures"
LANGS = ROOT / "skills" / "slopcheck" / "scripts" / "lang"

sys.path.insert(0, str(SCRIPT.parent))
import slopcheck  # noqa: E402


def run(args):
    return subprocess.run([sys.executable, str(SCRIPT)] + args,
                          capture_output=True, text=True)


def report(name):
    r = run([str(FIXTURES / name), "--json"])
    return json.loads(r.stdout)


class LanguagePacks(unittest.TestCase):
    def test_every_pack_is_valid(self):
        for path in sorted(LANGS.glob("*.json")):
            with self.subTest(pack=path.name):
                pack = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(pack["code"], path.stem)
                for key in ("name", "detect_hints", "categories", "copulas"):
                    self.assertIn(key, pack)
                ids = [c["id"] for c in pack["categories"]]
                self.assertEqual(len(ids), len(set(ids)), "duplicate category ids")
                for c in pack["categories"]:
                    for key in ("label", "severity", "budget", "why", "fix", "patterns"):
                        self.assertIn(key, c, f"{path.stem}/{c['id']} missing {key}")
                    self.assertIn(c["severity"], ("high", "medium", "low", "info"))
                    self.assertTrue(c["patterns"], f"{path.stem}/{c['id']} has no patterns")

    def test_every_pattern_compiles(self):
        import re
        for path in sorted(LANGS.glob("*.json")):
            pack = json.loads(path.read_text(encoding="utf-8"))
            for c in pack["categories"]:
                for raw in c["patterns"]:
                    with self.subTest(pack=path.stem, cat=c["id"], pattern=raw):
                        re.compile(raw)

    def test_ui_keys_are_known(self):
        for path in sorted(LANGS.glob("*.json")):
            pack = json.loads(path.read_text(encoding="utf-8"))
            for key in pack.get("ui", {}):
                self.assertIn(key, slopcheck.UI_DEFAULT,
                              f"{path.stem}: unknown ui key '{key}'")


class Separation(unittest.TestCase):
    """The tool must tell the two fixtures apart. This is the whole point."""

    def test_machine_like_spanish_is_flagged(self):
        r = report("slop_es.txt")
        anti = [f for f in r["findings"] if f["id"] == "antithesis"]
        self.assertTrue(anti, "missed the antithesis pile-up")
        self.assertGreaterEqual(anti[0]["count"], 4)

    def test_human_spanish_is_clean(self):
        r = report("human_es.txt")
        high = [f for f in r["findings"] if f["severity"] == "high"]
        self.assertEqual(high, [], f"false positives: {high}")

    def test_machine_like_english_is_flagged(self):
        r = report("slop_en.txt")
        ids = {f["id"] for f in r["findings"]}
        for expected in ("antithesis", "metadiscourse", "inflated_lexicon",
                         "vague_attribution", "formulaic_opener", "formulaic_closer"):
            self.assertIn(expected, ids)

    def test_human_english_is_clean(self):
        r = report("human_en.txt")
        high = [f for f in r["findings"] if f["severity"] == "high"]
        self.assertEqual(high, [], f"false positives: {high}")

    def test_rhythm_separates_the_fixtures(self):
        self.assertLess(report("slop_en.txt")["rhythm"]["cv"],
                        report("human_en.txt")["rhythm"]["cv"])

    def test_hits_are_deduplicated(self):
        for f in report("slop_en.txt")["findings"]:
            spans = [(h["line"], h["excerpt"]) for h in f["hits"]]
            self.assertEqual(len(spans), len(set(spans)), f"{f['id']} has duplicate hits")


class FalsePositives(unittest.TestCase):
    """A false positive costs more than a miss: a writer who gets flagged for
    ordinary prose stops running the tool."""

    def _ids(self, text, lang):
        r = json.loads(subprocess.run(
            [sys.executable, str(SCRIPT), "--json", "--lang", lang],
            input=text, capture_output=True, text=True).stdout)
        return {f["id"] for f in r["findings"]} | {a["id"] for a in r["allowed"]}

    def test_four_item_list_is_not_a_tricolon(self):
        self.assertNotIn("tricolon", self._ids(
            "Trabajo con empresas de produccion, retail, consultoria y marketing.", "es"))
        self.assertNotIn("tricolon", self._ids(
            "We serve retail, logistics, manufacturing and healthcare clients.", "en"))

    def test_three_item_list_is_still_caught(self):
        self.assertIn("tricolon", self._ids(
            "Mejora la precision, reduce errores y optimiza tiempos.", "es"))


class CommandLine(unittest.TestCase):
    def test_detects_language(self):
        self.assertEqual(report("slop_es.txt")["language"], "es")
        self.assertEqual(report("slop_en.txt")["language"], "en")

    def test_reads_stdin(self):
        r = subprocess.run([sys.executable, str(SCRIPT), "--json"],
                           input="In today's evolving landscape, it's important to note this.",
                           capture_output=True, text=True)
        self.assertEqual(r.returncode in (0, 1), True)
        self.assertIn("findings", json.loads(r.stdout))

    def test_exit_code_is_zero_for_clean_text(self):
        self.assertEqual(run([str(FIXTURES / "human_en.txt")]).returncode, 0)

    def test_exit_code_is_one_for_flagged_text(self):
        self.assertEqual(run([str(FIXTURES / "slop_en.txt")]).returncode, 1)

    def test_strict_flags_medium_severity(self):
        self.assertEqual(run([str(FIXTURES / "human_es.txt"), "--strict"]).returncode, 0)

    def test_unknown_language_fails_clearly(self):
        r = run([str(FIXTURES / "human_en.txt"), "--lang", "xx"])
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("no language pack", r.stderr + r.stdout)

    def test_missing_file_returns_two(self):
        self.assertEqual(run(["/nonexistent/file.txt"]).returncode, 2)

    def test_list_langs(self):
        out = run(["--list-langs"]).stdout
        for code in ("en", "es", "fr", "pt"):
            self.assertIn(code, out)


class QuotedMaterial(unittest.TestCase):
    """Documentation about these patterns contains these patterns."""

    SAMPLE = (
        "This paragraph is clean and says something specific about invoices.\n\n"
        "```\nIt's important to note that experts say this is pivotal.\n```\n\n"
        "> In conclusion, studies show it is not just fast, but transformative.\n"
    )

    def _run(self, args):
        return json.loads(subprocess.run(
            [sys.executable, str(SCRIPT), "--json", "--lang", "en"] + args,
            input=self.SAMPLE, capture_output=True, text=True).stdout)

    def test_quoted_examples_are_skipped_by_default(self):
        self.assertEqual(self._run([])["findings"], [])

    def test_include_quoted_sees_them(self):
        ids = {f["id"] for f in self._run(["--include-quoted"])["findings"]}
        self.assertIn("metadiscourse", ids)
        self.assertIn("vague_attribution", ids)

    def test_line_numbers_survive_masking(self):
        text = "Padding line.\n\n```\ncode\n```\n\nExperts say this is pivotal and robust.\n"
        r = json.loads(subprocess.run(
            [sys.executable, str(SCRIPT), "--json", "--lang", "en", "--strict"],
            input=text, capture_output=True, text=True).stdout)
        hits = [h for f in r["findings"] for h in f["hits"]]
        self.assertTrue(hits)
        self.assertTrue(all(h["line"] >= 7 for h in hits), hits)


if __name__ == "__main__":
    unittest.main(verbosity=2)
