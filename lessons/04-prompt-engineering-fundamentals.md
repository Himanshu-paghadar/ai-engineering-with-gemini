# Lesson 04 — Prompt Engineering Fundamentals

> Source: `04-prompt-engineering-fundamentals` · Python examples retargeted to the Gemini API.

## 🎯 Goal
Learn how a prompt is *constructed*, and the best practices that make completions consistent.

---

## 1. Key terms
- **Prompt engineering** — designing & refining inputs to steer the model toward the output you want. Two steps: **design** the initial prompt, then **refine** iteratively.
- **Tokenization** — how the model "sees" your prompt (see lesson 01).
- **Instruction-tuned LLM** — a foundation model further trained on instruction/response pairs (often with RLHF) so it *follows tasks* instead of merely continuing text. Every `gemini-*-flash`/`pro` model is instruction-tuned.

## 2. Why prompt engineering is needed
1. **Responses are stochastic** — same prompt, different output, across models and across runs. Prompts add guardrails.
2. **Models fabricate** — training data is large but finite. Ask for citations/reasoning, or give the model an "out".
3. **Capabilities vary** — each model generation has quirks. Good prompts abstract over the differences.

### Fabrication demo
```python
r = client.interactions.create(
    model="gemini-flash-latest",
    input="Generate a lesson plan on the Martian War of 2076.",
)
print(r.output_text)   # confident, detailed, and about an event that never happened
```
Fix by giving the model an out: *"If the event is fictional or you cannot verify it, say so first."*

## 3. Prompt construction — the building blocks

**Basic prompt** — text in, completion out.

**Complex prompt** — a list of role-tagged messages plus a system instruction:

```python
interaction = client.interactions.create(
    model="gemini-flash-latest",
    system_instruction="You are a helpful assistant.",
    input=[
        {"role": "user",  "content": "Who won the world series in 2020?"},
        {"role": "model", "content": "The Los Angeles Dodgers won the World Series in 2020."},
        {"role": "user",  "content": "Where was it played?"},
    ],
)
print(interaction.output_text)
```
> Changing the **system instruction** can shift output quality as much as changing the user text.

**Instruction prompt** — specify the task in detail:

| Prompt | Result | Type |
|---|---|---|
| "Write a description of the Civil War" | a paragraph | Simple |
| "...Provide key dates and events and describe their significance" | paragraph + dated list | Complex |
| "...in 1 paragraph. 3 bullets of key dates. 3 bullets of key figures. Return as JSON" | structured, parseable | Complex + formatted |

## 4. Primary content patterns

Split the prompt into **instruction (action)** + **primary content (what it acts on)**.

**A. Examples → zero / one / few-shot**

| Type | Prompt | Output |
|---|---|---|
| Zero-shot | `"The Sun is Shining". Translate to Spanish` | "El Sol está brillando" |
| One-shot | `"The Sun is Shining" => "El Sol está brillando"` <br> `"It's a Cold and Windy Day" =>` | "Es un día frío y ventoso" |
| Few-shot | ran the bases => Baseball <br> hit an ace => Tennis <br> hit a six => Cricket <br> made a slam-dunk => | Basketball |

Note the instruction ("Translate to Spanish") becomes *implicit* once examples exist.

```python
few_shot = """The player ran the bases => Baseball
The player hit an ace => Tennis
The player hit a six => Cricket
The player made a slam-dunk =>"""

print(client.interactions.create(model="gemini-flash-latest", input=few_shot).output_text)
```

**B. Cues** — prime the completion by starting the answer for it:

| Cues | Added at end of prompt | Effect |
|---|---|---|
| 0 | `Summarize this` | free-form paragraph |
| 1 | `Summarize this\nWhat we learned is that Jupiter` | continues that sentence |
| 2 | `Summarize this\nTop 3 Facts We Learned:` | numbered list of 3 |

**C. Templates** — reusable recipes with placeholders:

```python
TEMPLATE = """You are an expert {subject} tutor.
Explain "{topic}" to a {level} student.
Format:
- Concept
- Worked example
- One practice question"""

prompt = TEMPLATE.format(subject="Python", topic="list comprehensions", level="beginner")
```

**D. Supporting (secondary) content** — extra context that tunes *how* the answer comes out: formatting rules, taxonomies, priority tags, tone.

## 5. Best practices

| Do | Why |
|---|---|
| Evaluate the latest models | New generations improve quality — but re-test cost & behaviour |
| Separate instructions from content | Use delimiters so the model weights tokens correctly |
| Be specific & clear | State context, outcome, length, format, style |
| Be descriptive, use examples | "Show and tell" beats telling; start zero-shot, refine to few-shot |
| Use cues to jump-start | Leading words steer the shape of the answer |
| Double down | Repeat key instructions before *and* after primary content |
| Mind ordering | Recency bias is real — order of examples changes output |
| Give the model an "out" | A fallback response reduces fabrication |

## 6. Mindset
1. **Domain understanding matters** — your expertise makes the templates good.
2. **Model understanding matters** — know your model's strengths and limits.
3. **Iteration & validation matter** — record what worked; build a prompt library.

---

## 🧠 Crux Notes
- Prompts are the **programming interface** of a generative app — treat them as code: version them, template them, test them.
- The **system instruction** sets persona + rules; the **user content** sets the task. Keep them separate.
- The ladder is: zero-shot → add instructions → add examples (few-shot) → add cues → templatize.
- Always give the model a fallback ("say you're unsure") — it's the cheapest fabrication defence.
- There is no single right prompt; it's trial and error plus domain knowledge.
- Knowledge check: the best prompt is the **most specific** one — subject + attributes + setting.

---

## ✅ Test Your Knowledge

**1.** Which is the best prompt?
a) "Show me an image of red car"
b) "Show me an image of red car of make Volvo and model XC90 parked by a cliff with the sun setting"
c) "Show me an image of red car of make Volvo and model XC90"
<details><summary>Answer</summary>

**b** — most specific on both the *what* (make and model, not just "a car") and the overall setting. **c** is next best.
</details>

**2.** What is the difference between one-shot and few-shot prompting?
<details><summary>Answer</summary>

One example versus several. More examples let the model infer the pattern more accurately — and with examples present, the explicit instruction often becomes unnecessary.
</details>

**3.** What is a "cue"?
<details><summary>Answer</summary>

Text at the end of the prompt that starts the answer for the model, priming the output format — e.g. ending with `Top 3 Facts We Learned:` to force a numbered list.
</details>

**4.** Why does "give the model an out" reduce fabrication?
<details><summary>Answer</summary>

Without a permitted fallback, the model's objective is to produce a plausible continuation — so it invents one. Explicitly allowing "say you are unsure" makes non-answering a valid, high-probability path.
</details>

**5.** You need identical formatting across 10,000 calls. Better: a very detailed prompt, or a template?
<details><summary>Answer</summary>

A **template** — a reusable recipe with placeholders. It makes prompts versionable, testable and consistent at scale, which a hand-written prompt per call never is.
</details>

---

## 🛠️ Practical Task

**Build:** `practice/04_prompt_ladder.py` — measure how much prompt technique actually buys you.

### The task
Classify customer-support messages into exactly one of: `billing`, `technical`, `account`, `other`.

### Requirements
1. Hand-write **12 test messages** with the correct label (your ground truth).
2. Implement 4 escalating prompt strategies:
   - **v1 zero-shot**: "Classify this message."
   - **v2 instruction**: add the exact label list and "reply with one word only".
   - **v3 few-shot**: add 4 labelled examples.
   - **v4 few-shot + cue + out**: add a cue and permission to answer `other` when unsure.
3. Score each version against your 12 cases and print an accuracy table.

### Passing criteria

| # | Criterion | Expected |
|---|---|---|
| 1 | All 4 versions run over all 12 cases | 48 calls total |
| 2 | Output normalised before comparison | `.strip().lower()` — do not fail on `"Billing."` |
| 3 | Accuracy printed per version | e.g. `v1: 8/12` |
| 4 | v4 >= v1 | Later strategies should not be worse |
| 5 | Any stray formatting is reported | Count replies that were not one of the 4 labels |

### Verify
```bash
python practice/04_prompt_ladder.py
# PASS if: all 4 accuracies print, and v4 >= v1
```

**Expect a surprise:** v1 often scores well on easy cases. The gap shows up on ambiguous ones — which is exactly why you write the ground-truth set *before* seeing any output.
