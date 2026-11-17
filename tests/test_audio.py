import numpy as np
import pytest
from pydub import AudioSegment
from pydub.generators import Sine
from scipy.io import wavfile

from dublagem import audio


def tone(ms):
    return Sine(440).to_audio_segment(duration=ms).set_channels(1).set_frame_rate(44100)


@pytest.mark.parametrize("source_ms", [3_000, 50_000, 80_000])
def test_fit_duration_sempre_retorna_o_tamanho_alvo(source_ms):
    assert len(audio.fit_duration(tone(source_ms), 50_000)) == 50_000


def test_fit_duration_recusa_audio_vazio():
    with pytest.raises(ValueError):
        audio.fit_duration(AudioSegment.empty(), 1_000)


def test_match_duration_acelera_audio_mais_longo():
    result = audio.match_duration(tone(6_000), 4_000)
    assert len(result) == 4_000
    assert result.rms > 0


def test_match_duration_completa_audio_mais_curto_com_silencio():
    result = audio.match_duration(tone(2_000), 5_000)
    assert len(result) == 5_000
    assert result[3_000:].rms == 0


def test_prepare_dataset_gera_partes_de_dez_segundos(tmp_path):
    source = tmp_path / "original.wav"
    tone(23_000).export(source, format="wav")

    parts = audio.prepare_dataset(source, tmp_path / "dataset_raw" / "voz")

    assert [p.name for p in parts] == [f"voice_part_{i}.wav" for i in range(1, 6)]
    assert all(len(AudioSegment.from_wav(p)) == 10_000 for p in parts)
    assert sorted(p.name for p in (tmp_path / "dataset_raw" / "voz").iterdir()) == sorted(p.name for p in parts)


@pytest.mark.parametrize("dtype", [np.int16, np.float32])
def test_reduce_noise_aceita_wav_inteiro_e_float(tmp_path, dtype):
    data = (np.sin(np.linspace(0, 2000, 44100)) * (0.5 if dtype == np.float32 else 16000)).astype(dtype)
    source = tmp_path / "in.wav"
    wavfile.write(source, 44100, data)

    rate, cleaned = wavfile.read(audio.reduce_noise(source, tmp_path / "out.wav"))

    assert rate == 44100
    assert cleaned.dtype == np.int16
    assert len(cleaned) == len(data)
