# Generative AI for Beginners — Python + Gemini Notes

Condensed, Python-focused notes for [microsoft/generative-ai-for-beginners](https://github.com/microsoft/generative-ai-for-beginners),
**retargeted from Azure OpenAI to the Google Gemini API free tier**.

Every lesson has the same shape:

**concepts → runnable Python → 🧠 Crux Notes (revise) → ✅ Test Your Knowledge (quiz) → 🛠️ Practical Task (build)**

Each practical task specifies a deliverable file in `practice/`, a **passing-criteria table**, and
**test cases** with expected behaviour, so you can grade yourself objectively.
Track completion in [PROGRESS.md](PROGRESS.md).

## Setup once

```bash
pip install -U google-genai python-dotenv numpy pandas pillow pydantic
echo 'GEMINI_API_KEY=your_key_here' > .env      # already done in this repo; .env is gitignored
```

```python
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client()
r = client.interactions.create(model="gemini-flash-latest", input="Hello")
print(r.output_text)
```

## Lessons

| #   | Lesson                                                                   | Type      | Core takeaway                                      |
| --- | ------------------------------------------------------------------------ | --------- | -------------------------------------------------- |
| 00  | [Course Setup](00-course-setup.md)                                       | Setup     | `google-genai`, `.env`, model IDs, thinking tokens |
| 01  | [Intro to GenAI &amp; LLMs](01-introduction-to-genai.md)                 | Learn     | Tokenize → predict → sample                        |
| 02  | [Comparing Models](02-comparing-llms.md)                                 | Learn     | Model taxonomy + the improvement ladder            |
| 03  | [Responsible AI](03-responsible-ai.md)                                   | Learn     | 4 mitigation layers;`safety_settings`              |
| 04  | [Prompt Engineering Fundamentals](04-prompt-engineering-fundamentals.md) | Learn     | Zero/one/few-shot, cues, templates                 |
| 05  | [Advanced Prompts](05-advanced-prompts.md)                               | Learn     | CoT, self-refine, maieutic, temperature            |
| 06  | [Text Generation Apps](06-text-generation-apps.md)                       | **Build** | First app;`previous_interaction_id`                |
| 07  | [Chat Applications](07-building-chat-applications.md)                    | **Build** | State, system message framework, metrics           |
| 08  | [Search Applications](08-building-search-applications.md)                | **Build** | Embeddings + cosine similarity                     |
| 09  | [Image Applications](09-building-image-applications.md)                  | **Build** | `gemini-3.1-flash-image`, base64, metaprompts      |
| 10  | [Low-Code AI Apps](10-low-code-ai-applications.md)                       | Learn     | Prebuilt vs custom; structured extraction          |
| 11  | [Function Calling](11-function-calling.md)                               | **Build** | Structured output + tools, the 3-step flow         |
| 12  | [Designing UX](12-designing-ux.md)                                       | Learn     | Calibrated trust: explainability + control         |
| 13  | [Securing AI Apps](13-securing-ai-applications.md)                       | Learn     | Data poisoning,**prompt injection**, red teaming   |
| 14  | [GenAI App Lifecycle](14-genai-application-lifecycle.md)                 | Learn     | LLMOps; build an evaluation set                    |
| 15  | [RAG &amp; Vector Databases](15-rag-and-vector-databases.md)             | **Build** | ⭐ Chunk → embed → retrieve → ground               |
| 16  | [Open Source Models](16-open-source-models.md)                           | Learn     | Gemma, Llama, Mistral, Falcon; Ollama              |
| 17  | [AI Agents](17-ai-agents.md)                                             | **Build** | LLM + state + tools + bounded loop                 |
| 18  | [Fine-Tuning](18-fine-tuning.md)                                         | Learn     | ⚠️ Not on the Gemini API — what to do instead      |
| 19  | [Small Language Models](19-small-language-models.md)                     | Learn     | Phi/Gemma, MoE, local inference                    |
| 20  | [Mistral Models](20-mistral-models.md)                                   | Learn     | Large vs Small, tokenizer efficiency               |
| 21  | [Meta Llama Models](21-meta-llama-models.md)                             | Learn     | Context window, native tools, multimodality        |

## How to work through a lesson

1. Read the notes and the **Crux Notes**.
2. Answer the **quiz** before revealing the answers.
3. Build the **practical task** into `practice/`.
4. Run the **verify** commands — every criteria row must pass.
5. Tick it off in [PROGRESS.md](PROGRESS.md).

## Suggested path

**Concepts** 01 → 02 → 03 → 04 → 05
**Core build** 06 → 07 → 11 → 08 → 15 → 17
**Production** 12 → 13 → 14
**Breadth** 09 → 10 → 16 → 18 → 19 → 20 → 21

Lesson **15 (RAG)** and **11 (function calling)** carry the most practical weight — everything else builds toward or on them.

## Gemini-specific notes that differ from the original course

- `client.interactions.create(...).output_text` is the current API; `client.models.generate_content(...).text` still works.
- Conversation state via **`previous_interaction_id`**, not by resending history.
- **Fine-tuning is unavailable** on the Gemini API (lesson 18) — use system instructions, few-shot, structured output and RAG.
- Image models return **base64**, not URLs, and take no `temperature`.
- Watch **`thoughtsTokenCount`** — reasoning tokens dominate small requests and consume free-tier quota.
