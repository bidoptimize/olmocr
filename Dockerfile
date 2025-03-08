FROM pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime-ubuntu22.04

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    ttf-mscorefonts-installer \
    msttcorefonts \
    fonts-crosextra-caladea \
    fonts-crosextra-carlito \
    gsfonts \
    lcdf-typetools \
    && rm -rf /var/lib/apt/lists/*

# Install fontconfig for proper font rendering within docker
RUN apt-get update && apt-get install -y fontconfig

# Copy the repository code
COPY . /app/allenai-olmocr/
WORKDIR /app/allenai-olmocr

# Install python dependencies
RUN pip install --no-cache-dir -r gantry-requirements.txt
RUN pip install --no-cache-dir -e .
# Install sglang with flashinfer (adjust torch version if needed)
RUN pip install sgl-kernel==0.0.3.post1 --force-reinstall --no-deps
RUN pip install "sglang[all]==0.4.2" --find-links https://flashinfer.ai/whl/cu124/torch2.4/flashinfer/


# Copy handler and any other necessary scripts outside the repo directory for easier access in serverless context
COPY handler.py /app/handler.py

# Expose the port your server will run on (adjust if needed, sglang default is 30024)
EXPOSE 8080

# Command to run your handler (adjust based on your handler implementation)
CMD ["python", "/app/handler.py"]
