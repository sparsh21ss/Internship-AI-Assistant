import os
import sys
from google import genai

def get_client():
    """
    Initializes and returns the Google GenAI client.
    Verifies that the GEMINI_API_KEY environment variable is set.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[ERROR] GEMINI_API_KEY environment variable is not set.", file=sys.stderr)
        print("Please set it in your environment. For example, in PowerShell:", file=sys.stderr)
        print("  $env:GEMINI_API_KEY = \"your_api_key_here\"", file=sys.stderr)
        sys.exit(1)
    return genai.Client(api_key=api_key)
