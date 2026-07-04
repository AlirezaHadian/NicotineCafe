"""
product_builder.py — Combine brand and variant into a final product.

This module is intentionally thin: it applies the business rules for
combining a detected brand with an optional variant, and computes a
final weighted confidence score.

The heavy lifting (fuzzy matching, phonetics) happens upstream in
BrandMatcher / VariantMatcher.  The builder just assembles the result.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from config import MatcherConfig


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class ProductResult:
    """
    Final product detection result.

    Attributes
    ----------
    product_name:
        Canonical product string, e.g. "وینستون آبی" or "مارلبرو گلد".
        None when nothing was detected with sufficient confidence.
    brand:
        Canonical brand name detected, or None.
    variant:
        Canonical variant name detected, or None.
    brand_score:
        Raw brand match confidence (0.0 – 1.0).
    variant_score:
        Raw variant match confidence (0.0 – 1.0), 0.0 when not found.
    confidence:
        Weighted final confidence (0.0 – 1.0).
    is_valid:
        True when confidence ≥ configured threshold AND a brand was found.
    """
    product_name: Optional[str]
    brand: Optional[str]
    variant: Optional[str]
    brand_score: float
    variant_score: float
    confidence: float
    is_valid: bool

    def __str__(self) -> str:  # pragma: no cover
        if not self.is_valid:
            return "[no product detected]"
        return (
            f"{self.product_name}  "
            f"(conf={self.confidence:.0%}, "
            f"brand={self.brand_score:.0%}, "
            f"variant={self.variant_score:.0%})"
        )


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------

class ProductBuilder:
    """
    Assembles a ProductResult from brand + variant match scores.

    Parameters
    ----------
    config : MatcherConfig
        Provides brand_weight, variant_weight, and min_confidence.
    """

    def __init__(self, config: MatcherConfig) -> None:
        self.config = config

    # ------------------------------------------------------------------
    # Confidence calculation
    # ------------------------------------------------------------------

    def _compute_confidence(
        self,
        brand_score: float,
        variant_score: float,
        has_variant: bool,
    ) -> float:
        """
        Weighted confidence.

        When no variant is present the brand score is used directly but
        penalised to reflect the missing information.
        """
        cfg = self.config
        if has_variant:
            return (
                cfg.brand_weight * brand_score
                + cfg.variant_weight * variant_score
            )
        else:
            # Brand-only: apply a slight penalty (0.9×) to signal uncertainty
            return cfg.brand_weight * brand_score * 0.90

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build(
        self,
        brand: Optional[str],
        brand_score: float,
        variant: Optional[str],
        variant_score: float,
    ) -> ProductResult:
        """
        Build and validate a ProductResult.

        Parameters
        ----------
        brand, variant:
            Canonical names from their respective matchers.  May be None.
        brand_score, variant_score:
            Match confidence scores in [0, 1].

        Returns
        -------
        ProductResult
            Always returns an instance; check ``.is_valid`` before acting.
        """
        has_variant = variant is not None and variant_score > 0

        confidence = self._compute_confidence(brand_score, variant_score, has_variant)

        # A product is only valid when a brand was found and confidence is high
        is_valid = (brand is not None) and (confidence >= self.config.min_confidence)

        if is_valid:
            parts = [brand]
            if has_variant:
                parts.append(variant)  # type: ignore[arg-type]
            product_name: Optional[str] = " ".join(parts)
        else:
            product_name = None

        return ProductResult(
            product_name=product_name,
            brand=brand,
            variant=variant if has_variant else None,
            brand_score=brand_score,
            variant_score=variant_score if has_variant else 0.0,
            confidence=confidence,
            is_valid=is_valid,
        )
