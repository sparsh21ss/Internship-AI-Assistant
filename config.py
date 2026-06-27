import os
import sys
from google import genai

def get_client():
    """
    Initializes and returns the Google GenAI client.
    Returns None if the GEMINI_API_KEY environment variable is not set,
    allowing the application to start up and run in fallback mode.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[WARNING] GEMINI_API_KEY environment variable is not set.", file=sys.stderr)
        print("[WARNING] The application will run using Jaccard and rule-based local fallback models.", file=sys.stderr)
        return None
    try:
        return genai.Client(api_key=api_key)
    except Exception as e:
        print(f"[ERROR] Failed to initialize Gemini Client: {e}", file=sys.stderr)
        return None
