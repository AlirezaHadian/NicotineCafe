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

-- ---------- Compound variety aliases (برند + رنگ/تنوع) ----------
-- Customers almost always say brand + colour/variety together
-- ("وینستون آبی", "وینستون اولترالایت", ...). Registering these as
-- explicit aliases (in addition to the bare brand name) helps the
-- fuzzy matcher score them just as confidently as the bare brand.
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (1,'منچستر آبی'), (1,'منچستر قرمز'), (1,'منچستر طلایی'), (1,'منچستر نقره‌ای'), (1,'منچستر منتول'), (1,'منچستر اولترالایت'), (1,'منچستر مشکی'), (1,'منچستر سفید');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (2,'وینستون آبی'), (2,'وینستون قرمز'), (2,'وینستون طلایی'), (2,'وینستون نقره‌ای'), (2,'وینستون منتول'), (2,'وینستون اولترالایت'), (2,'وینستون مشکی'), (2,'وینستون سفید');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (3,'سناتور آبی'), (3,'سناتور قرمز'), (3,'سناتور طلایی'), (3,'سناتور نقره‌ای'), (3,'سناتور منتول'), (3,'سناتور اولترالایت'), (3,'سناتور مشکی'), (3,'سناتور سفید');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (4,'میلانو آبی'), (4,'میلانو قرمز'), (4,'میلانو طلایی'), (4,'میلانو نقره‌ای'), (4,'میلانو منتول'), (4,'میلانو اولترالایت'), (4,'میلانو مشکی'), (4,'میلانو سفید');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (5,'جی‌تی‌ام آبی'), (5,'جی‌تی‌ام قرمز'), (5,'جی‌تی‌ام طلایی'), (5,'جی‌تی‌ام نقره‌ای'), (5,'جی‌تی‌ام منتول'), (5,'جی‌تی‌ام اولترالایت'), (5,'جی‌تی‌ام مشکی'), (5,'جی‌تی‌ام سفید');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (6,'ایست آبی'), (6,'ایست قرمز'), (6,'ایست طلایی'), (6,'ایست نقره‌ای'), (6,'ایست منتول'), (6,'ایست اولترالایت'), (6,'ایست مشکی'), (6,'ایست سفید');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (7,'فورمن آبی'), (7,'فورمن قرمز'), (7,'فورمن طلایی'), (7,'فورمن نقره‌ای'), (7,'فورمن منتول'), (7,'فورمن اولترالایت'), (7,'فورمن مشکی'), (7,'فورمن سفید');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (8,'پرت آبی'), (8,'پرت قرمز'), (8,'پرت طلایی'), (8,'پرت نقره‌ای'), (8,'پرت منتول'), (8,'پرت اولترالایت'), (8,'پرت مشکی'), (8,'پرت سفید');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (9,'کاپیتان بلک آبی'), (9,'کاپیتان بلک قرمز'), (9,'کاپیتان بلک طلایی'), (9,'کاپیتان بلک نقره‌ای'), (9,'کاپیتان بلک منتول'), (9,'کاپیتان بلک اولترالایت'), (9,'کاپیتان بلک مشکی'), (9,'کاپیتان بلک سفید');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (10,'کاوالو آبی'), (10,'کاوالو قرمز'), (10,'کاوالو طلایی'), (10,'کاوالو نقره‌ای'), (10,'کاوالو منتول'), (10,'کاوالو اولترالایت'), (10,'کاوالو مشکی'), (10,'کاوالو سفید');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (11,'مونتانا آبی'), (11,'مونتانا قرمز'), (11,'مونتانا طلایی'), (11,'مونتانا نقره‌ای'), (11,'مونتانا منتول'), (11,'مونتانا اولترالایت'), (11,'مونتانا مشکی'), (11,'مونتانا سفید');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (12,'پال مال آبی'), (12,'پال مال قرمز'), (12,'پال مال طلایی'), (12,'پال مال نقره‌ای'), (12,'پال مال منتول'), (12,'پال مال اولترالایت'), (12,'پال مال مشکی'), (12,'پال مال سفید');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (13,'کنت آبی'), (13,'کنت قرمز'), (13,'کنت طلایی'), (13,'کنت نقره‌ای'), (13,'کنت منتول'), (13,'کنت اولترالایت'), (13,'کنت مشکی'), (13,'کنت سفید');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (14,'کمل آبی'), (14,'کمل قرمز'), (14,'کمل طلایی'), (14,'کمل نقره‌ای'), (14,'کمل منتول'), (14,'کمل اولترالایت'), (14,'کمل مشکی'), (14,'کمل سفید');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (15,'بلیک آبی'), (15,'بلیک قرمز'), (15,'بلیک طلایی'), (15,'بلیک نقره‌ای'), (15,'بلیک منتول'), (15,'بلیک اولترالایت'), (15,'بلیک مشکی'), (15,'بلیک سفید');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (16,'بهمن آبی'), (16,'بهمن قرمز'), (16,'بهمن طلایی'), (16,'بهمن نقره‌ای'), (16,'بهمن منتول'), (16,'بهمن اولترالایت'), (16,'بهمن مشکی'), (16,'بهمن سفید');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (17,'بنس آبی'), (17,'بنس قرمز'), (17,'بنس طلایی'), (17,'بنس نقره‌ای'), (17,'بنس منتول'), (17,'بنس اولترالایت'), (17,'بنس مشکی'), (17,'بنس سفید');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (18,'ناپولی آبی'), (18,'ناپولی قرمز'), (18,'ناپولی طلایی'), (18,'ناپولی نقره‌ای'), (18,'ناپولی منتول'), (18,'ناپولی اولترالایت'), (18,'ناپولی مشکی'), (18,'ناپولی سفید');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (19,'آریزونا آبی'), (19,'آریزونا قرمز'), (19,'آریزونا طلایی'), (19,'آریزونا نقره‌ای'), (19,'آریزونا منتول'), (19,'آریزونا اولترالایت'), (19,'آریزونا مشکی'), (19,'آریزونا سفید');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (20,'مارلبرو آبی'), (20,'مارلبرو قرمز'), (20,'مارلبرو طلایی'), (20,'مارلبرو نقره‌ای'), (20,'مارلبرو منتول'), (20,'مارلبرو اولترالایت'), (20,'مارلبرو مشکی'), (20,'مارلبرو سفید');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (21,'جولیو آبی'), (21,'جولیو قرمز'), (21,'جولیو طلایی'), (21,'جولیو نقره‌ای'), (21,'جولیو منتول'), (21,'جولیو اولترالایت'), (21,'جولیو مشکی'), (21,'جولیو سفید');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (22,'فورور آبی'), (22,'فورور قرمز'), (22,'فورور طلایی'), (22,'فورور نقره‌ای'), (22,'فورور منتول'), (22,'فورور اولترالایت'), (22,'فورور مشکی'), (22,'فورور سفید');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (23,'مکزیکو آبی'), (23,'مکزیکو قرمز'), (23,'مکزیکو طلایی'), (23,'مکزیکو نقره‌ای'), (23,'مکزیکو منتول'), (23,'مکزیکو اولترالایت'), (23,'مکزیکو مشکی'), (23,'مکزیکو سفید');
INSERT INTO BrandAliases (BrandId, Alias) VALUES
 (24,'موند آبی'), (24,'موند قرمز'), (24,'موند طلایی'), (24,'موند نقره‌ای'), (24,'موند منتول'), (24,'موند اولترالایت'), (24,'موند مشکی'), (24,'موند سفید');
