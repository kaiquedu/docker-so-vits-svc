import numpy as np
import noisereduce as nr
from pydub import AudioSegment, effects
from scipy.io import wavfile
import os
import sys

def clean_audio(audio_path):
    sample_rate, data = wavfile.read(audio_path)
    data = data.astype(np.float32) / 32768.0  

    reduced_noise = nr.reduce_noise(y=data, sr=sample_rate, prop_decrease=0.2, stationary=True)
    final_audio = np.int16(reduced_noise * 32767)
    
    processed_audio_path = audio_path.replace(".wav", "_cleaned.wav")
    wavfile.write(processed_audio_path, sample_rate, final_audio)
    
    print(f"Áudio limpo salvo em {processed_audio_path}")

if __name__ == "__main__":
    input_audio = sys.argv[1]
    clean_audio(input_audio)
