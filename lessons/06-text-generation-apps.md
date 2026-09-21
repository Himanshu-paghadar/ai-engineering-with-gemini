# Lesson 06 — Building Text Generation Apps

> Source: `06-text-generation-apps` · Retargeted from `openai` to `google-genai`.

## 🎯 Goal
Build your first real app: a recipe generator with user input, filters and a follow-up prompt.

---

## 1. Why a text-generation app?
A console/GUI app is **limited** (only supported commands) and **language-specific**. A prompt-driven
app takes natural language and draws on a model trained on a vast corpus — not just your database.

Things you can build: **chatbot**, **helper** (summarize, extract, draft), **code assistant**.

## 2. Two ways to integrate
- **Raw API** — build HTTP requests yourself (the `curl` in lesson 00).
- **Library/SDK** — `google-genai` wraps it. Higher-level orchestration frameworks: **LangChain**, **LlamaIndex**, **Google ADK**.

## 3. Minimum viable app

```python
# app.py
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client()                 # reads GEMINI_API_KEY
MODEL = "gemini-flash-latest"

prompt = "Complete the following: Once upon a time there was a"

response = client.interactions.create(model=MODEL, input=prompt)
print(response.output_text)
```

```bash
python app.py
```

## 4. Build up: the recipe generator

### Step 1 — hardcoded prompt
```python
prompt = ("Show me 5 recipes for a dish with the following ingredients: "
          "chicken, potatoes, and carrots. Per recipe, list all the ingredients used")
```

### Step 2 — make it flexible with user input
```python
no_recipes  = input("No of recipes (for example, 5): ")
ingredients = input("List of ingredients (for example, chicken, potatoes, and carrots): ")

prompt = (f"Show me {no_recipes} recipes for a dish with the following ingredients: "
          f"{ingredients}. Per recipe, list all the ingredients used")
```

### Step 3 — add a filter
```python
filter_ = input("Filter (for example, vegetarian, vegan, or gluten-free): ")

prompt = (f"Show me {no_recipes} recipes for a dish with the following ingredients: "
          f"{ingredients}. Per recipe, list all the ingredients used, no {filter_}")
```
> ⚠️ Be explicit. "no milk" filtered milk but left cheese in — the model does exactly what you said, not what you meant.

### Step 4 — a second, context-aware prompt (shopping list)
```python
recipes = response.output_text

followup = client.interactions.create(
    model=MODEL,
    input="Produce a shopping list for the generated recipes, and don't include ingredients I already have.",
    previous_interaction_id=response.id,     # model can see the recipes it just produced
)
print("Shopping list:")
print(followup.output_text)
```

Two ways to give the second call context — know both:

| Approach | Code | When |
|---|---|---|
| **Chain by ID** | `previous_interaction_id=response.id` | Gemini-native, no re-sending tokens ✅ |
| **Concatenate** | `input=f"{recipes}\n\n{new_prompt}"` | Portable across providers, explicit control |

## 5. Full working app

```python
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client()
MODEL = "gemini-flash-latest"

no_recipes  = input("No of recipes (for example, 5): ")
ingredients = input("List of ingredients (for example, chicken, potatoes, and carrots): ")
filter_     = input("Filter (for example, vegetarian, vegan, or gluten-free): ")

prompt = (f"Show me {no_recipes} recipes for a dish with the following ingredients: "
          f"{ingredients}. Per recipe, list all the ingredients used, no {filter_}")

recipes = client.interactions.create(
    model=MODEL,
    system_instruction="You are a concise, practical cooking assistant.",
    input=prompt,
    generation_config={"max_output_tokens": 1200},
)
print(recipes.output_text)

shopping = client.interactions.create(
    model=MODEL,
    input="Produce a shopping list for the recipes above. Exclude ingredients I already listed as having.",
    previous_interaction_id=recipes.id,
    generation_config={"max_output_tokens": 600},
)
print("\nShopping list:")
print(shopping.output_text)
```

## 6. Tuning the call

```python
generation_config={
    "temperature": 0.5,          # 0 = predictable, higher = varied
    "max_output_tokens": 800,    # cost/length ceiling
}
```

> 💡 **Thinking tokens.** Gemini reasons internally before replying; those tokens count toward your
> quota (lesson 00 measured 329 thought tokens on a trivial prompt). For high-volume simple tasks
> use `gemini-flash-lite-latest`.

## 7. Assignment ideas
- **Study buddy** — "You're an expert on Python. Suggest a beginner lesson in the format: concepts / brief explanation / exercise with solution."
- **History bot** — "You are Abe Lincoln, respond using grammar and words Abe would have used. Tell me about your greatest accomplishments in 300 words."

---

## 🧠 Crux Notes
- The app loop is always: **collect input → interpolate into a prompt template → call → print**.
- `previous_interaction_id` chains turns without resending history — the cheap way to do follow-ups.
- `max_output_tokens` is your cost ceiling; `temperature` is your variance dial.
- Secrets in `.env` + `load_dotenv()`; never inline the key.
- Prompt precision beats code complexity: "no milk" ≠ "no dairy".
- Knowledge check: **temperature controls how random the output is** (not its length or token count).

---

## ✅ Test Your Knowledge

**1.** What does temperature do?
a) Controls how random the output is. b) Controls how big the response is. c) Controls how many tokens are used.
<details><summary>Answer</summary>

**a.** Randomness only. Length is `max_output_tokens`; token usage is a consequence of both input and output.
</details>

**2.** Two ways to give a follow-up call the context of the previous answer — name both and a trade-off.
<details><summary>Answer</summary>

`previous_interaction_id=r.id` (Gemini-native, no resend, cheaper) versus concatenating the previous text into the new prompt (portable across providers, explicit control over what is included).
</details>

**3.** A user filtered "no milk" but got recipes with cheese. Bug or prompt?
<details><summary>Answer</summary>

Prompt. The model did exactly what was asked. "No dairy" is the instruction that matches the intent — precision in the prompt, not more code.
</details>

**4.** Where should `max_output_tokens` be set, and why care on a free tier?
<details><summary>Answer</summary>

In `generation_config`. It caps cost and latency, and stops one runaway response from consuming your quota.
</details>

**5.** Why does a trivially short answer sometimes consume hundreds of tokens?
<details><summary>Answer</summary>

Thinking tokens. The model reasons internally before replying and those count. Use `gemini-flash-lite-latest` for simple high-volume work.
</details>

---

## 🛠️ Practical Task

**Build:** `practice/06_recipe_app.py` — the full recipe generator, production-shaped.

### Requirements
1. Prompt the user for **number of recipes**, **ingredients**, **dietary filter**.
2. Generate the recipes with a system instruction.
3. Make a **second** call producing a shopping list that excludes ingredients the user already has, using `previous_interaction_id`.
4. Set `max_output_tokens` on both calls.
5. Handle: empty response, `429` rate limit, and a user pressing Enter on a required field.

### Passing criteria

| # | Criterion | How to verify |
|---|---|---|
| 1 | Runs end to end with `3 / chicken, potatoes, carrots / none` | Two sections printed: recipes, then shopping list |
| 2 | Shopping list references the generated recipes | It excludes chicken/potatoes/carrots |
| 3 | Second call uses `previous_interaction_id` | `grep previous_interaction_id practice/06_recipe_app.py` |
| 4 | Empty input does not crash | Press Enter at each prompt — get a message, not a traceback |
| 5 | Rate limit handled | Wrap calls in try/except; print a friendly message |
| 6 | No hardcoded key | `grep -c 'AQ\.' practice/06_recipe_app.py` returns 0 |

### Test cases

| Input | Expected |
|---|---|
| `2` / `apple, flour` / `sugar` | 2 recipes, none headlining sugar; shopping list excludes apple and flour |
| `3` / `onion, milk` / `no dairy` | No milk **or cheese** — if cheese appears, tighten the prompt and re-run |
| `` (empty ingredients) | Re-prompt or a clear error; no traceback |
| `50` / `rice` / `none` | Truncates cleanly at `max_output_tokens` — no crash |

### Verify
```bash
printf '2\napple, flour\nsugar\n' | python practice/06_recipe_app.py
echo "exit=$?"    # expect 0
```

**Stretch:** add `--json` to return the recipes as a validated Pydantic model instead of prose (borrow the schema pattern from lesson 11).
