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

INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (1,'ونستون'), (1,'وینسون'), (1,'وینستون'), (1,'وین استون'), (1,'وینستن');

INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (2,'مارلبرو'), (2,'مارلبورو'), (2,'مارلبرا'), (2,'ماربرو'), (2,'مارالبرو'), (2,'مارلبورا');

INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (3,'بهمن'), (3,'به من'), (3,'بحمن');

INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (4,'کنت'), (4,'کنّت'), (4,'کِنت'), (4,'کنت سیگار');

INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (5,'کاپیتان بلک'), (5,'کاپیتان'), (5,'کاپیتن بلک'), (5,'کاپیتن'), (5,'کپیتان بلک');

INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (6,'باند استریت'), (6,'باند'), (6,'بوند'), (6,'بوند استریت'), (6,'باند استریت آبی');

INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (7,'ایست'), (7,'اسه'), (7,'ایسه'), (7,'اس اس ای');

INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (8,'گلوآز'), (8,'گولوآز'), (8,'گلواز'), (8,'گیتان');

INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (9,'پارلیامنت'), (9,'پارلمان'), (9,'پارلیمنت');

INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (10,'ال ام'), (10,'ال‌ام'), (10,'ال اند ام'), (10,'الاند ام'), (10,'الام'), (10,'ال ام سیگار');

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
