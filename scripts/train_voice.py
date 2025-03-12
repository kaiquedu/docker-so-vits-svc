import subprocess
import os
import json

def train_model():
    os.makedirs("/app/so-vits-svc-fork/dataset_raw", exist_ok=True)
    files_in_dataset = os.listdir("/app/so-vits-svc-fork/dataset_raw/voz")
    print(f"Arquivos em dataset_raw: {files_in_dataset}")
    os.makedirs("/app/so-vits-svc-fork/voz", exist_ok=True)

    subprocess.run(["svc", "pre-resample", "-i", "/app/so-vits-svc-fork/dataset_raw"], check=True)
    subprocess.run(["svc", "pre-config", "-i", "/app/so-vits-svc-fork/dataset_raw"], check=True)

    config_path = "/app/so-vits-svc-fork/configs/44k/config.json"
    
    if os.path.exists(config_path):
        with open(config_path, "r+") as file:
            config = json.load(file)
            config['train']['epochs'] = 98
            file.seek(0)
            json.dump(config, file, indent=4)
            file.truncate()
        print("Configuração de epochs modificada para 98.")
    else:
        print(f"Arquivo {config_path} não encontrado.")

    subprocess.run(["svc", "pre-hubert", "-i", "/app/so-vits-svc-fork/dataset_raw"], check=True)

    subprocess.run(["svc", "train", "-t"], check=True)
    
if __name__ == "__main__":
    train_model()
