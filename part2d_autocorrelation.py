"""
بخش 2d: استفاده از اتوکرولیشن برای شناسایی بخش‌های واکدار
و مقایسه با روش‌های قبلی
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
num_frames = int((len(audio_data) - frame_length) / frame_shift) + 1)
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

# محاسبه ZCR (برای مقایسه)
def calculate_zcr(frame):
    signs = np.sign(frame)
    zero_crossings = np.where(np.diff(signs) != 0)[0]
    zcr = len(zero_crossings) / len(frame)
    return zcr

zcr_values = np.array([calculate_zcr(frame) for frame in frames])

# محاسبه انرژی کوتاه‌مدت (برای مقایسه)
short_term_energy = np.array([np.sum(frame ** 2) for frame in frames])

# محاسبه اتوکرولیشن برای هر فریم
def calculate_autocorrelation(frame, max_lag=None):
    """
    محاسبه اتوکرولیشن برای یک فریم
    """
    if max_lag is None:
        max_lag = len(frame) // 2
    
    # نرمال‌سازی فریم
    frame_normalized = frame - np.mean(frame)
    
    # محاسبه اتوکرولیشن
    autocorr = np.correlate(frame_normalized, frame_normalized, mode='full')
    autocorr = autocorr[len(autocorr)//2:]
    autocorr = autocorr[:max_lag+1]
    
    # نرمال‌سازی
    if autocorr[0] > 0:
        autocorr = autocorr / autocorr[0]
    
    return autocorr

# محاسبه ویژگی‌های اتوکرولیشن
autocorr_peaks = []  # قله اصلی اتوکرولیشن
autocorr_strength = []  # قدرت قله اصلی
autocorr_peak_lag = []  # تاخیر قله اصلی

# محدوده فرکانس پایه (F0) برای گفتار: 80-400 Hz
min_f0 = 80
max_f0 = 400
min_lag = int(sample_rate / max_f0)  # تاخیر حداکثر
max_lag = int(sample_rate / min_f0)  # تاخیر حداقل

print(f"\nمحدوده تاخیر برای F0:")
print(f"حداقل تاخیر (حداکثر F0): {min_lag} نمونه ({max_f0} Hz)")
print(f"حداکثر تاخیر (حداقل F0): {max_lag} نمونه ({min_f0} Hz)")

for frame in frames:
    autocorr = calculate_autocorrelation(frame, max_lag=max_lag*2)
    
    # جستجوی قله در محدوده F0
    search_range = autocorr[min_lag:max_lag+1]
    if len(search_range) > 0:
        peak_idx = np.argmax(search_range) + min_lag
        peak_value = autocorr[peak_idx]
        peak_lag = peak_idx
    else:
        peak_value = 0
        peak_lag = 0
    
    autocorr_peaks.append(peak_value)
    autocorr_strength.append(peak_value)
    autocorr_peak_lag.append(peak_lag)

autocorr_peaks = np.array(autocorr_peaks)
autocorr_strength = np.array(autocorr_strength)
autocorr_peak_lag = np.array(autocorr_peak_lag)

# محاسبه F0 از تاخیر قله
f0_values = np.zeros_like(autocorr_peak_lag, dtype=float)
f0_values[autocorr_peak_lag > 0] = sample_rate / autocorr_peak_lag[autocorr_peak_lag > 0]
f0_values[autocorr_peak_lag == 0] = 0

print(f"\nآمار اتوکرولیشن:")
print(f"میانگین قدرت قله: {np.mean(autocorr_strength):.4f}")
print(f"حداکثر قدرت قله: {np.max(autocorr_strength):.4f}")
print(f"میانگین F0 (برای فریم‌های واکدار): {np.mean(f0_values[f0_values > 0]):.2f} Hz")

# طبقه‌بندی بر اساس اتوکرولیشن
# واکدار: قدرت قله بالا
autocorr_threshold = np.mean(autocorr_strength) + 0.3 * np.std(autocorr_strength)
classification_autocorr = (autocorr_strength > autocorr_threshold).astype(int)

# طبقه‌بندی قبلی بر اساس ZCR و انرژی
energy_mean = np.mean(short_term_energy)
energy_std = np.std(short_term_energy)
zcr_mean = np.mean(zcr_values)
zcr_std = np.std(zcr_values)

silence_energy_threshold = energy_mean - 0.5 * energy_std
voiced_energy_threshold = energy_mean + 0.3 * energy_std
voiced_zcr_threshold = zcr_mean - 0.3 * zcr_std

classification_previous = np.zeros(num_frames, dtype=int)
for i in range(num_frames):
    if short_term_energy[i] < silence_energy_threshold:
        classification_previous[i] = 0  # سکوت
    elif short_term_energy[i] > voiced_energy_threshold and zcr_values[i] < voiced_zcr_threshold:
        classification_previous[i] = 2  # واکدار
    else:
        classification_previous[i] = 1  # بی‌واک

# مقایسه نتایج
voiced_autocorr = np.sum(classification_autocorr == 1)
voiced_previous = np.sum(classification_previous == 2)

print(f"\nمقایسه نتایج:")
print(f"واکدار (اتوکرولیشن): {voiced_autocorr} فریم ({voiced_autocorr/num_frames*100:.1f}%)")
print(f"واکدار (ZCR+انرژی): {voiced_previous} فریم ({voiced_previous/num_frames*100:.1f}%)")

# محاسبه همپوشانی
overlap = np.sum((classification_autocorr == 1) & (classification_previous == 2))
print(f"همپوشانی: {overlap} فریم ({overlap/num_frames*100:.1f}%)")

# ایجاد نمودار
plt.figure(figsize=(14, 12))

# نمودار سیگنال اصلی
time_axis = np.arange(len(audio_data)) / sample_rate
plt.subplot(6, 1, 1)
plt.plot(time_axis, audio_data, 'b-', linewidth=0.5)
plt.title('سیگنال صوتی اصلی', fontsize=14, fontfamily='DejaVu Sans')
plt.xlabel('زمان (ثانیه)', fontsize=12)
plt.ylabel('دامنه', fontsize=12)
plt.grid(True, alpha=0.3)

# نمودار قدرت اتوکرولیشن
plt.subplot(6, 1, 2)
plt.plot(frame_times, autocorr_strength, 'g-', linewidth=1.5, label='قدرت قله اتوکرولیشن')
plt.axhline(y=autocorr_threshold, color='r', linestyle='--', 
            label=f'آستانه: {autocorr_threshold:.3f}', alpha=0.7)
plt.title('قدرت قله اتوکرولیشن', fontsize=14, fontfamily='DejaVu Sans')
plt.xlabel('زمان (ثانیه)', fontsize=12)
plt.ylabel('قدرت', fontsize=12)
plt.legend()
plt.grid(True, alpha=0.3)

# نمودار F0
plt.subplot(6, 1, 3)
plt.plot(frame_times, f0_values, 'm-', linewidth=1.5, label='فرکانس پایه (F0)')
plt.title('فرکانس پایه (F0) از اتوکرولیشن', fontsize=14, fontfamily='DejaVu Sans')
plt.xlabel('زمان (ثانیه)', fontsize=12)
plt.ylabel('فرکانس (Hz)', fontsize=12)
plt.ylim([0, 500])
plt.legend()
plt.grid(True, alpha=0.3)

# نمودار ZCR (برای مقایسه)
plt.subplot(6, 1, 4)
plt.plot(frame_times, zcr_values, 'r-', linewidth=1.5, label='ZCR')
plt.axhline(y=voiced_zcr_threshold, color='g', linestyle='--', 
            label='آستانه واکدار', alpha=0.7)
plt.title('ZCR (برای مقایسه)', fontsize=14, fontfamily='DejaVu Sans')
plt.xlabel('زمان (ثانیه)', fontsize=12)
plt.ylabel('ZCR', fontsize=12)
plt.legend()
plt.grid(True, alpha=0.3)

# نمودار طبقه‌بندی با اتوکرولیشن
plt.subplot(6, 1, 5)
colors_autocorr = ['gray', 'green']
labels_autocorr = ['غیر واکدار', 'واکدار']
for i, (color, label) in enumerate(zip(colors_autocorr, labels_autocorr)):
    mask = classification_autocorr == i
    if np.any(mask):
        plt.scatter(frame_times[mask], classification_autocorr[mask], 
                   c=color, label=label, s=20, alpha=0.6)
plt.title('طبقه‌بندی با اتوکرولیشن', fontsize=14, fontfamily='DejaVu Sans')
plt.xlabel('زمان (ثانیه)', fontsize=12)
plt.ylabel('دسته', fontsize=12)
plt.yticks([0, 1], ['غیر واکدار', 'واکدار'])
plt.legend()
plt.grid(True, alpha=0.3, axis='y')

# نمودار مقایسه دو روش
plt.subplot(6, 1, 6)
plt.plot(frame_times, classification_previous, 'b-', linewidth=2, 
         label='ZCR+انرژی', alpha=0.7)
plt.plot(frame_times, classification_autocorr * 2, 'g--', linewidth=2, 
         label='اتوکرولیشن (واکدار=2)', alpha=0.7)
plt.title('مقایسه دو روش طبقه‌بندی', fontsize=14, fontfamily='DejaVu Sans')
plt.xlabel('زمان (ثانیه)', fontsize=12)
plt.ylabel('دسته', fontsize=12)
plt.yticks([0, 1, 2], ['سکوت', 'بی‌واک', 'واکدار'])
plt.legend()
plt.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('part2d_autocorrelation.png', dpi=150, bbox_inches='tight')
print("\nنمودار در فایل 'part2d_autocorrelation.png' ذخیره شد.")
plt.show()

# ذخیره نتایج
np.save('autocorr_strength.npy', autocorr_strength)
np.save('f0_values.npy', f0_values)
np.save('classification_autocorr.npy', classification_autocorr)
print("نتایج در فایل‌های مربوطه ذخیره شد.")

