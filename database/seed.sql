-- ==========================================================
-- Nicotine Cafe — Seed data: major cigarette brands sold in Iran
-- Extend freely: add more Brands/Variants/Products/Aliases as needed.
-- Aliases cover common colloquial Persian pronunciations to help the
-- fuzzy/phonetic matcher, but you should keep adding real ones you hear
-- from customers over time.
-- ==========================================================

-- ---------- Brands ----------
INSERT INTO Brands (NameFa, NameEn) VALUES ('وینستون', 'Winston');          -- 1
INSERT INTO Brands (NameFa, NameEn) VALUES ('مارلبرو', 'Marlboro');         -- 2
INSERT INTO Brands (NameFa, NameEn) VALUES ('بهمن', 'Bahman');              -- 3
INSERT INTO Brands (NameFa, NameEn) VALUES ('کنت', 'Kent');                 -- 4
INSERT INTO Brands (NameFa, NameEn) VALUES ('کاپیتان بلک', 'Captain Black'); -- 5
INSERT INTO Brands (NameFa, NameEn) VALUES ('باند استریت', 'Bond Street');  -- 6
INSERT INTO Brands (NameFa, NameEn) VALUES ('ایست', 'ESSE');                -- 7
INSERT INTO Brands (NameFa, NameEn) VALUES ('گلوآز', 'Gauloises');          -- 8
INSERT INTO Brands (NameFa, NameEn) VALUES ('پارلیامنت', 'Parliament');    -- 9
INSERT INTO Brands (NameFa, NameEn) VALUES ('ال‌ام', 'L&M');               -- 10
INSERT INTO Brands (NameFa, NameEn) VALUES ('دانهیل', 'Dunhill');          -- 11
INSERT INTO Brands (NameFa, NameEn) VALUES ('کمل', 'Camel');               -- 12
INSERT INTO Brands (NameFa, NameEn) VALUES ('لاکی استرایک', 'Lucky Strike'); -- 13
INSERT INTO Brands (NameFa, NameEn) VALUES ('وست', 'West');                -- 14
INSERT INTO Brands (NameFa, NameEn) VALUES ('پال مال', 'Pall Mall');       -- 15
INSERT INTO Brands (NameFa, NameEn) VALUES ('روتمنس', 'Rothmans');         -- 16

INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (1,'ونستون'), (1,'وینسون'), (1,'وینستون'), (1,'وین استون'), (1,'وینستن'), (1,'بینستون'), (1,'وینستو'), (1,'وینستوم');

INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (2,'مارلبرو'), (2,'مارلبورو'), (2,'مارلبرا'), (2,'ماربرو'), (2,'مارالبرو'), (2,'مارلبورا'), (2,'ماربو'), (2,'ماربر'), (2,'مالبرو'), (2,'مارورو'), (2,'مارور');

INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (3,'بهمن'), (3,'به من'), (3,'بحمن'), (3,'باهمان'), (3,'با همان'), (3,'بامن'), (3,'بخمان'), (3,'بخمن'), (3,'برمان'), (3,'برمن');

INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (4,'کنت'), (4,'کنّت'), (4,'کِنت'), (4,'کنت سیگار'), (4,'کند'), (4,'کنط');

INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (5,'کاپیتان بلک'), (5,'کاپیتان'), (5,'کاپیتن بلک'), (5,'کاپیتن'), (5,'کپیتان بلک'), (5,'کبیتان بلک'), (5,'کاپیتان بلاک');

INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (6,'باند استریت'), (6,'باند'), (6,'بوند'), (6,'بوند استریت'), (6,'باند استریت آبی');

INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (7,'ایست'), (7,'اسه'), (7,'ایسه'), (7,'اس اس ای');

INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (8,'گلوآز'), (8,'گولوآز'), (8,'گلواز'), (8,'گیتان');

INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (9,'پارلیامنت'), (9,'پارلمان'), (9,'پارلیمنت'), (9,'پارلیامت'), (9,'پرلمان');

INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (10,'ال ام'), (10,'ال‌ام'), (10,'ال اند ام'), (10,'الاند ام'), (10,'الام'), (10,'ال ام سیگار');

INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (11,'دانهیل'), (11,'دان هیل'), (11,'دنهیل');

INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (12,'کمل'), (12,'کمال'), (12,'شتر'), (12,'کمبل'), (12,'کاملیا');

INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (13,'لاکی استرایک'), (13,'لاکی'), (13,'لاکی استریک'), (13,'لوکی استرایک');

INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (14,'وست'), (14,'وست سیگار');

INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (15,'پال مال'), (15,'پالمال'), (15,'پال مالو');

INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (16,'روتمنس'), (16,'روتمن'), (16,'راتمنس');

-- ---------- Variants ----------
INSERT INTO Variants (NameFa, NameEn) VALUES ('آبی', 'Blue');        -- 1
INSERT INTO Variants (NameFa, NameEn) VALUES ('قرمز', 'Red');        -- 2
INSERT INTO Variants (NameFa, NameEn) VALUES ('طلایی', 'Gold');      -- 3
INSERT INTO Variants (NameFa, NameEn) VALUES ('نقره‌ای', 'Silver');   -- 4
INSERT INTO Variants (NameFa, NameEn) VALUES ('منتول', 'Menthol');   -- 5
INSERT INTO Variants (NameFa, NameEn) VALUES ('سفید', 'White');      -- 6
INSERT INTO Variants (NameFa, NameEn) VALUES ('مشکی', 'Black');      -- 7
INSERT INTO Variants (NameFa, NameEn) VALUES ('اولترالایت', 'Ultra Light'); -- 8

INSERT INTO VariantAliases (VariantId, Alias) VALUES (1,'آبی'),(1,'ابی');
INSERT INTO VariantAliases (VariantId, Alias) VALUES (2,'قرمز'),(2,'رد'),(2,'سرخ');
INSERT INTO VariantAliases (VariantId, Alias) VALUES (3,'طلایی'),(3,'گلد'),(3,'طلای');
INSERT INTO VariantAliases (VariantId, Alias) VALUES (4,'نقره ای'),(4,'سیلور'),(4,'نقره‌ای');
INSERT INTO VariantAliases (VariantId, Alias) VALUES (5,'منتول'),(5,'یخی'),(5,'مینتول'),(5,'خنک');
INSERT INTO VariantAliases (VariantId, Alias) VALUES (6,'سفید'),(6,'وایت');
INSERT INTO VariantAliases (VariantId, Alias) VALUES (7,'مشکی'),(7,'بلک');
INSERT INTO VariantAliases (VariantId, Alias) VALUES (8,'اولترالایت'),(8,'اولترا لایت'),(8,'اورتالایت'),(8,'او ال'),(8,'یو ال');

-- ---------- Products ----------
-- Winston
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (1,1,'وینستون آبی','Winston Blue','Images/winston_blue.png', 8, 0.6, 8, 20);
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (1,2,'وینستون قرمز','Winston Red','Images/winston_red.png', 10, 0.8, 10, 20);
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (1,4,'وینستون نقره‌ای','Winston Silver','Images/winston_silver.png', 4, 0.4, 5, 20);
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (1,8,'وینستون اولترالایت','Winston Ultra Light','Images/winston_ultralight.png', 3, 0.3, 4, 20);

-- Marlboro
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (2,2,'مارلبرو قرمز','Marlboro Red','Images/marlboro_red.png', 10, 0.8, 10, 20);
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (2,3,'مارلبرو طلایی','Marlboro Gold','Images/marlboro_gold.png', 7, 0.5, 7, 20);
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (2,4,'مارلبرو نقره‌ای','Marlboro Silver','Images/marlboro_silver.png', 4, 0.4, 5, 20);
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (2,5,'مارلبرو منتول (آیس بلاست)','Marlboro Ice Blast','Images/marlboro_ice_blast.png', 6, 0.5, 6, 20);
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (2,8,'مارلبرو اولترالایت','Marlboro Ultra Light','Images/marlboro_ultralight.png', 3, 0.3, 4, 20);

-- Bahman — sold as a single classic variant, no colour line
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (3,NULL,'بهمن','Bahman','Images/bahman.png', 12, 1.0, 12, 20);

-- Kent
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (4,1,'کنت آبی','Kent Blue','Images/kent_blue.png', 8, 0.6, 8, 20);
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (4,4,'کنت نقره‌ای','Kent Silver','Images/kent_silver.png', 4, 0.4, 5, 20);

-- Captain Black
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (5,7,'کاپیتان بلک مشکی (اورجینال)','Captain Black Original','Images/captainblack_original.png', 11, 0.9, 11, 20);

-- Bond Street
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (6,1,'باند استریت آبی','Bond Street Blue','Images/bond_blue.png', 8, 0.6, 8, 20);
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (6,2,'باند استریت قرمز','Bond Street Red','Images/bond_red.png', 10, 0.8, 10, 20);

-- ESSE
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (7,5,'ایست چنج (کپسول منتول)','ESSE Change','Images/esse_change.png', 5, 0.4, 5, 20);
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (7,3,'ایست گلدن لیف','ESSE Golden Leaf','Images/esse_golden_leaf.png', 6, 0.5, 6, 20);

-- Gauloises
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (8,6,'گلوآز سفید (بلوند)','Gauloises Blonde','Images/gauloises_blonde.png', 8, 0.6, 8, 20);
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (8,1,'گلوآز آبی','Gauloises Blue','Images/gauloises_blue.png', 6, 0.5, 6, 20);

-- Parliament
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (9,1,'پارلیامنت آبی','Parliament Blue','Images/parliament_blue.png', 6, 0.5, 6, 20);
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (9,4,'پارلیامنت نقره‌ای','Parliament Silver','Images/parliament_silver.png', 4, 0.4, 5, 20);

-- L&M
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (10,2,'ال‌ام قرمز','L&M Red','Images/lm_red.png', 10, 0.8, 10, 20);
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (10,1,'ال‌ام آبی','L&M Blue','Images/lm_blue.png', 8, 0.6, 8, 20);

-- Dunhill
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (11,4,'دانهیل نقره‌ای','Dunhill Silver','Images/dunhill_silver.png', 6, 0.5, 6, 20);
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (11,2,'دانهیل قرمز','Dunhill Red','Images/dunhill_red.png', 10, 0.8, 10, 20);

-- Camel
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (12,6,'کمل سفید (لایت)','Camel White','Images/camel_white.png', 6, 0.5, 6, 20);
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (12,2,'کمل قرمز','Camel Red','Images/camel_red.png', 11, 0.9, 11, 20);

-- Lucky Strike
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (13,2,'لاکی استرایک قرمز','Lucky Strike Red','Images/lucky_red.png', 10, 0.8, 10, 20);

-- West
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (14,1,'وست آبی','West Blue','Images/west_blue.png', 8, 0.6, 8, 20);
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (14,2,'وست قرمز','West Red','Images/west_red.png', 10, 0.8, 10, 20);

-- Pall Mall
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (15,2,'پال مال قرمز','Pall Mall Red','Images/pallmall_red.png', 10, 0.8, 10, 20);
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (15,1,'پال مال آبی','Pall Mall Blue','Images/pallmall_blue.png', 8, 0.6, 8, 20);

-- Rothmans
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (16,1,'روتمنس آبی','Rothmans Blue','Images/rothmans_blue.png', 8, 0.6, 8, 20);
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (16,4,'روتمنس نقره‌ای','Rothmans Silver','Images/rothmans_silver.png', 5, 0.4, 5, 20);

-- ---------- Additional variants for existing brands (deeper catalog) ----------
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (1,5,'وینستون منتول','Winston Menthol','Images/winston_menthol.png', 6, 0.5, 6, 20);
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (2,7,'مارلبرو مشکی (بلک منتول)','Marlboro Black Menthol','Images/marlboro_black.png', 9, 0.7, 9, 20);
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (4,5,'کنت منتول','Kent Menthol','Images/kent_menthol.png', 6, 0.5, 6, 20);
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (4,8,'کنت اولترالایت','Kent Ultra Light','Images/kent_ultralight.png', 3, 0.3, 4, 20);
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (5,5,'کاپیتان بلک چری (منتول میوه‌ای)','Captain Black Cherry','Images/captainblack_cherry.png', 10, 0.8, 10, 20);
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (10,4,'ال‌ام نقره‌ای','L&M Silver','Images/lm_silver.png', 5, 0.4, 5, 20);
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (11,1,'دانهیل آبی','Dunhill Blue','Images/dunhill_blue.png', 8, 0.6, 8, 20);
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (12,1,'کمل آبی','Camel Blue','Images/camel_blue.png', 8, 0.6, 8, 20);
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (12,5,'کمل منتول','Camel Menthol','Images/camel_menthol.png', 6, 0.5, 6, 20);
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (14,4,'وست نقره‌ای','West Silver','Images/west_silver.png', 5, 0.4, 5, 20);
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (15,5,'پال مال منتول','Pall Mall Menthol','Images/pallmall_menthol.png', 6, 0.5, 6, 20);
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (16,2,'روتمنس قرمز','Rothmans Red','Images/rothmans_red.png', 10, 0.8, 10, 20);
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (9,5,'پارلیامنت منتول','Parliament Menthol','Images/parliament_menthol.png', 6, 0.5, 6, 20);
INSERT INTO Products (BrandId, VariantId, NameFa, NameEn, ImagePath, TarMg, NicotineMg, CarbonMonoxideMg, PackSize)
VALUES (7,1,'ایست آبی','ESSE Blue','Images/esse_blue.png', 5, 0.4, 5, 20);

-- ---------- Default voice-engine settings (editable in WPF Admin) ----------
INSERT INTO EngineSettings (Key, Value) VALUES ('model_size', 'tiny');
INSERT INTO EngineSettings (Key, Value) VALUES ('beam_size', '1');
INSERT INTO EngineSettings (Key, Value) VALUES ('speech_threshold', '0.09');
INSERT INTO EngineSettings (Key, Value) VALUES ('silence_hangover_s', '0.55');
INSERT INTO EngineSettings (Key, Value) VALUES ('min_utterance_s', '0.9');
INSERT INTO EngineSettings (Key, Value) VALUES ('cpu_threads', '2');
INSERT INTO EngineSettings (Key, Value) VALUES ('min_confidence', '0.60');
