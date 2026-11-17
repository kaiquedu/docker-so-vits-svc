FROM nvidia/cuda:12.4.1-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 WORK_DIR=/app/work

RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg \
        libsndfile1 \
        python3 \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt

COPY dublagem ./dublagem
COPY main.py .

RUN useradd --create-home app && mkdir -p /app/work && chown app /app/work
USER app

EXPOSE 7580
CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7580"]
