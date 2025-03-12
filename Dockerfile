FROM nvidia/cuda:12.1.1-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

RUN apt update && apt install -y \
    ffmpeg \
    git \
    python3 \
    python3-pip \
    python3-dev \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python3 -m pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt

RUN git clone https://github.com/voicepaw/so-vits-svc-fork.git && \
    cd so-vits-svc-fork && \
    git checkout 0f015e32aada5cf7481f91bbe6758e574c9c5f39

WORKDIR /app/so-vits-svc-fork

COPY scripts/ scripts/
COPY main.py main.py

RUN mkdir -p /app/so-vits-svc-fork/dataset_raw /app/so-vits-svc-fork/dataset_raw/voz /app/so-vits-svc-fork/input_videos /app/so-vits-svc-fork/output_audio

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7580"]
