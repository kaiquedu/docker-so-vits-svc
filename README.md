# docker-so-vits – Dublagem Automática com IA  

**docker-so-vits** é um sistema de dublagem automática baseado em IA. Ele extrai o áudio de um vídeo, traduz para outro idioma e reconstrói a voz original com o modelo **so-vits-svc-fork**, mantendo o tom e a naturalidade da fala.  

## Recursos  
- Extração de áudio de vídeos  
- Redução de ruído e normalização de áudio
- Treinamento de modelo do so-vits-svc-fork para gerar uma voz personalizada
- Transcrição e tradução automática (Whisper + Google Translate) 
- Conversão de texto em fala (edge-tts)  
- Geração de voz personalizada com **so-vits-svc-fork**   
- API FastAPI para processamento de áudio  

---

## Tecnologias Utilizadas  
- **Python** (FastAPI, NumPy, Pydub, Noisereduce, Whisper, edge-tts)  
- **so-vits-svc-fork** 
- **Docker** (Para empacotamento e execução)  
- **FFmpeg** (Manipulação de áudio/vídeo)  

---

## Requisitos Mínimos  

### Hardware:  
- CPU com suporte a AVX  
- **GPU NVIDIA (Opcional, mas recomendável para inferência rápida de voz)**  
- 8GB de RAM (mínimo) 

### Software:  
- **Docker**
- **Python 3.8+** (se rodar sem Docker)  
- **FFmpeg** instalado  

---

## Instalação e Uso  

### 1️⃣ Clonar o Repositório  
```sh
git clone https://github.com/seu-usuario/docker-so-vits.git
cd docker-so-vits
```

### 2️⃣ Rodar com Docker
```sh
docker build -t docker-so-vits .
docker run --gpus all -p 7580:7580 docker-so-vits
```
Caso não tenha GPU, remova --gpus all no comando acima.

### 3️⃣ Testar a API
Após rodar o contêiner, a API estará disponível em:
http://localhost:7580/docs

Exemplo de requisição:
```sh
curl -X 'POST' 'http://localhost:7580/process/' \
-H 'accept: application/json' \
-H 'Content-Type: multipart/form-data' \
-F 'file=@meu_video.mp4' \
-F 'target_lang=es'
```
Isso processará o vídeo e retornará um áudio dublado em espanhol.
