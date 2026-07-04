"""
matcher.py — Orchestrates the full detection pipeline.

Pipeline
--------
raw_text
  → PersianNormalizer   (clean, consistent text)
  → BrandMatcher        (find brand)
  → VariantMatcher      (find variant)
  → ProductBuilder      (combine, score, validate)
  → MatchResult

This module owns the pipeline assembly and is the primary integration
point for both the interactive CLI and the benchmark runner.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from config import AppConfig
from normalizer import PersianNormalizer
from phonetic import PhoneticNormalizer
from brand_matcher import BrandMatcher, BrandMatch
from variant_matcher import VariantMatcher, VariantMatch
from product_builder import ProductBuilder, ProductResult


# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------

@dataclass
class MatchResult:
    """Complete output of one pipeline run."""

    raw_text: str
    normalised_text: str
    phonetic_text: str          # phonetic-encoded form (for debug)
    phonetic_skeleton: str      # skeleton form (for debug)

    brand_match: BrandMatch
    variant_match: VariantMatch
    product: ProductResult
    product_id: Optional[int] = None   # resolved via ProductCatalog, None in offline/JSON mode

    @property
    def is_valid(self) -> bool:
        return self.product.is_valid

    def summary(self) -> str:
        """Single-line human-readable summary."""
        if not self.is_valid:
            return "❌  محصولی شناسایی نشد"
        parts = [f"✅  {self.product.product_name}"]
        parts.append(f"(اطمینان: {self.product.confidence:.0%})")
        return "  ".join(parts)


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

class ProductMatcher:
    """
    Assembled detection pipeline.  Instantiate once, call ``match()``
    many times without re-loading any resources.

    Parameters
    ----------
    config : AppConfig
    """

    def __init__(self, config: AppConfig, catalog=None) -> None:
        """
        Parameters
        ----------
        catalog : sqlite_catalog.ProductCatalog | None
            When provided, brands/variants are read from SQLite and
            ``product_id`` is resolved on every match. When None, falls
            back to brands.json / variants.json (legacy/offline mode).
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
            self._variant_matcher = VariantMatcher(
                normalizer=self._norm, phonetic=self._phon,
                threshold=config.matcher.variant_fuzzy_threshold,
                preloaded=catalog.variants_raw,
            )
        else:
            self._brand_matcher = BrandMatcher(
                brands_file=config.brands_file,
                normalizer=self._norm, phonetic=self._phon,
                threshold=config.matcher.fuzzy_threshold,
            )
            self._variant_matcher = VariantMatcher(
                variants_file=config.variants_file,
                normalizer=self._norm, phonetic=self._phon,
                threshold=config.matcher.variant_fuzzy_threshold,
            )
        self._builder = ProductBuilder(config.matcher)

    @classmethod
    def from_sqlite(cls, db_path, config: AppConfig) -> "ProductMatcher":
        """Convenience factory: build a matcher backed by the shared SQLite DB."""
        from sqlite_catalog import ProductCatalog
        catalog = ProductCatalog(Path(db_path))
        return cls(config, catalog=catalog)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def match(self, raw_text: str) -> MatchResult:
        """
        Run the full detection pipeline on *raw_text*.

        Parameters
        ----------
        raw_text : str
            Whisper output (or any Persian text).

        Returns
        -------
        MatchResult
        """
        # 1. Normalise
        normalised = self._norm(raw_text)

        # 2. Phonetic encode (for debug / logging)
        phon_key = self._phon.encode(normalised)

        # 3. Match brand and variant concurrently (on normalised text)
        brand_match = self._brand_matcher.match(normalised)
        variant_match = self._variant_matcher.match(normalised)

        # 4. Build product
        product = self._builder.build(
            brand=brand_match.brand,
            brand_score=brand_match.score,
            variant=variant_match.variant,
            variant_score=variant_match.score,
        )

        product_id = None
        if self._catalog is not None and product.is_valid:
            product_id = self._catalog.find_product_id(product.brand, product.variant)

        return MatchResult(
            raw_text=raw_text,
            normalised_text=normalised,
            phonetic_text=phon_key.full,
            phonetic_skeleton=phon_key.skeleton,
            brand_match=brand_match,
            variant_match=variant_match,
            product=product,
            product_id=product_id,
        )

    def match_many(self, texts: list[str]) -> list[MatchResult]:
        """Convenience: match a list of utterances."""
        return [self.match(t) for t in texts]

    # ------------------------------------------------------------------
    # Debug helpers
    # ------------------------------------------------------------------

    def explain(self, raw_text: str) -> str:
        """Return a multi-line diagnostic string for *raw_text*."""
        r = self.match(raw_text)
        lines = [
            f"  Raw text        : {r.raw_text!r}",
            f"  Normalised      : {r.normalised_text!r}",
            f"  Phonetic (full) : {r.phonetic_text!r}",
            f"  Phonetic (skel) : {r.phonetic_skeleton!r}",
            f"  Brand           : {r.brand_match.brand}  "
            f"(score={r.brand_match.score:.0%}, "
            f"alias={r.brand_match.matched_alias!r})",
            f"  Variant         : {r.variant_match.variant}  "
            f"(score={r.variant_match.score:.0%}, "
            f"alias={r.variant_match.matched_alias!r})",
            f"  Confidence      : {r.product.confidence:.0%}",
            f"  Product         : {r.product.product_name}",
            f"  Valid           : {r.is_valid}",
        ]
        return "\n".join(lines)

    @property
    def available_brands(self) -> list[str]:
        return self._brand_matcher.brand_names

    @property
    def available_variants(self) -> list[str]:
        return self._variant_matcher.variant_names