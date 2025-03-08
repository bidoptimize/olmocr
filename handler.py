import asyncio
import logging
import os
import tempfile
from flask import Flask, request, jsonify

from olmocr.pipeline import process_page, Args, MetricsKeeper, WorkerTracker, sglang_server_host, sglang_server_ready

app = Flask(__name__)

# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Initialize global metrics and tracker (if needed for server-level stats, otherwise can be per-request)
metrics = MetricsKeeper(window=60 * 5) # Adjust window as needed for server context
tracker = WorkerTracker()

# Initialize Args for process_page (you can customize these via environment variables or config)
pipeline_args = Args()

# Semaphore to control concurrent requests (optional, adjust based on GPU memory and desired concurrency)
request_semaphore = asyncio.Semaphore(1) # Limit to 1 concurrent request for simplicity

sglang_server_task = None

async def initialize_sglang_server():
    global sglang_server_task
    if sglang_server_task is None:
        logger.info("Starting sglang server...")
        semaphore = asyncio.Semaphore(1) # Dummy semaphore for server startup in handler
        sglang_server_task = asyncio.create_task(sglang_server_host(pipeline_args, semaphore))
        await sglang_server_ready()
        logger.info("sglang server started and ready.")
    else:
        logger.info("sglang server already running.")


@app.before_first_request
def startup_event():
    # Start sglang server in the background when the Flask app starts
    loop = asyncio.get_event_loop()
    loop.run_until_complete(initialize_sglang_server())


async def process_pdf_page_serverless(pdf_content_bytes, page_num):
    """Processes a single page of PDF content using olmocr pipeline."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as tmp_file:
        tmp_file.write(pdf_content_bytes)
        pdf_path = tmp_file.name # Use temp file path as both orig and local path for serverless context

        page_result = await process_page(
            args=pipeline_args,
            worker_id=0, # Single serverless instance, worker_id can be fixed
            pdf_orig_path=pdf_path, # Using temp file as orig path
            pdf_local_path=pdf_path, # Using temp file as local path
            page_num=page_num
        )

        if page_result and page_result.response and page_result.response.natural_text:
            return page_result.response.natural_text
        else:
            return None


@app.route("/", methods=['POST'])
async def handler():
    try:
        async with request_semaphore: # Limit concurrent requests if needed
            if 'pdf_file' not in request.files:
                return jsonify({"error": "No pdf_file part"}), 400

            pdf_file = request.files['pdf_file']

            if pdf_file.filename == '':
                return jsonify({"error": "No selected pdf_file"}), 400

            if pdf_file:
                pdf_content_bytes = pdf_file.read()
                page_num = request.form.get('page_num', default=1, type=int) # Get page_num from form data, default to 1

                extracted_text = await process_pdf_page_serverless(pdf_content_bytes, page_num)

                if extracted_text:
                    return jsonify({"extracted_text": extracted_text})
                else:
                    return jsonify({"error": "Text extraction failed or returned empty."}), 500
            else:
                return jsonify({"error": "Invalid pdf_file"}), 400

    except Exception as e:
        logger.exception("Error processing request:") # Log full exception for debugging
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


if __name__ == '__main__':
    # Flask development server (not for production, RunPod will handle server)
    app.run(host='0.0.0.0', port=8080, debug=False) # debug=False for serverless
