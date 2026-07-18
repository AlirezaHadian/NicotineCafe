-- ==========================================================
-- Nicotine Cafe — SQLite Schema (v2: brand-only recognition)
-- One database file shared by BOTH the WPF app and the
-- Python voice-recognition engine (read-only from Python side).
--
-- Recognition only needs to identify the BRAND — not which specific
-- model/variant was said. The display shows the brand (name + image)
-- plus a "what we carry" list of model names underneath (display-only,
-- free text, not used for matching).
-- ==========================================================
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Brands (
    Id              INTEGER PRIMARY KEY AUTOINCREMENT,
    NameFa          TEXT NOT NULL,
    NameEn          TEXT NOT NULL,
    ImagePath       TEXT NULL,          -- brand-level image (shown on the display card)
    VideoPath       TEXT NULL,          -- optional per-brand demo video (looped after 1 min on screen)
    IsActive        INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS BrandAliases (
    Id              INTEGER PRIMARY KEY AUTOINCREMENT,
    BrandId         INTEGER NOT NULL REFERENCES Brands(Id) ON DELETE CASCADE,
    Alias           TEXT NOT NULL
);

-- Free-text "models we carry" list per brand — shown under the brand name
-- on the display card. NOT used for voice matching (that's brand-only now).
CREATE TABLE IF NOT EXISTS BrandModels (
    Id              INTEGER PRIMARY KEY AUTOINCREMENT,
    BrandId         INTEGER NOT NULL REFERENCES Brands(Id) ON DELETE CASCADE,
    ModelName       TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS IX_BrandAliases_Alias ON BrandAliases(Alias);
CREATE INDEX IF NOT EXISTS IX_BrandModels_Brand  ON BrandModels(BrandId);

CREATE TABLE IF NOT EXISTS RecognitionLog (
    Id              INTEGER PRIMARY KEY AUTOINCREMENT,
    RawText         TEXT NOT NULL,
    NormalisedText  TEXT NOT NULL,
    MatchedBrandId  INTEGER NULL REFERENCES Brands(Id),
    Confidence      REAL NOT NULL,
    IsValid         INTEGER NOT NULL,
    CreatedAt       TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Tunable voice-engine + display parameters, editable from the WPF admin
-- screen. Voice-engine keys need an app restart to take effect (the Python
-- process reads them once at startup). Display keys (like show_model_list)
-- are read directly by the WPF app and take effect on next launch.
CREATE TABLE IF NOT EXISTS EngineSettings (
    Key             TEXT PRIMARY KEY,
    Value           TEXT NOT NULL
);
