import subprocess
from pathlib import Path

import noisereduce as nr
import numpy as np
from pydub import AudioSegment, effects
from scipy.io import wavfile

from .config import DATASET_SECONDS, SAMPLE_RATE, SEGMENT_SECONDS


def extract_audio(video_path: Path, output_wav: Path) -> Path:
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(video_path), "-vn", "-ac", "1", "-ar", str(SAMPLE_RATE), str(output_wav)],
        check=True,
    )
    return output_wav


def reduce_noise(input_wav: Path, output_wav: Path, strength: float = 0.2) -> Path:
    sample_rate, data = wavfile.read(input_wav)
    if np.issubdtype(data.dtype, np.integer):
        data = data.astype(np.float32) / np.iinfo(data.dtype).max
    cleaned = nr.reduce_noise(y=data.astype(np.float32), sr=sample_rate, prop_decrease=strength, stationary=True)
    wavfile.write(output_wav, sample_rate, np.int16(np.clip(cleaned, -1, 1) * 32767))
    return output_wav


def fit_duration(audio: AudioSegment, target_ms: int) -> AudioSegment:
    if len(audio) == 0:
        raise ValueError("O áudio está vazio")
    if len(audio) < target_ms:
        audio = audio * (target_ms // len(audio) + 1)
    return audio[:target_ms]


def prepare_dataset(source_wav: Path, dataset_dir: Path) -> list[Path]:
    dataset_dir.mkdir(parents=True, exist_ok=True)
    cleaned = reduce_noise(source_wav, dataset_dir.parent / "dataset_source.wav")
    audio = effects.normalize(AudioSegment.from_wav(cleaned))
    audio = fit_duration(audio, DATASET_SECONDS * 1000)
    segment_ms = SEGMENT_SECONDS * 1000
    parts = []
    for index, start in enumerate(range(0, len(audio), segment_ms), start=1):
        path = dataset_dir / f"voice_part_{index}.wav"
        audio[start : start + segment_ms].export(path, format="wav")
        parts.append(path)
    cleaned.unlink()
    return parts


def match_duration(translated: AudioSegment, target_ms: int) -> AudioSegment:
    if len(translated) > target_ms:
        translated = translated.speedup(playback_speed=len(translated) / target_ms, chunk_size=50, crossfade=25)
    if len(translated) < target_ms:
        translated += AudioSegment.silent(duration=target_ms - len(translated), frame_rate=translated.frame_rate)
    return translated[:target_ms]
