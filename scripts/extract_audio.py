import subprocess
import os
import shutil
import sys

def extract_audio(video_path, output_audio_path):
    subprocess.run(["ffmpeg", "-i", video_path, "-ac", "1", "-ar", "44100", "-vn", output_audio_path], check=True)
    
    dataset_raw_path = "/app/so-vits-svc-fork/dataset_raw/voz"
    os.makedirs(dataset_raw_path, exist_ok=True)
    
    final_audio_path = os.path.join(dataset_raw_path, "extracted_audio.wav")
    
    shutil.move(output_audio_path, final_audio_path)

    output_audio_dir = "/app/so-vits-svc-fork/output_audio"
    os.makedirs(output_audio_dir, exist_ok=True)

    final_output_path = os.path.join(output_audio_dir, "extracted_audio.wav")
    shutil.copy(final_audio_path, final_output_path)

if __name__ == "__main__":
    video_file = sys.argv[1]
    output_file = sys.argv[2]
    extract_audio(video_file, output_file)
