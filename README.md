# پروژه تشخیص بخش‌های واکدار، بی‌واک و سکوت در سیگنال صوتی

این پروژه شامل تحلیل و پردازش سیگنال‌های صوتی برای شناسایی بخش‌های مختلف گفتار است.

## ساختار پروژه

### بخش 1: دریافت و پردازش اولیه سیگنال صوتی

- **part1a_read_audio.py**: خواندن و نمایش فایل صوتی
- **part1b_short_term_energy.py**: محاسبه و نمایش انرژی کوتاه‌مدت

### بخش 2: تشخیص بخش‌های واکدار و بی‌واک و سکوت

- **part2a_frame_segmentation.py**: تقسیم سیگنال به فریم‌های 20 میلی‌ثانیه‌ای
- **part2b_zcr_calculation.py**: محاسبه ZCR (Zero Crossing Rate)
- **part2c_classification.py**: طبقه‌بندی بر اساس ZCR و انرژی
- **part2d_autocorrelation.py**: استفاده از اتوکرولیشن برای تشخیص واکدار
- **part2e_combined_method.py**: ترکیب روش‌ها برای بهبود تشخیص
- **generate_report.py**: تولید گزارش Word با تمام مراحل و تصاویر

## نصب وابستگی‌ها

```bash
pip install -r requirements.txt
```

## نحوه استفاده

1. فایل صوتی خود را با نام `audio.flac` یا `audio.wav` در همان پوشه قرار دهید (اولویت با FLAC است)
2. هر فایل را به ترتیب اجرا کنید:

```bash
python part1a_read_audio.py
python part1b_short_term_energy.py
python part2a_frame_segmentation.py
python part2b_zcr_calculation.py
python part2c_classification.py
python part2d_autocorrelation.py
python part2e_combined_method.py

# تولید گزارش Word برای استاد
python generate_report.py
```

**نکته**: اگر فایل صوتی موجود نباشد، هر فایل به صورت خودکار یک سیگنال نمونه ایجاد می‌کند.

## خروجی‌ها

هر فایل نمودارهای مربوطه را در فایل‌های PNG ذخیره می‌کند:
- `part1a_audio_display.png`
- `part1b_short_term_energy.png`
- `part2a_frame_segmentation.png`
- `part2b_zcr_calculation.png`
- `part2c_classification.png`
- `part2d_autocorrelation.png`
- `part2e_combined_method.png`
- `part2e_final_result.png`

## توضیحات فنی

### انرژی کوتاه‌مدت
انرژی هر فریم به صورت مجموع مربعات نمونه‌ها محاسبه می‌شود.

### ZCR (Zero Crossing Rate)
نرخ عبور از صفر نشان‌دهنده تعداد تغییرات علامت در یک فریم است و برای تشخیص بی‌واک مفید است.

### اتوکرولیشن
اتوکرولیشن برای شناسایی تناوب در سیگنال استفاده می‌شود و می‌تواند فرکانس پایه (F0) را برای بخش‌های واکدار تشخیص دهد.

### طبقه‌بندی
- **سکوت**: انرژی پایین
- **بی‌واک**: انرژی متوسط، ZCR بالا، اتوکرولیشن ضعیف
- **واکدار**: انرژی بالا، ZCR پایین، اتوکرولیشن قوی

## تولید گزارش

پس از اجرای تمام فایل‌ها، می‌توانید با اجرای `generate_report.py` یک گزارش کامل Word با تمام مراحل و تصاویر ایجاد کنید:

```bash
python generate_report.py
```

این فایل یک گزارش حرفه‌ای با فرمت Word ایجاد می‌کند که شامل:
- تمام مراحل پروژه
- توضیحات تشریحی
- تمام تصاویر و نمودارها
- نتیجه‌گیری

فایل گزارش با نام `گزارش_پروژه_پردازش_سیگنال_صوتی.docx` ذخیره می‌شود.

## فایل‌های مستندات

- **README.md**: راهنمای استفاده از پروژه
- **explanations.md**: توضیحات تشریحی کامل فارسی
- **PROJECT_DESCRIPTION.md**: توضیحات پروژه برای رزومه و لینکدین

