# Lesson 20 — Building with Mistral Models

> Source: `20-mistral` · The original calls Azure/Foundry. Below: the concepts, plus how to follow
> along with **only your Gemini key** (Gemma) or a **local Mistral** via Ollama.

## 🎯 Goal
Understand the Mistral family and the trade-offs it illustrates: large vs small, tokenizer efficiency, MoE.

---

## 1. The three models

| Model | Category | Distinctive |
|---|---|---|
| **Mistral Large 2 (2407)** | Flagship, enterprise | 128k context (vs 32k), 76.9% avg on math/coding (vs 60.4%), 13 languages |
| **Mistral Small** | SLM, premier tier | ~80% cheaper than Large, low latency, flexible deployment |
| **Mistral NeMo** | Open, **Apache 2.0** | Tekken tokenizer, fine-tunable, native function calling |

**Mistral Large excels at:** RAG (large context window), **native function calling** (parallel or
sequential), code generation (Python, Java, TypeScript, C++).

**Mistral Small is for:** summarization, sentiment, translation; high-frequency requests where cost
matters; low-latency code review and suggestions.

**Mistral NeMo** is the only free/Apache-2.0 one — an upgrade to Mistral 7B, with a more efficient
**Tekken** tokenizer that produces **fewer tokens** for the same text than tiktoken (better across
languages and code — fewer tokens means lower cost and more room in context).

## 2. Concepts worth taking away

**Large vs Small is a real engineering decision.** The lesson's exercise is to run the same prompt
against both and observe a **3–5 second latency difference**, plus different response lengths and
styles. Do this with any model family:

```python
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client()

prompt = "Can you write a Python function for the fizz buzz test?"

for model in ["gemini-flash-lite-latest", "gemini-flash-latest", "gemini-pro-latest"]:
    t0 = time.perf_counter()
    r = client.interactions.create(
        model=model,
        system_instruction="You are a helpful coding assistant.",
        input=prompt,
    )
    print(f"\n=== {model} — {time.perf_counter()-t0:.2f}s ===\n{r.output_text[:300]}")
```
**Tokenizer efficiency is a cost lever.** Different tokenizers split the same text differently:

```python
print(client.models.count_tokens(model="gemini-flash-latest",
                                 contents="What's the weather like today in Paris"))
```
Compare across models/providers — fewer tokens for identical text is a direct cost saving.

## 3. RAG with Mistral — the original pattern

The lesson builds RAG over a text document: chunk it, embed with Cohere embeddings, index with
**faiss**, retrieve the top-k similar chunks, and put them in the prompt. Note the question is
asked in Korean against an English document — **embeddings are multilingual**, so retrieval works
across languages.

```python
import requests, numpy as np, faiss
from google import genai

client = genai.Client()

text = requests.get(
    "https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/"
    "data/paul_graham/paul_graham_essay.txt").text

chunk_size = 2048
chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

def embed(items):
    r = client.models.embed_content(model="gemini-embedding-001", contents=items)
    return np.array([e.values for e in r.embeddings], dtype="float32")

emb = embed(chunks)
index = faiss.IndexFlatL2(emb.shape[1])
index.add(emb)

question = "저자가 대학에 오기 전에 주로 했던 두 가지 일은 무엇이었나요?"
D, I = index.search(embed([question]), k=2)
retrieved = [chunks[i] for i in I[0]]

answer = client.interactions.create(
    model="gemini-flash-latest",
    input=f"""Context information is below.
---------------------
{retrieved}
---------------------
Given the context information and not prior knowledge, answer the query.
Query: {question}
Answer:""",
)
print(answer.output_text)
```
```bash
pip install faiss-cpu
```

## 4. Running actual Mistral without an Azure account
```bash
ollama run mistral            # or: ollama run mistral-nemo
```
```python
# mistral-common: inspect Mistral's own tokenizer
# pip install mistral-common
from mistral_common.tokens.tokenizers.mistral import MistralTokenizer
tok = MistralTokenizer.from_model("open-mistral-nemo")
```

---

## 🧠 Crux Notes
- **Large vs Small is a latency/cost/quality trade** — measure it on your own prompt, don't assume.
- **Context window size drives RAG quality** — more retrieved chunks fit in a 128k window.
- **Tokenizer efficiency is an invisible cost lever**: fewer tokens for the same text = cheaper + more context.
- **MoE** (used across Mistral and Phi) activates only relevant experts — big-model quality, small-model compute.
- Embeddings are **multilingual**: you can retrieve English documents with a Korean query.
- Apache-2.0 models (NeMo) are the ones you can freely self-host and fine-tune.

---

## ✅ Test Your Knowledge

**1.** What did Mistral Large 2 improve over the original Mistral Large?
<details><summary>Answer</summary>

Context window 32k → **128k**, math/coding accuracy 60.4% → **76.9%**, and broader multilingual support (13 languages).
</details>

**2.** Why does a larger context window improve RAG?
<details><summary>Answer</summary>

More retrieved chunks fit in the prompt, so the model sees more potentially relevant evidence — better recall without re-architecting retrieval.
</details>

**3.** What is the Tekken tokenizer's practical benefit?
<details><summary>Answer</summary>

**Fewer tokens for the same text** than tiktoken, especially across languages and code. Fewer tokens means lower cost and more content fitting in the context window.
</details>

**4.** Mistral Small is ~80% cheaper than Large. When is that the wrong trade?
<details><summary>Answer</summary>

When the task needs the capability Large has — complex reasoning, large-context RAG, hard code generation. Small suits summarization, sentiment, translation, and high-frequency low-latency calls.
</details>

**5.** The RAG example asks a Korean question against an English document. Why does retrieval work?
<details><summary>Answer</summary>

Embeddings are **multilingual** — they encode meaning, not surface language, so a Korean query lands near semantically-related English chunks.
</details>

---

## 🛠️ Practical Task

**Build:** `practice/20_tokenizer_economics.py` — quantify the invisible cost lever.

### Requirements
1. Assemble 6 text samples: English prose, Hindi/Gujarati prose, Chinese text, Python code, JSON, and a URL-heavy string.
2. Count tokens for each with `client.models.count_tokens`.
3. Compute **characters per token** for each.
4. Project the cost of 1,000,000 characters of each type, ranked most to least expensive.
5. Write a conclusion: which content types are expensive to send, and one mitigation for each.

### Passing criteria

| # | Criterion | Expected |
|---|---|---|
| 1 | All 6 sample types measured | Table with chars, tokens, ratio |
| 2 | Non-Latin scripts show a **lower** ratio | More tokens per character |
| 3 | Ranked projection printed | Most → least expensive |
| 4 | Conclusion proposes mitigations | e.g. summarize before embedding; strip boilerplate JSON keys |

### Verify
```bash
python practice/20_tokenizer_economics.py
# PASS: 6 rows with ratios, ranking printed, conclusion written
```

### Part B — multilingual retrieval
Extend `practice/15_rag.py`: ask **3 questions in a non-English language** against your English lesson
notes.

**Passing criteria:** at least 2 of 3 retrieve the correct English lesson. Record the similarity scores
and compare them with the equivalent English queries — are they lower? Does your relevance threshold
still work for both languages, or does it need to be language-aware?

**That last question is the real finding.** A threshold tuned on English queries can silently reject
valid non-English ones.
