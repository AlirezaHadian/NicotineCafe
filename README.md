# نیکوتین کافه — Nicotine Cafe

سیستم تشخیص محصول از روی صدا (فارسی، آفلاین) + نمایشگر محصول WPF برای فروشگاه دخانیات.

## ساختار سولوشن

```
NicotineCafe/
├── NicotineCafe.sln
├── database/
│   ├── schema.sql              # ساختار جداول SQLite (منبع مشترک دو پروژه)
│   ├── seed.sql                 # داده نمونه
│   └── nicotinecafe.db.sample   # دیتابیس ساخته‌شده نمونه (کپی کن به database\nicotinecafe.db)
├── src/
│   ├── NicotineCafe.Core/       # مدل‌ها + اینترفیس‌ها (بدون وابستگی به دیتابیس/UI)
│   ├── NicotineCafe.Data/       # پیاده‌سازی Repository روی SQLite (Dapper)
│   ├── NicotineCafe.Services/   # لایه سرویس + کلاینت TCP موتور صدا
│   └── NicotineCafe.WPF/        # اپلیکیشن WPF (MVVM, DI)
└── voice-engine/                 # موتور تشخیص گفتار پایتون (نسخه Production)
```

## معماری لایه‌ها (WPF)

```
IProductRepository  ──►  SqliteProductRepository   (فقط کوئری خام اینجاست)
IProductService      ──►  ProductService             (منطق کسب‌وکار + کش)
ISpeechEngineClient  ──►  SpeechEngineClient          (اتصال TCP به موتور پایتون)
```

هر بخشی که کوئری SQL داره فقط داخل `NicotineCafe.Data` هست و از `IProductRepository`
ارث‌بری می‌کنه. UI هیچ‌وقت مستقیم SQL نمی‌زنه.

## ارتباط WPF ⇄ Python

- WPF هنگام استارت، `voice-engine/main.py serve --port 8765 --db <path>` رو به‌عنوان
  پروسه فرزند اجرا می‌کنه (`VoiceEngineProcessLauncher`).
- موتور پایتون یک سرور TCP لوکال (`127.0.0.1:8765`) بالا می‌آره و برای هر تشخیص یک
  خط JSON می‌فرسته:
  ```json
  {"type":"recognition","isValid":true,"productId":1,"rawText":"...", "confidence":0.92}
  ```
- سطح صدای میکروفون هم به‌صورت جدا برای اکولایزر UI فرستاده می‌شه:
  ```json
  {"type":"audio_level","level":0.42}
  ```
- کاتالوگ محصولات (برند/رنگ/محصول) مستقیم از همون فایل SQLite خونده می‌شه —
  نیازی به ویرایش دستی JSON نیست. `sqlite_catalog.py` این کار رو انجام می‌ده.

## قانون نمایش محصول (۵ دقیقه)

در `MainViewModel`:
- با تشخیص هر محصول معتبر، تایمر ۵ دقیقه‌ای ری‌ست می‌شه.
- محصول قبل از ۵ دقیقه فقط در دو حالت پنهان می‌شه:
  1. یک محصول جدید تشخیص داده بشه (جایگزین می‌شه و تایمر دوباره شروع می‌شه)
  2. اپراتور روی دکمه ✕ کلیک کنه

## فونت‌ها

پوشه `src/NicotineCafe.WPF/Assets/Fonts/` رو با فونت **Vazirmatn** (فارسی+لاتین،
لایسنس آزاد، طراحی مدرن هندسی — نه فونت‌های پیش‌فرض مثل Tahoma/Segoe) پر کن:
دانلود از GitHub رسمی پروژه Vazirmatn. فایل‌های `.ttf` رو داخل این پوشه بذار،
`Themes/Fonts.xaml` از قبل بهشون رفرنس می‌ده.

## راه‌اندازی

### ۱) دیتابیس
```powershell
copy database\nicotinecafe.db.sample database\nicotinecafe.db
```
یا با `schema.sql` + `seed.sql` خودت از صفر بساز.
دیتابیس باید در `src\NicotineCafe.WPF\bin\Debug\net8.0-windows\Data\nicotinecafe.db`
هم در دسترس باشه (کپی build-action داخل csproj قابل اضافه‌شدنه).

### ۲) موتور صدا
```powershell
cd voice-engine
pip install -r requirements.txt
python main.py serve --port 8765 --db ..\database\nicotinecafe.db
```

### ۳) WPF
سولوشن رو با Visual Studio 2022 باز کن، `NicotineCafe.WPF` رو Startup Project کن، Run.
(اپ به‌صورت خودکار موتور پایتون رو هم استارت می‌کنه — اجرای دستی بالا فقط برای دیباگ لازمه.)

## چیزهایی که هنوز باید اضافه بشه (قدم بعدی)

- [ ] صفحه ادمین WPF برای افزودن/ویرایش محصول، برند، رنگ (الان فقط seed.sql هست)
- [ ] کپی خودکار عکس محصول به پوشه Assets هنگام افزودن محصول در ادمین
- [ ] فایل‌های فونت Vazirmatn.ttf واقعی داخل Assets/Fonts
- [ ] گرفتن عکس واقعی محصولات و اتصال به ImagePath
- [ ] راه‌اندازی خودکارِ ری‌استارت موتور پایتون اگر کرش کرد (health-check ساده)
- [ ] احتمالاً جایگزینی trigger کلید SPACE با یک پدال/دکمه فیزیکی مناسب مغازه
