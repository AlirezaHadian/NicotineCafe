"""
brand_matcher.py — Fuzzy brand detection with alias and phonetic support.

Matching strategy (4 layers, in priority order):
  1. Per-token exact alias    — each word of utterance vs aliases
  2. Per-token phonetic full  — phonetic-encoded token vs phonetic index
  3. Per-token phonetic skel  — skeleton token vs skeleton index
  4. Whole-sentence token_set — fallback for multi-word brands (ال ام)

Per-token matching prevents short aliases (هوم، مار) from doing
partial matches against long sentence strings via WRatio.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    from rapidfuzz import fuzz, process
except ImportError as e:
    raise ImportError("Install rapidfuzz:  pip install rapidfuzz") from e

from normalizer import PersianNormalizer
from phonetic import PhoneticNormalizer

# ---------------------------------------------------------------------------
# Known ambiguous brand pair: کاپیتان بلک (Captain Black) vs بلیک (Blake).
#
# Root cause: PhoneticNormalizer.skeleton() drops long vowels (ا و ی), so
# "بلک" and "بلیک" collapse to the exact same skeleton ("بلک"). When the ASR
# output is noisy, the per-token/bigram fuzzy matcher can end up picking
# whichever of the two happens to score a hair higher — regardless of
# whether a "کاپیتان" prefix was actually said. This caused real
# misclassifications in both directions (e.g. "اپتان بلعچ مخون" — clearly
# Captain Black — got matched to Blake instead).
#
# Fix: after the normal fuzzy match, check independently whether a
# "کاپیتان"-like token exists anywhere in the sentence, and use that to
# force the correct brand. This is decoupled from the ambiguous
# alias/skeleton scoring entirely.
# ---------------------------------------------------------------------------
_CAPTAIN_BLACK_NAME = "کاپیتان بلک"
_BLAKE_NAME = "بلیک"
_CAPTAIN_SKELETON_HINT = "کپتن"
_CAPTAIN_HINT_THRESHOLD = 50.0

# Words that are never brand names — skip in per-token matching
_STOPWORDS: frozenset[str] = frozenset({
    "یه", "یک", "یو", "یتا",
    "داری", "دارید", "داره", "دارین", "داریم", "دری", "ندری",
    "بده", "بدید", "بدین",
    "میخوام", "میخواستم", "میخوای",
    "حاجی", "حجی", "حجیه", "داداش", "دادا", "آقا", "خانم",
    "لطفا", "لطفاً", "ممنون",
    "هم", "که", "تا", "از", "به", "با", "در", "رو", "را",
    "یه‌تا", "سلام", "سالم", "هدیه", "حدیه", "هدی",
    "میخستن", "مخستن", "مقروم", "مخروم", "مخصن", "مخصر",
})


@dataclass(frozen=True)
class BrandEntry:
    canonical: str
    aliases: tuple[str, ...]
    phonetic_full_forms: tuple[str, ...]
    phonetic_skeletons: tuple[str, ...]


@dataclass
class BrandMatch:
    brand: Optional[str]
    score: float
    matched_alias: Optional[str]


class BrandMatcher:
    """
    Loads brands from JSON and matches per-token against brand index.
    Per-token matching prevents short aliases from false-matching
    against unrelated words in long sentences.
    """

    def __init__(
        self,
        brands_file: Optional[Path] = None,
        normalizer: PersianNormalizer = None,  # type: ignore[assignment]
        phonetic: PhoneticNormalizer = None,  # type: ignore[assignment]
        threshold: float = 68.0,
        preloaded: Optional[list[dict]] = None,
    ) -> None:
        """
        Either pass ``brands_file`` (JSON path, legacy/offline mode) or
        ``preloaded`` (list of {"name", "aliases"} dicts, e.g. from
        sqlite_catalog.ProductCatalog.brands_raw) — never both.
        """
        self._norm = normalizer
        self._phon = phonetic
        self._threshold = threshold
        self._brands: list[BrandEntry] = self._load(brands_file, preloaded)
        self._alias_index:    list[tuple[str, str]] = []
        self._phonetic_index: list[tuple[str, str]] = []
        self._skeleton_index: list[tuple[str, str]] = []
        self._build_index()

    def _load(self, path: Optional[Path], preloaded: Optional[list[dict]] = None) -> list[BrandEntry]:
        raw: list[dict] = preloaded if preloaded is not None else json.loads(path.read_text(encoding="utf-8"))
        entries: list[BrandEntry] = []
        for item in raw:
            canonical = self._norm(item["name"])
            raw_aliases = [self._norm(a) for a in item.get("aliases", [])]
            all_forms = list({canonical, *raw_aliases})
            phonetic_fulls = tuple({self._phon.encode_str(f) for f in all_forms})
            phonetic_skels = tuple({self._phon.skeleton(f) for f in all_forms})
            entries.append(BrandEntry(
                canonical=canonical,
                aliases=tuple(all_forms),
                phonetic_full_forms=phonetic_fulls,
                phonetic_skeletons=phonetic_skels,
            ))
        return entries

    def _build_index(self) -> None:
        for entry in self._brands:
            for alias in entry.aliases:
                self._alias_index.append((alias, entry.canonical))
            for pf in entry.phonetic_full_forms:
                self._phonetic_index.append((pf, entry.canonical))
            for sk in entry.phonetic_skeletons:
                self._skeleton_index.append((sk, entry.canonical))

    def _best_from_index(
        self,
        query: str,
        index: list[tuple[str, str]],
        scorer=fuzz.WRatio,
        threshold: float | None = None,
    ) -> tuple[Optional[str], float, Optional[str]]:
        """Match query against index, return (canonical, score_0_1, form)."""
        if not index or not query:
            return None, 0.0, None
        thr = threshold if threshold is not None else self._threshold
        forms = [f for f, _ in index]
        result = process.extractOne(query, forms, scorer=scorer)
        if result is None:
            return None, 0.0, None
        matched_form, raw_score, idx = result
        # Extra-strict bar for very short index keys: short strings
        # (<=4 chars) are prone to deceptively high fuzzy/partial-ratio
        # scores against unrelated fragments in noisy ASR output — e.g.
        # جولیو's short alias "ازیو" partial-matching an unrelated filler
        # fragment "ازی" and winning over the real, longer وینستون match
        # elsewhere in the same sentence. Require near-exact confidence
        # before trusting a short key.
        if len(matched_form) <= 6:
            thr = max(thr, 92.0)
        if raw_score < thr:
            return None, 0.0, None
        return index[idx][1], raw_score / 100.0, matched_form

    def _match_tokens(self, text: str) -> tuple[Optional[str], float, Optional[str]]:
        """
        Compare each token of the utterance individually against the brand index.
        This prevents short aliases (e.g. هوم=3 chars) from partial-matching
        against unrelated words via WRatio's internal partial_ratio.
        """
        best: tuple[Optional[str], float, Optional[str]] = (None, 0.0, None)
        tokens = [t for t in text.split() if t not in _STOPWORDS and len(t) >= 3]

        # Bigrams from filtered tokens only — prevents stopword-containing
        # bigrams like "با احمان" from matching brand aliases like "بمان"
        token_groups = tokens.copy()
        for i in range(len(tokens) - 1):
            token_groups.append(tokens[i] + " " + tokens[i + 1])

        for token in token_groups:
            phon_key = self._phon.encode(token)
            # Skeleton matching uses a higher threshold: skeleton forms are
            # very compressed (e.g. برت for بورتا) and prone to false positives.
            skel_threshold = min(self._threshold + 12, 88)
            for query, index, scorer, thr in [
                (token,              self._alias_index,    fuzz.WRatio, self._threshold),
                (phon_key.full,      self._phonetic_index, fuzz.WRatio, self._threshold),
                (phon_key.skeleton,  self._skeleton_index, fuzz.WRatio, skel_threshold),
            ]:
                cand = self._best_from_index(query, index, scorer, thr)
                if cand[1] > best[1]:
                    best = cand
        return best

    def _has_captain_hint(self, text: str) -> bool:
        """
        True if any token in the sentence phonetically resembles «کاپیتان»
        (covers the observed misheard forms: کاپیتن، کپیتان، کبیتان، اپتان،
        عبطان، کاپتن، کبتن، کامتن، ...) — used to disambiguate
        کاپیتان بلک vs بلیک, which are otherwise indistinguishable at the
        skeleton level (see module docstring above).
        """
        for tok in text.split():
            if len(tok) < 3 or tok in _STOPWORDS:
                continue
            sk = self._phon.skeleton(tok)
            if fuzz.ratio(sk, _CAPTAIN_SKELETON_HINT) >= _CAPTAIN_HINT_THRESHOLD:
                return True
        return False

    def match(self, text: str) -> BrandMatch:
        """
        Find the best brand using per-token + bigram matching only.
        Whole-sentence scoring removed — it caused false positives via
        token_set_ratio partial-matching short aliases against long sentences.
        Multi-word brands (ال ام) are handled by the bigram window in
        _match_tokens.
        """
        if not text:
            return BrandMatch(brand=None, score=0.0, matched_alias=None)

        brand, score, alias = self._match_tokens(text)

        # Captain Black / Blake disambiguation — see module docstring.
        if brand in (_CAPTAIN_BLACK_NAME, _BLAKE_NAME):
            captain_hint = self._has_captain_hint(text)
            if captain_hint and brand == _BLAKE_NAME:
                brand = _CAPTAIN_BLACK_NAME
            elif not captain_hint and brand == _CAPTAIN_BLACK_NAME:
                brand = _BLAKE_NAME

        return BrandMatch(brand=brand, score=score, matched_alias=alias)

    @property
    def brand_names(self) -> list[str]:
        return [e.canonical for e in self._brands]