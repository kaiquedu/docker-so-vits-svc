import subprocess
import sys
import os

def infer(input_audio, output_audio):
    print("Arquivos disponíveis após tradução:")
    os.system("ls -lah /app/so-vits-svc-fork/output_audio/")
    subprocess.run(["svc", "infer", input_audio, "--output-path", output_audio])
    print(f"Voz dublada salva em {output_audio}")

if __name__ == "__main__":
    input_audio = sys.argv[1]
    output_audio = sys.argv[2]
    infer(input_audio, output_audio)
