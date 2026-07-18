"""
normalizer.py — Persian text normalization.

Converts raw Whisper output into a clean, consistent Persian string
before any matching logic runs.

Transformations applied (in order):
  1. Strip Arabic diacritics (tashkeel) and tatweel
  2. Remove zero-width characters
  3. Arabic letter → Persian letter substitutions
  4. Collapse repeated letters (ASR elongation artifacts, e.g. "کاواللو" -> "کاوالو")
  5. Persian/Arabic digits → ASCII digits
  6. Lowercase Latin characters
  7. Remove punctuation (keep Persian letters, Latin letters, digits, spaces)
  8. Collapse repeated spaces
  9. Strip surrounding whitespace
"""
from __future__ import annotations

import re
import unicodedata

# ---------------------------------------------------------------------------
# Substitution tables
# ---------------------------------------------------------------------------

# Arabic letters → Persian equivalents (byte-level swap is fastest)
_ARABIC_TO_PERSIAN: dict[str, str] = {
    "\u064A": "\u06CC",  # ي → ی
    "\u0643": "\u06A9",  # ك → ک
    "\u0629": "\u0647",  # ة → ه
    "\u0623": "\u0627",  # أ → ا
    "\u0625": "\u0627",  # إ → ا
    "\u0624": "\u0648",  # ؤ → و
    "\u0626": "\u06CC",  # ئ → ی
    "\u0621": "",        # ء → (drop standalone hamza)
}

# Persian/Arabic digits → Western (ASCII) digits
_PERSIAN_DIGITS: dict[str, str] = {
    "۰": "0", "۱": "1", "۲": "2", "۳": "3", "۴": "4",
    "۵": "5", "۶": "6", "۷": "7", "۸": "8", "۹": "9",
    "٠": "0", "٩": "9",  # also Arabic-Indic
}

# ---------------------------------------------------------------------------
# Pre-compiled regex patterns
# ---------------------------------------------------------------------------

# Arabic diacritics (U+064B–U+065F) + tatweel (U+0640) + superscript alef (U+0670)
_DIACRITICS_RE = re.compile(r"[\u064B-\u065F\u0670\u0640]")

# Zero-width and direction characters
_ZWC_RE = re.compile(r"[\u200B-\u200F\u202A-\u202E\u2060\uFEFF]")

# Keep only: Persian/Arabic script, Latin letters, digits (ASCII), and spaces
_ALLOWED_RE = re.compile(
    r"[^\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF"
    r"A-Za-z0-9\s]"
)

_MULTI_SPACE_RE = re.compile(r" {2,}")

# 2+ identical consecutive letters -> collapse to 1. Persian native spelling
# essentially never has legitimately doubled letters (unlike English) — a
# run like "کاواللو" or "وینستوووم" is always a Whisper elongation artifact,
# not real spelling. Collapsing this generically means we don't need a
# manual alias for every possible doubling of every brand name.
_REPEATED_LETTER_RE = re.compile(r"([\u0600-\u06FF])\1{1,}")


# ---------------------------------------------------------------------------
# Public class
# ---------------------------------------------------------------------------

class PersianNormalizer:
    """
    Stateless normalizer — call ``normalize(text)`` directly.
    All methods are idempotent.
    """

    # ------------------------------------------------------------------
    # Low-level helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _remove_diacritics(text: str) -> str:
        return _DIACRITICS_RE.sub("", text)

    @staticmethod
    def _remove_zwc(text: str) -> str:
        return _ZWC_RE.sub("", text)

    @staticmethod
    def _arabic_to_persian(text: str) -> str:
        for src, dst in _ARABIC_TO_PERSIAN.items():
            text = text.replace(src, dst)
        return text

    @staticmethod
    def _normalize_digits(text: str) -> str:
        """Convert Eastern Arabic / Persian digits to ASCII."""
        for src, dst in _PERSIAN_DIGITS.items():
            text = text.replace(src, dst)
        return text

    @staticmethod
    def _lowercase_latin(text: str) -> str:
        """Lowercase only the Latin portion of the text."""
        return "".join(ch.lower() if ch.isascii() and ch.isalpha() else ch for ch in text)

    @staticmethod
    def _remove_punctuation(text: str) -> str:
        return _ALLOWED_RE.sub(" ", text)

    @staticmethod
    def _collapse_spaces(text: str) -> str:
        return _MULTI_SPACE_RE.sub(" ", text).strip()

    @staticmethod
    def _collapse_repeated_letters(text: str) -> str:
        return _REPEATED_LETTER_RE.sub(r"\1", text)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def normalize(self, text: str) -> str:
        """
        Full normalization pipeline.

        Parameters
        ----------
        text:
            Raw string from Whisper or any other source.

        Returns
        -------
        str
            Clean, consistent Persian string ready for matching.
        """
        if not text:
            return ""
        text = self._remove_diacritics(text)
        text = self._remove_zwc(text)
        text = self._arabic_to_persian(text)
        text = self._collapse_repeated_letters(text)
        text = self._normalize_digits(text)
        text = self._lowercase_latin(text)
        text = self._remove_punctuation(text)
        text = self._collapse_spaces(text)
        return text

    def normalize_list(self, items: list[str]) -> list[str]:
        """Normalize every string in *items*."""
        return [self.normalize(item) for item in items]

    def __call__(self, text: str) -> str:
        """Allow using the instance as a function."""
        return self.normalize(text)
