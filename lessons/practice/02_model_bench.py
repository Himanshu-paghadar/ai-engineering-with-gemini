"""Lesson 02 practice: pick a model on evidence, not vibes.

Works with any OpenAI-compatible provider. Set these in .env:
    OPENAI_BASE_URL=https://your-provider.com/v1
    OPENAI_API_KEY=your-provider-key
    BENCH_MODELS=model-a,model-b,model-c

    python lessons/practice/02_model_bench.py | tee lessons/practice/02_results.txt
"""

import os
import time

from dotenv import load_dotenv
from openai import OpenAI, RateLimitError

load_dotenv()
client = OpenAI(base_url=os.environ["OPENAI_BASE_URL"], api_key=os.environ["OPENAI_API_KEY"])

MODELS = [m.strip() for m in os.environ["BENCH_MODELS"].split(",") if m.strip()]
PROMPTS = {
    "factual": "What is the capital of Australia? Answer in one sentence.",
    "reasoning": (
        "A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. "
        "How much does the ball cost? Show your reasoning briefly."
    ),
    "creative": "Write a four-line poem about a lighthouse keeper who is afraid of the dark.",
}

def run(model: str, prompt: str) -> dict:
    """One call. Timer wraps the API call only — the prompt is already built."""
    try:
        t0 = time.perf_counter()
        r = client.chat.completions.create(model=model, messages=[{"role": "user", "content": prompt}])
        latency = time.perf_counter() - t0
    except Exception as e:
        status = "RATE_LIMITED" if isinstance(e, RateLimitError) else "ERROR"
        return {"latency": None, "total": None, "thinking": None, "output": f"{status}: {str(e).splitlines()[0][:80]}"}
    # Not every provider reports usage or reasoning tokens, so fall back to None/0.
    details = r.usage.completion_tokens_details if r.usage else None
    return {
        "latency": latency,
        "total": r.usage.total_tokens if r.usage else None,
        "thinking": (details.reasoning_tokens if details else None) or 0,
        "output": " ".join((r.choices[0].message.content or "").split())[:200],
    }

def fmt(value, spec: str) -> str:
    return "-" if value is None else format(value, spec)

rows = [(kind, model, run(model, prompt)) for kind, prompt in PROMPTS.items() for model in MODELS]

print(f"{'prompt':<10} {'model':<38} {'latency_s':>9} {'total':>6} {'think':>6}  output[:100]")
print("-" * 160)
for kind, model, r in rows:
    print(
        f"{kind:<10} {model:<38} {fmt(r['latency'], '.2f'):>9} {fmt(r['total'], 'd'):>6} "
        f"{fmt(r['thinking'], 'd'):>6}  {r['output']}"
    )

print("\nFastest per prompt:")
for kind in PROMPTS:
    timed = [(r["latency"], model) for k, model, r in rows if k == kind and r["latency"] is not None]
    print(f"  {kind:<10} {min(timed)[1] if timed else 'no successful runs'}")

# What I Learnt :
# Lesson 02: Comparing LLMs
# Choosing a model should rest on measurements, not on reputation. This script sends the same factual, reasoning and creative prompts to several models and records latency, total tokens, thinking tokens and the start of each answer, so the trade-offs are visible side by side. The timer wraps only the API call, so string building is not counted. Each call has its own try/except, so one 429 or error is marked RATE_LIMITED/ERROR and the other runs continue. Providers also report usage differently: some leave out reasoning tokens altogether, so the code falls back to None or 0 instead of crashing. The key takeaway: a bigger model is not always better. Run the same prompts, compare the numbers, and use the cheapest, fastest model that still answers correctly for each type of task.

# Why I switched from google-genai to the OpenAI SDK:
# The lesson was written for three Gemini models, but the Gemini free tier kept hitting rate limits and restricts the Pro models, so a full 9-run comparison was hard to finish. Most providers (OpenRouter, Groq, Together, local servers such as Ollama, and Gemini itself) expose the OpenAI-compatible Chat Completions API, so the `openai` client with a custom OPENAI_BASE_URL can reach almost any model. Switching providers or models now only means editing .env (OPENAI_BASE_URL, OPENAI_API_KEY, BENCH_MODELS), with no code changes. That makes the benchmark vendor-neutral, which is what a fair comparison needs.
