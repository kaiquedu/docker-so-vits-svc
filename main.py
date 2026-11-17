import shutil
import threading
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from dublagem import pipeline
from dublagem.config import VOICES, WORK_DIR

ALLOWED_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm", ".avi"}

Runner = Callable[[Path, str, Path, Path, Callable[[str], None]], Path]


@dataclass
class Job:
    id: str
    target_lang: str
    status: str = "na fila"
    step: Optional[str] = None
    error: Optional[str] = None
    output: Optional[Path] = field(default=None, repr=False)

    def public(self) -> dict:
        return {"job_id": self.id, "target_lang": self.target_lang, "status": self.status, "step": self.step, "error": self.error}


def create_app(work_dir: Path = WORK_DIR, runner: Runner = pipeline.run, run_in_thread: bool = True) -> FastAPI:
    app = FastAPI(title="Dublagem automática com so-vits-svc")
    jobs: dict[str, Job] = {}
    busy = threading.Lock()

    def execute(job: Job, video_path: Path) -> None:
        job.status = "processando"
        try:
            job.output = runner(video_path, job.target_lang, work_dir / "jobs" / job.id, work_dir / "svc", lambda s: setattr(job, "step", s))
            job.status = "concluído"
        except Exception as exc:
            job.status = "erro"
            job.error = str(exc) or exc.__class__.__name__
        finally:
            job.step = None
            busy.release()

    @app.post("/process/", status_code=202)
    def process_video(file: UploadFile = File(...), target_lang: str = Form("es")):
        if target_lang not in VOICES:
            raise HTTPException(400, f"Idioma não suportado. Use um destes: {', '.join(VOICES)}")
        extension = Path(file.filename or "").suffix.lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(400, f"Formato não suportado. Use um destes: {', '.join(sorted(ALLOWED_EXTENSIONS))}")
        if not busy.acquire(blocking=False):
            raise HTTPException(409, "Já existe um vídeo em processamento. Tente novamente depois.")

        job = Job(id=uuid.uuid4().hex, target_lang=target_lang)
        input_dir = work_dir / "jobs" / job.id
        input_dir.mkdir(parents=True, exist_ok=True)
        video_path = input_dir / f"input{extension}"
        with video_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        jobs[job.id] = job

        if run_in_thread:
            threading.Thread(target=execute, args=(job, video_path), daemon=True).start()
        else:
            execute(job, video_path)
        return job.public()

    def get_job(job_id: str) -> Job:
        job = jobs.get(job_id)
        if job is None:
            raise HTTPException(404, "Processamento não encontrado")
        return job

    @app.get("/jobs/{job_id}")
    def job_status(job_id: str):
        return get_job(job_id).public()

    @app.get("/jobs/{job_id}/audio")
    def job_audio(job_id: str):
        job = get_job(job_id)
        if job.status != "concluído" or job.output is None:
            raise HTTPException(409, f"Áudio ainda não disponível. Status atual: {job.status}")
        return FileResponse(job.output, media_type="audio/wav", filename=job.output.name)

    return app


app = create_app()
