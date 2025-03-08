import runpod
import asyncio
import base64
import tempfile
import os
from olmocr.pipeline import process_pdf

MODEL_NAME = os.environ.get("MODEL_PATH", "allenai/olmOCR-7B-0225-preview") # Default model, can be overridden by env var

async def handler(job):
    """
    This is the handler function that will be executed for each runpod job.

    It loads the allenai/olmOCR-7B-0225-preview model and processes the PDF
    from the input, returning the extracted text.
    """
    job_input = job['input']
    pdf_base64 = job_input.get('pdf_base64')

    if not pdf_base64:
        return {"error": "No pdf_base64 input provided"}

    pdf_bytes = base64.b64decode(pdf_base64)

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_pdf_file:
        tmp_pdf_file.write(pdf_bytes)
        pdf_path = tmp_pdf_file.name

    try:
        # Process the PDF using the olmocr pipeline
        dolma_doc = await process_pdf(Args(), worker_id=0, pdf_orig_path=pdf_path) # Args() will use default pipeline arguments, worker_id is arbitrary for serverless

        if dolma_doc:
            extracted_text = dolma_doc['text']
            return {"text": extracted_text}
        else:
            return {"error": "PDF processing failed or returned no text."}

    except Exception as e:
        return {"error": f"PDF processing error: {e}"}
    finally:
        os.remove(pdf_path) # Clean up temporary PDF file


class Args:  # Dummy Args class to satisfy process_pdf, mimicking command-line arguments
    model = MODEL_NAME  # Use MODEL_PATH env var or default
    model_chat_template = "qwen2-vl" # Assuming qwen2-vl is appropriate for olmOCR-7B
    model_max_context = 8192
    target_longest_image_dim = 1024
    target_anchor_text_len = 6000
    max_page_retries = 2
    max_page_error_rate = 0.004
    apply_filter = False # disable filter for serverless, can enable via env var if needed
    stats = False # stats are not relevant for single requests
    workspace = "/runpod_data/workspace" # dummy workspace path for s3 workqueue, not used in serverless
    pdfs = None # not used in serverless
    workspace_profile = None # not used in serverless
    pdf_profile = None # not used in serverless
    pages_per_group = 500 # not used in serverless
    workers = 1 # only 1 worker in serverless
    beaker = False # beaker is not relevant for serverless
    beaker_workspace = None # beaker is not relevant for serverless
    beaker_cluster = None # beaker is not relevant for serverless
    beaker_gpus = 1 # beaker is not relevant for serverless
    beaker_priority = "normal" # beaker is not relevant for serverless


if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
