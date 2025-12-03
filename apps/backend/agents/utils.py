import os
from google.adk.runners import Runner
from google.genai import types
from google.adk.sessions import InMemorySessionService

retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1, # Initial delay before first retry (in seconds)
    http_status_codes=[429, 500, 503, 504] # Retry on these HTTP errors

)

def load_instruction(path: str) -> str:
    """Load instruction text from a file path safely."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""
