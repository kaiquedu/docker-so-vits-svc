import shutil
from pathlib import Path
from typing import Callable

from . import audio, translation, voice

GENERATED_DIRS = ("dataset_raw", "dataset", "configs", "filelists", "logs")


def reset_workspace(work_dir: Path) -> None:
    for name in GENERATED_DIRS:
        shutil.rmtree(work_dir / name, ignore_errors=True)
    work_dir.mkdir(parents=True, exist_ok=True)


def run(video_path: Path, target_lang: str, job_dir: Path, work_dir: Path, report: Callable[[str], None]) -> Path:
    reset_workspace(work_dir)
    job_dir.mkdir(parents=True, exist_ok=True)

    report("extraindo áudio")
    original = audio.extract_audio(video_path, job_dir / "original.wav")

    report("preparando dataset de voz")
    audio.prepare_dataset(original, work_dir / "dataset_raw" / "voz")

    report("treinando modelo de voz")
    voice.train_voice(work_dir)

    report("transcrevendo e traduzindo")
    speech = translation.dub_speech(original, target_lang, job_dir)

    report("aplicando a voz original")
    converted = voice.convert_voice(speech, job_dir / "converted.wav", work_dir)

    report("limpando áudio final")
    return audio.reduce_noise(converted, job_dir / f"dublado_{target_lang}.wav")
