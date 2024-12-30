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

def create_note(frequency, duration, waveform='sine'):
    samples = []
    n_samples = int(44100 * duration)
    for i in range(n_samples):
        t = i / 44100
        if waveform == 'sine':
            sample = math.sin(2 * math.pi * frequency * t)
        elif waveform == 'square':
            sample = 1.0 if math.sin(2 * math.pi * frequency * t) > 0 else -1.0
        elif waveform == 'sawtooth':
            sample = 2.0 * (frequency * t - math.floor(0.5 + frequency * t))
        samples.append(sample * 0.5)  # 减小音量
    return samples

def create_background_music():
    # 音乐参数
    bpm = 90  # 每分钟节拍数
    beat_duration = 60 / bpm  # 一拍的持续时间
    
    # 音符频率（以A4=440Hz为基准）
    notes = {
        'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23,
        'G4': 392.00, 'A4': 440.00, 'B4': 493.88, 'C5': 523.25
    }
    
    # 创建旋律
    melody = []
    melody_sequence = [
        ('E4', 1), ('G4', 1), ('A4', 2),
        ('G4', 1), ('E4', 1), ('C4', 2),
        ('D4', 1), ('F4', 1), ('G4', 2),
        ('F4', 1), ('D4', 1), ('C4', 2),
    ]
    
    # 生成旋律
    for note, beats in melody_sequence:
        duration = beat_duration * beats
        note_samples = create_note(notes[note], duration, 'sine')
        # 添加简单的包络
        envelope = []
        attack = int(44100 * 0.05)  # 50ms attack
        decay = int(44100 * 0.1)    # 100ms decay
        for i in range(len(note_samples)):
            if i < attack:
                envelope.append(i / attack)
            elif i < attack + decay:
                envelope.append(1.0 - 0.3 * (i - attack) / decay)
            else:
                envelope.append(0.7)
        melody.extend([s * e for s, e in zip(note_samples, envelope)])
    
    # 创建简单的和弦伴奏
    chords = []
    chord_sequence = [
        (['C4', 'E4', 'G4'], 4),
        (['F4', 'A4', 'C5'], 4),
        (['G4', 'B4', 'D4'], 4),
    ]
    
    # 生成和弦
    for chord_notes, beats in chord_sequence:
        duration = beat_duration * beats
        chord_samples = [0] * int(44100 * duration)
        for note in chord_notes:
            note_samples = create_note(notes[note], duration, 'sine')
            chord_samples = [a + b * 0.3 for a, b in zip(chord_samples, note_samples)]
        chords.extend(chord_samples)
    
    # 合并旋律和和弦
    # 重复几次以创建更长的音乐
    combined = []
    repeats = 4
    for _ in range(repeats):
        for m, c in zip(melody, chords):
            combined.append(m * 0.7 + c * 0.3)  # 混合旋律和和弦
    
    return combined

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

def main():
    # 创建资源目录
    resource_dir = Path("resources")
    resource_dir.mkdir(exist_ok=True)
    
    # 生成并保存背景音乐
    print("Generating background music...")
    music_samples = create_background_music()
    save_wave_file(str(resource_dir / "background.wav"), music_samples)
    print("Created background.wav")

if __name__ == "__main__":
    main() 