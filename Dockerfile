FROM nvidia/cuda:12.4.1-base-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv git \
    poppler-utils ttf-mscorefonts-installer msttcorefonts \
    fonts-crosextra-caladea fonts-crosextra-carlito gsfonts lcdf-typetools && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN python3 -m pip install --upgrade pip && \
    pip install -e . && \
    pip install sgl-kernel==0.0.3.post1 --force-reinstall --no-deps && \
    pip install "sglang[all]==0.4.2" --find-links https://flashinfer.ai/whl/cu124/torch2.4/flashinfer/ && \
    pip install fastapi uvicorn python-multipart

EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
