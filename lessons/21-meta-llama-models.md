# Lesson 21 — Building with the Meta (Llama) Models

> Source: `21-meta` · The original calls Azure/Foundry. Concepts + how to follow along locally or
> with your Gemini key.

## 🎯 Goal
Understand the Llama family and the two capabilities it showcases: native function calling and multimodality.

---

## 1. The models

| Variant | Notes |
|---|---|
| Llama 3.1 – 70B Instruct | Mid-size open LLM |
| Llama 3.1 – 405B Instruct | Open-weight frontier scale |
| Llama 3.2 – 11B Vision Instruct | Multimodal, smaller |
| Llama 3.2 – 90B Vision Instruct | Multimodal, larger |

## 2. Llama 3.1 — what the upgrade bought

| | Llama 3 | Llama 3.1 |
|---|---|---|
| Context window | 8k | **128k** |
| Max output tokens | 2048 | **4096** |
| Multilingual | Limited | Better (more training tokens) |

Enabling: **native function calling**, **better RAG** (bigger context), **synthetic data generation**
(create training data for fine-tuning).

### Native function calling
Llama 3.1 is fine-tuned for tool calls and ships with two **built-in** tools it can invoke by name:
- **Brave Search** — up-to-date info via web search,
- **Wolfram Alpha** — complex math without writing your own function.

Tools are declared in the **system prompt** using Llama's special token format, and the model
responds with a call like:
```
<|python_tag|>brave_search.call(query="Stockholm weather")
```
> Note the contrast with Gemini/OpenAI: Llama expresses tools as **prompt-level text conventions**,
> while Gemini uses a **structured `tools` parameter** and returns a typed `function_call` step.
> Same concept, different interface — and the structured version is far less error-prone to parse.

## 3. Llama 3.2 — multimodality
Llama 3.1's limitation was text-only. Llama 3.2 adds:
- **Multimodality** — evaluate text *and* image prompts,
- **11B / 90B** variants — flexible deployment,
- **1B / 3B text-only** variants — edge/mobile deployment, low latency.

This was a significant step for open models.

## 4. The same two capabilities with your Gemini key

**Multimodal — image + text in one call:**
```python
import base64
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client()

with open("sample.jpg", "rb") as f:
    img = base64.b64encode(f.read()).decode("utf-8")

r = client.interactions.create(
    model="gemini-flash-latest",
    system_instruction="You are a helpful assistant that describes images in detail.",
    input=[
        {"type": "text",  "text": "What's in this image?"},
        {"type": "image", "data": img, "mime_type": "image/jpeg"},
    ],
)
print(r.output_text)
```

**Built-in search tool** (the Brave Search equivalent):
```python
r = client.interactions.create(
    model="gemini-flash-latest",
    input="What is the weather in Stockholm?",
    tools=[{"type": "google_search"}],
)
```

## 5. Running Llama locally
```bash
ollama run llama3.2              # text
ollama run llama3.2-vision       # multimodal
```

---

## 🧠 Crux Notes
- Llama's headline jump was **context window 8k → 128k**, which is what made it usable for RAG.
- **Native function calling** = the model was *trained* to emit tool calls, not prompted into it.
- Llama expresses tools as **prompt-text conventions**; Gemini uses a **structured `tools` API** — prefer structured interfaces, they're parseable and less brittle.
- **Llama 3.2 brought multimodality to open weights**, plus 1B/3B variants for edge devices.
- Built-in tools (Brave Search, Wolfram Alpha / Google Search) save you writing and hosting functions.
- Model family lessons are interchangeable at the concept level: **context window, tool calling, modality, size tier**.

---

## ✅ Test Your Knowledge

**1.** What were the three main Llama 3 → 3.1 upgrades?
<details><summary>Answer</summary>

Context window 8k → **128k**, max output 2048 → **4096**, better multilingual support from more training tokens.
</details>

**2.** What are Llama 3.1's two built-in tools, and what are they for?
<details><summary>Answer</summary>

**Brave Search** (up-to-date information via web search) and **Wolfram Alpha** (complex mathematical calculation without writing your own function).
</details>

**3.** How does Llama express a tool call versus Gemini, and which is more robust?
<details><summary>Answer</summary>

Llama uses **prompt-level text conventions** with special tokens (`<|python_tag|>brave_search.call(...)`), which you parse out of the text. Gemini returns a **structured `function_call` step** with typed arguments. The structured version is more robust — no string parsing, no ambiguity.
</details>

**4.** What did Llama 3.2 add, and why did the 1B/3B variants matter?
<details><summary>Answer</summary>

**Multimodality** — image plus text input. The 1B/3B text-only variants enable edge/mobile deployment with low latency.
</details>

**5.** "Synthetic data generation" appears as a Llama 3.1 use case. What is it for?
<details><summary>Answer</summary>

Generating training data for tasks such as fine-tuning — using a large capable model to produce examples that train a smaller, cheaper one.
</details>

---

## 🛠️ Practical Task

**Build:** `practice/21_multimodal.py` — a vision pipeline plus a tool-interface comparison.

### Part A — Multimodal extraction
1. Gather 5 images: a chart, a screenshot of a table, a handwritten note, a photo of a scene, a diagram.
2. For each, extract **structured data** with a Pydantic schema suited to the type (e.g. chart → `{title, x_axis, y_axis, data_points[]}`).
3. Validate every response against its schema.
4. Cross-check one result manually and record the accuracy.

#### Passing criteria

| # | Criterion | Expected |
|---|---|---|
| 1 | All 5 images processed | Base64-encoded, correct `mime_type` |
| 2 | Responses schema-valid | Pydantic validation passes |
| 3 | Handles an unreadable image | Blurry/blank input → graceful message, no crash |
| 4 | Manual accuracy check recorded | You compared at least one against ground truth |
| 5 | Wrong MIME type handled | Send a `.png` labelled `image/jpeg` — observe and handle |

### Part B — Tool interface comparison
Get the *same* tool call two ways:
1. **Structured** — Gemini `tools=[...]`, read `function_call.arguments`.
2. **Prompt-convention** — instruct a model to reply with `TOOL: name(arg="value")` as plain text, then regex it out.

Run both over **10 queries**, including awkward ones: arguments containing quotes, commas, parentheses, and a query needing two tool calls.

#### Passing criteria

| # | Criterion | Expected |
|---|---|---|
| 1 | Both approaches run all 10 | 20 results |
| 2 | **Parse failure rate reported** | The structured approach should be near 0% |
| 3 | An edge case that breaks regex parsing | e.g. an argument containing `)` or a comma |
| 4 | Written conclusion | Why structured tool APIs exist |

### Verify
```bash
python practice/21_multimodal.py
# PASS: 5 images schema-valid; Part B reports parse failure rates for both approaches
```

**The lesson in Part B:** you will find a query where regex parsing breaks and the structured API does
not. That failure *is* the deliverable — it is why every major provider moved to structured tool calling.
