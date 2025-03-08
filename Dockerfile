FROM runpod/worker-sglang:v0.4.1stable

# Install any additional dependencies if needed.
# For olmocr, it's likely that worker-sglang already includes all dependencies.
# If you encounter missing dependencies during testing, you can add them here.
# Example:
# RUN pip install some-dependency

# Copy handler script into the image
COPY handler.py /handler.py

# Set the entrypoint to run the handler script using runpod serve
CMD ["runpod", "serve", "--handler", "/handler.py"]
