"""
sqlite_catalog.py — Loads brands directly from the SHARED SQLite database
(same file the WPF app uses) instead of brands.json. No manual JSON editing
needed: add a brand + aliases via the WPF admin screen and the voice engine
picks it up on the next restart (or call BrandCatalog.reload()).

Recognition is brand-only now — this module does NOT deal with variants/
models/products at all. The "what we carry" model list is purely a WPF-side
display concern (BrandModels table), irrelevant to matching.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

from normalizer import PersianNormalizer


class BrandCatalog:
    """
    Reads Brands/BrandAliases from the shared SQLite database and exposes
    them in the exact shape BrandMatcher already consumes (list of
    {"name": ..., "aliases": [...]}), plus a name -> brand_id lookup so
    recognised text can be turned into a concrete BrandId for the WPF side.
    """

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.brands_raw: list[dict] = []
        self._brand_id_by_name: dict[str, int] = {}
        self._norm = PersianNormalizer()
        self.reload()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def reload(self) -> None:
        """Re-read everything from SQLite. Call after catalog edits."""
        with self._connect() as conn:
            rows = conn.execute("SELECT Id, NameFa FROM Brands WHERE IsActive = 1").fetchall()
            self.brands_raw = []
            self._brand_id_by_name = {}
            for row in rows:
                aliases = conn.execute(
                    "SELECT Alias FROM BrandAliases WHERE BrandId = ?", (row["Id"],)
                ).fetchall()
                self.brands_raw.append({
                    "id": row["Id"],
                    "name": row["NameFa"],
                    "aliases": [a["Alias"] for a in aliases],
                })
                self._brand_id_by_name[self._norm(row["NameFa"])] = row["Id"]

    def find_brand_id(self, brand_name: Optional[str]) -> Optional[int]:
        if brand_name is None:
            return None
        return self._brand_id_by_name.get(brand_name)

    def log_recognition(self, raw_text: str, normalised_text: str,
                         brand_id: Optional[int], confidence: float, is_valid: bool) -> None:
        """
        Append one row to RecognitionLog. Best-effort — a logging failure
        must never interrupt the recognition flow. This is the raw material
        for continuously improving aliases/thresholds over time: periodically
        review invalid/low-confidence rows and add real phrases as aliases.
        """
        try:
            with self._connect() as conn:
                conn.execute(
                    """
                    INSERT INTO RecognitionLog (RawText, NormalisedText, MatchedBrandId, Confidence, IsValid)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (raw_text, normalised_text, brand_id, confidence, 1 if is_valid else 0),
                )
                conn.commit()
        except sqlite3.Error:
            pass
