-- ==========================================================
-- Nicotine Cafe — Seed data v2 (brand-only recognition)
-- Models are PLACEHOLDERS — edit real ones from the Admin screen.
-- ==========================================================

INSERT INTO Brands (NameFa, NameEn) VALUES ('منچستر', 'Manchester');  -- 1
INSERT INTO Brands (NameFa, NameEn) VALUES ('وینستون', 'Winston');  -- 2
INSERT INTO Brands (NameFa, NameEn) VALUES ('سناتور', 'Senator');  -- 3
INSERT INTO Brands (NameFa, NameEn) VALUES ('میلانو', 'Milano');  -- 4
INSERT INTO Brands (NameFa, NameEn) VALUES ('جی‌تی‌ام', 'GTM');  -- 5
INSERT INTO Brands (NameFa, NameEn) VALUES ('ایست', 'ESSE');  -- 6
INSERT INTO Brands (NameFa, NameEn) VALUES ('فورمن', 'Forman');  -- 7
INSERT INTO Brands (NameFa, NameEn) VALUES ('پرت', 'Perth');  -- 8
INSERT INTO Brands (NameFa, NameEn) VALUES ('کاپیتان بلک', 'Captain Black');  -- 9
INSERT INTO Brands (NameFa, NameEn) VALUES ('کاوالو', 'Cavallo');  -- 10
INSERT INTO Brands (NameFa, NameEn) VALUES ('مونتانا', 'Montana');  -- 11
INSERT INTO Brands (NameFa, NameEn) VALUES ('پال مال', 'Pall Mall');  -- 12
INSERT INTO Brands (NameFa, NameEn) VALUES ('کنت', 'Kent');  -- 13
INSERT INTO Brands (NameFa, NameEn) VALUES ('کمل', 'Camel');  -- 14
INSERT INTO Brands (NameFa, NameEn) VALUES ('بلیک', 'Blake');  -- 15
INSERT INTO Brands (NameFa, NameEn) VALUES ('بهمن', 'Bahman');  -- 16
INSERT INTO Brands (NameFa, NameEn) VALUES ('بنس', 'Bens');  -- 17
INSERT INTO Brands (NameFa, NameEn) VALUES ('ناپولی', 'Napoli');  -- 18
INSERT INTO Brands (NameFa, NameEn) VALUES ('آریزونا', 'Arizona');  -- 19
INSERT INTO Brands (NameFa, NameEn) VALUES ('مارلبرو', 'Marlboro');  -- 20
INSERT INTO Brands (NameFa, NameEn) VALUES ('جولیو', 'Julio');  -- 21
INSERT INTO Brands (NameFa, NameEn) VALUES ('فورور', 'Forever');  -- 22
INSERT INTO Brands (NameFa, NameEn) VALUES ('مکزیکو', 'Maxico');  -- 23
INSERT INTO Brands (NameFa, NameEn) VALUES ('موند', 'Mond');  -- 24

INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (1,'منچستر'), (1,'من چستر'), (1,'منجستر');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (2,'ونستون'), (2,'وینسون'), (2,'وینستون'), (2,'وین استون'), (2,'وینستن'), (2,'بینستون'), (2,'وینستو'), (2,'وینستوم');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (3,'سناتور'), (3,'سنیتور'), (3,'سناطور');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (4,'میلانو'), (4,'میلان'), (4,'میلانوو');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (5,'جی تی ام'), (5,'جی‌تی‌ام'), (5,'GTM');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (6,'ایست'), (6,'اسه'), (6,'ایسه'), (6,'اس اس ای');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (7,'فورمن'), (7,'فرمن'), (7,'فورمان');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (8,'پرت'), (8,'پرث'), (8,'پورت');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (9,'کاپیتان بلک'), (9,'کاپیتان'), (9,'کاپیتن بلک'), (9,'کاپیتن'), (9,'کپیتان بلک'), (9,'کبیتان بلک'), (9,'کاپیتان بلاک');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (10,'کاوالو'), (10,'کاوالّو'), (10,'کاوالو سیگار');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (11,'مونتانا'), (11,'منتانا');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (12,'پال مال'), (12,'پالمال'), (12,'پال مالو');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (13,'کنت'), (13,'کنّت'), (13,'کِنت'), (13,'کنت سیگار'), (13,'کند'), (13,'کنط');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (14,'کمل'), (14,'کمال'), (14,'شتر'), (14,'کمبل'), (14,'کاملیا');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (15,'بلیک'), (15,'بلک'), (15,'بلیک سیگار');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (16,'بهمن'), (16,'به من'), (16,'بحمن'), (16,'باهمان'), (16,'با همان'), (16,'بامن'), (16,'بخمان'), (16,'بخمن'), (16,'برمان'), (16,'برمن');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (17,'بنس'), (17,'بنز'), (17,'بنّس');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (18,'ناپولی'), (18,'ناپلی'), (18,'ناپولی سیگار');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (19,'آریزونا'), (19,'اریزونا'), (19,'ارضونا');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (20,'مارلبرو'), (20,'مارلبورو'), (20,'مارلبرا'), (20,'ماربرو'), (20,'مارالبرو'), (20,'مارلبورا'), (20,'ماربو'), (20,'ماربر'), (20,'مالبرو'), (20,'مارورو'), (20,'مارور');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (21,'جولیو'), (21,'جولیو سیگار'), (21,'جولیا');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (22,'فورور'), (22,'فوراور'), (22,'فور اور');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (23,'مکزیکو'), (23,'مکسیکو'), (23,'ماکسیکو');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (24,'موند'), (24,'ماند'), (24,'موندو');

INSERT INTO BrandModels (BrandId, ModelName) VALUES
 (1,'Manchester Blue'), (1,'Manchester Red');
INSERT INTO BrandModels (BrandId, ModelName) VALUES
 (2,'Winston Blue'), (2,'Winston Red'), (2,'Winston Silver'), (2,'Winston Menthol'), (2,'Winston Ultra Light');
INSERT INTO BrandModels (BrandId, ModelName) VALUES
 (3,'Senator Blue'), (3,'Senator Red');
INSERT INTO BrandModels (BrandId, ModelName) VALUES
 (4,'Milano Blue'), (4,'Milano Slims');
INSERT INTO BrandModels (BrandId, ModelName) VALUES
 (5,'GTM Blue'), (5,'GTM Red');
INSERT INTO BrandModels (BrandId, ModelName) VALUES
 (6,'ESSE Change'), (6,'ESSE Golden Leaf'), (6,'ESSE Blue');
INSERT INTO BrandModels (BrandId, ModelName) VALUES
 (7,'Forman Blue'), (7,'Forman Red');
INSERT INTO BrandModels (BrandId, ModelName) VALUES
 (8,'Perth Blue'), (8,'Perth Red');
INSERT INTO BrandModels (BrandId, ModelName) VALUES
 (9,'Captain Black Original'), (9,'Captain Black Cherry');
INSERT INTO BrandModels (BrandId, ModelName) VALUES
 (10,'Cavallo Blue'), (10,'Cavallo Red');
INSERT INTO BrandModels (BrandId, ModelName) VALUES
 (11,'Montana Blue'), (11,'Montana Red');
INSERT INTO BrandModels (BrandId, ModelName) VALUES
 (12,'Pall Mall Red'), (12,'Pall Mall Blue'), (12,'Pall Mall Menthol');
INSERT INTO BrandModels (BrandId, ModelName) VALUES
 (13,'Kent Blue'), (13,'Kent Silver'), (13,'Kent Menthol'), (13,'Kent Ultra Light');
INSERT INTO BrandModels (BrandId, ModelName) VALUES
 (14,'Camel Blue'), (14,'Camel White'), (14,'Camel Red'), (14,'Camel Menthol');
INSERT INTO BrandModels (BrandId, ModelName) VALUES
 (15,'Blake Blue'), (15,'Blake Red');
INSERT INTO BrandModels (BrandId, ModelName) VALUES
 (16,'Bahman Classic'), (16,'Bahman Extra');
INSERT INTO BrandModels (BrandId, ModelName) VALUES
 (17,'Bens Blue'), (17,'Bens Red');
INSERT INTO BrandModels (BrandId, ModelName) VALUES
 (18,'Napoli Blue'), (18,'Napoli Red');
INSERT INTO BrandModels (BrandId, ModelName) VALUES
 (19,'Arizona Blue'), (19,'Arizona Red');
INSERT INTO BrandModels (BrandId, ModelName) VALUES
 (20,'Marlboro Red'), (20,'Marlboro Gold'), (20,'Marlboro Silver'), (20,'Marlboro Ice Blast'), (20,'Marlboro Black Menthol');
INSERT INTO BrandModels (BrandId, ModelName) VALUES
 (21,'Julio Blue'), (21,'Julio Red');
INSERT INTO BrandModels (BrandId, ModelName) VALUES
 (22,'Forever Blue'), (22,'Forever Red');
INSERT INTO BrandModels (BrandId, ModelName) VALUES
 (23,'Maxico Blue'), (23,'Maxico Red');
INSERT INTO BrandModels (BrandId, ModelName) VALUES
 (24,'Mond Blue'), (24,'Mond Red');

-- ---------- Default settings (editable in WPF Admin) ----------
INSERT INTO EngineSettings (Key, Value) VALUES ('model_size', 'tiny');
INSERT INTO EngineSettings (Key, Value) VALUES ('beam_size', '1');
INSERT INTO EngineSettings (Key, Value) VALUES ('speech_threshold', '0.09');
INSERT INTO EngineSettings (Key, Value) VALUES ('silence_hangover_s', '0.55');
INSERT INTO EngineSettings (Key, Value) VALUES ('min_utterance_s', '0.9');
INSERT INTO EngineSettings (Key, Value) VALUES ('cpu_threads', '4');
INSERT INTO EngineSettings (Key, Value) VALUES ('min_confidence', '0.60');
INSERT INTO EngineSettings (Key, Value) VALUES ('show_model_list', 'true');  -- toggle the model-list panel on the display card
