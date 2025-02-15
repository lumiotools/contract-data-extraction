import os
import math
import google.generativeai as genai
from google.generativeai.types.file_types import File
from dotenv import load_dotenv
import json
from fastapi import UploadFile
from google.generativeai import ChatSession
from concurrent.futures import ThreadPoolExecutor
import time
from threading import Lock
import google.api_core.exceptions  # To catch ResourceExhausted errors

# Load environment variables and configure Gemini API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"

# Create the model configuration
generation_config = {
    "temperature": 0,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
}

model = genai.GenerativeModel("gemini-2.0-flash-exp")


class ContractDataExtractionService:
    _lock = Lock()

    @classmethod
    def rate_limited_call(cls, func, *args, **kwargs):
        max_attempts = 5
        initial_delay = 2
        backoff_factor = 2
        last_response = None
        for attempt in range(max_attempts):
            try:
                cls._lock.acquire()
                time.sleep(1)  # small wait after acquiring lock
                cls._lock.release()

                print(f"Calling Gemini API, attempt {attempt+1}")
                response = func(*args, **kwargs)
            except google.api_core.exceptions.ResourceExhausted as exc:
                print(f"Resource exhausted error encountered (attempt {attempt+1}): {exc}")
                time.sleep(initial_delay * (backoff_factor ** attempt))
                continue
            except Exception as exc:
                print(f"Unexpected error on attempt {attempt+1}: {exc}")
                time.sleep(initial_delay * (backoff_factor ** attempt))
                continue

            # Clean the response text from markdown formatting.
            cleaned_text = response.text.replace("```json\n", "").replace("\n```", "")
            try:
                data = json.loads(cleaned_text)
                # Check for expected keys and non-empty data
                if data and (
                    ("tables" in data and len(data["tables"]) > 0)
                    or ("table" in data and data["table"])
                    or ("addresses" in data and data["addresses"])
                    or ("contract_type" in data and data["contract_type"])
                    or ("services" in data and data["services"])
                    or ("table_rows" in data and data["table_rows"])
                ):
                    return response  # Successful response
                else:
                    print(f"Received empty or incomplete data on attempt {attempt+1}, retrying...")
            except Exception as e:
                print(f"Error parsing JSON response on attempt {attempt+1}: {e}")

            time.sleep(initial_delay * (backoff_factor ** attempt))
            last_response = response
        return last_response  # Return the last response even if it is incomplete

