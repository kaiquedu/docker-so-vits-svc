import json
import subprocess
from pathlib import Path

from .config import TRAIN_EPOCHS


def svc(*args: str, cwd: Path) -> None:
    subprocess.run(["svc", *args], cwd=cwd, check=True)


def train_voice(work_dir: Path, epochs: int = TRAIN_EPOCHS) -> None:
    svc("pre-resample", cwd=work_dir)
    svc("pre-config", cwd=work_dir)
    config_path = work_dir / "configs" / "44k" / "config.json"
    config = json.loads(config_path.read_text())
    config["train"]["epochs"] = epochs
    config_path.write_text(json.dumps(config, indent=2))
    svc("pre-hubert", cwd=work_dir)
    svc("train", cwd=work_dir)


def convert_voice(input_wav: Path, output_wav: Path, work_dir: Path) -> Path:
    svc("infer", str(input_wav), "-o", str(output_wav), cwd=work_dir)
    return output_wav
