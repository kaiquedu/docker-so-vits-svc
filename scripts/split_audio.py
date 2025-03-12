import os
import numpy as np
import noisereduce as nr
from pydub import AudioSegment, effects
from scipy.io import wavfile
import tempfile

def process_audio(audio_path, output_folder):
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Áudio não encontrado: {audio_path}")

    audio = AudioSegment.from_wav(audio_path)
    audio = effects.normalize(audio)
    
    segment_duration = 10 * 1000  
    target_duration = 50 * 1000
    os.makedirs(output_folder, exist_ok=True)

    if len(audio) < target_duration:
        times_to_repeat = (target_duration // len(audio)) + 1 
        audio = audio * times_to_repeat
        print(f"Áudio repetido até atingir {len(audio) / 1000} segundos.")

    elif len(audio) > target_duration:
        audio = audio[:target_duration]
        print(f"Áudio cortado para {len(audio) / 1000} segundos.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
        audio.export(temp_wav.name, format="wav")
        sample_rate, data = wavfile.read(temp_wav.name)

    data = data.astype(np.float32) / 32768.0 

    reduced_noise = nr.reduce_noise(y=data, sr=sample_rate, prop_decrease=0.2, stationary=True)

    def apply_equalization(signal):
        return signal * 1.2  

    equalized_audio = apply_equalization(reduced_noise)

    def compress_audio(signal):
        return np.clip(signal * 0.8, -1, 1) 

    compressed_audio = compress_audio(equalized_audio)

    def reduce_reverb(signal):
        return np.clip(signal * 0.9, -1, 1) 

    final_audio = reduce_reverb(compressed_audio)

    final_audio = np.int16(final_audio * 32767)

    processed_audio_file = "processed_audio.wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as processed_wav:
        wavfile.write(processed_wav.name, sample_rate, final_audio)

    audio = AudioSegment.from_wav(processed_wav.name)

    audio = effects.normalize(audio)

    audio.export(processed_audio_file, format="wav")
    print("Áudio processado e salvo com qualidade aprimorada!")

    os.remove(temp_wav.name)
    os.remove(processed_wav.name)

    return processed_audio_file

def split_audio_into_parts(audio_path, output_folder):
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Áudio não encontrado: {audio_path}")

    audio = AudioSegment.from_wav(audio_path)
    
    print(f"Duração do áudio: {len(audio) / 1000} segundos")
    
    segment_duration = 10 * 1000
    num_segments = 5
    os.makedirs(output_folder, exist_ok=True)

    for i in range(num_segments):
        start = i * segment_duration
        end = start + segment_duration
        segment = audio[start:end]
        segment.export(os.path.join(output_folder, f"voice_part_{i+1}.wav"), format="wav")

    print("Áudio dividido e salvo em 5 partes.")

def remove_extraneous_files(output_folder):
    for filename in os.listdir(output_folder):
        file_path = os.path.join(output_folder, filename)
        if filename.startswith("voice_part_") and os.path.isfile(file_path):
            continue
        os.remove(file_path)
    print("Arquivos não necessários removidos.")

if __name__ == "__main__":
    input_audio = '/app/so-vits-svc-fork/dataset_raw/voz/extracted_audio.wav'
    
    processed_audio = process_audio(input_audio, "/app/so-vits-svc-fork/voz/dataset_raw")

    remove_extraneous_files("/app/so-vits-svc-fork/dataset_raw/voz")
    
    split_audio_into_parts(processed_audio, "/app/so-vits-svc-fork/dataset_raw/voz")
