import asyncio
import re
from functools import lru_cache
from pathlib import Path

import edge_tts
from deep_translator import GoogleTranslator, MyMemoryTranslator
from pydub import AudioSegment

from .audio import match_duration
from .config import MYMEMORY_CODES, SAMPLE_RATE, VOICES, WHISPER_MODEL

MYMEMORY_MAX_CHARS = 450


@lru_cache(maxsize=1)
def whisper_model():
    import whisper

    return whisper.load_model(WHISPER_MODEL)


def transcribe(audio_path: Path) -> tuple[str, str]:
    result = whisper_model().transcribe(str(audio_path))
    return result["text"].strip(), result["language"]


def split_text(text: str, limit: int = MYMEMORY_MAX_CHARS) -> list[str]:
    chunks: list[str] = []
    current = ""
    for sentence in re.split(r"(?<=[.!?])\s+", text.strip()):
        if len(sentence) > limit and current:
            chunks.append(current)
            current = ""
        while len(sentence) > limit:
            cut = sentence.rfind(" ", 0, limit)
            cut = cut if cut > 0 else limit
            chunks.append(sentence[:cut].strip())
            sentence = sentence[cut:].strip()
        if current and len(current) + len(sentence) + 1 > limit:
            chunks.append(current)
            current = sentence
        else:
            current = f"{current} {sentence}".strip()
    if current:
        chunks.append(current)
    return chunks


def translate(text: str, source_lang: str, target_lang: str) -> str:
    try:
        return GoogleTranslator(source="auto", target=target_lang).translate(text)
    except Exception:
        translator = MyMemoryTranslator(
            source=MYMEMORY_CODES.get(source_lang, source_lang), target=MYMEMORY_CODES[target_lang]
        )
        return " ".join(translator.translate(chunk) for chunk in split_text(text))


def synthesize(text: str, target_lang: str, output_mp3: Path) -> Path:
    asyncio.run(edge_tts.Communicate(text, VOICES[target_lang]).save(str(output_mp3)))
    return output_mp3


def dub_speech(original_wav: Path, target_lang: str, work_dir: Path) -> Path:
    text, source_lang = transcribe(original_wav)
    if not text:
        raise ValueError("Nenhuma fala encontrada no vídeo")
    translated = translate(text, source_lang, target_lang)
    speech = AudioSegment.from_file(synthesize(translated, target_lang, work_dir / "tts.mp3"))
    speech = speech.set_channels(1).set_frame_rate(SAMPLE_RATE)
    aligned = match_duration(speech, len(AudioSegment.from_wav(original_wav)))
    output = work_dir / "tts_aligned.wav"
    aligned.export(output, format="wav")
    return output
