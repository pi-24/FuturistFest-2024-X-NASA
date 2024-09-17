from PIL import Image
import numpy as np
from scipy.io.wavfile import write
import scipy.signal
from colorsys import rgb_to_hsv

def generate_sound_wave(frequency, duration, sample_rate, volume=0.3, overtone_factor=0.2):
    """Generates a soft sine wave with smooth overtones."""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    envelope = 0.5 * (1 - np.cos(np.pi * t / duration))  # Smooth rise and fall (Hann window)
    wave = volume * envelope * np.sin(2 * np.pi * frequency * t)
    
    # Add soft overtones
    wave += 0.1 * envelope * np.sin(4 * np.pi * frequency * t) * overtone_factor  # First overtone
    wave += 0.05 * envelope * np.sin(6 * np.pi * frequency * t) * (overtone_factor ** 0.5)  # Second overtone
    
    return wave

def apply_reverb(wave, sample_rate, reverb_time=0.2):
    """Adds a subtle reverb effect to the audio signal."""
    delay = int(reverb_time * sample_rate)
    reverb_filter = np.zeros(delay + 1)
    reverb_filter[0] = 1
    reverb_filter[1] = 0.15  # Softer, shorter decay for a smooth effect
    
    reverb_wave = scipy.signal.convolve(wave, reverb_filter, mode='full')
    
    return reverb_wave[:len(wave)]  # Trim to original length

def map_colors_to_frequencies(image_array, num_colors=50):
    """Maps image colors to a frequency range."""
    colors = image_array.reshape(-1, image_array.shape[2])
    unique_colors, counts = np.unique(colors, axis=0, return_counts=True)
    
    # Limit to the most common colors
    if len(unique_colors) > num_colors:
        sorted_colors = unique_colors[np.argsort(-counts)][:num_colors]
    else:
        sorted_colors = unique_colors

    # Use HSV to determine frequencies
    color_frequencies = []
    for color in sorted_colors:
        r, g, b = color / 255.0  # Normalize RGB to [0, 1]
        h, s, v = rgb_to_hsv(r, g, b)
        
        # Map hue to a frequency range and adjust for a smooth sound
        base_frequency = 150 + h * 250  # Frequency range (150Hz to 400Hz)
        overtone_factor = 1 + s * 0.3    # Keep overtones soft
        pitch_shift = 1 + v * 0.2        # Gentle pitch changes based on brightness
        
        color_frequencies.append((base_frequency, overtone_factor, pitch_shift))
    
    return color_frequencies

def image_to_sound(image_path, output_wav_path, duration=15, sample_rate=44100):
    """Converts an image into sound based on its color properties."""
    image = Image.open(image_path).convert('RGB')
    image = image.resize((100, 100))  # Resize to reduce complexity
    image_array = np.array(image)

    # Get distinct frequencies based on the image's color properties
    color_frequencies = map_colors_to_frequencies(image_array)
    
    num_samples = sample_rate * duration
    audio_signal = np.zeros(num_samples)

    # Generate sound based on the image's color distribution
    for frequency, overtone_factor, pitch_shift in color_frequencies:
        sound_duration = np.random.uniform(1.5, 3)  # Adjust for more variation
        start_time = np.random.uniform(0, duration - sound_duration)
        start_sample = int(start_time * sample_rate)
        wave = generate_sound_wave(frequency * pitch_shift, sound_duration, sample_rate, volume=0.2, overtone_factor=overtone_factor)
        
        # Add soft reverb for a spatial effect
        wave = apply_reverb(wave, sample_rate, reverb_time=0.3)
        
        # Add the wave to the audio signal
        end_sample = start_sample + len(wave)
        if end_sample > len(audio_signal):
            wave = wave[:len(audio_signal) - start_sample]
        audio_signal[start_sample:start_sample + len(wave)] += wave

    # Normalize and save the audio signal
    audio_signal = np.int16(audio_signal / np.max(np.abs(audio_signal)) * 32767)
    write(output_wav_path, sample_rate, audio_signal)
    print(f"WAV file created: {output_wav_path}")

# Example usage
image_path = 'image.jpg'  # Replace with your image path
output_wav_path = 'output_sound.wav'  # Output WAV file path
image_to_sound(image_path, output_wav_path, duration=7, sample_rate=44100)
