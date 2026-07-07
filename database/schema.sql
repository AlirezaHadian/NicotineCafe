-- ==========================================================
-- Nicotine Cafe — SQLite Schema
-- One database file shared by BOTH the WPF app and the
-- Python voice-recognition engine (read-only from Python side).
-- ==========================================================
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Brands (
    Id              INTEGER PRIMARY KEY AUTOINCREMENT,
    NameFa          TEXT NOT NULL,
    NameEn          TEXT NOT NULL,
    IsActive        INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS BrandAliases (
    Id              INTEGER PRIMARY KEY AUTOINCREMENT,
    BrandId         INTEGER NOT NULL REFERENCES Brands(Id) ON DELETE CASCADE,
    Alias           TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Variants (
    Id              INTEGER PRIMARY KEY AUTOINCREMENT,
    NameFa          TEXT NOT NULL,
    NameEn          TEXT NOT NULL,
    IsActive        INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS VariantAliases (
    Id              INTEGER PRIMARY KEY AUTOINCREMENT,
    VariantId       INTEGER NOT NULL REFERENCES Variants(Id) ON DELETE CASCADE,
    Alias           TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Products (
    Id              INTEGER PRIMARY KEY AUTOINCREMENT,
    BrandId         INTEGER NOT NULL REFERENCES Brands(Id),
    VariantId       INTEGER NULL REFERENCES Variants(Id),
    NameFa          TEXT NOT NULL,
    NameEn          TEXT NOT NULL,
    ImagePath       TEXT NULL,
    TarMg           REAL NULL,
    NicotineMg       REAL NULL,
    CarbonMonoxideMg REAL NULL,
    PackSize        INTEGER NULL,
    Price            INTEGER NULL,
    IsActive        INTEGER NOT NULL DEFAULT 1,
    CreatedAt       TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(BrandId, VariantId)
);

CREATE INDEX IF NOT EXISTS IX_Products_Brand   ON Products(BrandId);
CREATE INDEX IF NOT EXISTS IX_Products_Variant ON Products(VariantId);
CREATE INDEX IF NOT EXISTS IX_BrandAliases_Alias   ON BrandAliases(Alias);
CREATE INDEX IF NOT EXISTS IX_VariantAliases_Alias ON VariantAliases(Alias);

CREATE TABLE IF NOT EXISTS RecognitionLog (
    Id              INTEGER PRIMARY KEY AUTOINCREMENT,
    RawText         TEXT NOT NULL,
    NormalisedText  TEXT NOT NULL,
    MatchedProductId INTEGER NULL REFERENCES Products(Id),
    Confidence      REAL NOT NULL,
    IsValid         INTEGER NOT NULL,
    CreatedAt       TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Tunable voice-engine parameters, editable from the WPF admin screen.
-- The Python engine reads these at startup (changes need an app restart).
CREATE TABLE IF NOT EXISTS EngineSettings (
    Key             TEXT PRIMARY KEY,
    Value           TEXT NOT NULL
);
