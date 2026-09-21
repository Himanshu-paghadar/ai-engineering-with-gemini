# AI Engineering with Gemini

I took Microsoft's [Generative AI for Beginners](https://github.com/microsoft/generative-ai-for-beginners) course, rewrote it for Google's Gemini API, and cut it down to the parts that actually matter. 22 lessons. Every one ends with a quiz and something to build.

It runs on the **free tier**. You don't need a credit card or a cloud account.

```python
from google import genai

client = genai.Client()
print(client.interactions.create(
    model="gemini-flash-latest",
    input="Explain how AI works in a few words",
).output_text)
```

## Why I made this

Microsoft's course is genuinely good, but I hit two walls with it.

The first was Azure. Every code sample needs an Azure subscription and an OpenAI deployment. I wanted to start learning on a Tuesday evening, not fill in a cloud signup form and worry about billing.

The second was that it's written to be read. Long prose, not many checkpoints. I'd finish a lesson feeling like I understood it and have no way to find out whether I actually did.

So I rebuilt it. Gemini instead of Azure, notes I can revise from in ten minutes, and an exercise at the end of each lesson with pass/fail criteria I can't talk myself out of.

## What I changed

I ran the API instead of trusting the docs. That turned up four things worth knowing before you start:

**The SDK moved.** Current docs use `client.interactions.create()`. The older `client.models.generate_content()` still works, so tutorials out there are split between them. My notes cover both and tell you which you're looking at.

**You can't fine-tune on the Gemini API.** There hasn't been a tunable model since Gemini 1.5 Flash-001 was deprecated. That's an entire lesson whose premise no longer holds, so Lesson 18 says so at the top and covers what to do instead.

**Thinking tokens are expensive.** I sent an 8-token prompt and got a 14-token answer back. It cost 351 tokens. 329 of those were internal reasoning I never saw. Nothing warned me about this, so the notes do.

**Google Search grounding hits rate limits on the free tier.** It 429'd while I was testing, so it's documented as rate-limited rather than presented as free.

## Goals

What I wanted out of this, and what you'd get from working through it:

- Build the five things that show up in every real AI project: a chat app, semantic search, RAG, function calling, and an agent
- Know when to reach for RAG instead of fine-tuning, and a small model instead of a big one
- Write prompts that hold up across a hundred calls instead of one lucky demo
- Take LLM security seriously, especially prompt injection
- Be able to tell whether a change made things better, using an eval set rather than a hunch

## Learning curve

| Stage | Lessons | Time | You'll be doing |
|---|---|---|---|
| **Foundations** | 01–05 | ~4 hrs | Reading and prompting. No architecture yet. |
| **First builds** | 06, 07 | ~4 hrs | A working CLI app and a chat bot that remembers context. |
| **The step up** | 11, 08 | ~6 hrs | Function calling and embeddings. This is where it stops feeling like chatting and starts feeling like engineering. |
| **The real thing** | 15, 17 | ~8 hrs | RAG and agents. Hardest part of the course, and the reason to do the rest. |
| **Production** | 12, 13, 14 | ~5 hrs | UX, security, evaluation. Less fun, matters more than you'd think. |
| **Breadth** | 09, 10, 16, 18–21 | ~6 hrs | Images, open models, small models, other model families. |

Roughly 30 hours if you do the exercises properly. Less if you only read, but then you're back to the problem I started with.

**Difficulty jumps in two places.** Lesson 11 (function calling), because you stop treating the model as a text box and start wiring it into your code. And Lesson 15 (RAG), because it's the first time several pieces have to work together.

## Lessons

Learn = concepts. Build = you write code.

| # | Lesson | | |
|---|---|---|---|
| 00 | [Setup](lessons/00-course-setup.md) | Setup | SDK, keys, model IDs |
| 01 | [Intro to GenAI & LLMs](lessons/01-introduction-to-genai.md) | Learn | How a model actually generates text |
| 02 | [Comparing Models](lessons/02-comparing-llms.md) | Learn | Picking one, and four ways to improve results |
| 03 | [Responsible AI](lessons/03-responsible-ai.md) | Learn | Harms and the four places to mitigate them |
| 04 | [Prompt Fundamentals](lessons/04-prompt-engineering-fundamentals.md) | Learn | Zero-shot to few-shot, cues, templates |
| 05 | [Advanced Prompts](lessons/05-advanced-prompts.md) | Learn | Chain-of-thought, self-refine, temperature |
| 06 | [Text Generation Apps](lessons/06-text-generation-apps.md) | Build | Your first app |
| 07 | [Chat Applications](lessons/07-building-chat-applications.md) | Build | Multi-turn state |
| 08 | [Search Applications](lessons/08-building-search-applications.md) | Build | Embeddings and cosine similarity |
| 09 | [Image Applications](lessons/09-building-image-applications.md) | Build | Generating and editing images |
| 10 | [Low-Code AI](lessons/10-low-code-ai-applications.md) | Learn | When not to write code |
| 11 | [Function Calling](lessons/11-function-calling.md) | Build | Letting the model call your code ⭐ |
| 12 | [Designing UX](lessons/12-designing-ux.md) | Learn | Trust, and why too much is as bad as too little |
| 13 | [Securing AI Apps](lessons/13-securing-ai-applications.md) | Learn | Prompt injection, poisoning, red teaming |
| 14 | [App Lifecycle](lessons/14-genai-application-lifecycle.md) | Build | Evaluation sets ⭐ |
| 15 | [RAG & Vector DBs](lessons/15-rag-and-vector-databases.md) | Build | Grounding a model in your own data ⭐ |
| 16 | [Open Source Models](lessons/16-open-source-models.md) | Learn | Gemma, Llama, Mistral, running local |
| 17 | [AI Agents](lessons/17-ai-agents.md) | Build | Tools, state, and a loop ⭐ |
| 18 | [Fine-Tuning](lessons/18-fine-tuning.md) | Learn | Why you probably don't need it |
| 19 | [Small Language Models](lessons/19-small-language-models.md) | Learn | Finding the smallest model that works |
| 20 | [Mistral Models](lessons/20-mistral-models.md) | Learn | Context windows, tokenizer cost |
| 21 | [Meta Llama Models](lessons/21-meta-llama-models.md) | Learn | Native tools, multimodality |

⭐ If you only do four, do these.

## Getting started

**1. Get a free API key**

Go to [aistudio.google.com/app/api-keys](https://aistudio.google.com/app/api-keys), sign in with any Google account, click **Create API key**. No credit card. Copy it.

You can check your quota at [aistudio.google.com/rate-limit](https://aistudio.google.com/rate-limit). Free limits change, so trust that page over anything written down.

**2. Clone and install**

```bash
git clone https://github.com/Himanshu-paghadar/ai-engineering-with-gemini
cd ai-engineering-with-gemini

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

**3. Add your key**

```bash
cp .env.example .env
```

Open `.env` and paste it in:

```env
GEMINI_API_KEY=your_key_here
```

`.env` is gitignored, so your key stays out of the repo. Don't put it in a notebook cell, a screenshot or a chat message. If it leaks, delete it in AI Studio and make a new one. Takes ten seconds.

**4. Check it works**

```bash
python lessons/practice/00_setup_check.py
```

## How the exercises work

Each lesson ends with a task. The task names a file to write, a table of pass/fail criteria, and test cases with expected behaviour. The criteria go after the awkward cases on purpose, because that's where you find out whether you understood it:

- **Lesson 08** — search for "purple elephant tax law". Every score has to come back low. Retrieval always hands you its best results, however useless they are, and you need to see that happen.
- **Lesson 11** — ask "Who was Napoleon?". It must call zero tools. A model that reaches for a tool every time is as broken as one that never does.
- **Lesson 13** — at least one prompt injection has to succeed against the naive version before you're allowed to fix it.
- **Lesson 15** — ask for the capital of Mongolia. It has to refuse without calling the model at all.
- **Lesson 17** — ask the agent about something absent from its notes. It must say it doesn't know instead of inventing an answer.

Track what you've finished in [PROGRESS.md](lessons/PROGRESS.md).

## Where things stand

All 22 lessons are written and the API behaviour in them is verified. 116 quiz questions with answers. 22 exercises specified, with 141 criteria between them.

The exercise **solutions** are still in progress. `lessons/practice/` is where they go. So: the specs are real and tested against the API, but I haven't shipped a solution for every one yet. [PROGRESS.md](lessons/PROGRESS.md) tracks which.

## Credits

The curriculum structure, lesson order and the running "education startup" scenario come from [**microsoft/generative-ai-for-beginners**](https://github.com/microsoft/generative-ai-for-beginners), MIT licensed. It's a great course and worth reading in full if you have Azure access.

Everything else here is mine: the Gemini port, the condensed notes, the quizzes, the exercises and their grading criteria. See [NOTICE](NOTICE) for the attribution details.

## Contributing

Corrections welcome, especially where the Gemini API has moved on since I wrote something. One rule: **run it before you write it down**. That's the whole point of the repo, and it's how I found the four things listed above.

- [Report a broken lesson](https://github.com/Himanshu-paghadar/ai-engineering-with-gemini/issues/new)
- [Contributing guide](CONTRIBUTING.md)
- [Security policy](SECURITY.md), including how to keep your key safe
- [Code of conduct](CODE_OF_CONDUCT.md). Beginners welcome, no question is too basic.

## Notes on Gemini specifically

Things that differ from the Azure-based original:

- Conversation state uses `previous_interaction_id`, so you don't resend history
- Image models return base64, not URLs, and don't take a `temperature`
- Fine-tuning isn't available, so system instructions, few-shot and RAG do that work
- Use the `-latest` model aliases so your code doesn't break between generations
- Keep an eye on `thoughtsTokenCount`. It's the free tier's most common surprise.

## License

[MIT](LICENSE)
