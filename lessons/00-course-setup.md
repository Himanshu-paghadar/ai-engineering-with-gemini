# Lesson 00 — Course Setup (Python + Gemini Free API)

> Adapted from `microsoft/generative-ai-for-beginners/00-course-setup` — retargeted from Azure OpenAI to the **Google Gemini API free tier**.

## 🎯 Goal

A working Python env + a free Gemini API key, so every later lesson runs at zero cost.

---

## 1. Get the free API key

1. Go to **[aistudio.google.com](https://aistudio.google.com/apikey)** and sign in with a Google account.
2. **Create API key** → copy it. No credit card needed for the free tier.
3. Check your live limits any time at [aistudio.google.com/rate-limit](https://aistudio.google.com/rate-limit) — free-tier RPM/TPM/RPD vary by model and change often, so read the dashboard rather than trusting a blog post.

> Free tier = real limits. Build in retries and expect `429` on tight loops. Prefer `flash-lite` models for high-volume experiments.

## 2. Install

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -U google-genai python-dotenv
# extras used later in the course:
pip install numpy pandas pillow pydantic
```

## 3. Secrets

```bash
# .env   — add to .gitignore, never commit
GEMINI_API_KEY=AIza...
```

```python
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()                 # loads .env into os.environ
client = genai.Client()       # auto-reads GEMINI_API_KEY

# explicit form, if you prefer:
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
```

`genai.Client()` picks up `GEMINI_API_KEY` from the environment automatically — that is the idiomatic form.

## 4. Hello world

**Smoke-test with curl first** — proves the key before any Python is involved:

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent" \
  -H 'Content-Type: application/json' \
  -H "X-goog-api-key: $GEMINI_API_KEY" \
  -X POST \
  -d '{"contents":[{"parts":[{"text":"Explain how AI works in a few words"}]}]}'
```

Then in Python:

```python
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client()

interaction = client.interactions.create(
    model="gemini-flash-latest",
    input="Explain how AI works in a few words",
)
print(interaction.output_text)
```

### Read the `usageMetadata` — thinking is not free

The curl response above reported, for an 8-token prompt and a 14-token answer:

```json
"totalTokenCount": 351, "thoughtsTokenCount": 329
```

**329 of 351 tokens were internal reasoning.** Current Gemini models think before answering, and
you are billed/rate-limited on those thought tokens. For simple tasks, reach for a `flash-lite`
model or cap output — otherwise a trivial prompt quietly costs 25x what it looks like.

## 5. Two APIs, both supported — know which you're reading

| API                                     | Call                                                                | Notes                                                                             |
| --------------------------------------- | ------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| **Interactions** (current docs)         | `client.interactions.create(model=..., input=...)` → `.output_text` | Stateful: chain turns with`previous_interaction_id`. Used throughout these notes. |
| **Models / generate_content** (classic) | `client.models.generate_content(model=..., contents=...)` → `.text` | Still fully supported; most existing tutorials use it. Stateless.                 |

Older tutorials may use the **legacy `google-generativeai` package** (`import google.generativeai as genai`). That one is superseded — install `google-genai` and use `from google import genai`.

## 6. Model quick-pick — ✅ verified against this project's key

**Prefer the `-latest` aliases.** They track the current generation so your code doesn't rot.

| Need               | Model                                  | Resolves to (today)   |
| ------------------ | -------------------------------------- | --------------------- |
| Default workhorse  | `gemini-flash-latest`                  | `gemini-3.8-flash`    |
| Cheapest / fastest | `gemini-flash-lite-latest`             | flash-lite generation |
| Deep reasoning     | `gemini-pro-latest`                    | pro generation        |
| Images             | `gemini-3.1-flash-image`               | —                     |
| Embeddings         | `gemini-embedding-001`                 | 3072-dim vectors      |
| Open weights       | `gemma-4-31b-it`, `gemma-4-26b-a4b-it` | —                     |

Also available to this key: `gemini-3.5-transcribe` (speech-to-text), `gemini-3.8-live` (voice),
`veo-3.1-*` (video), `lyria-3.5` (music), `deep-research-*`, `gemini-2.5-computer-use-preview`.

```python
for m in client.models.list():
    print(m.name)      # ground truth for what YOUR key can call
```

## 7. Troubleshooting

| Symptom                       | Fix                                                                        |
| ----------------------------- | -------------------------------------------------------------------------- |
| `API key not valid`           | Key not in env;`load_dotenv()` not called; or key from a deleted project   |
| `429 RESOURCE_EXHAUSTED`      | Free-tier rate limit — back off, or switch to a`flash-lite` model          |
| `404` on model name           | Model ID wrong or not available to your key — run`client.models.list()`    |
| Import error on`google.genai` | You installed`google-generativeai` (legacy). `pip install -U google-genai` |
| Notebook kernel missing       | Kernel ▸ Select Kernel ▸ Python 3 (your venv)                              |

## 8. 🔐 Key hygiene

This project's key lives in `.env` at the repo root and `.env` is in `.gitignore`. Two rules:

- **Never** paste a key into a `.md`, a notebook cell, or a screenshot. Anything pasted into a
  chat, an issue, or a support thread should be considered public.
- **Rotate** a key the moment it is exposed: AI Studio → API keys → Delete key → create a new one.
  Rotation is free and takes 10 seconds; a leaked key on your Google Cloud project is not.

---

## 🧠 Crux Notes

- **One SDK for the whole course**: `pip install -U google-genai`; `from google import genai`. (Verified here: v2.24.0.)
- `genai.Client()` reads `GEMINI_API_KEY` from the environment — keep the key in `.env`, never in code.
- `interactions.create(...).output_text` is the new canonical call; `models.generate_content(...).text` still works.
- Free tier is generous but rate-limited: design for `429`, prefer `flash-lite` when looping.
- On Gemini you pass a **real model ID** (`gemini-flash-latest`), unlike Azure where you pass a deployment name.
- Watch `thoughtsTokenCount` — reasoning tokens dominate small requests and burn free-tier quota.

---

## ✅ Test Your Knowledge

**1.** Which package do you install, and which import line is correct?
<details><summary>Answer</summary>

`pip install -U google-genai`, then `from google import genai`.
The older `google-generativeai` package (`import google.generativeai as genai`) is the superseded one.
</details>

**2.** You call `genai.Client()` with no arguments and it works. Where did the key come from?
<details><summary>Answer</summary>

From the `GEMINI_API_KEY` environment variable, which `load_dotenv()` read out of `.env`. The client reads it automatically.
</details>

**3.** A trivial 8-token prompt reported `totalTokenCount: 351`. Explain the gap.
<details><summary>Answer</summary>

`thoughtsTokenCount: 329` — internal reasoning tokens. Gemini thinks before answering and you are billed and rate-limited on those. Use a `flash-lite` model for simple high-volume work.
</details>

**4.** What does `gemini-flash-latest` give you that `gemini-3.8-flash` does not?
<details><summary>Answer</summary>

It is an alias that tracks the current generation, so your code does not rot when a new model ships. Pin an exact version only when you need reproducibility.
</details>

**5.** You get `429 RESOURCE_EXHAUSTED`. Is your key invalid?
<details><summary>Answer</summary>

No — the key is fine. You hit a free-tier rate limit. Back off and retry, or switch to a lighter model. An invalid key returns `API key not valid`, not 429.
</details>

---

## 🛠️ Practical Task

**Build:** `practice/00_setup_check.py` — an environment self-test you can re-run any time something breaks.

### Requirements
1. Load the key from `.env` (never hardcode it).
2. Exit with a clear message if `GEMINI_API_KEY` is missing — do not crash with a traceback.
3. Make one call to `gemini-flash-latest` and print the text.
4. Print the total token count **and** the thinking-token count for that call.
5. Print how many models your key can access.

### Passing criteria

| # | Criterion | How to verify |
|---|---|---|
| 1 | Runs clean from the repo root | `python practice/00_setup_check.py` exits 0 |
| 2 | No key in the source | `grep -c 'AQ\.' practice/00_setup_check.py` returns `0` |
| 3 | Handles a missing key gracefully | `env -u GEMINI_API_KEY python practice/00_setup_check.py` prints a readable error, no traceback |
| 4 | Reports token usage | Output contains a thinking-token number |
| 5 | Lists models | Prints a count of 40+ models |

### Verify
```bash
python practice/00_setup_check.py && echo "PASS" || echo "FAIL"
grep -c 'AQ\.' practice/00_setup_check.py   # must print 0
```

<details><summary>Stuck? Reference solution</summary>

```python
import os, sys
from dotenv import load_dotenv
from google import genai

load_dotenv()
if not os.getenv("GEMINI_API_KEY"):
    sys.exit("ERROR: GEMINI_API_KEY not set. Add it to .env — see lesson 00.")

client = genai.Client()
r = client.interactions.create(model="gemini-flash-latest", input="Say hello in 5 words")
print("Response:", r.output_text)
print("Usage:", r.usage)
print("Models available:", len(list(client.models.list())))
```
</details>
