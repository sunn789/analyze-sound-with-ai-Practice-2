"""
بخش 2b: محاسبه ZCR (Zero Crossing Rate) برای هر فریم و رسم نمودار تغییرات
این فایل نرخ عبور از صفر را برای هر فریم محاسبه می‌کند.
"""

import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
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
frame_length_ms = 20
frame_length = int(sample_rate * frame_length_ms / 1000)
frame_shift_ms = 10
frame_shift = int(sample_rate * frame_shift_ms / 1000)

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
frame_times = np.arange(num_frames) * frame_shift / sample_rate

print(f"تعداد فریم‌ها: {num_frames}")
print(f"طول هر فریم: {frame_length} نمونه")

# محاسبه ZCR برای هر فریم
def calculate_zcr(frame):
    """
    محاسبه نرخ عبور از صفر (Zero Crossing Rate)
    ZCR = تعداد تغییرات علامت / طول فریم
    """
    # محاسبه تغییرات علامت
    signs = np.sign(frame)
    # پیدا کردن نقاط عبور از صفر
    zero_crossings = np.where(np.diff(signs) != 0)[0]
    # نرمال‌سازی بر اساس طول فریم
    zcr = len(zero_crossings) / len(frame)
    return zcr

zcr_values = []
for frame in frames:
    zcr = calculate_zcr(frame)
    zcr_values.append(zcr)

zcr_values = np.array(zcr_values)

# محاسبه ZCR به صورت نرمال‌سازی شده بر اساس نرخ نمونه‌برداری
zcr_normalized = zcr_values * sample_rate / (2 * frame_length)  # نرمال‌سازی

print(f"\nآمار ZCR:")
print(f"حداقل: {np.min(zcr_values):.4f}")
print(f"حداکثر: {np.max(zcr_values):.4f}")
print(f"میانگین: {np.mean(zcr_values):.4f}")
print(f"انحراف معیار: {np.std(zcr_values):.4f}")

# محاسبه انرژی کوتاه‌مدت برای مقایسه
short_term_energy = []
for frame in frames:
    energy = np.sum(frame ** 2)
    short_term_energy.append(energy)
short_term_energy = np.array(short_term_energy)

# ایجاد نمودار
plt.figure(figsize=(14, 10))

# تنظیم فونت فارسی (اگر فونت خاصی دارید مسیر آن را بدهید، در غیر این صورت نام فونت نصب شده را بنویسید)
# plt.rcParams['font.family'] = 'Vazir'

# نمودار سیگنال اصلی
time_axis = np.arange(len(audio_data)) / sample_rate
plt.subplot(4, 1, 1)
plt.plot(time_axis, audio_data, 'b-', linewidth=0.5)
plt.title(farsi_text('سیگنال صوتی اصلی'), fontsize=14)
plt.xlabel(farsi_text('زمان (ثانیه)'), fontsize=12)
plt.ylabel(farsi_text('دامنه'), fontsize=12)
plt.grid(True, alpha=0.3)

# نمودار ZCR
plt.subplot(4, 1, 2)
plt.plot(frame_times, zcr_values, 'r-', linewidth=1.5, label='ZCR')
plt.axhline(y=np.mean(zcr_values), color='g', linestyle='--', 
            label=farsi_text(f'میانگین: {np.mean(zcr_values):.4f}'), alpha=0.7)
plt.title(farsi_text('نرخ عبور از صفر (ZCR) برای هر فریم'), fontsize=14)
plt.xlabel(farsi_text('زمان (ثانیه)'), fontsize=12)
plt.ylabel('ZCR', fontsize=12)
plt.legend()
plt.grid(True, alpha=0.3)

# نمودار ZCR نرمال‌سازی شده
plt.subplot(4, 1, 3)
plt.plot(frame_times, zcr_normalized, 'm-', linewidth=1.5, label=farsi_text('ZCR نرمال‌سازی شده'))
plt.axhline(y=np.mean(zcr_normalized), color='g', linestyle='--', 
            label=farsi_text(f'میانگین: {np.mean(zcr_normalized):.2f}'), alpha=0.7)
plt.title(farsi_text('ZCR نرمال‌سازی شده (نسبت به نرخ نمونه‌برداری)'), fontsize=14)
plt.xlabel(farsi_text('زمان (ثانیه)'), fontsize=12)
plt.ylabel(farsi_text('ZCR نرمال‌سازی شده'), fontsize=12)
plt.legend()
plt.grid(True, alpha=0.3)

# مقایسه ZCR و انرژی
plt.subplot(4, 1, 4)
ax1 = plt.gca()
ax1.plot(frame_times, zcr_values, 'r-', linewidth=1.5, label='ZCR')
ax1.set_xlabel(farsi_text('زمان (ثانیه)'), fontsize=12)
ax1.set_ylabel('ZCR', color='r', fontsize=12)
ax1.tick_params(axis='y', labelcolor='r')
ax1.grid(True, alpha=0.3)

ax2 = ax1.twinx()
energy_normalized = (short_term_energy - np.min(short_term_energy)) / \
                    (np.max(short_term_energy) - np.min(short_term_energy) + 1e-10)
ax2.plot(frame_times, energy_normalized, 'b-', linewidth=1.5, alpha=0.7, label=farsi_text('انرژی (نرمال‌سازی شده)'))
ax2.set_ylabel(farsi_text('انرژی (نرمال‌سازی شده)'), color='b', fontsize=12)
ax2.tick_params(axis='y', labelcolor='b')

plt.title(farsi_text('مقایسه ZCR و انرژی کوتاه‌مدت'), fontsize=14)
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

plt.tight_layout()
plt.savefig('part2b_zcr_calculation.png', dpi=150, bbox_inches='tight')
print("\nنمودار در فایل 'part2b_zcr_calculation.png' ذخیره شد.")
plt.show()

# ذخیره ZCR برای استفاده در بخش‌های بعدی
np.save('zcr_values.npy', zcr_values)
print("مقادیر ZCR در فایل 'zcr_values.npy' ذخیره شد.")

