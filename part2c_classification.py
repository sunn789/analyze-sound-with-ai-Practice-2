"""
بخش 2c: طبقه‌بندی فریم‌ها به سه دسته واکدار، بی‌واک و سکوت
بر اساس ویژگی‌های ZCR و انرژی کوتاه‌مدت
"""

import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf

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

# محاسبه ZCR
def calculate_zcr(frame):
    signs = np.sign(frame)
    zero_crossings = np.where(np.diff(signs) != 0)[0]
    zcr = len(zero_crossings) / len(frame)
    return zcr

zcr_values = np.array([calculate_zcr(frame) for frame in frames])

# محاسبه انرژی کوتاه‌مدت
short_term_energy = np.array([np.sum(frame ** 2) for frame in frames])

# محاسبه آمار برای تعیین آستانه‌ها
energy_mean = np.mean(short_term_energy)
energy_std = np.std(short_term_energy)
zcr_mean = np.mean(zcr_values)
zcr_std = np.std(zcr_values)

print(f"\nآمار انرژی:")
print(f"میانگین: {energy_mean:.6f}")
print(f"انحراف معیار: {energy_std:.6f}")

print(f"\nآمار ZCR:")
print(f"میانگین: {zcr_mean:.4f}")
print(f"انحراف معیار: {zcr_std:.4f}")

# تعیین آستانه‌ها
# سکوت: انرژی پایین
silence_energy_threshold = energy_mean - 0.5 * energy_std

# واکدار: انرژی بالا و ZCR پایین
voiced_energy_threshold = energy_mean + 0.3 * energy_std
voiced_zcr_threshold = zcr_mean - 0.3 * zcr_std

# بی‌واک: انرژی متوسط و ZCR بالا
unvoiced_zcr_threshold = zcr_mean + 0.3 * zcr_std

print(f"\nآستانه‌های طبقه‌بندی:")
print(f"آستانه انرژی سکوت: {silence_energy_threshold:.6f}")
print(f"آستانه انرژی واکدار: {voiced_energy_threshold:.6f}")
print(f"آستانه ZCR واکدار: {voiced_zcr_threshold:.4f}")
print(f"آستانه ZCR بی‌واک: {unvoiced_zcr_threshold:.4f}")

# طبقه‌بندی فریم‌ها
# 0: سکوت, 1: بی‌واک, 2: واکدار
classification = np.zeros(num_frames, dtype=int)

for i in range(num_frames):
    energy = short_term_energy[i]
    zcr = zcr_values[i]
    
    # اول سکوت را بررسی می‌کنیم
    if energy < silence_energy_threshold:
        classification[i] = 0  # سکوت
    # سپس واکدار را بررسی می‌کنیم
    elif energy > voiced_energy_threshold and zcr < voiced_zcr_threshold:
        classification[i] = 2  # واکدار
    # در غیر این صورت بی‌واک
    else:
        classification[i] = 1  # بی‌واک

# شمارش فریم‌های هر دسته
silence_count = np.sum(classification == 0)
unvoiced_count = np.sum(classification == 1)
voiced_count = np.sum(classification == 2)

print(f"\nنتایج طبقه‌بندی:")
print(f"سکوت: {silence_count} فریم ({silence_count/num_frames*100:.1f}%)")
print(f"بی‌واک: {unvoiced_count} فریم ({unvoiced_count/num_frames*100:.1f}%)")
print(f"واکدار: {voiced_count} فریم ({voiced_count/num_frames*100:.1f}%)")

# ایجاد نمودار
plt.figure(figsize=(14, 10))

# نمودار سیگنال اصلی
time_axis = np.arange(len(audio_data)) / sample_rate
plt.subplot(5, 1, 1)
plt.plot(time_axis, audio_data, 'b-', linewidth=0.5)
plt.title('سیگنال صوتی اصلی', fontsize=14, fontfamily='DejaVu Sans')
plt.xlabel('زمان (ثانیه)', fontsize=12)
plt.ylabel('دامنه', fontsize=12)
plt.grid(True, alpha=0.3)

# نمودار انرژی
plt.subplot(5, 1, 2)
plt.plot(frame_times, short_term_energy, 'b-', linewidth=1.5, label='انرژی')
plt.axhline(y=silence_energy_threshold, color='r', linestyle='--', 
            label='آستانه سکوت', alpha=0.7)
plt.axhline(y=voiced_energy_threshold, color='g', linestyle='--', 
            label='آستانه واکدار', alpha=0.7)
plt.title('انرژی کوتاه‌مدت', fontsize=14, fontfamily='DejaVu Sans')
plt.xlabel('زمان (ثانیه)', fontsize=12)
plt.ylabel('انرژی', fontsize=12)
plt.legend()
plt.grid(True, alpha=0.3)

# نمودار ZCR
plt.subplot(5, 1, 3)
plt.plot(frame_times, zcr_values, 'r-', linewidth=1.5, label='ZCR')
plt.axhline(y=voiced_zcr_threshold, color='g', linestyle='--', 
            label='آستانه واکدار', alpha=0.7)
plt.axhline(y=unvoiced_zcr_threshold, color='orange', linestyle='--', 
            label='آستانه بی‌واک', alpha=0.7)
plt.title('نرخ عبور از صفر (ZCR)', fontsize=14, fontfamily='DejaVu Sans')
plt.xlabel('زمان (ثانیه)', fontsize=12)
plt.ylabel('ZCR', fontsize=12)
plt.legend()
plt.grid(True, alpha=0.3)

# نمودار طبقه‌بندی
plt.subplot(5, 1, 4)
colors = ['gray', 'orange', 'green']
labels = ['سکوت', 'بی‌واک', 'واکدار']
for i, (color, label) in enumerate(zip(colors, labels)):
    mask = classification == i
    if np.any(mask):
        plt.scatter(frame_times[mask], classification[mask], 
                   c=color, label=label, s=20, alpha=0.6)
plt.title('طبقه‌بندی فریم‌ها', fontsize=14, fontfamily='DejaVu Sans')
plt.xlabel('زمان (ثانیه)', fontsize=12)
plt.ylabel('دسته', fontsize=12)
plt.yticks([0, 1, 2], labels)
plt.legend()
plt.grid(True, alpha=0.3, axis='y')

# نمودار سیگنال با رنگ‌بندی بر اساس طبقه‌بندی
plt.subplot(5, 1, 5)
# ایجاد یک سیگنال رنگی بر اساس طبقه‌بندی
colored_signal = np.zeros_like(audio_data)
for i in range(num_frames):
    start = i * frame_shift
    end = min(start + frame_length, len(audio_data))
    colored_signal[start:end] = classification[i]

# رسم با رنگ‌بندی
for i, (color, label) in enumerate(zip(colors, labels)):
    mask = colored_signal == i
    if np.any(mask):
        plt.plot(time_axis[mask], audio_data[mask], 
                color=color, linewidth=1, label=label, alpha=0.7)

plt.title('سیگنال با رنگ‌بندی بر اساس طبقه‌بندی', 
          fontsize=14, fontfamily='DejaVu Sans')
plt.xlabel('زمان (ثانیه)', fontsize=12)
plt.ylabel('دامنه', fontsize=12)
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('part2c_classification.png', dpi=150, bbox_inches='tight')
print("\nنمودار در فایل 'part2c_classification.png' ذخیره شد.")
plt.show()

# ذخیره نتایج
np.save('classification.npy', classification)
print("نتایج طبقه‌بندی در فایل 'classification.npy' ذخیره شد.")

