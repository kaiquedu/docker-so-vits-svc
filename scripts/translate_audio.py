import os
import whisper
import asyncio
from pydub import AudioSegment
from deep_translator import GoogleTranslator
import edge_tts

OUTPUT_DIR = "/app/so-vits-svc-fork/output_audio/"

async def text_to_speech(text, output_wav_path, lang):
    """Converte texto para fala usando edge-tts com voz natural."""
    VOICE_MAP = {
        "es": "es-ES-AlvaroNeural",
        "en": "en-US-GuyNeural"
    }
    voice = VOICE_MAP.get(lang, "en-US-GuyNeural")

    tts = edge_tts.Communicate(text, voice)
    await tts.save(output_wav_path)
    print(f"Áudio traduzido salvo em {output_wav_path}")

    return convert_to_wav(output_wav_path)

def convert_to_wav(input_wav):
    """Converte um arquivo de áudio para um formato WAV padrão."""
    audio = AudioSegment.from_file(input_wav)
    output_wav = input_wav.replace(".wav", "_converted.wav")
    audio.export(output_wav, format="wav")
    print(f"Arquivo convertido para WAV padrão: {output_wav}")
    return output_wav

def adjust_audio_speed(input_wav, reference_wav, output_wav):
    """Ajusta a velocidade do áudio traduzido para coincidir com o original."""
    original = AudioSegment.from_wav(reference_wav)
    translated = AudioSegment.from_wav(input_wav)

    speed_factor = len(original) / len(translated)
    adjusted_audio = translated.speedup(playback_speed=speed_factor)
    adjusted_audio.export(output_wav, format="wav")
    print(f"Áudio ajustado salvo em {output_wav}")
    return output_wav

def transcribe_audio(audio_path):
    """Transcreve o áudio usando Whisper sem traduzir automaticamente."""
    model = whisper.load_model("medium")  
    print("Transcrevendo áudio...")
    result = model.transcribe(audio_path)
    transcribed_text = result["text"]
    print(f"Texto original: {transcribed_text}")
    return transcribed_text

def translate_text(text, target_lang):
    """Traduz o texto transcrito para o idioma desejado."""
    translated_text = GoogleTranslator(source="auto", target=target_lang).translate(text)
    print(f"Texto traduzido ({target_lang}): {translated_text}")
    return translated_text

def translate_audio(audio_path, target_lang):
    """Transcreve e traduz o áudio, gerando um novo áudio dublado."""
    transcribed_text = transcribe_audio(audio_path)
    translated_text = translate_text(transcribed_text, target_lang)

    translated_wav = os.path.join(OUTPUT_DIR, f"translated_audio_{target_lang}.wav")
    final_output_wav = os.path.join(OUTPUT_DIR, f"translated_audio_{target_lang}_final.wav")

    converted_wav = asyncio.run(text_to_speech(translated_text, translated_wav, target_lang))

    adjusted_wav = adjust_audio_speed(converted_wav, audio_path, final_output_wav)

    return adjusted_wav

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Uso correto: python translate_audio.py <caminho_do_audio> <idioma_destino>")
        sys.exit(1)

    input_audio = sys.argv[1]
    target_lang = sys.argv[2]

    translated_audio = translate_audio(input_audio, target_lang)
    print(f"✅ Tradução finalizada. Arquivo salvo em: {translated_audio}")
