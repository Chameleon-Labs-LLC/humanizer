"""Regression tests for issue #3: prompt and voice files are read as UTF-8.

On Windows the default text encoding is the locale code page (cp1252), so a
bare ``Path.read_text()`` turns every em dash in the UTF-8 prompt files into
mojibake. These tests fail on such a locale unless every read passes
``encoding="utf-8"``.

Standard library only. Run from the repo root:

    python -m unittest discover -s tests -v
"""
from __future__ import annotations

import ast
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# run.py imports the Anthropic SDK and python-dotenv at module level. Neither is
# needed to read a DNA file, so stand-ins keep this test install-free.
for _name in ("anthropic", "dotenv"):
    if _name not in sys.modules:
        try:
            __import__(_name)
        except ImportError:
            _stub = types.ModuleType(_name)
            if _name == "dotenv":
                _stub.load_dotenv = lambda *a, **k: None
            sys.modules[_name] = _stub

import run  # noqa: E402

EM_DASH = chr(0x2014)
# Curly quotes, accents, an em dash and an ellipsis: all outside ASCII.
SAMPLE = "".join(
    chr(c)
    for c in (0x201C, 0x43, 0x61, 0x66, 0xE9, 0x201D, 0x20, 0x2014, 0x20, 0x6E,
              0x61, 0xEF, 0x76, 0x65, 0x20, 0x2026)
)
# How an em dash starts when its UTF-8 bytes are decoded as cp1252.
MOJIBAKE = EM_DASH.encode("utf-8").decode("cp1252", errors="replace")[:2]
CRLF, LF = chr(13) + chr(10), chr(10)


class FetchUserDnaTest(unittest.TestCase):
    def test_user_profile_round_trips_utf8(self):
        with tempfile.TemporaryDirectory() as tmp:
            dna_dir = Path(tmp)
            (dna_dir / "user_123.md").write_bytes(SAMPLE.encode("utf-8"))
            with mock.patch.object(run, "DNA_DIR", dna_dir):
                self.assertEqual(run.fetch_user_dna("user_123"), SAMPLE)

    def test_template_fallback_has_no_mojibake(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(run, "DNA_DIR", Path(tmp)):
                text = run.fetch_user_dna("nobody")
        self.assertTrue(EM_DASH in text, "em dash missing: not decoded as UTF-8")
        self.assertFalse(MOJIBAKE in text, "mojibake: decoded with the locale code page")
        raw = (ROOT / "dna_bible_template.md").read_bytes().decode("utf-8")
        self.assertTrue(text == raw.replace(CRLF, LF), "template text differs")


class ReadTextCallSitesTest(unittest.TestCase):
    """setup.py and update.py call the API in main(), so check their source."""

    def test_every_read_text_passes_utf8(self):
        found = 0
        for name in ("run.py", "setup.py", "update.py"):
            tree = ast.parse((ROOT / name).read_text(encoding="utf-8"), name)
            for node in ast.walk(tree):
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "read_text"
                ):
                    found += 1
                    encodings = [
                        kw.value.value
                        for kw in node.keywords
                        if kw.arg == "encoding" and isinstance(kw.value, ast.Constant)
                    ]
                    self.assertEqual(
                        encodings,
                        ["utf-8"],
                        f"{name}:{node.lineno} read_text() must pass encoding='utf-8'",
                    )
        self.assertGreaterEqual(found, 4)


if __name__ == "__main__":
    unittest.main()
