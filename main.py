from fastapi import FastAPI, File, UploadFile
import subprocess
import os

app = FastAPI()

INPUT_DIR = "/app/so-vits-svc-fork/input_videos"
OUTPUT_DIR = "/app/so-vits-svc-fork/output_audio"
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.post("/process/")
async def process_video(file: UploadFile = File(...), target_lang: str = "es"):
    video_path = os.path.join(INPUT_DIR, file.filename)
    with open(video_path, "wb") as buffer:
        buffer.write(await file.read())

    extracted_audio = os.path.join(OUTPUT_DIR, "extracted_audio.wav")
    subprocess.run(["python3", "scripts/extract_audio.py", video_path, extracted_audio], cwd="/app/so-vits-svc-fork")

    subprocess.run(["python3", "scripts/split_audio.py", extracted_audio], cwd="/app/so-vits-svc-fork")

    subprocess.run(["python3", "scripts/train_voice.py"], cwd="/app/so-vits-svc-fork")

    translated_audio = os.path.join(OUTPUT_DIR, f"translated_audio_{target_lang}.wav")
    subprocess.run(["python3", "scripts/translate_audio.py", extracted_audio, target_lang], cwd="/app/so-vits-svc-fork")

    output_audio = os.path.join(OUTPUT_DIR, "translated_audio_output.wav")
    subprocess.run(["svc", "infer", translated_audio, "--output-path", output_audio], cwd="/app/so-vits-svc-fork")

    subprocess.run(["python3", "scripts/process_audio.py", output_audio], cwd="/app/so-vits-svc-fork")

    return {"message": "Processamento concluído", "output_file": output_audio}
