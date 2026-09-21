# Lesson 18 — Fine-Tuning Your LLM

> Source: `18-fine-tuning`
> ⚠️ **Reality check for this course setup:** fine-tuning is **not available on the Gemini API**.
> Read §5 before planning any work around it.

## 🎯 Goal
Know what fine-tuning is, when it's the right answer — and what to do instead here.

---

## 1. What is fine-tuning?
Take a pre-trained model and **retrain it with new curated data** to create a **custom model** with
updated weights, better at your task or domain.

Contrast with the earlier techniques, which modify the **prompt input**:
- Prompt engineering / few-shot → *modifies the prompt*
- RAG → *modifies the prompt* (with retrieved data)
- **Fine-tuning → modifies the model**

It also fixes two limits of few-shot learning:
- **Token limits** cap how many examples you can include,
- **Token costs** make examples expensive on *every* request.

## 2. When to fine-tune — ask these first

| Question | What to check |
|---|---|
| **Use case** | What exactly do you want to improve? |
| **Alternatives** | Did you baseline with prompt engineering *and* RAG first? |
| **Costs** | Tunability, effort (data prep), compute, data availability |
| **Benefits** | Quality vs baseline? Fewer tokens? Reusable base model? |

**Proceed only if benefits outweigh costs.**

**Fine-tune for:** consistent task pattern, output format, tone, domain style; smaller task-specific
models; latency (shorter prompts).
**Don't fine-tune for:** fresh facts or private knowledge that changes — **that's RAG**.

## 3. Techniques

| Technique | What it does | When |
|---|---|---|
| **SFT** (Supervised Fine-Tuning) | Trains on input/output pairs | ⭐ Default — domain specialization, format, tone, instruction-following |
| **DPO** (Direct Preference Optimization) | Learns from preferred vs non-preferred response pairs | Alignment, safety, quality with comparative feedback |
| **RFT** (Reinforcement Fine-Tuning) | Optimizes via reward signals from graders | Objective reasoning domains (math, physics); needs ML expertise |

Modern platforms use **LoRA (low-rank adaptation)** under the hood — train a small set of adapter
weights instead of every parameter, which is far faster and cheaper.

## 4. Best practices (universal)
- **Baseline first.** Measure prompt engineering + RAG *before* tuning, so you can prove the gain.
- **Start small, then scale.** 50–100 high-quality examples to validate; 500+ for production. **Quality beats quantity** — prune bad examples.
- **Format data correctly.** JSONL, chat-message format, with a **validation file** to catch overfitting.
- **Keep the training system prompt at inference.** Use the same system message you trained with.
- **Evaluate checkpoints** — don't blindly deploy the last epoch. Watch `train_loss` / `valid_loss`.
- **Measure token cost alongside quality.**
- **Iterate** — you can fine-tune an already fine-tuned model on new data.
- **Mind hosting costs** — a deployed custom model bills continuously.

## 5. ⚠️ Fine-tuning on the Gemini API: not available

Google's documentation is explicit: with the deprecation of Gemini 1.5 Flash-001 in May 2025, **no
model in the Gemini API or AI Studio supports fine-tuning**, and there are no immediate plans to
bring it back. It remains available in the **Gemini Enterprise Agent Platform**.

### What to do instead (all free-tier friendly)

| Instead of fine-tuning for... | Use |
|---|---|
| Consistent **format** | **Structured output** — a JSON schema guarantees shape (lesson 11) |
| Consistent **tone/behaviour** | A carefully written **system instruction** + few-shot examples (lessons 04–05) |
| **Domain knowledge** | **RAG** over your corpus (lesson 15) |
| **Fresh facts** | **Google Search grounding** (lesson 15) |
| **Repeated long context** | **Context caching** — reuse a large fixed prefix across calls |
| Genuinely needing **custom weights** | Fine-tune an **open model** — Gemma, Llama, Mistral (below) |

### The free path to real custom weights: tune Gemma

```bash
pip install transformers peft trl datasets     # LoRA fine-tuning stack
# or: Unsloth, AutoTrain — both wrap this with far less boilerplate
```

Because Gemma weights are open, you can LoRA-tune on a single GPU (Colab's free tier is enough for
the smaller variants) and then serve the result yourself with Ollama or Transformers (lesson 16).

## 6. Tutorials worth doing
| Provider | Tutorial |
|---|---|
| **Hugging Face** | Fine-tuning LLMs with `transformers` + **TRL** on open datasets |
| 🤗 **AutoTrain** | No-code fine-tuning — GUI, CLI, or YAML config; local, cloud, or Spaces |
| 🦥 **Unsloth** | Open-source framework for fast LLM fine-tuning + RL; ready-made notebooks |
| **OpenAI / Microsoft Foundry** | Managed SFT/DPO/RFT if you have those accounts |

---

## 🧠 Crux Notes
- Fine-tuning changes the **model**; prompting and RAG change the **prompt**. Different problems.
- **Fresh/private facts → RAG. Consistent behaviour/format → tuning.** Never fine-tune to teach facts.
- **On the Gemini API you cannot fine-tune** — plan around system instructions, few-shot, structured output and RAG.
- If you truly need custom weights on a budget: **LoRA-tune Gemma or Llama** locally.
- Always baseline first — most "we need fine-tuning" turns out to be "our prompt was vague".
- Quality over quantity: 100 clean examples beat 1,000 noisy ones.

---

## ✅ Test Your Knowledge

**1.** Fine-tuning modifies the ___, while prompt engineering and RAG modify the ___.
<details><summary>Answer</summary>

Fine-tuning modifies the **model** (new weights). Prompt engineering and RAG modify the **prompt**.
</details>

**2.** Your support bot must know this week's pricing. Fine-tune on pricing data?
<details><summary>Answer</summary>

**No.** Fresh, changing facts are a RAG problem. Fine-tuning teaches behaviour, not knowledge, and you would retrain on every price change.
</details>

**3.** SFT, DPO, RFT — match each to its data requirement.
<details><summary>Answer</summary>

**SFT**: input/output example pairs. **DPO**: preferred vs non-preferred response pairs. **RFT**: reward signals from graders, for objective reasoning domains.
</details>

**4.** Can you fine-tune with your Gemini API key?
<details><summary>Answer</summary>

**No.** Since Gemini 1.5 Flash-001's deprecation in May 2025 no Gemini API or AI Studio model supports fine-tuning, with no near-term plans to restore it. It exists in the Gemini Enterprise Agent Platform. On a free key, use system instructions, few-shot, structured output and RAG — or LoRA-tune an open model like Gemma.
</details>

**5.** Why keep the training system prompt at inference time?
<details><summary>Answer</summary>

The model learned the behaviour *conditioned on* that system message. Changing it at inference puts the model outside its training distribution and degrades results.
</details>

**6.** Why not deploy the final epoch's checkpoint by default?
<details><summary>Answer</summary>

It may be overfitted. Compare checkpoints on `train_loss` vs `valid_loss` and token accuracy, and pick the one that generalizes — which is why a validation file is mandatory.
</details>

---

## 🛠️ Practical Task

Fine-tuning is unavailable on your key, so this task has two parts: **prove you do not need it**, then
optionally do it for real on open weights.

### Part A (required) — `practice/18_no_finetune.py`

Pick a task a team would normally propose fine-tuning for: *classify support tickets into 6 categories
and extract urgency, customer sentiment and a one-line summary, in a fixed JSON shape.*

Build and compare three approaches on the **same 20 hand-labelled cases**:
1. **Naive** — plain prompt asking for JSON.
2. **Structured output** — Pydantic schema via `response_format`.
3. **Structured + few-shot + tuned system instruction** — 5 examples plus explicit rules.

Score: **schema-valid rate**, **classification accuracy**, **latency**, **tokens**.

#### Passing criteria

| # | Criterion | Expected |
|---|---|---|
| 1 | 60 runs complete | 20 cases × 3 approaches |
| 2 | Approach 1 shows real variance | Inconsistent shapes/values — this is the point |
| 3 | Approaches 2 and 3 are **100% schema-valid** | A schema is enforced |
| 4 | Accuracy reported per approach | 3 numbers |
| 5 | Written conclusion | Does approach 3 close the gap enough to make fine-tuning unnecessary? |

#### Verify
```bash
python practice/18_no_finetune.py | tee practice/18_results.txt
# PASS: schema-valid rate is 100% for approaches 2-3, and all 3 accuracies print
```

### Part B (optional, stretch) — LoRA-tune Gemma
On Colab's free GPU, LoRA-tune `gemma-3-4b-it` on 100 examples of your task with `transformers` + `peft`
+ `trl` (or Unsloth). Compare against Part A's approach 3.

**Passing criteria:** training completes, you can run inference on the tuned adapter, and you report
whether it beat approach 3 — **including if it did not**. A negative result is a valid, useful finding
and the most common real outcome.
