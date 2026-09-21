# AI Engineering with Gemini

**A 22-lesson, build-first curriculum for generative AI — ported from Azure OpenAI to the Google Gemini API, and verified against a live endpoint rather than copied from docs.**

Every lesson ends with a quiz you can grade yourself on and a practical task with explicit pass/fail criteria. The whole curriculum runs on the Gemini **free tier** — [grab a free API key here](https://aistudio.google.com/app/api-keys), no credit card needed.

```python
from google import genai

client = genai.Client()
print(client.interactions.create(
    model="gemini-flash-latest",
    input="Explain how AI works in a few words",
).output_text)
```

---

## Why this repo exists

Microsoft's [Generative AI for Beginners](https://github.com/microsoft/generative-ai-for-beginners) is an excellent curriculum. Two things stopped me using it directly:

1. **It assumes an Azure subscription.** Every code sample targets Azure OpenAI or the Foundry model catalog. That's a paywall and a signup flow between you and the first line of running code.
2. **It's written to be read, not drilled.** Long prose, few checkpoints. I wanted something I could revise from in ten minutes and then prove I'd actually understood.

So I rebuilt it: **retargeted to Gemini**, compressed to the concepts and code that carry the weight, and rebuilt around self-assessment.

> **The goal was never to collect notes.** It was to end up with a set of claims I'd personally verified and a set of exercises whose passing criteria I couldn't fudge.

## What makes this different from a summary

I ran the API instead of trusting the documentation. That surfaced four things that would otherwise have shipped as confidently-wrong notes:

| Finding                                             | Why it matters                                                                                                                                                                       |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **The SDK moved to `client.interactions.create()`** | `client.models.generate_content()` still works, so tutorials are split across both. The notes cover each and say which you're reading.                                               |
| **Fine-tuning no longer exists on the Gemini API**  | No tunable model since Gemini 1.5 Flash-001's deprecation. An entire lesson's premise was invalid — so Lesson 18 says so up front and pivots to structured output, few-shot and RAG. |
| **Reasoning tokens dominate small requests**        | An 8-token prompt returning a 14-token answer burned**351 tokens — 329 of them invisible internal reasoning**. A 25× cost multiplier that no tutorial mentions.                      |
| **Google Search grounding 429s on the free tier**   | Documented as rate-limited instead of presented as freely available.                                                                                                                 |

Model IDs, embedding dimensionality (3072), structured output, function calling and the full RAG pipeline were each confirmed end to end before being written up.

## How each lesson is built

```
concepts  →  runnable Python  →  🧠 Crux Notes  →  ✅ Quiz  →  🛠️ Practical Task
   what        copy-paste ready     revise in 60s    116 Qs      graded, not vibes
```

Practical tasks specify a deliverable file, a **passing-criteria table**, and **test cases with expected behaviour**. The criteria deliberately target the awkward paths, because that's where the real failures live:

- Lesson 08 — query `"purple elephant tax law"`: **all scores must be low**, proving retrieval always returns its best _k_ however irrelevant
- Lesson 11 — `"Who was Napoleon?"` must make **zero** tool calls; knowing when _not_ to act is half the job
- Lesson 13 — **at least one prompt injection must succeed** against the naive build before you're allowed to harden it
- Lesson 15 — `"Capital of Mongolia?"` must refuse **without calling the model at all**
- Lesson 17 — asked about something absent, the agent must report low confidence, not invent findings

## Curriculum

| #   | Lesson                                                               | Type      | Core takeaway                                  |
| --- | -------------------------------------------------------------------- | --------- | ---------------------------------------------- |
| 00  | [Course Setup](lessons/00-course-setup.md)                           | Setup     | SDK,`.env`, model IDs, the thinking-token trap |
| 01  | [Intro to GenAI &amp; LLMs](lessons/01-introduction-to-genai.md)     | Learn     | Tokenize → predict → sample                    |
| 02  | [Comparing Models](lessons/02-comparing-llms.md)                     | Learn     | Model taxonomy + the improvement ladder        |
| 03  | [Responsible AI](lessons/03-responsible-ai.md)                       | Learn     | Four mitigation layers; safety settings        |
| 04  | [Prompt Fundamentals](lessons/04-prompt-engineering-fundamentals.md) | Learn     | Zero/one/few-shot, cues, templates             |
| 05  | [Advanced Prompts](lessons/05-advanced-prompts.md)                   | Learn     | CoT, self-refine, maieutic, temperature        |
| 06  | [Text Generation Apps](lessons/06-text-generation-apps.md)           | **Build** | First app; chaining turns                      |
| 07  | [Chat Applications](lessons/07-building-chat-applications.md)        | **Build** | State, system-message framework, metrics       |
| 08  | [Search Applications](lessons/08-building-search-applications.md)    | **Build** | Embeddings + cosine similarity                 |
| 09  | [Image Applications](lessons/09-building-image-applications.md)      | **Build** | Image models, base64, metaprompts              |
| 10  | [Low-Code AI](lessons/10-low-code-ai-applications.md)                | Learn     | Prebuilt vs custom; structured extraction      |
| 11  | [Function Calling](lessons/11-function-calling.md) ⭐                | **Build** | Structured output + tools, the 3-step flow     |
| 12  | [Designing UX](lessons/12-designing-ux.md)                           | Learn     | Calibrated trust: explainability + control     |
| 13  | [Securing AI Apps](lessons/13-securing-ai-applications.md)           | Learn     | Poisoning,**prompt injection**, red teaming    |
| 14  | [App Lifecycle](lessons/14-genai-application-lifecycle.md) ⭐        | **Build** | LLMOps; build an evaluation set                |
| 15  | [RAG &amp; Vector DBs](lessons/15-rag-and-vector-databases.md) ⭐    | **Build** | Chunk → embed → retrieve → ground              |
| 16  | [Open Source Models](lessons/16-open-source-models.md)               | Learn     | Gemma, Llama, Mistral; running local           |
| 17  | [AI Agents](lessons/17-ai-agents.md) ⭐                              | **Build** | LLM + state + tools + a bounded loop           |
| 18  | [Fine-Tuning](lessons/18-fine-tuning.md)                             | Learn     | Unavailable here — and what to do instead      |
| 19  | [Small Language Models](lessons/19-small-language-models.md)         | Learn     | Find the*smallest* model that passes           |
| 20  | [Mistral Models](lessons/20-mistral-models.md)                       | Learn     | Context windows, tokenizer economics           |
| 21  | [Meta Llama Models](lessons/21-meta-llama-models.md)                 | Learn     | Native tools, multimodality                    |

⭐ = the four that carry the most practical weight. If you only do four, do those.

## Quickstart

### 1. Get a free Gemini API key

👉 **[aistudio.google.com/app/api-keys](https://aistudio.google.com/app/api-keys)**

Sign in with any Google account and click **Create API key**. **No credit card required** — the free
tier covers this entire curriculum. Copy the key; you'll paste it in step 3.

> Check your live quota any time at [aistudio.google.com/rate-limit](https://aistudio.google.com/rate-limit).
> Free-tier limits vary by model and change over time, so read the dashboard rather than trusting a blog post.

### 2. Clone and install

```bash
git clone https://github.com/himanshu-paghadar/ai-engineering-with-gemini
cd ai-engineering-with-gemini

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Add your key

```bash
cp .env.example .env
```

Open `.env` and paste the key from step 1:

```env
GEMINI_API_KEY=your_key_here
```

`.env` is gitignored — your key never reaches the repo. Never paste a key into a `.md` file, a
notebook cell, a screenshot or a chat; if one leaks, delete and recreate it in AI Studio immediately.

### 4. Verify

```bash
python lessons/practice/00_setup_check.py
```

**Suggested Lesson path :**

- **Concepts** 01 → 02 → 03 → 04 → 05
- **Core build** 06 → 07 → 11 → 08 → 15 → 17
- **Production** 12 → 13 → 14
- **Breadth** 09 → 10 → 16 → 18 → 19 → 20 → 21

Tasks 08 → 15 → 14 → 17 build on each other — do those in order. The rest stand alone.

## Repo layout

```
lessons/
├── README.md              index and learning path
├── PROGRESS.md            checkbox tracker + task dependency graph
├── 00-…21-*.md            the 22 lessons
└── practice/              your task deliverables land here
.env.example               copy to .env and add your key
requirements.txt           pinned dependencies
```

## Status

Honest state of play, so nobody has to guess:

- ✅ **All 22 lessons written**, with the API surface verified against a live endpoint
- ✅ **116 quiz questions** with answers
- ✅ **22 practical tasks specified** — deliverables, 141 pass/fail criteria rows, test cases
- 🔄 **Task solutions in progress** — `practice/` is the working area; see [PROGRESS.md](lessons/PROGRESS.md) for what's done

The tasks are specifications I wrote, not solutions I've shipped. Where a threshold needs tuning — Lesson 15's retrieval cut-off, for instance — the task tells you to derive it from measured similarity scores rather than hardcoding a number I guessed.

## Notes on the Gemini port

Things that differ from the upstream Azure-based course:

- Conversation state via `previous_interaction_id`, not by resending history
- Image models return **base64**, not URLs, and accept no `temperature`
- Fine-tuning is unavailable — system instructions, few-shot, structured output and RAG carry the load
- Prefer the `-latest` model aliases so code doesn't rot between model generations
- Watch `thoughtsTokenCount`; it's the free tier's most common surprise

## Contributing

Corrections and improvements are welcome — especially anything that has drifted as
the Gemini API evolves. See [CONTRIBUTING.md](CONTRIBUTING.md) for the setup, the
lesson structure to follow, and the one rule that matters: **verify against a live
endpoint before you write it down**.

- 🐛 [Report a broken lesson or stale API call](https://github.com/himanshu-paghadar/ai-engineering-with-gemini/issues/new)
- 🔒 [Security policy](SECURITY.md) — including how to handle your own API key safely
- 🤝 [Code of conduct](CODE_OF_CONDUCT.md) — beginners explicitly welcome; no question is too basic

## Credits

Curriculum structure and teaching scenarios adapted from [microsoft/generative-ai-for-beginners](https://github.com/microsoft/generative-ai-for-beginners) (MIT). Code, verification, exercises and grading criteria are my own port to the Gemini API.
