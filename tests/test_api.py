import io

import pytest
from fastapi.testclient import TestClient

from main import create_app


def upload(client, name="video.mp4", lang="es"):
    return client.post("/process/", files={"file": (name, io.BytesIO(b"video"), "video/mp4")}, data={"target_lang": lang})


@pytest.fixture
def calls():
    return []


@pytest.fixture
def client(tmp_path, calls):
    def runner(video, lang, job_dir, work_dir, report):
        calls.append((video.read_bytes(), lang))
        report("etapa")
        output = job_dir / f"dublado_{lang}.wav"
        output.write_bytes(b"RIFF")
        return output

    return TestClient(create_app(tmp_path, runner, run_in_thread=False))


def test_processa_e_permite_baixar_o_audio(client, calls):
    res = upload(client, lang="fr")
    assert res.status_code == 202
    job_id = res.json()["job_id"]

    assert calls == [(b"video", "fr")]
    assert client.get(f"/jobs/{job_id}").json()["status"] == "concluído"

    audio = client.get(f"/jobs/{job_id}/audio")
    assert audio.status_code == 200
    assert audio.headers["content-type"] == "audio/wav"
    assert audio.content == b"RIFF"


def test_idioma_vem_do_formulario(client, calls):
    upload(client, lang="en")
    assert calls[0][1] == "en"


def test_recusa_idioma_nao_suportado(client, calls):
    assert upload(client, lang="xx").status_code == 400
    assert calls == []


@pytest.mark.parametrize("name", ["../../etc/passwd", "audio.exe", "sem_extensao"])
def test_recusa_arquivo_que_nao_e_video(client, name):
    assert upload(client, name=name).status_code == 400


def test_nome_do_arquivo_nao_define_o_caminho_salvo(tmp_path, client, calls):
    upload(client, name="../../fora.mp4")
    assert not (tmp_path.parent / "fora.mp4").exists()
    assert calls


def test_registra_erro_da_etapa(tmp_path):
    def runner(*_args):
        raise RuntimeError("svc train falhou")

    client = TestClient(create_app(tmp_path, runner, run_in_thread=False))
    job_id = upload(client).json()["job_id"]

    job = client.get(f"/jobs/{job_id}").json()
    assert job["status"] == "erro"
    assert job["error"] == "svc train falhou"
    assert client.get(f"/jobs/{job_id}/audio").status_code == 409

    assert upload(client).status_code == 202


def test_job_inexistente(client):
    assert client.get("/jobs/nao-existe").status_code == 404
