# Lesson 05 — Advanced Prompting Techniques

> Source: `05-advanced-prompts` · Python examples retargeted to the Gemini API.

## 🎯 Goal
Go from "trying prompts" to knowing *why* one prompt beats another, and how to control output variance.

---

## 1. The technique catalogue

| Technique | Idea | Use when |
|---|---|---|
| **Zero-shot** | Single prompt, no examples | Simple, well-known tasks |
| **Few-shot** | Provide 1+ examples of desired output | You need a specific format/style |
| **Chain-of-thought** | Show the model *how* to break a problem into steps | Multi-step reasoning, arithmetic, logic |
| **Generated knowledge** | Inject your own facts/data into the prompt via a template | Company data, catalogues, product lists |
| **Least-to-most** | Decompose a big problem into ordered subproblems | Planning, pipelines, multi-stage work |
| **Self-refine** | Ask the model to critique and improve its own output | Code quality, drafts, designs |
| **Maieutic** | Ask it to explain each part; discard inconsistencies | Verifying an answer you can't check directly |

## 2. Chain-of-thought — the classic example

Without CoT:
> *"Alice has 5 apples, throws 3, gives 2 to Bob, Bob gives one back. How many?"* → **5** ❌ (correct: 5−3−2+1 = **1**)

With CoT — give a solved analogue first:
```python
cot = """Lisa has 7 apples, throws 1 apple, gives 4 apples to Bart and Bart gives one back:
7 - 1 = 6
6 - 4 = 2
2 + 1 = 3

Alice has 5 apples, throws 3 apples, gives 2 to Bob and Bob gives one back, how many apples does Alice have?"""

print(client.interactions.create(model="gemini-flash-latest", input=cot).output_text)   # → 1 ✅
```

> **Gemini note:** current Gemini models reason internally before answering, so they often get this right unaided. CoT still pays off for *your* domain logic, and for making the reasoning auditable — ask "show your steps" when you need to check the work.

## 3. Generated knowledge — templates + your data

```python
TEMPLATE = """Insurance company: {company}
Insurance products (cost per month):
{products}

Please suggest an insurance given the following budget and requirements:
Budget: {budget} restrict choice to types: {allowed}"""

prompt = TEMPLATE.format(
    company="ACME Insurance",
    products="\n".join([
        "- type: Car,  cheap,     cost: 500 USD",
        "- type: Car,  expensive, cost: 1100 USD",
        "- type: Home, cheap,     cost: 600 USD",
        "- type: Home, expensive, cost: 1200 USD",
        "- type: Life, cheap,     cost: 100 USD",
    ]),
    budget="$1000",
    allowed="Car, Home",
)
```

**The lesson within the lesson:** the first version of this prompt (plain list, no `type:`/`cost:` labels, no `restrict`) returned a $1,200 package including Life insurance — over budget and out of scope. Adding **structure** (`type:`, `cost:`) and a **constraint keyword** (`restrict`) fixed it. Even with a good technique, you still iterate.

## 4. Self-refine

```python
first = client.interactions.create(
    model="gemini-flash-latest",
    input="Create a Python Web API with routes products and customers",
)

critique = client.interactions.create(
    model="gemini-flash-latest",
    input="Suggest exactly 3 improvements to the above code, focused on security and structure. Then output the improved code.",
    previous_interaction_id=first.id,     # the model can see its own earlier answer
)
print(critique.output_text)
```

> 💡 `previous_interaction_id` is how you chain turns without re-sending history. Tip: bound the critique ("3 improvements", "focus on performance") or it sprawls.

## 5. Maieutic prompting
1. Ask the question.
2. For each part of the answer, ask for a deeper explanation.
3. Discard inconsistent parts. Repeat until satisfied.

Example: "5 steps for a pandemic crisis plan" → "Explain step 1, what are the risks in detail?" → "Which is the biggest risk and why?" → "What are the two biggest risks?" — if the answers stay consistent ("life", "business"), confidence rises. **Still verify independently.**

## 6. Controlling variance — temperature

Temperature ≈ 0 → deterministic/repetitive · higher → more varied/creative.

```python
interaction = client.interactions.create(
    model="gemini-flash-latest",
    input="Generate code for a Python Web API",
    generation_config={"temperature": 0.1},   # try 0.1 vs 0.9 and compare
)
print(interaction.output_text)
```

At `0.1` two runs of the same prompt differ only cosmetically; at `0.9` you get structurally different programs (one a stub, one a full books API).

> Other knobs exist — `top_p`, `top_k`, penalties — out of scope here. Note that on strongly reasoning-oriented models, prompt clarity matters more than sampling knobs.

## 7. Good practices
- **Specify context** — domain, topic, audience.
- **Limit the output** — number of items, length.
- **Specify what *and* how** — "…divide it into 3 files".
- **Use templates** — enrich prompts with real data via placeholders.
- **Spell correctly** — sloppy input, sloppy output.

---

## 🧠 Crux Notes
- Prompting is an **emergent** property — discovered by use, not built into the model.
- CoT = show the *method*, not just the answer; few-shot = show the *format*.
- Structure your injected data (labels, units, explicit constraints) — unlabelled lists get misread.
- **Self-refine** is the highest value-per-token technique for code: generate → critique → regenerate.
- `temperature` low = predictable, high = varied. Pick based on whether variation is a feature or a bug.
- Never trust the output because it is consistent — consistency is not correctness.

---

## ✅ Test Your Knowledge

**1.** Why use chain-of-thought prompting?
a) To teach the LLM how to solve a problem. b) To teach the LLM to find errors in code. c) To instruct the LLM to come up with different solutions.
<details><summary>Answer</summary>

**a.** CoT shows the model *how* to solve a problem by walking through a similar problem and its steps.
</details>

**2.** Difference between few-shot and chain-of-thought?
<details><summary>Answer</summary>

Few-shot shows the **format** of the answer. Chain-of-thought shows the **method** for reaching it. You often want both.
</details>

**3.** What is self-refine, and why cap it?
<details><summary>Answer</summary>

Generate → critique → regenerate. Cap the number of improvements ("suggest exactly 3") or the model sprawls into unfocused rewrites and burns tokens.
</details>

**4.** The insurance prompt returned an over-budget package including Life insurance. What fixed it?
<details><summary>Answer</summary>

Structure and constraints: labelling the data (`type:`, `cost:`) and using the keyword `restrict` to limit allowed types. The technique was already right — the prompt needed iteration.
</details>

**5.** Maieutic prompting gave consistent answers across three probes. Is the answer correct?
<details><summary>Answer</summary>

Not necessarily. **Consistency is not correctness** — a model can be consistently wrong. It raises confidence; it does not replace verification.
</details>

---

## 🛠️ Practical Task

**Build:** `practice/05_techniques.py` — a head-to-head on a problem plain prompting gets wrong.

### Requirements
1. Write **8 word problems** with multi-step arithmetic and known answers, in the style of:
   *"Alice has 5 apples, throws 3, gives 2 to Bob, Bob gives one back. How many?"* (answer: 1)
2. Solve each with 3 strategies:
   - **A** zero-shot
   - **B** chain-of-thought (one worked example showing the arithmetic, then the question)
   - **C** zero-shot + "show your steps, then give the final answer on the last line as `ANSWER: <n>`"
3. Extract the final number from each response and compare to ground truth.
4. Print accuracy per strategy plus average latency.

### Passing criteria

| # | Criterion | Expected |
|---|---|---|
| 1 | 24 runs complete | 8 problems × 3 strategies |
| 2 | Answer extraction is robust | Regex the last integer, or parse the `ANSWER:` line |
| 3 | Accuracy printed per strategy | `A: 6/8  B: 8/8  C: 8/8` |
| 4 | Latency compared | CoT costs more tokens/time — quantify it |
| 5 | Written conclusion | When is CoT worth the extra cost? |

### Verify
```bash
python practice/05_techniques.py
# PASS if all 24 runs complete, extraction never crashes, and 3 accuracies print
```

**Note:** modern Gemini models reason internally, so A may already score 8/8. That is a real finding — write it down. The value of CoT then shifts to **auditability** (you can see the steps) and to *your* domain logic, which the model was never trained on.
