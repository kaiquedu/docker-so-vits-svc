import os
from pathlib import Path

WORK_DIR = Path(os.getenv("WORK_DIR", "/app/work"))
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "medium")
TRAIN_EPOCHS = int(os.getenv("TRAIN_EPOCHS", "98"))
SAMPLE_RATE = 44100
DATASET_SECONDS = 50
SEGMENT_SECONDS = 10

VOICES = {
    "pt": "pt-BR-AntonioNeural",
    "en": "en-US-GuyNeural",
    "es": "es-ES-AlvaroNeural",
    "fr": "fr-FR-HenriNeural",
    "de": "de-DE-ConradNeural",
    "it": "it-IT-DiegoNeural",
}

MYMEMORY_CODES = {
    "pt": "pt-BR",
    "en": "en-US",
    "es": "es-ES",
    "fr": "fr-FR",
    "de": "de-DE",
    "it": "it-IT",
}
