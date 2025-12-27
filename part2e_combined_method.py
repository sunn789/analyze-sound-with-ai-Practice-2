"""
بخش 2e: استفاده از ترکیب اتوکرولیشن و ZCR برای بهبود تشخیص
و رسم نمودار نهایی سیگنال با بخش‌های واکدار، بی‌واک و سکوت مشخص‌شده
"""

import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
from scipy import signal

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

# محاسبه اتوکرولیشن
def calculate_autocorrelation(frame, max_lag=None):
    if max_lag is None:
        max_lag = len(frame) // 2
    
    frame_normalized = frame - np.mean(frame)
    autocorr = np.correlate(frame_normalized, frame_normalized, mode='full')
    autocorr = autocorr[len(autocorr)//2:]
    autocorr = autocorr[:max_lag+1]
    
    if autocorr[0] > 0:
        autocorr = autocorr / autocorr[0]
    
    return autocorr

# محاسبه ویژگی‌های اتوکرولیشن
min_f0 = 80
max_f0 = 400
min_lag = int(sample_rate / max_f0)
max_lag = int(sample_rate / min_f0)

autocorr_strength = []
f0_values = []

for frame in frames:
    autocorr = calculate_autocorrelation(frame, max_lag=max_lag*2)
    
    search_range = autocorr[min_lag:max_lag+1]
    if len(search_range) > 0:
        peak_idx = np.argmax(search_range) + min_lag
        peak_value = autocorr[peak_idx]
        peak_lag = peak_idx
    else:
        peak_value = 0
        peak_lag = 0
    
    autocorr_strength.append(peak_value)
    if peak_lag > 0:
        f0_values.append(sample_rate / peak_lag)
    else:
        f0_values.append(0)

autocorr_strength = np.array(autocorr_strength)
f0_values = np.array(f0_values)

# نرمال‌سازی ویژگی‌ها برای ترکیب
energy_norm = (short_term_energy - np.min(short_term_energy)) / \
              (np.max(short_term_energy) - np.min(short_term_energy) + 1e-10)
zcr_norm = (zcr_values - np.min(zcr_values)) / \
           (np.max(zcr_values) - np.min(zcr_values) + 1e-10)
autocorr_norm = (autocorr_strength - np.min(autocorr_strength)) / \
                (np.max(autocorr_strength) - np.min(autocorr_strength) + 1e-10)

# محاسبه آستانه‌ها
energy_mean = np.mean(short_term_energy)
energy_std = np.std(short_term_energy)
zcr_mean = np.mean(zcr_values)
zcr_std = np.std(zcr_values)
autocorr_mean = np.mean(autocorr_strength)
autocorr_std = np.std(autocorr_strength)

# آستانه‌های بهبود یافته با ترکیب روش‌ها
silence_energy_threshold = energy_mean - 0.5 * energy_std

# واکدار: انرژی بالا، ZCR پایین، و اتوکرولیشن قوی
voiced_energy_threshold = energy_mean + 0.2 * energy_std
voiced_zcr_threshold = zcr_mean - 0.2 * zcr_std
voiced_autocorr_threshold = autocorr_mean + 0.2 * autocorr_std

# بی‌واک: انرژی متوسط، ZCR بالا، اتوکرولیشن ضعیف
unvoiced_zcr_threshold = zcr_mean + 0.2 * zcr_std
unvoiced_autocorr_threshold = autocorr_mean - 0.2 * autocorr_std

print(f"\nآستانه‌های ترکیبی:")
print(f"آستانه انرژی سکوت: {silence_energy_threshold:.6f}")
print(f"آستانه انرژی واکدار: {voiced_energy_threshold:.6f}")
print(f"آستانه ZCR واکدار: {voiced_zcr_threshold:.4f}")
print(f"آستانه ZCR بی‌واک: {unvoiced_zcr_threshold:.4f}")
print(f"آستانه اتوکرولیشن واکدار: {voiced_autocorr_threshold:.4f}")
print(f"آستانه اتوکرولیشن بی‌واک: {unvoiced_autocorr_threshold:.4f}")

# طبقه‌بندی ترکیبی
# 0: سکوت, 1: بی‌واک, 2: واکدار
classification_combined = np.zeros(num_frames, dtype=int)

for i in range(num_frames):
    energy = short_term_energy[i]
    zcr = zcr_values[i]
    autocorr = autocorr_strength[i]
    
    # اول سکوت را بررسی می‌کنیم
    if energy < silence_energy_threshold:
        classification_combined[i] = 0  # سکوت
    # سپس واکدار را بررسی می‌کنیم (باید همه شرایط را داشته باشد)
    elif (energy > voiced_energy_threshold and 
          zcr < voiced_zcr_threshold and 
          autocorr > voiced_autocorr_threshold):
        classification_combined[i] = 2  # واکدار
    # در غیر این صورت بی‌واک
    else:
        classification_combined[i] = 1  # بی‌واک

# شمارش فریم‌های هر دسته
silence_count = np.sum(classification_combined == 0)
unvoiced_count = np.sum(classification_combined == 1)
voiced_count = np.sum(classification_combined == 2)

print(f"\nنتایج طبقه‌بندی ترکیبی:")
print(f"سکوت: {silence_count} فریم ({silence_count/num_frames*100:.1f}%)")
print(f"بی‌واک: {unvoiced_count} فریم ({unvoiced_count/num_frames*100:.1f}%)")
print(f"واکدار: {voiced_count} فریم ({voiced_count/num_frames*100:.1f}%)")

# ایجاد نمودار نهایی
plt.figure(figsize=(16, 12))

# نمودار سیگنال اصلی
time_axis = np.arange(len(audio_data)) / sample_rate
plt.subplot(6, 1, 1)
plt.plot(time_axis, audio_data, 'b-', linewidth=0.5)
plt.title('سیگنال صوتی اصلی', fontsize=14, fontfamily='DejaVu Sans')
plt.xlabel('زمان (ثانیه)', fontsize=12)
plt.ylabel('دامنه', fontsize=12)
plt.grid(True, alpha=0.3)

# نمودار انرژی
plt.subplot(6, 1, 2)
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
plt.subplot(6, 1, 3)
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

# نمودار قدرت اتوکرولیشن
plt.subplot(6, 1, 4)
plt.plot(frame_times, autocorr_strength, 'g-', linewidth=1.5, 
         label='قدرت قله اتوکرولیشن')
plt.axhline(y=voiced_autocorr_threshold, color='g', linestyle='--', 
            label='آستانه واکدار', alpha=0.7)
plt.axhline(y=unvoiced_autocorr_threshold, color='orange', linestyle='--', 
            label='آستانه بی‌واک', alpha=0.7)
plt.title('قدرت قله اتوکرولیشن', fontsize=14, fontfamily='DejaVu Sans')
plt.xlabel('زمان (ثانیه)', fontsize=12)
plt.ylabel('قدرت', fontsize=12)
plt.legend()
plt.grid(True, alpha=0.3)

# نمودار طبقه‌بندی
plt.subplot(6, 1, 5)
colors = ['gray', 'orange', 'green']
labels = ['سکوت', 'بی‌واک', 'واکدار']
for i, (color, label) in enumerate(zip(colors, labels)):
    mask = classification_combined == i
    if np.any(mask):
        plt.scatter(frame_times[mask], classification_combined[mask], 
                   c=color, label=label, s=20, alpha=0.6)
plt.title('طبقه‌بندی نهایی (ترکیب ZCR + انرژی + اتوکرولیشن)', 
          fontsize=14, fontfamily='DejaVu Sans')
plt.xlabel('زمان (ثانیه)', fontsize=12)
plt.ylabel('دسته', fontsize=12)
plt.yticks([0, 1, 2], labels)
plt.legend()
plt.grid(True, alpha=0.3, axis='y')

# نمودار نهایی: سیگنال با رنگ‌بندی
plt.subplot(6, 1, 6)
# ایجاد یک سیگنال رنگی بر اساس طبقه‌بندی
colored_signal = np.zeros_like(audio_data)
for i in range(num_frames):
    start = i * frame_shift
    end = min(start + frame_length, len(audio_data))
    colored_signal[start:end] = classification_combined[i]

# رسم با رنگ‌بندی
for i, (color, label) in enumerate(zip(colors, labels)):
    mask = colored_signal == i
    if np.any(mask):
        plt.plot(time_axis[mask], audio_data[mask], 
                color=color, linewidth=1.5, label=label, alpha=0.8)

plt.title('سیگنال نهایی با بخش‌های واکدار، بی‌واک و سکوت مشخص‌شده', 
          fontsize=14, fontfamily='DejaVu Sans')
plt.xlabel('زمان (ثانیه)', fontsize=12)
plt.ylabel('دامنه', fontsize=12)
plt.legend(loc='upper right')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('part2e_combined_method.png', dpi=150, bbox_inches='tight')
print("\nنمودار نهایی در فایل 'part2e_combined_method.png' ذخیره شد.")
plt.show()

# ایجاد یک نمودار خلاصه و زیبا
plt.figure(figsize=(16, 8))

# نمودار اصلی با رنگ‌بندی
plt.subplot(2, 1, 1)
for i, (color, label) in enumerate(zip(colors, labels)):
    mask = colored_signal == i
    if np.any(mask):
        plt.plot(time_axis[mask], audio_data[mask], 
                color=color, linewidth=2, label=label, alpha=0.9)

plt.title('سیگنال صوتی با طبقه‌بندی: واکدار (سبز)، بی‌واک (نارنجی)، سکوت (خاکستری)', 
          fontsize=16, fontfamily='DejaVu Sans', fontweight='bold')
plt.xlabel('زمان (ثانیه)', fontsize=14)
plt.ylabel('دامنه', fontsize=14)
plt.legend(loc='upper right', fontsize=12)
plt.grid(True, alpha=0.3)

# نمودار ویژگی‌های ترکیبی
plt.subplot(2, 1, 2)
ax1 = plt.gca()
ax1.plot(frame_times, energy_norm, 'b-', linewidth=1.5, label='انرژی (نرمال‌سازی)', alpha=0.7)
ax1.plot(frame_times, 1 - zcr_norm, 'r-', linewidth=1.5, label='1-ZCR (نرمال‌سازی)', alpha=0.7)
ax1.plot(frame_times, autocorr_norm, 'g-', linewidth=1.5, label='اتوکرولیشن (نرمال‌سازی)', alpha=0.7)
ax1.set_xlabel('زمان (ثانیه)', fontsize=14)
ax1.set_ylabel('مقدار نرمال‌سازی شده', fontsize=14)
ax1.legend(loc='upper right', fontsize=11)
ax1.grid(True, alpha=0.3)

# اضافه کردن نشان‌گذاری طبقه‌بندی
for i, (color, label) in enumerate(zip(colors, labels)):
    mask = classification_combined == i
    if np.any(mask):
        ax1.scatter(frame_times[mask], np.ones(np.sum(mask)) * (0.95 - i*0.1), 
                   c=color, label=f'{label} (طبقه‌بندی)', s=15, alpha=0.6, marker='|')

plt.title('ویژگی‌های ترکیبی و طبقه‌بندی نهایی', 
          fontsize=16, fontfamily='DejaVu Sans', fontweight='bold')

plt.tight_layout()
plt.savefig('part2e_final_result.png', dpi=150, bbox_inches='tight')
print("نمودار نهایی خلاصه در فایل 'part2e_final_result.png' ذخیره شد.")
plt.show()

# ذخیره نتایج نهایی
np.save('classification_combined.npy', classification_combined)
print("\nنتایج نهایی در فایل 'classification_combined.npy' ذخیره شد.")

