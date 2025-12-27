"""
بخش 1a: خواندن و نمایش فایل صوتی
این فایل یک فایل صوتی را می‌خواند و آن را نمایش می‌دهد.
"""

import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
from scipy import signal

# خواندن فایل صوتی
# اگر فایل صوتی موجود نیست، یک سیگنال نمونه ایجاد می‌کنیم
audio_file = None
audio_data = None
sample_rate = None

# تلاش برای خواندن فایل FLAC یا WAV
for filename in ['audio.flac', 'audio.wav']:
    try:
        audio_data, sample_rate = sf.read(filename)
        audio_file = filename
        print(f"فایل صوتی با موفقیت خوانده شد: {audio_file}")
        print(f"نرخ نمونه‌برداری: {sample_rate} Hz")
        print(f"تعداد نمونه‌ها: {len(audio_data)}")
        print(f"مدت زمان: {len(audio_data)/sample_rate:.2f} ثانیه")
        break
    except FileNotFoundError:
        continue

if audio_file is None:
    print("فایل صوتی یافت نشد. یک سیگنال نمونه ایجاد می‌شود...")
    # ایجاد یک سیگنال نمونه برای تست
    sample_rate = 16000  # 16 kHz
    duration = 2  # 2 ثانیه
    t = np.linspace(0, duration, sample_rate * duration)
    
    # ترکیبی از سینوس (گفتار شبیه‌سازی شده) و نویز
    audio_data = (np.sin(2 * np.pi * 440 * t) * 0.5 +  # نت A4
                  np.sin(2 * np.pi * 880 * t) * 0.3 +  # نت A5
                  np.random.normal(0, 0.1, len(t)))    # نویز
    
    # نرمال‌سازی
    audio_data = audio_data / np.max(np.abs(audio_data))
    print(f"سیگنال نمونه ایجاد شد")
    print(f"نرخ نمونه‌برداری: {sample_rate} Hz")
    print(f"تعداد نمونه‌ها: {len(audio_data)}")
    print(f"مدت زمان: {duration} ثانیه")

# تبدیل به مونو در صورت استریو
if len(audio_data.shape) > 1:
    audio_data = np.mean(audio_data, axis=1)

# ایجاد نمودار
plt.figure(figsize=(14, 6))

# نمودار سیگنال در دامنه زمانی
time_axis = np.arange(len(audio_data)) / sample_rate
plt.subplot(2, 1, 1)
plt.plot(time_axis, audio_data)
plt.title('سیگنال صوتی در دامنه زمانی', fontsize=14, fontfamily='DejaVu Sans')
plt.xlabel('زمان (ثانیه)', fontsize=12)
plt.ylabel('دامنه', fontsize=12)
plt.grid(True, alpha=0.3)

# نمودار طیف فرکانسی
frequencies, spectrum = signal.welch(audio_data, sample_rate, nperseg=1024)
plt.subplot(2, 1, 2)
plt.semilogy(frequencies, spectrum)
plt.title('طیف فرکانسی سیگنال', fontsize=14, fontfamily='DejaVu Sans')
plt.xlabel('فرکانس (Hz)', fontsize=12)
plt.ylabel('قدرت طیفی', fontsize=12)
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('part1a_audio_display.png', dpi=150, bbox_inches='tight')
print("نمودار در فایل 'part1a_audio_display.png' ذخیره شد.")
plt.show()

