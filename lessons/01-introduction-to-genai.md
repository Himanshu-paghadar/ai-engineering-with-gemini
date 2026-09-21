# Lesson 01 — Introduction to Generative AI & LLMs

> Source: `01-introduction-to-genai` · Concept lesson — but this mental model is why `temperature`, tokens and context limits behave as they do.

## 🎯 Goal
Understand what a model like `gemini-3.8-flash` actually does when you call it.

---

## 1. How we got here

```
Rule-based chatbots (1960s)
  → Statistical ML (1990s: learn patterns from labelled text)
    → Neural nets / RNNs (2000s: context-aware assistants)
      → Transformers (attention, 2017) → LLMs → Generative AI
```

**Transformer's key idea — attention:** weight every input token by relevance regardless of position. That removed the RNN sequence-length ceiling and made today's long-context models possible.

Hierarchy: `AI ⊃ Machine Learning ⊃ Deep Learning ⊃ Generative AI`.

## 2. The three mechanics inside one API call

| Step | What happens | What you see in Python |
|---|---|---|
| **Tokenizer** | Text → chunks → integer IDs. Models train on tokens, not characters. | Tokens drive **cost**, **context limits**, **truncation** |
| **Next-token prediction** | Given *n* tokens, predict token *n+1*, append, repeat | Why streaming works; why output can stop mid-sentence |
| **Probability sampling** | Model emits a distribution over all possible next tokens; one is sampled with controlled randomness | Same prompt ≠ same output; tuned by `temperature` |

```python
# The whole loop, conceptually:
tokens = tokenize(prompt)
while not done:
    distribution = model(tokens)        # P(next_token | tokens)
    next_token   = sample(distribution) # the randomness lives here
    tokens.append(next_token)
```

**See tokens for real:**

```python
from google import genai

client = genai.Client()
print(client.models.count_tokens(
    model="gemini-flash-latest",
    contents="Generative AI is artificial intelligence capable of generating content.",
))
```

## 3. Prompt → Completion
- **Prompt** = your input. **Completion** = the model literally completing the token sequence.

Prompt shapes to recognize:
- **Instruction** — "Summarize this for a 2nd grader in 3 bullets."
- **Question** — a conversational turn.
- **Text to complete** — writing assistance.
- **Code** — generate, explain, or document code.

## 4. What LLMs are *not*
- Not deterministic — sampling means output varies.
- Not reliable — **fabrications** arrive confident and fluent.
- Not intelligent — no critical reasoning or emotional intelligence.
- Not a calculator — exact arithmetic is a weak spot (give it a tool instead → lesson 11).

---

## 🧠 Crux Notes
- An LLM is a **statistical next-token predictor**, not a database of facts.
- Tokens are the unit of cost, context window, and truncation — `count_tokens` before you guess.
- Non-determinism is a design choice (sampling), not a bug; `temperature` is the dial.
- Treat output as a **strong first draft** that something — a human, a test, a retrieval step — must verify.
- Knowledge check: *"The response may vary despite the same prompt; great for a first draft you then improve."*

---

## ✅ Test Your Knowledge

**1.** What is true about large language models?
a) You get the exact same response every time.
b) It does things perfectly — great at arithmetic and working code.
c) The response may vary despite the same prompt; it gives a good first draft you must improve.
<details><summary>Answer</summary>

**c.** An LLM is non-deterministic; you can reduce variance with `temperature` but not eliminate it. Expect a solid first attempt, not perfection.
</details>

**2.** Put these in order: sampling, tokenization, next-token prediction.
<details><summary>Answer</summary>

Tokenization → next-token prediction → sampling. Text becomes token IDs, the model predicts a probability distribution over the next token, then one is sampled.
</details>

**3.** Why is "tokens" the unit that matters rather than "words" or "characters"?
<details><summary>Answer</summary>

Models are trained on tokens, so tokens determine cost, context-window limits and where truncation happens. A 10-word prompt and a 10-word code snippet can tokenize very differently.
</details>

**4.** Why does a response sometimes stop mid-sentence?
<details><summary>Answer</summary>

Generation is a loop that appends one token at a time. It stops on a stop condition — usually hitting `max_output_tokens` or the context limit — which can land mid-sentence.
</details>

**5.** Your app must add up invoice totals. Should the LLM do the arithmetic?
<details><summary>Answer</summary>

No. Exact arithmetic is a known weak spot — it predicts plausible tokens, it does not calculate. Have it extract the numbers (lesson 11) and do the maths in Python.
</details>

---

## 🛠️ Practical Task

**Build:** `practice/01_tokens.py` — prove to yourself that tokens, not words, are the unit.

### Requirements
1. Count tokens for these three strings with `client.models.count_tokens`:
   - `"Hello world"`
   - `"Generative AI is artificial intelligence capable of generating content."`
   - a 50-line code snippet of your choice
2. Print tokens, character count, and the **characters-per-token ratio** for each.
3. Run the *same* prompt 3 times and print whether the 3 outputs were identical.

### Passing criteria

| # | Criterion | Expected |
|---|---|---|
| 1 | Ratio is printed for all 3 inputs | English prose lands near 4 chars/token |
| 2 | Code has a **lower** ratio than prose | Code tokenizes less efficiently |
| 3 | Non-determinism is demonstrated | At least one of 3 runs differs, OR you explain why they matched |
| 4 | No hardcoded token counts | Every number comes from an API call |

### Verify
```bash
python practice/01_tokens.py
# Expect roughly: "Hello world" -> 2-3 tokens; prose -> ~4 chars/token; code -> ~2-3 chars/token
```

**Bonus:** re-run the identical-output test with `generation_config={"temperature": 0}`. Does it become deterministic? Explain what you observe.
