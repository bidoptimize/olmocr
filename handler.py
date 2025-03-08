import runpod
import os
from openai import OpenAI

def handler(job):
    """
    This is the handler function that will be executed for each job.
    """
    input_data = job['input']

    try:
        # Initialize OpenAI client with RunPod API Key and Endpoint URL
        client = OpenAI(
            api_key=os.getenv("RUNPOD_API_KEY"), # or job['api_key'], if you want to pass it in input
            base_url=f"https://api.runpod.ai/v2/{job['endpointId']}/openai/v1", # or directly from job context
        )

        # Assuming the input is a text prompt in 'prompt' key
        prompt = input_data.get("prompt", "Give a two lines on Planet Earth ?")

        response = client.chat.completions.create(
            model="allenai/olmOCR-7B-0225-preview", # Model name doesn't really matter for serverless, but needs to be set
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=100,
        )

        # Extract the text response
        output_text = response.choices[0].message.content

        return {"output": output_text}

    except Exception as e:
        return {"error": str(e)}


if __name__ == '__main__':
    print("Worker starting up...")
    runpod.serverless.start({"handler": handler})
    print("Worker started successfully")
