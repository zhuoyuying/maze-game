import wave
import math
import struct
import random
from pathlib import Path

def generate_sine_wave(frequency, duration, amplitude=0.5, sample_rate=44100):
    n_samples = int(sample_rate * duration)
    samples = []
    for i in range(n_samples):
        t = i / sample_rate
        sample = amplitude * math.sin(2 * math.pi * frequency * t)
        samples.append(sample)
    return samples

def save_wave_file(filename, samples, sample_rate=44100):
    # 确保samples在-1到1之间
    max_amplitude = max(abs(min(samples)), abs(max(samples)))
    if max_amplitude > 1:
        samples = [s / max_amplitude for s in samples]
    
    # 转换为16位整数
    samples = [int(s * 32767) for s in samples]
    
    with wave.open(filename, 'w') as wav_file:
        # 设置参数
        n_channels = 1
        sampwidth = 2
        
        # 设置文件参数
        wav_file.setnchannels(n_channels)
        wav_file.setsampwidth(sampwidth)
        wav_file.setframerate(sample_rate)
        
        # 写入数据
        for sample in samples:
            wav_file.writeframes(struct.pack('h', sample))

def create_key_sound():
    # 创建一个清脆的拾取音效
    duration = 0.15
    samples = []
    base_freq = 880  # A5音
    
    # 添加主音
    samples.extend(generate_sine_wave(base_freq, duration, 0.5))
    # 添加泛音
    samples = [s + 0.3 * s2 for s, s2 in zip(samples, generate_sine_wave(base_freq * 1.5, duration, 0.3))]
    
    # 添加衰减
    decay = [math.exp(-4 * i / (44100 * duration)) for i in range(len(samples))]
    samples = [s * d for s, d in zip(samples, decay)]
    
    return samples

def create_door_sound():
    # 创建一个沉重的开门声
    duration = 0.3
    samples = []
    base_freq = 220  # A3音
    
    # 添加基础音
    samples.extend(generate_sine_wave(base_freq, duration, 0.6))
    # 添加摩擦声
    noise = [random.uniform(-0.2, 0.2) for _ in range(int(44100 * duration))]
    samples = [s + n for s, n in zip(samples, noise)]
    
    # 添加衰减
    decay = [math.exp(-3 * i / (44100 * duration)) for i in range(len(samples))]
    samples = [s * d for s, d in zip(samples, decay)]
    
    return samples

def create_win_sound():
    # 创建胜利音效（上升的音阶）
    duration = 0.8
    samples = []
    frequencies = [440, 554, 659, 880]  # A4, C#5, E5, A5
    
    for freq in frequencies:
        # 为每个音符生成样本
        note_samples = generate_sine_wave(freq, duration/len(frequencies), 0.4)
        # 添加泛音
        harmonics = generate_sine_wave(freq * 1.5, duration/len(frequencies), 0.2)
        note_samples = [s + h for s, h in zip(note_samples, harmonics)]
        samples.extend(note_samples)
    
    # 添加渐变
    envelope = []
    attack = int(44100 * 0.1)  # 100ms attack
    decay = int(44100 * 0.3)   # 300ms decay
    for i in range(len(samples)):
        if i < attack:
            envelope.append(i / attack)
        elif i < attack + decay:
            envelope.append(1.0 - 0.5 * (i - attack) / decay)
        else:
            envelope.append(0.5)
    
    samples = [s * e for s, e in zip(samples, envelope)]
    return samples

def create_monster_sound():
    # 创建怪物音效（低沉的咆哮）
    duration = 0.5
    samples = []
    base_freq = 110  # A2音
    
    # 基础咆哮声
    base_samples = generate_sine_wave(base_freq, duration, 0.6)
    # 添加频率调制
    mod_freq = 5  # 5Hz的调制
    modulation = [1 + 0.2 * math.sin(2 * math.pi * mod_freq * t) for t in range(len(base_samples))]
    samples = [s * m for s, m in zip(base_samples, modulation)]
    
    # 添加噪声
    noise = [random.uniform(-0.3, 0.3) for _ in range(len(samples))]
    samples = [s + n for s, n in zip(samples, noise)]
    
    return samples

def create_death_sound():
    # 创建死亡音效（下降的音调加噪声）
    duration = 0.6
    samples = []
    start_freq = 440  # A4
    end_freq = 110    # A2
    
    # 生成下降的音调
    n_samples = int(44100 * duration)
    for i in range(n_samples):
        t = i / 44100
        freq = start_freq + (end_freq - start_freq) * t / duration
        sample = 0.5 * math.sin(2 * math.pi * freq * t)
        samples.append(sample)
    
    # 添加噪声
    noise = [random.uniform(-0.3, 0.3) for _ in range(len(samples))]
    samples = [s + n for s, n in zip(samples, noise)]
    
    # 添加衰减
    decay = [math.exp(-3 * i / len(samples)) for i in range(len(samples))]
    samples = [s * d for s, d in zip(samples, decay)]
    
    return samples

def main():
    # 创建资源目录
    resource_dir = Path("resources")
    resource_dir.mkdir(exist_ok=True)
    
    # 生成并保存所有音效
    sound_generators = {
        'key.wav': create_key_sound,
        'door.wav': create_door_sound,
        'win.wav': create_win_sound,
        'monster.wav': create_monster_sound,
        'death.wav': create_death_sound
    }
    
    for filename, generator in sound_generators.items():
        filepath = resource_dir / filename
        samples = generator()
        save_wave_file(str(filepath), samples)
        print(f"Created {filename}")

if __name__ == "__main__":
    main() 