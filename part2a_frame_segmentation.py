"""
بخش 2a: تقسیم سیگنال به فریم‌های زمانی کوتاه (20 میلی‌ثانیه)
این فایل سیگنال را به فریم‌های 20 میلی‌ثانیه‌ای تقسیم می‌کند.
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
frame_length_ms = 20  # طول فریم به میلی‌ثانیه
frame_length = int(sample_rate * frame_length_ms / 1000)  # طول فریم به نمونه
frame_shift_ms = 10  # جابجایی فریم به میلی‌ثانیه (50% overlap)
frame_shift = int(sample_rate * frame_shift_ms / 1000)  # جابجایی فریم به نمونه

print(f"\nپارامترهای فریم:")
print(f"نرخ نمونه‌برداری: {sample_rate} Hz")
print(f"طول فریم: {frame_length_ms} ms ({frame_length} نمونه)")
print(f"جابجایی فریم: {frame_shift_ms} ms ({frame_shift} نمونه)")
print(f"درصد همپوشانی: {(1 - frame_shift/frame_length)*100:.1f}%")

# تقسیم به فریم‌ها
num_frames = int((len(audio_data) - frame_length) / frame_shift) + 1
frames = []
frame_starts = []

for i in range(num_frames):
    start = i * frame_shift
    end = start + frame_length
    if end > len(audio_data):
        # padding برای آخرین فریم
        frame = np.pad(audio_data[start:], (0, end - len(audio_data)), 'constant')
    else:
        frame = audio_data[start:end]
    frames.append(frame)
    frame_starts.append(start)

frames = np.array(frames)
frame_starts = np.array(frame_starts)
frame_times = frame_starts / sample_rate

print(f"تعداد فریم‌ها: {num_frames}")
print(f"مدت زمان کل: {len(audio_data)/sample_rate:.2f} ثانیه")

# نمایش چند فریم اول
print(f"\nنمایش اطلاعات 5 فریم اول:")
for i in range(min(5, num_frames)):
    print(f"فریم {i+1}: شروع={frame_times[i]:.3f}s, طول={len(frames[i])} نمونه, "
          f"دامنه میانگین={np.mean(np.abs(frames[i])):.4f}")

# ایجاد نمودار
plt.figure(figsize=(14, 8))

# نمودار سیگنال اصلی با نشان‌گذاری فریم‌ها
time_axis = np.arange(len(audio_data)) / sample_rate
plt.subplot(3, 1, 1)
plt.plot(time_axis, audio_data, 'b-', linewidth=0.5, label='سیگنال اصلی')

# نمایش مرزهای فریم‌ها
for i in range(0, num_frames, max(1, num_frames//20)):  # نمایش هر 20 فریم
    frame_time = frame_times[i]
    plt.axvline(x=frame_time, color='r', linestyle='--', alpha=0.3, linewidth=0.5)

plt.title('سیگنال صوتی با نشان‌گذاری فریم‌های 20 میلی‌ثانیه‌ای', 
          fontsize=14, fontfamily='DejaVu Sans')
plt.xlabel('زمان (ثانیه)', fontsize=12)
plt.ylabel('دامنه', fontsize=12)
plt.legend()
plt.grid(True, alpha=0.3)

# نمایش چند فریم نمونه
plt.subplot(3, 1, 2)
num_sample_frames = min(10, num_frames)
for i in range(0, num_sample_frames, 2):
    frame_time_samples = np.arange(len(frames[i])) / sample_rate + frame_times[i]
    plt.plot(frame_time_samples, frames[i], linewidth=1, 
             label=f'فریم {i+1}' if i < 4 else '')
plt.title('نمایش چند فریم نمونه', fontsize=14, fontfamily='DejaVu Sans')
plt.xlabel('زمان (ثانیه)', fontsize=12)
plt.ylabel('دامنه', fontsize=12)
plt.legend()
plt.grid(True, alpha=0.3)

# نمایش توزیع طول فریم‌ها
plt.subplot(3, 1, 3)
frame_lengths = [len(frame) for frame in frames]
plt.hist(frame_lengths, bins=20, edgecolor='black', alpha=0.7)
plt.title('توزیع طول فریم‌ها', fontsize=14, fontfamily='DejaVu Sans')
plt.xlabel('طول فریم (تعداد نمونه)', fontsize=12)
plt.ylabel('تعداد فریم‌ها', fontsize=12)
plt.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('part2a_frame_segmentation.png', dpi=150, bbox_inches='tight')
print("\nنمودار در فایل 'part2a_frame_segmentation.png' ذخیره شد.")
plt.show()

# ذخیره اطلاعات فریم‌ها برای استفاده در بخش‌های بعدی
np.save('frames.npy', frames)
np.save('frame_times.npy', frame_times)
print("\nاطلاعات فریم‌ها در فایل‌های 'frames.npy' و 'frame_times.npy' ذخیره شد.")

