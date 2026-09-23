"""Lesson 01 practice: tokens, not words, are the unit.

    python lessons/practice/01_tokens.py
"""

from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client()
MODEL = "gemini-3.5-flash-lite"

# A 50-line code snippet
code = "\n".join(f"def add_{i}(x):\n    return x + {i}\n" for i in range(17))[:-1]

texts = [
    "Hello world",
    "Generative AI is artificial intelligence capable of generating content.",
    code,
]

# 1-2. Tokens, characters and characters-per-token
for text in texts:
    tokens = client.models.count_tokens(model=MODEL, contents=text).total_tokens
    chars = len(text)
    print(f"{text[:30]!r:34} tokens={tokens:<4} chars={chars:<5} ratio={chars / tokens:.2f}")

# 3. Same prompt 3 times: are the outputs identical?
prompt = "Invent a name for a new coffee shop. Reply with the name only."

outputs = [client.interactions.create(model=MODEL, input=prompt).output_text for _ in range(3)]
print("\nDefault:", outputs, "identical:", len(set(outputs)) == 1)

# Bonus: temperature 0
outputs = [
    client.interactions.create(model=MODEL, input=prompt, generation_config={"temperature": 0}).output_text
    for _ in range(3)
]
print("Temp 0: ", outputs, "identical:", len(set(outputs)) == 1)

# What I Learnt :
# Lesson 01: Tokens and Probability
# LLMs read text as tokens, not words or characters, and generate responses by sampling one token at a time from a probability distribution. This lesson shows that token cost varies by content type (code uses about 3× more tokens than English prose) and that outputs vary between runs, even when you try to reduce randomness. Some models, like Gemini 3.5 Flash-Lite, silently ignore temperature settings. The key takeaway: measure tokens instead of guessing, and design for variable outputs rather than expecting identical results.