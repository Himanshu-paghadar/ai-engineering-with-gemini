# Lesson 02 — Exploring & Comparing Different Models

> Source: `02-exploring-and-comparing-different-llms` · Retargeted to the Gemini model family.

## 🎯 Goal
Pick the right Gemini model for a job, and know the four ways to make any model perform better.

---

## 1. Model taxonomy (four axes)

**A. By modality / task — the Gemini family**

| Task | Model IDs (✅ confirmed available to this project's key) |
|---|---|
| Text / reasoning (workhorse) | `gemini-flash-latest` → `gemini-3.8-flash`; also `3.7`, `3.6`, `3.5`, `2.5-flash` |
| Cheapest / fastest | `gemini-flash-lite-latest`, `gemini-3.5-flash-lite`, `gemini-3.1-flash-lite` |
| Deep reasoning | `gemini-pro-latest`, `gemini-2.5-pro`, `gemini-3.1-pro-preview` |
| Image generation | `gemini-3.1-flash-image`, `gemini-3-pro-image`, `gemini-2.5-flash-image` |
| Embeddings | `gemini-embedding-001` (3072-dim), `gemini-embedding-2` |
| Speech-to-text | `gemini-3.5-transcribe`, `gemini-3.5-transcribe-live` |
| TTS / live voice | `gemini-3.1-flash-tts-preview`, `gemini-3.8-live` |
| Video / music | `veo-3.1-generate-preview`, `lyria-3.5` |
| Open weights (Google) | `gemma-4-31b-it`, `gemma-4-26b-a4b-it` |
| Agentic / research | `deep-research-preview-*`, `gemini-2.5-computer-use-preview`, `antigravity-preview-*` |

Use the **`-latest` aliases** in code you intend to keep; pin an exact version only when you need
reproducibility.

```python
for m in client.models.list():
    print(m.name)      # ground truth for what YOUR key can call
```

**B. Foundation model vs LLM** — foundation models are self-supervised, very large, and intended as a *base* for other models. An LLM is a text-focused foundation model.

**C. Open-weight vs proprietary**
- **Open** (Google's **Gemma**, Llama, Mistral, HF models): control, data locality, offline use, customization — but you own serving, security, evals and licence review.
- **Proprietary** (Gemini, GPT, Claude): managed scale, safety systems, tool integration — no weight access; review retention/compliance terms.

**D. By architecture**

| Architecture | Analogy | Good at | Example |
|---|---|---|---|
| Decoder-only | The *writer* | Generation | Gemini, GPT, Llama |
| Encoder-only | The *reviewer* | Classification, retrieval | BERT |
| Encoder-decoder | Both | Translation, seq2seq | T5, BART |

## 2. Service vs Model
- **Service** = product (models + infra + safety + quota + SLA), e.g. the Gemini API / AI Studio, or Vertex AI.
- **Model** = the artifact (weights, tokenizer, config). Self-hosting Gemma means GPUs, serving infra and monitoring are yours.

## 3. Test and iterate
- **AI Studio playground** — try a prompt across models side by side before writing code.
- **Same prompt, three models** — measure quality, latency and token cost together:

```python
import time
from google import genai

client = genai.Client()
prompt = "Explain cosine similarity to a first-year student in 3 sentences."

for model in ["gemini-flash-lite-latest", "gemini-flash-latest", "gemini-pro-latest"]:
    t0 = time.perf_counter()
    r = client.interactions.create(model=model, input=prompt)
    # tip: also print r.usage to compare thinking-token cost
    print(f"\n=== {model}  ({time.perf_counter()-t0:.2f}s) ===\n{r.output_text}")
```

## 4. The improvement ladder — 🔑 the core of this lesson

```
Cheapest / fastest                                       Most expensive
│                                                                     │
Prompt engineering  →  RAG  →  Fine-tuning  →  Train from scratch
(context + examples)   (fresh/private facts)  (stable behaviour)  (domain corpus + GPUs)
```

| Approach | Use when | Gemini-free-tier reality |
|---|---|---|
| **Prompt engineering + context** | Always start here (zero/one/few-shot) | ✅ Free |
| **RAG** | Model needs *current* or *private* facts | ✅ Free (embeddings + your own vector store) |
| **Grounding with Google Search** | Needs live public facts, with citations | ✅ Built-in tool — see lesson 15 |
| **Fine-tuning** | Consistent task pattern / format / tone | ❌ **Not available on the Gemini API** — see lesson 18 |
| **Train from scratch** | Huge domain corpus + ML team | ❌ |

**Decision rule:** fresh facts → RAG or Search grounding. Consistent behaviour → system instruction + few-shot (since tuning is off the table here).

---

## 🧠 Crux Notes
- Don't pick by name or price alone — compare **task quality, latency, context window, tool support, safety behaviour, cost**.
- `client.models.list()` is the only trustworthy list of what your key can call.
- Embeddings ≠ generation: embeddings turn text into vectors for search/clustering (lessons 08 & 15).
- **Flash-lite for volume, Flash for default, Pro for reasoning** is a workable everyday heuristic.
- On the Gemini free tier the ladder effectively stops at RAG — so prompt craft and retrieval are where your leverage is.

---

## ✅ Test Your Knowledge

**1.** What is a good approach to improve LLM completion results — prompt engineering with context, RAG, or a fine-tuned model?
<details><summary>Answer</summary>

**All three**, in that order of effort. Start with prompt engineering and context for quick wins. Use RAG when the model needs current facts or private data. Fine-tune when you have high-quality examples and need consistent task, format, tone or domain patterns.
</details>

**2.** Your chatbot must answer questions about a product manual written last month. RAG or fine-tuning?
<details><summary>Answer</summary>

**RAG.** The problem is missing *facts*, and those facts change. Fine-tuning teaches behaviour, not knowledge, and would need re-running every time the manual changes.
</details>

**3.** Which architecture is best at classification and retrieval, and why is it bad at writing?
<details><summary>Answer</summary>

**Encoder-only** (e.g. BERT) — the "reviewer". It builds rich representations of input relationships but is not designed to generate continuations. Decoder-only models (Gemini, GPT, Llama) are the "writers".
</details>

**4.** What is the difference between a *service* and a *model*?
<details><summary>Answer</summary>

A service is a product bundling models, infrastructure, safety systems, quota and SLA (the Gemini API, Vertex AI). A model is the artifact — weights, architecture, tokenizer. Self-hosting a model means you own the GPUs, serving and monitoring.
</details>

**5.** Why is `client.models.list()` more trustworthy than a docs table?
<details><summary>Answer</summary>

It reports what *your key in your project* can actually call right now. Availability varies by key, tier and region, and docs lag reality.
</details>

---

## 🛠️ Practical Task

**Build:** `practice/02_model_bench.py` — a benchmark harness that picks a model on evidence rather than vibes.

### Requirements
1. Run the **same 3 prompts** (one factual, one reasoning, one creative) against 3 models:
   `gemini-flash-lite-latest`, `gemini-flash-latest`, `gemini-pro-latest`
2. For each run record: **latency (s)**, **total tokens**, **thinking tokens**, and the first 100 chars of output.
3. Print a comparison table.
4. Write a 3-sentence conclusion as a comment at the bottom: which model you would ship for which prompt type, and why.

### Passing criteria

| # | Criterion | How to verify |
|---|---|---|
| 1 | 9 runs complete (3 prompts × 3 models) | Table has 9 rows |
| 2 | Latency measured with `time.perf_counter()` around the call only | Read the code |
| 3 | Handles a `429` without crashing the whole run | Wrap each call in try/except; record `RATE_LIMITED` |
| 4 | flash-lite is fastest on at least one prompt | Check the table |
| 5 | Conclusion cites **numbers**, not impressions | Your comment mentions actual measured values |

### Verify
```bash
python practice/02_model_bench.py | tee practice/02_results.txt
# PASS if the table has 9 rows and no unhandled exception
```

**Trap to avoid:** do not start the timer before building the prompt string. You are measuring the API, not your own string formatting.
