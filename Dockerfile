FROM runpod/worker-sglang:v0.4.1stable

# Install poppler-utils and fonts for PDF rendering (as mentioned in olmOCR README)
RUN apt-get update && apt-get install -y poppler-utils ttf-mscorefonts-installer msttcorefonts fonts-crosextra-caladea fonts-crosextra-carlito gsfonts lcdf-typetools --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Set environment variables for SGLang server configuration
# MODEL_PATH is crucial for specifying the model
ENV MODEL_PATH="allenai/olmOCR-7B-0225-preview"
# PORT is set to 30000 as per documentation, though it might be default anyway
ENV PORT=30000

# Copy the handler script into the container
COPY handler.py /handler.py

# Set the entrypoint to run the handler script
CMD ["python", "/handler.py"]
