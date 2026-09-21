# Lesson 19 — Small Language Models (SLMs)

> Source: `19-slm` (Microsoft Phi-3/3.5) · Extended with Google's Gemma and the flash-lite tier.

## 🎯 Goal
Know when smaller is better, and how to run a model on your own hardware.

---

## 1. What is an SLM?
A scaled-down LLM: same architectural principles, **significantly smaller computational footprint**.
Usually built by **compressing or distilling** a larger model, retaining much of its capability.

Still handles: text generation, text completion, translation, summarization — with trade-offs in
depth of understanding.

## 2. LLM vs SLM — five axes

| Axis | LLM | SLM |
|---|---|---|
| **Size** | ~1.76T params (GPT-4 est.) | ~3–14B (Phi-3-mini 3.8B, Mistral 7B) |
| **Comprehension** | Broad, general, versatile | Optimized for specific domains; narrower |
| **Computing** | GPU clusters; thousands of GPUs to train | Trains/runs on a local machine with a moderate GPU |
| **Bias** | Higher — trained on raw internet data | Lower — constrained domain-specific datasets (not immune) |
| **Inference** | Needs parallel compute; slows under concurrent load | Fast on local hardware |

**Why they exist:** deployment in resource-constrained environments — mobile, edge, offline,
privacy-sensitive.

**Applications:** chatbots, content creation, education, accessibility (e.g. text-to-speech tools).

## 3. The Phi-3 / 3.5 family (the lesson's reference SLM)

| Model | Params | Notes |
|---|---|---|
| **Phi-3-mini** | 3.8B | Outperforms models twice its size |
| **Phi-3-small / medium** | 7B / 14B | Small beats GPT-3.5T on language/reasoning/coding/math; medium beats Gemini 1.0 Pro |
| **Phi-3.5-mini** | 3.8B | Same params, 20+ languages, stronger long context |
| **Phi-3-Vision** | 4.2B | Beats Claude-3 Haiku & Gemini 1.0 Pro V on OCR, tables, diagrams |
| **Phi-3.5-Vision** | — | Adds **multi-image / video** reasoning |
| **Phi-3.5-MoE** | 16×3.8B, **6.6B active** | Mixture-of-Experts: pretrain with far less compute for the same quality |

**MoE idea:** only a subset of "expert" sub-networks activates per input, so you scale model size
without scaling compute per token.

## 4. The Google equivalents

| Option | What | How |
|---|---|---|
| **`gemini-flash-lite-latest`** | Smallest hosted tier — fastest, cheapest | Same API, just swap the model ID ✅ |
| **Gemma** (`gemma-4-31b-it`, `gemma-4-26b-a4b-it`) | Open weights, Gemini-family | Callable with your key, or run locally |

```python
# The one-line SLM: same code, a smaller model
r = client.interactions.create(
    model="gemini-flash-lite-latest",
    input="Summarize this paragraph in one sentence: ...",
)
```
> For high-volume simple work this is the single biggest saving available on the free tier — it
> avoids the heavy thinking-token cost measured in lesson 00.

## 5. Running locally — four routes

**A. Ollama** — simplest
```bash
ollama run phi3.5          # or: ollama run gemma3
```

**B. Hugging Face Transformers** — most control (GPU recommended)
```python
from transformers import pipeline
pipe = pipeline("text-generation", model="google/gemma-3-4b-it", device_map="auto")
print(pipe("Explain SLMs in one sentence.", max_new_tokens=80)[0]["generated_text"])
```

**C. Foundry Local** — Microsoft's offline on-device runtime; auto-selects NPU/GPU/CPU and exposes
an **OpenAI-compatible endpoint**, so existing SDK code repoints with minimal change.
```bash
winget install Microsoft.FoundryLocal
foundry model run phi-3.5-mini
```

**D. ONNX Runtime for GenAI** — cross-platform accelerated inference (Windows, Linux, macOS, Android, iOS)
```bash
pip install onnxruntime onnxruntime-genai
```
```python
import onnxruntime_genai as og

model = og.Model('path_to_your_model.onnx')
tokenizer = og.Tokenizer(model)
tokens = tokenizer.encode("Hello, how are you?")
print(tokenizer.decode(model.generate(tokens)))
```
Handles the generation loop, KV-cache management, greedy/beam search and TopP/TopK sampling.

**Others:** Apple MLX (Metal), Qualcomm QNN (NPU), Intel OpenVINO (CPU/GPU).

## 6. Cloud APIs for SLMs
Microsoft Foundry Models catalog (Phi Instruct/Vision/MoE), **NVIDIA NIM** (single-command deploy,
TensorRT-optimized, Kubernetes autoscaling, self-hostable, standard APIs).

---

## 🧠 Crux Notes
- SLMs trade breadth for **efficiency, speed, privacy and offline capability**.
- The decision axes are **size, comprehension, computing, bias, inference speed** — pick on your constraints, not on benchmarks.
- **MoE** gets you large-model quality at small-model compute by activating only the relevant experts.
- The cheapest SLM move in this course: change the model ID to **`gemini-flash-lite-latest`**.
- For true local/offline: **Ollama** to start, **ONNX Runtime / Foundry Local** for production on-device.
- Quantization matters — unquantized vision/MoE models are painfully slow on CPU.

---

## ✅ Test Your Knowledge

**1.** Name the five axes distinguishing LLMs from SLMs.
<details><summary>Answer</summary>

**Size, comprehension, computing, bias, inference speed.**
</details>

**2.** How are SLMs typically built?
<details><summary>Answer</summary>

By **compressing or distilling** a larger model, retaining much of its functionality and linguistic capability at a fraction of the computational footprint.
</details>

**3.** Explain Mixture-of-Experts in one sentence, using Phi-3.5-MoE's numbers.
<details><summary>Answer</summary>

Only a subset of expert sub-networks activates per input, so Phi-3.5-MoE has 16×3.8B experts but just **6.6B active parameters** — large-model quality at small-model compute.
</details>

**4.** Why are SLMs less prone to bias, and why is that not a guarantee?
<details><summary>Answer</summary>

They train on more constrained, domain-specific datasets rather than raw internet data. But constrained data can carry its own biases — they are less susceptible, not immune.
</details>

**5.** Cheapest way to get SLM-like economics without leaving the Gemini API?
<details><summary>Answer</summary>

Switch the model ID to **`gemini-flash-lite-latest`** — same code, smallest hosted tier, and it avoids much of the thinking-token cost.
</details>

**6.** Four ways to run a model locally?
<details><summary>Answer</summary>

**Ollama** (simplest), **Hugging Face Transformers** (most control), **Foundry Local** (on-device, OpenAI-compatible endpoint), **ONNX Runtime for GenAI** (cross-platform, accelerated). Also Apple MLX, Qualcomm QNN, Intel OpenVINO.
</details>

---

## 🛠️ Practical Task

**Build:** `practice/19_size_tiers.py` — find the smallest model that is good enough.

### The principle
Do not pick the biggest model you can afford. Find the **smallest one that passes your bar** — that is
where the cost, latency and privacy wins live.

### Requirements
1. Define a real task with an objective pass/fail — e.g. classify 25 sentences by sentiment, or extract 3 fields from 25 short documents.
2. Run it against three tiers: `gemini-flash-lite-latest`, `gemini-flash-latest`, `gemini-pro-latest`.
3. Record per tier: **accuracy**, **mean latency**, **total tokens**, **thinking tokens**.
4. Set a quality bar up front (e.g. "≥ 90% accuracy") and report the **cheapest tier that clears it**.
5. Estimate cost per 10,000 requests for each tier from your measured token counts.

### Passing criteria

| # | Criterion | Expected |
|---|---|---|
| 1 | 75 runs complete | 25 cases × 3 tiers |
| 2 | Quality bar set **before** seeing results | Defined at the top of the file |
| 3 | All 4 metrics per tier | Table |
| 4 | Recommendation is the **cheapest passing** tier | Not simply the most accurate |
| 5 | Cost projection included | Uses measured tokens, not guesses |
| 6 | Rate limits handled | 75 calls will likely hit one — back off and retry |

### Verify
```bash
python practice/19_size_tiers.py | tee practice/19_results.txt
# PASS: all 3 tiers scored, recommendation justified by the pre-set bar
```

**Stretch (local):** `ollama pull gemma3` and add it as a fourth row with latency and accuracy. Its cost
column is £0 and its privacy column is "data never leaves the machine" — which for some tasks outweighs
a few accuracy points.

**Expect this result:** flash-lite very often clears the bar. Teams routinely overpay by defaulting to
the largest model without ever measuring whether they needed it.
