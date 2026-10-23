"""Behavioral oracle for the first independent project task."""
import os
from pathlib import Path
import subprocess
import sys
import unittest

from src.greeting import greet

ROOT = Path(__file__).resolve().parents[1]


class FunctionalGreetingTests(unittest.TestCase):
    def test_plain_name(self):
        self.assertEqual(greet("Ana"), "Hola, Ana!")

    def test_trim_outer_spaces(self):
        self.assertEqual(greet("  Ana Maria  "), "Hola, Ana Maria!")

    def test_preserve_unicode(self):
        self.assertEqual(greet("Jos\u00e9 \u674e"), "Hola, Jos\u00e9 \u674e!")

    def test_eighty_characters(self):
        self.assertEqual(greet("a" * 80), "Hola, " + "a" * 80 + "!")

    def test_literal_metacharacters(self):
        self.assertEqual(greet("$(echo demo); & <x>"), "Hola, $(echo demo); & <x>!")


class AdversarialGreetingTests(unittest.TestCase):
    def test_empty_name_rejected(self):
        for name in ("", "   "):
            with self.subTest(name=name), self.assertRaises(ValueError):
                greet(name)

    def test_oversize_name_rejected(self):
        with self.assertRaises(ValueError):
            greet("a" * 81)

    def test_forbidden_controls_rejected(self):
        for char in ("\r", "\n", "\t", "\0"):
            for name in (char + "Ana", "Ana" + char, "A" + char + "na"):
                with self.subTest(name=repr(name)), self.assertRaises(ValueError):
                    greet(name)

    def test_non_strings_rejected(self):
        for name in (None, 12, True, b"Ana", ["Ana"]):
            with self.subTest(name=repr(name)), self.assertRaises(TypeError):
                greet(name)

    def test_length_checked_after_trim(self):
        self.assertEqual(greet("  " + "x" * 80 + "  "), "Hola, " + "x" * 80 + "!")


class GreetingCliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "src.greeting", *args], cwd=ROOT,
            env=dict(os.environ, PYTHONUTF8="1"), capture_output=True,
            text=True, encoding="utf-8", timeout=10, check=False)

    def test_valid_name_output(self):
        result = self.run_cli("--name", "  Jos\u00e9  ")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "Hola, Jos\u00e9!\n")
        self.assertEqual(result.stderr, "")

    def test_missing_name_rejected(self):
        result = self.run_cli()
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("--name", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_invalid_name_rejected_without_traceback(self):
        for name in (" ", "a\nb", "x" * 81):
            with self.subTest(name=repr(name)):
                result = self.run_cli("--name", name)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                self.assertIn("name", result.stderr)
                self.assertNotIn("Traceback", result.stderr)

    def test_help_is_available(self):
        result = self.run_cli("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("--name", result.stdout)

    def test_metacharacters_are_literal(self):
        result = self.run_cli("--name", "$(echo demo); & <x>")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "Hola, $(echo demo); & <x>!\n")


if __name__ == "__main__":
    unittest.main()
