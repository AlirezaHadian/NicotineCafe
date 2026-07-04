"""
variant_matcher.py — Fuzzy variant (colour/type) detection.

Follows the same layered fuzzy-matching strategy as BrandMatcher but
applies it to variant names (آبی، گلد، لایت، منتول، …).

Variants are matched against the ENTIRE normalised utterance, not just
a residual after brand extraction, because spoken order can vary.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from rapidfuzz import fuzz, process

from normalizer import PersianNormalizer
from phonetic import PhoneticNormalizer

# Common Persian filler/function words that appear in virtually every
# purchase utterance and must NOT be matched against variant names.
# Example: «یه» (=یک) scores 90% against «آبیو» (phonetic form of آبیه).
_STOPWORDS: frozenset[str] = frozenset({
    "یه", "یک", "یو", "یه‌تا", "یتا",
    "داری", "دارید", "داره",
    "بده", "بدید", "بدین",
    "میخوام", "میخواستم", "میخوام",
    "حاجی", "داداش", "آقا", "خانم",
    "لطفا", "لطفاً", "ممنون",
    "هم", "که", "تا", "از", "به", "با", "در",
})


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class VariantEntry:
    canonical: str
    aliases: tuple[str, ...]
    phonetic_full_forms: tuple[str, ...]
    phonetic_skeletons: tuple[str, ...]


@dataclass
class VariantMatch:
    variant: Optional[str]        # canonical variant name, or None
    score: float                  # 0.0 – 1.0
    matched_alias: Optional[str]


# ---------------------------------------------------------------------------
# Matcher
# ---------------------------------------------------------------------------

class VariantMatcher:
    """
    Detects product variant from a normalised Persian utterance.

    Parameters
    ----------
    variants_file : Path
        Path to variants.json.
    normalizer : PersianNormalizer
    phonetic : PhoneticNormalizer
    threshold : float
        Minimum RapidFuzz score (0–100) to accept a candidate.
    """

    def __init__(
        self,
        variants_file: Optional[Path] = None,
        normalizer: PersianNormalizer = None,  # type: ignore[assignment]
        phonetic: PhoneticNormalizer = None,  # type: ignore[assignment]
        threshold: float = 62.0,
        preloaded: Optional[list[dict]] = None,
    ) -> None:
        """
        Either pass ``variants_file`` (JSON path, legacy/offline mode) or
        ``preloaded`` (list of {"name", "aliases"} dicts, e.g. from
        sqlite_catalog.ProductCatalog.variants_raw) — never both.
        """
        self._norm = normalizer
        self._phon = phonetic
        self._threshold = threshold
        self._variants: list[VariantEntry] = self._load(variants_file, preloaded)
        self._alias_index:    list[tuple[str, str]] = []
        self._phonetic_index: list[tuple[str, str]] = []
        self._skeleton_index: list[tuple[str, str]] = []
        self._build_index()

    # ------------------------------------------------------------------
    # Load + index
    # ------------------------------------------------------------------

    def _load(self, path: Optional[Path], preloaded: Optional[list[dict]] = None) -> list[VariantEntry]:
        raw: list[dict] = preloaded if preloaded is not None else json.loads(path.read_text(encoding="utf-8"))
        entries: list[VariantEntry] = []
        for item in raw:
            canonical = self._norm(item["name"])
            raw_aliases = [self._norm(a) for a in item.get("aliases", [])]
            all_forms = list({canonical, *raw_aliases})

            phonetic_fulls = tuple({self._phon.encode_str(f) for f in all_forms})
            phonetic_skels = tuple({self._phon.skeleton(f) for f in all_forms})

            entries.append(VariantEntry(
                canonical=canonical,
                aliases=tuple(all_forms),
                phonetic_full_forms=phonetic_fulls,
                phonetic_skeletons=phonetic_skels,
            ))
        return entries

    def _build_index(self) -> None:
        for entry in self._variants:
            for alias in entry.aliases:
                self._alias_index.append((alias, entry.canonical))
            for pf in entry.phonetic_full_forms:
                self._phonetic_index.append((pf, entry.canonical))
            for sk in entry.phonetic_skeletons:
                self._skeleton_index.append((sk, entry.canonical))

    # ------------------------------------------------------------------
    # Private helper
    # ------------------------------------------------------------------

    def _best_from_index(
        self,
        query: str,
        index: list[tuple[str, str]],
        scorer=fuzz.WRatio,
    ) -> tuple[Optional[str], float, Optional[str]]:
        if not index or not query:
            return None, 0.0, None

        forms = [f for f, _ in index]
        result = process.extractOne(query, forms, scorer=scorer)
        if result is None:
            return None, 0.0, None

        matched_form, raw_score, idx = result
        if raw_score < self._threshold:
            return None, 0.0, None

        canonical = index[idx][1]
        return canonical, raw_score / 100.0, matched_form

    # ------------------------------------------------------------------
    # Matching against individual tokens
    # ------------------------------------------------------------------

    def _match_tokens(self, text: str) -> tuple[Optional[str], float, Optional[str]]:
        """
        Try matching every individual token in *text* against the variant
        index.  This handles cases where the variant word is embedded in
        a sentence (e.g. "یه وینستون آبی بده").
        """
        best: tuple[Optional[str], float, Optional[str]] = (None, 0.0, None)
        for token in text.split():
            if token in _STOPWORDS or len(token) < 2:
                continue
            phon_key = self._phon.encode(token)
            for query, index, scorer in [
                (token,           self._alias_index,    fuzz.token_set_ratio),
                (phon_key.full,   self._phonetic_index, fuzz.WRatio),
                (phon_key.skeleton, self._skeleton_index, fuzz.WRatio),
            ]:
                cand = self._best_from_index(query, index, scorer)
                if cand[1] > best[1]:
                    best = cand
        return best

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def match(self, text: str) -> VariantMatch:
        """
        Find the best variant in *text*.

        Parameters
        ----------
        text:
            Normalised Persian utterance (output of PersianNormalizer).
        """
        if not text:
            return VariantMatch(variant=None, score=0.0, matched_alias=None)

        phon_key = self._phon.encode(text)

        # Whole-sentence candidates
        sentence_candidates = [
            self._best_from_index(text, self._alias_index, fuzz.token_set_ratio),
            self._best_from_index(phon_key.full, self._phonetic_index, fuzz.WRatio),
        ]
        # Per-token candidates (handles variants embedded in longer sentences)
        token_best = self._match_tokens(text)

        all_candidates = [*sentence_candidates, token_best]
        variant, score, alias = max(all_candidates, key=lambda c: c[1])
        return VariantMatch(variant=variant, score=score, matched_alias=alias)

    @property
    def variant_names(self) -> list[str]:
        return [e.canonical for e in self._variants]