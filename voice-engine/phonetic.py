"""
phonetic.py — Persian phonetic normalizer.

Converts casual / mispronounced forms of (mostly transliterated foreign)
brand names into a canonical phonetic representation.

Design goals
------------
* NO hardcoded per-brand ``if`` statements.
* Reusable rules expressed as ordered regex substitutions.
* Two representations produced:
    ``encode()``    — full phonetic normal form  (primary matching key)
    ``skeleton()``  — consonant skeleton         (fallback matching key)

How it handles Winston variants
--------------------------------
  ونستون   → وینستون  (rule: word-initial «و» without ی is expanded to «وی»)
  وینسون   → fuzzy match on encode() catches this (edit distance 1 from وینستون)
  وینه سون → rule strips intervening «ه»; fuzzy then aligns it
"""
from __future__ import annotations

import re
from typing import NamedTuple

# ---------------------------------------------------------------------------
# Consonant equivalence table
# Acoustically-similar consonants are mapped to a single canonical glyph.
# ---------------------------------------------------------------------------
_CONSONANT_MAP: dict[str, str] = {
    # Arabic emphatics / interdentals → Persian common equivalents
    "ث": "س",
    "ذ": "ز",
    "ض": "ز",
    "ظ": "ز",
    "ط": "ت",
    "ص": "س",
    # Hamza variants
    "أ": "ا",
    "إ": "ا",

    "ئ": "ی",
    "ؤ": "و",
    "ة": "ه",
    "ء": "",
    # Latin phonetic → Persian (for mixed input e.g. "Gold" typed mid-sentence)
    "v": "و",
    "w": "و",
    "g": "گ",
    "p": "پ",
}

# Long vowels written in Persian script
_LONG_VOWELS: frozenset[str] = frozenset("اوی")

# Arabic diacritics range (already removed by normalizer, but belt+suspenders)
_DIACRITICS_RE = re.compile(r"[\u064B-\u065F\u0670\u0640]")

# ---------------------------------------------------------------------------
# Ordered phonetic transformation rules: (compiled_re, replacement_str)
# Applied AFTER consonant normalization.
# ---------------------------------------------------------------------------
_RAW_RULES: list[tuple[str, str]] = [
    # Word-initial «و» not followed by «ی» → insert «ی»
    # ونستون → وینستون
    (r"\bو(?!ی)([^\s])", r"وی\1"),

    # Intervening «ه» between consonant clusters (colloquial filler vowel)
    # وینه‌سون → وینسون, مارلبره → مارلبرو (handled by fuzzy downstream)
    (r"(?<=[^\s\u0627\u0648\u06CC])ه(?=[^\s\u0627\u0648\u06CC])", ""),

    # Trailing «هن» colloquial → «ون»
    # مارلبرهن → مارلبرون
    (r"هن\b", "ون"),

    # Geminate deduplication — repeated identical consonant
    # گللد → گلد, ووینستون → وینستون
    (r"(.)\1+", r"\1"),

    # Trailing «ه» on foreign words often silent, equate with «و»
    # (does NOT apply to native Persian words — a risk we accept)
    # Only triggers when preceded by a consonant and end-of-word
    (r"(?<=[بپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی])ه\b", "و"),
]


# ---------------------------------------------------------------------------
# Public class
# ---------------------------------------------------------------------------

class PhoneticKey(NamedTuple):
    """Both representations of a phonetically-encoded string."""
    full: str       # Full encoded form — primary key
    skeleton: str   # Consonant skeleton — fallback key


class PhoneticNormalizer:
    """
    Converts normalised Persian text into phonetic representations
    for robust fuzzy matching.

    Usage
    -----
    pn = PhoneticNormalizer()
    key = pn.encode("ونستون")
    # key.full     → "وینستون"
    # key.skeleton → "ونستن"
    """

    def __init__(self) -> None:
        self._rules: list[tuple[re.Pattern[str], str]] = [
            (re.compile(pattern), repl) for pattern, repl in _RAW_RULES
        ]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _map_consonants(text: str) -> str:
        """Replace acoustically-equivalent consonants."""
        for src, dst in _CONSONANT_MAP.items():
            text = text.replace(src, dst)
        return text

    @staticmethod
    def _strip_diacritics(text: str) -> str:
        return _DIACRITICS_RE.sub("", text)

    def _apply_rules(self, text: str) -> str:
        """Apply phonetic transformation rules in order."""
        for pattern, replacement in self._rules:
            text = pattern.sub(replacement, text)
        return text

    @staticmethod
    def _extract_skeleton(text: str) -> str:
        """
        Return consonant skeleton: keep the first character of each word,
        then drop long vowels (ا، و، ی) from remaining positions.
        """
        words = text.split()
        parts: list[str] = []
        for word in words:
            if not word:
                continue
            skeleton = word[0]  # Always keep first char
            skeleton += "".join(
                ch for ch in word[1:] if ch not in _LONG_VOWELS
            )
            parts.append(skeleton)
        return " ".join(parts)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def encode(self, text: str) -> PhoneticKey:
        """
        Full phonetic encoding.

        Parameters
        ----------
        text : str
            Normalised Persian text (output of ``PersianNormalizer``).

        Returns
        -------
        PhoneticKey
            Named tuple with ``.full`` (primary) and ``.skeleton`` (fallback).
        """
        t = self._strip_diacritics(text)
        t = self._map_consonants(t)
        t = self._apply_rules(t)
        t = t.strip()
        return PhoneticKey(full=t, skeleton=self._extract_skeleton(t))

    def encode_str(self, text: str) -> str:
        """Convenience wrapper — returns full encoded form only."""
        return self.encode(text).full

    def skeleton(self, text: str) -> str:
        """Convenience wrapper — returns skeleton form only."""
        return self.encode(text).skeleton
