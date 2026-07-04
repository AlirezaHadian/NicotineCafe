"""
sqlite_catalog.py — Loads brands/variants/products directly from the SHARED
SQLite database (same file the WPF app uses) instead of brands.json /
variants.json. No manual JSON editing needed: add a row in Products/Brands/
Variants via the WPF admin screen and the voice engine picks it up on the
next restart (or call ProductCatalog.reload()).

This module does NOT touch the matching algorithm at all — it only feeds
BrandMatcher / VariantMatcher the same shaped data they already expect.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class ProductRow:
    id: int
    brand_canonical: str
    variant_canonical: Optional[str]


class ProductCatalog:
    """
    Reads Brands/BrandAliases/Variants/VariantAliases/Products from the
    shared SQLite database and exposes them in the exact shape
    BrandMatcher/VariantMatcher already consume (list of
    {"name": ..., "aliases": [...]}), plus a (brand, variant) -> product_id
    lookup so recognised text can be turned into a concrete ProductId for
    the WPF side.
    """

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.brands_raw: list[dict] = []
        self.variants_raw: list[dict] = []
        self._product_lookup: dict[tuple[str, Optional[str]], int] = {}
        self.reload()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def reload(self) -> None:
        """Re-read everything from SQLite. Call after catalog edits."""
        with self._connect() as conn:
            self.brands_raw = self._load_entities(conn, "Brands", "BrandAliases", "BrandId")
            self.variants_raw = self._load_entities(conn, "Variants", "VariantAliases", "VariantId")
            self._product_lookup = self._load_product_lookup(conn)

    @staticmethod
    def _load_entities(
        conn: sqlite3.Connection, table: str, alias_table: str, fk_col: str
    ) -> list[dict]:
        rows = conn.execute(f"SELECT Id, NameFa FROM {table} WHERE IsActive = 1").fetchall()
        result: list[dict] = []
        for row in rows:
            aliases = conn.execute(
                f"SELECT Alias FROM {alias_table} WHERE {fk_col} = ?", (row["Id"],)
            ).fetchall()
            result.append({
                "id": row["Id"],
                "name": row["NameFa"],
                "aliases": [a["Alias"] for a in aliases],
            })
        return result

    def _load_product_lookup(self, conn: sqlite3.Connection) -> dict[tuple[str, Optional[str]], int]:
        rows = conn.execute(
            """
            SELECT p.Id, b.NameFa AS BrandName, v.NameFa AS VariantName
            FROM Products p
            JOIN Brands b ON b.Id = p.BrandId
            LEFT JOIN Variants v ON v.Id = p.VariantId
            WHERE p.IsActive = 1
            """
        ).fetchall()
        lookup: dict[tuple[str, Optional[str]], int] = {}
        self._brand_product_ids: dict[str, list[int]] = {}
        for row in rows:
            lookup[(row["BrandName"], row["VariantName"])] = row["Id"]
            self._brand_product_ids.setdefault(row["BrandName"], []).append(row["Id"])
        return lookup

    def find_product_id(self, brand: Optional[str], variant: Optional[str]) -> Optional[int]:
        """
        Resolve (brand, variant) -> product id.

        Fallback order when there's no exact (brand, variant) row:
          1. (brand, None) — an explicit "no variant" catalog row, if you added one.
          2. The brand's DEFAULT product (lowest product id for that brand) — covers
             "یه وینستون میخوام" with no colour mentioned. This always shows
             *something* rather than nothing; if you'd rather ask the customer to
             specify a variant when the brand has multiple, override this method.
          3. None only if the brand itself has zero active products.
        """
        if brand is None:
            return None
        if (brand, variant) in self._product_lookup:
            return self._product_lookup[(brand, variant)]
        if (brand, None) in self._product_lookup:
            return self._product_lookup[(brand, None)]
        brand_products = self._brand_product_ids.get(brand, [])
        if brand_products:
            return min(brand_products)  # lowest id = "default" variant for that brand
        return None
