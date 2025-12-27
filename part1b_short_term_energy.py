"""
بخش 1b: محاسبه و نمایش انرژی کوتاه‌مدت
این فایل انرژی کوتاه‌مدت و دامنه زمانی کوتاه‌مدت را محاسبه می‌کند.
"""

import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
from scipy import signal
import arabic_reshaper
from bidi.algorithm import get_display

def farsi_text(text):
    """تبدیل متن فارسی برای نمایش صحیح در نمودارها"""
    reshaped_text = arabic_reshaper.reshape(text)  # اصلاح شکل حروف
    bidi_text = get_display(reshaped_text)  # راست‌چین کردن
    return bidi_text

# خواندن فایل صوتی
audio_file = None
audio_data = None
sample_rate = None

# تلاش برای خواندن فایل FLAC یا WAV
for filename in ['audio.flac', 'audio.wav']:
    try:
        audio_data, sample_rate = sf.read(filename)
        audio_file = filename
        print(f"فایل صوتی با موفقیت خوانده شد: {audio_file}")
        break
    except FileNotFoundError:
        continue

if audio_file is None:
    print("فایل صوتی یافت نشد. یک سیگنال نمونه ایجاد می‌شود...")
    sample_rate = 16000
    duration = 2
    t = np.linspace(0, duration, sample_rate * duration)
    audio_data = (np.sin(2 * np.pi * 440 * t) * 0.5 +
                  np.sin(2 * np.pi * 880 * t) * 0.3 +
                  np.random.normal(0, 0.1, len(t)))
    audio_data = audio_data / np.max(np.abs(audio_data))

# تبدیل به مونو در صورت استریو
if len(audio_data.shape) > 1:
    audio_data = np.mean(audio_data, axis=1)

# پارامترهای فریم
frame_length_ms = 20  # طول فریم به میلی‌ثانیه
frame_length = int(sample_rate * frame_length_ms / 1000)  # طول فریم به نمونه
frame_shift_ms = 10  # جابجایی فریم به میلی‌ثانیه
frame_shift = int(sample_rate * frame_shift_ms / 1000)  # جابجایی فریم به نمونه

print(f"\nپارامترهای فریم:")
print(f"طول فریم: {frame_length_ms} ms ({frame_length} نمونه)")
print(f"جابجایی فریم: {frame_shift_ms} ms ({frame_shift} نمونه)")

# تقسیم به فریم‌ها
num_frames = int((len(audio_data) - frame_length) / frame_shift) + 1
frames = []
for i in range(num_frames):
    start = i * frame_shift
    end = start + frame_length
    if end > len(audio_data):
        frame = np.pad(audio_data[start:], (0, end - len(audio_data)), 'constant')
    else:
        frame = audio_data[start:end]
    frames.append(frame)

frames = np.array(frames)
print(f"تعداد فریم‌ها: {num_frames}")

# محاسبه انرژی کوتاه‌مدت
short_term_energy = []
for frame in frames:
    energy = np.sum(frame ** 2)
    short_term_energy.append(energy)

short_term_energy = np.array(short_term_energy)

# محاسبه دامنه کوتاه‌مدت (RMS)
short_term_amplitude = []
for frame in frames:
    rms = np.sqrt(np.mean(frame ** 2))
    short_term_amplitude.append(rms)

short_term_amplitude = np.array(short_term_amplitude)

# محاسبه محور زمان برای فریم‌ها
frame_times = np.arange(num_frames) * frame_shift / sample_rate

# ایجاد نمودار
plt.figure(figsize=(14, 10))

# تنظیم فونت فارسی (اگر فونت خاصی دارید مسیر آن را بدهید، در غیر این صورت نام فونت نصب شده را بنویسید)
# plt.rcParams['font.family'] = 'Vazir'

# نمودار سیگنال اصلی
time_axis = np.arange(len(audio_data)) / sample_rate
plt.subplot(4, 1, 1)
plt.plot(time_axis, audio_data, linewidth=0.5)
plt.title(farsi_text('سیگنال صوتی اصلی'), fontsize=14)
plt.xlabel(farsi_text('زمان (ثانیه)'), fontsize=12)
plt.ylabel(farsi_text('دامنه'), fontsize=12)
plt.grid(True, alpha=0.3)

# نمودار انرژی کوتاه‌مدت
plt.subplot(4, 1, 2)
plt.plot(frame_times, short_term_energy, 'b-', linewidth=1.5)
plt.title(farsi_text('انرژی کوتاه‌مدت'), fontsize=14)
plt.xlabel(farsi_text('زمان (ثانیه)'), fontsize=12)
plt.ylabel(farsi_text('انرژی'), fontsize=12)
plt.grid(True, alpha=0.3)

# نمودار دامنه کوتاه‌مدت (RMS)
plt.subplot(4, 1, 3)
plt.plot(frame_times, short_term_amplitude, 'g-', linewidth=1.5)
plt.title(farsi_text('دامنه کوتاه‌مدت (RMS)'), fontsize=14)
plt.xlabel(farsi_text('زمان (ثانیه)'), fontsize=12)
plt.ylabel(farsi_text('دامنه RMS'), fontsize=12)
plt.grid(True, alpha=0.3)

# نمودار لگاریتم انرژی
plt.subplot(4, 1, 4)
log_energy = np.log10(short_term_energy + 1e-10)  # اضافه کردن مقدار کوچک برای جلوگیری از log(0)
plt.plot(frame_times, log_energy, 'r-', linewidth=1.5)
plt.title(farsi_text('لگاریتم انرژی کوتاه‌مدت'), fontsize=14)
plt.xlabel(farsi_text('زمان (ثانیه)'), fontsize=12)
plt.ylabel(farsi_text('log(انرژی)'), fontsize=12)
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('part1b_short_term_energy.png', dpi=150, bbox_inches='tight')
print("\nنمودار در فایل 'part1b_short_term_energy.png' ذخیره شد.")
plt.show()

# نمایش آمار
print(f"\nآمار انرژی کوتاه‌مدت:")
print(f"حداقل: {np.min(short_term_energy):.6f}")
print(f"حداکثر: {np.max(short_term_energy):.6f}")
print(f"میانگین: {np.mean(short_term_energy):.6f}")
print(f"انحراف معیار: {np.std(short_term_energy):.6f}")

