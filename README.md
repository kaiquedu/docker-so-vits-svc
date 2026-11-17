# docker-so-vits: Dublagem automática com IA

API que recebe um vídeo e devolve o áudio dublado em outro idioma com a voz de quem está falando. O pipeline transcreve a fala, traduz, gera a fala traduzida com TTS e aplica a voz original com um modelo so-vits-svc treinado a partir do próprio vídeo.

## Contexto

Projeto feito em março de 2025 para estudar como montar um pipeline de dublagem juntando modelos open source. Naquela época, clonar uma voz e dublar exigia combinar várias ferramentas separadas. Hoje serviços como ElevenLabs e HeyGen fazem isso de ponta a ponta, mais rápido e com qualidade melhor, inclusive com sincronia labial.

Em novembro de 2026 o código foi revisado para corrigir erros do fluxo original. A stack da época foi mantida, e as versões das dependências estão fixadas nas que eram atuais em março de 2025. A exceção é o `edge-tts`, que precisou ser atualizado porque a versão antiga deixou de ser aceita pelo serviço da Microsoft.

## Pipeline

```
vídeo
 └─ ffmpeg ─────────────── extrai o áudio (mono, 44,1 kHz)
     ├─ dataset ────────── normaliza, reduz ruído e divide em 5 trechos de 10 s
     │   └─ so-vits-svc ── treina um modelo com a voz do vídeo
     └─ Whisper ────────── transcreve a fala e detecta o idioma
         └─ tradução ───── Google Translate, com MyMemory se o Google falhar
             └─ edge-tts ─ gera a fala traduzida
                 └─ ajuste de duração para bater com o original
                     └─ so-vits-svc ── troca a voz do TTS pela voz original
                         └─ redução de ruído ── áudio final
```

| Etapa | Ferramenta |
|---|---|
| Extração de áudio | FFmpeg |
| Tratamento de áudio | pydub, noisereduce |
| Transcrição | OpenAI Whisper (`medium`) |
| Tradução | deep-translator (Google Translate e MyMemory) |
| Texto para fala | edge-tts |
| Conversão de voz | so-vits-svc-fork 4.2.26 |
| API | FastAPI |

## Estrutura

```
dublagem/
  audio.py        extração, redução de ruído, dataset e ajuste de duração
  translation.py  transcrição, tradução e TTS
  voice.py        treino e inferência do so-vits-svc
  pipeline.py     ordem das etapas
  config.py       idiomas, vozes e variáveis de ambiente
main.py           API
tests/
```

## API

O processamento leva de dezenas de minutos a algumas horas, porque cada vídeo treina um modelo novo. Por isso a API devolve um `job_id` na hora e o resultado é consultado depois. Só um vídeo é processado por vez.

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/process/` | Envia o vídeo (`file`) e o idioma de destino (`target_lang`) |
| `GET` | `/jobs/{job_id}` | Mostra o status e a etapa atual |
| `GET` | `/jobs/{job_id}/audio` | Baixa o áudio dublado em WAV |

Idiomas: `pt`, `en`, `es`, `fr`, `de`, `it`. Formatos de vídeo: `.mp4`, `.mov`, `.mkv`, `.webm`, `.avi`.

```bash
curl -F file=@meu_video.mp4 -F target_lang=es http://localhost:7580/process/
curl http://localhost:7580/jobs/<job_id>
curl -o dublado.wav http://localhost:7580/jobs/<job_id>/audio
```

A documentação interativa fica em http://localhost:7580/docs.

## Como rodar

Precisa de uma GPU NVIDIA com o [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html). Sem GPU o treino até roda, mas fica lento demais para uso prático. No macOS o Docker não acessa a GPU.

```bash
docker build -t docker-so-vits .
docker run --gpus all -p 7580:7580 -v so-vits-cache:/home/app/.cache docker-so-vits
```

O volume guarda os modelos do Whisper e do so-vits para não baixar de novo a cada execução.

| Variável | Padrão | Descrição |
|---|---|---|
| `TRAIN_EPOCHS` | `98` | Épocas de treino do modelo de voz |
| `WHISPER_MODEL` | `medium` | Tamanho do modelo do Whisper |
| `WORK_DIR` | `/app/work` | Pasta de trabalho |

## Testes

Os testes cobrem o tratamento de áudio, a divisão do texto para tradução e a API, com o pipeline substituído por uma versão falsa. Não precisam de GPU.

```bash
pip install -r requirements-dev.txt
pytest
```

## Limitações

- O modelo de voz é treinado com apenas 50 segundos de áudio. Se o vídeo for mais curto, o áudio é repetido até completar esse tempo. Isso dá um modelo fraco, e a voz final soa parecida com a original, mas longe de idêntica.
- O vídeo deve ter uma pessoa falando, sem música de fundo.
- A duração é ajustada acelerando a fala ou completando com silêncio no final. Não existe sincronia frase a frase nem labial.
- A API devolve só o áudio. Juntar o áudio dublado ao vídeo fica por conta de quem usa.
- Os jobs ficam em memória e se perdem quando o container reinicia.
- O Google Translate e o MyMemory são usados sem chave de API e podem limitar as requisições.
- O treino e a inferência do so-vits-svc não são cobertos pelos testes automatizados.

## Licença

O so-vits-svc-fork é distribuído sob a licença MIT. Use apenas vozes de pessoas que autorizaram o uso.
