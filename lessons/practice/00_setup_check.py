"""Environment self-test for the course. Re-run any time something breaks.

    python lessons/practice/00_setup_check.py
"""

import os
import sys

from dotenv import load_dotenv
from google import genai

MODEL = "gemini-3.5-flash-lite"

def main() -> None:
    load_dotenv()  # loads .env into os.environ (never hardcode the key)
    if not os.getenv("GEMINI_API_KEY"):
        sys.exit(
            "ERROR: GEMINI_API_KEY is not set.\n"
            "Copy .env.example to .env at the repo root and add your key — see lesson 00."
        )

    client = genai.Client()  # auto-reads GEMINI_API_KEY

    try:
        r = client.interactions.create(model=MODEL, input="Say hello in 5 words")
        models = list(client.models.list())
        names = [m.name for m in models]
    except Exception as e:  # interactions and models raise different error classes
        msg = str(e)
        if "API key not valid" in msg:
            hint = "Your key is wrong or its project was deleted — create a new one."
        elif "429" in msg or "Rate limit" in msg or "RESOURCE_EXHAUSTED" in msg:
            hint = "Free-tier rate limit hit. The key is fine — wait and retry."
        else:
            hint = msg.splitlines()[0][:300]
        sys.exit(f"ERROR: Gemini API call failed ({type(e).__name__}).\n{hint}")

    print(f"Model:           {MODEL}")
    print(f"Response:        {r.output_text.strip()}")
    print(f"Total tokens:    {r.usage.total_tokens}")
    print(f"Thinking tokens: {r.usage.total_thought_tokens}")
    print(f"Models available: {len(models)}")
    print(f"First 5 models:  {names}")

if __name__ == "__main__":
    main()
