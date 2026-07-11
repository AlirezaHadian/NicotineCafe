"""
matcher.py — Orchestrates the (now brand-only) detection pipeline.

Pipeline
--------
raw_text
  → PersianNormalizer   (clean, consistent text)
  → BrandMatcher        (find brand)
  → MatchResult

Recognition no longer needs to figure out WHICH variant/model was said —
only the brand. The display card shows the brand + a free-text "what we
carry" list (BrandModels table), not a specific matched product. Dropping
variant-level matching is also a real speed win: half the fuzzy/phonetic
work per utterance is simply gone.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from config import AppConfig
from normalizer import PersianNormalizer
from phonetic import PhoneticNormalizer
from brand_matcher import BrandMatcher, BrandMatch


@dataclass
class MatchResult:
    """Complete output of one pipeline run."""

    raw_text: str
    normalised_text: str
    phonetic_text: str          # phonetic-encoded form (for debug)
    phonetic_skeleton: str      # skeleton form (for debug)

    brand_match: BrandMatch
    confidence: float            # brand_match.score scaled to 0..1
    brand_id: Optional[int] = None   # resolved via BrandCatalog

    @property
    def is_valid(self) -> bool:
        return self.brand_match.brand is not None and self.confidence >= self._min_confidence

    _min_confidence: float = 0.60  # overwritten by ProductMatcher after construction

    def summary(self) -> str:
        if not self.is_valid:
            return "❌  برندی شناسایی نشد"
        return f"✅  {self.brand_match.brand}  (اطمینان: {self.confidence:.0%})"


class ProductMatcher:
    """
    Assembled detection pipeline (brand-only). Instantiate once, call
    ``match()`` many times without re-loading any resources.
    """

    def __init__(self, config: AppConfig, catalog=None) -> None:
        """
        Parameters
        ----------
        catalog : sqlite_catalog.BrandCatalog | None
            When provided, brands are read from SQLite and ``brand_id`` is
            resolved on every match. When None, falls back to brands.json
            (legacy/offline mode) and brand_id is always None.
        """
        self.config = config
        self._catalog = catalog
        self._norm = PersianNormalizer()
        self._phon = PhoneticNormalizer()

        if catalog is not None:
            self._brand_matcher = BrandMatcher(
                normalizer=self._norm, phonetic=self._phon,
                threshold=config.matcher.fuzzy_threshold,
                preloaded=catalog.brands_raw,
            )
        else:
            self._brand_matcher = BrandMatcher(
                brands_file=config.brands_file,
                normalizer=self._norm, phonetic=self._phon,
                threshold=config.matcher.fuzzy_threshold,
            )

    @classmethod
    def from_sqlite(cls, db_path, config: AppConfig) -> "ProductMatcher":
        """Convenience factory: build a matcher backed by the shared SQLite DB."""
        from sqlite_catalog import BrandCatalog
        catalog = BrandCatalog(Path(db_path))
        return cls(config, catalog=catalog)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def match(self, raw_text: str) -> MatchResult:
        normalised = self._norm(raw_text)
        phon_key = self._phon.encode(normalised)
        brand_match = self._brand_matcher.match(normalised)
        confidence = brand_match.score  # already 0..1 (see BrandMatcher._match)

        brand_id = None
        if self._catalog is not None and brand_match.brand is not None:
            brand_id = self._catalog.find_brand_id(brand_match.brand)

        result = MatchResult(
            raw_text=raw_text,
            normalised_text=normalised,
            phonetic_text=phon_key.full,
            phonetic_skeleton=phon_key.skeleton,
            brand_match=brand_match,
            confidence=confidence,
            brand_id=brand_id,
        )
        result._min_confidence = self.config.matcher.min_confidence
        return result

    def match_many(self, texts: list[str]) -> list[MatchResult]:
        return [self.match(t) for t in texts]

    def explain(self, raw_text: str) -> str:
        r = self.match(raw_text)
        lines = [
            f"  Raw text        : {r.raw_text!r}",
            f"  Normalised      : {r.normalised_text!r}",
            f"  Phonetic (full) : {r.phonetic_text!r}",
            f"  Phonetic (skel) : {r.phonetic_skeleton!r}",
            f"  Brand           : {r.brand_match.brand}  "
            f"(score={r.brand_match.score:.0%}, "
            f"alias={r.brand_match.matched_alias!r})",
            f"  Confidence      : {r.confidence:.0%}",
            f"  Valid           : {r.is_valid}",
        ]
        return "\n".join(lines)

    @property
    def available_brands(self) -> list[str]:
        return self._brand_matcher.brand_names
