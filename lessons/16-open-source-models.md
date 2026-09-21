# Lesson 16 — Open Source / Open Weight Models

> Source: `16-open-source-models` · Extended with Google's **Gemma** family, available to this key.

## 🎯 Goal
Understand open models, their benefits, and when to pick one over a hosted API.

---

## 1. What counts as "open source"?
The OSI defines 10 criteria for open-source software, but LLMs don't map cleanly. For a model to
match the traditional definition, all of this should be public:
- the **datasets** used for training,
- **full model weights**,
- the **evaluation code**,
- the **fine-tuning code**,
- full weights **and training metrics**.

Very few models qualify (AllenAI's **OLMo** is one). Most release weights but not data — hence the
course uses the term **"open models"** rather than "open source".

## 2. Benefits

| Benefit | Detail |
|---|---|
| **Highly customizable** | Modify internals; fine-tune for code, math, biology, a language |
| **Cost** | Lower cost per token to deploy than proprietary models |
| **Flexibility** | Swap or combine models; run offline / on-device / in your own VPC |
| **Data locality** | Your data never leaves your infrastructure |

## 3. The families

| Family | Notes |
|---|---|
| **Gemma** (Google) | Open-weight siblings of Gemini. ✅ `gemma-4-31b-it`, `gemma-4-26b-a4b-it` are callable with your Gemini API key |
| **Llama** (Meta) | Chat-optimized via dialogue + human feedback; huge fine-tune ecosystem (see lesson 21) |
| **Mistral** | High performance/efficiency; Mixture-of-Experts routes inputs to specialist sub-models (lesson 20) |
| **Falcon** (TII) | Falcon-40B beat GPT-3 with less compute via FlashAttention + multiquery attention |

Notable fine-tunes: Japanese Llama, Llama Pro, BioMistral (medical), OpenMath Mistral, OpenAssistant, GPT4ALL.

## 4. Calling Gemma with your existing key

The convenience of open weights *without* hosting anything yourself:

```python
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client()

r = client.models.generate_content(
    model="gemma-4-31b-it",
    contents="Explain mixture-of-experts in 3 sentences.",
)
print(r.text)
```
> Gemma models are plain text-in/text-out — no tools, no thinking steps. Use `models.generate_content`.

## 5. Running fully locally (no API, no key)

```bash
# Ollama — simplest path to local inference
ollama run gemma3
```

```python
# Hugging Face Transformers — full control, needs a GPU for comfort
from transformers import pipeline

pipe = pipeline("text-generation", model="google/gemma-3-4b-it", device_map="auto")
print(pipe("Explain embeddings in one sentence.", max_new_tokens=100)[0]["generated_text"])
```

## 6. How to choose
- Filter a model catalog **by task** to see what a model was trained for.
- Check leaderboards (Hugging Face LLM Leaderboard) and **[Artificial Analysis](https://artificialanalysis.ai/)** for quality-vs-price comparisons.
- For a specific use case, look for an existing **fine-tuned variant** in that domain.
- **Experiment with several** against your own data and users' expectations.

---

## 🧠 Crux Notes
- "Open model" ≠ "open source" — most release weights only. **Read the licence** before shipping.
- Open models buy you **control, cost, offline use and data locality**; you pay in serving, security, evals and ops.
- **Gemma is Google's open family** — and you can call it with the same free API key you already have.
- Local options: **Ollama** (easiest), **Transformers** (most control).
- Choose by measured performance on *your* task, not by leaderboard position or parameter count.

---

## ✅ Test Your Knowledge

**1.** Why does this course say "open models" rather than "open source models"?
<details><summary>Answer</summary>

Truly open source would require public training datasets, full weights, evaluation code, fine-tuning code and training metrics. Very few qualify (AllenAI's OLMo is one). Most release weights only.
</details>

**2.** Name three benefits and three costs of open models.
<details><summary>Answer</summary>

Benefits: customizability, lower cost per token, flexibility/offline use, data locality. Costs: you own serving infrastructure, security patching, evaluation quality, and licence review.
</details>

**3.** Which open family can you call with your existing Gemini key, and with which method?
<details><summary>Answer</summary>

**Gemma** — `gemma-4-31b-it`, `gemma-4-26b-a4b-it` — via `client.models.generate_content()`. They are plain text-in/text-out: no tools, no thinking steps.
</details>

**4.** What makes Falcon-40B notable?
<details><summary>Answer</summary>

It outperformed GPT-3 with a smaller compute budget by using FlashAttention and multiquery attention, cutting memory needs at inference — which suits chat applications.
</details>

**5.** How should you actually choose an open model?
<details><summary>Answer</summary>

Filter a catalog by task, check leaderboards and Artificial Analysis for quality-vs-price, look for an existing fine-tune in your domain, then **test several against your own data**. Not by parameter count or leaderboard rank alone.
</details>

---

## 🛠️ Practical Task

**Build:** `practice/16_open_vs_hosted.py` — an evidence-based comparison.

### Requirements
1. Run **the same 5 prompts** (mix of reasoning, summarization, code) against:
   - `gemini-flash-latest` (hosted proprietary)
   - `gemma-4-31b-it` (open weights, hosted on the same API)
   - *(optional)* a local model via Ollama, if installed
2. Record latency, output length and a quality judgement per response.
3. Score quality with **LLM-as-judge** (1–5), judging blind — do not tell the judge which model produced which answer.
4. Print a comparison table and write a recommendation.

### Passing criteria

| # | Criterion | Expected |
|---|---|---|
| 1 | 10+ runs complete | 5 prompts × 2+ models |
| 2 | Correct method per model | `interactions.create` for Gemini, `models.generate_content` for Gemma |
| 3 | Judging is **blind** | Model names stripped before judging — check the code |
| 4 | Latency and length recorded | In the table |
| 5 | Recommendation names a use case | "Gemma for X because Y" with numbers |

### Verify
```bash
python practice/16_open_vs_hosted.py | tee practice/16_results.txt
# PASS: table complete, judging blind, recommendation cites measured values
```

**Why blind judging matters:** if the judge knows which is the "big" model, its scores drift toward that
expectation. Stripping labels is the difference between an evaluation and a rationalization.

**Stretch:** install Ollama, `ollama pull gemma3`, add it as a third row, and include **cost per 1k
requests** — the open model's real argument is usually economics, not quality.
