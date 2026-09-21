# Lesson 14 — The Generative AI Application Lifecycle (LLMOps)

> Source: `14-the-generative-ai-application-lifecycle`

## 🎯 Goal
Keep an AI app relevant, reliable and robust after launch.

---

## 1. MLOps → LLMOps: the paradigm shift

| | MLOps ("ML Apps") | LLMOps ("GenAI Apps") |
|---|---|---|
| Who builds | Data scientists | **App developers** |
| Core asset | Your trained model | **Models-as-a-Service** + integration |
| Key technique | Feature engineering, training | **Prompting, RAG, fine-tuning, metaprompts** |
| Iteration unit | Training run | Prompt / retrieval / flow change |

### The five LLMOps metrics
| Metric | Question |
|---|---|
| **Quality** | Is the response good? |
| **Harm** | Is it responsible and safe? |
| **Honesty** | Is it grounded — does it make sense and is it correct? |
| **Cost** | Are we within budget? |
| **Latency** | Average time per token/response? |

## 2. The lifecycle — three stages plus an overarching cycle

```
        ┌──────────────── Management (security, compliance, governance) ────────────────┐
        │                                                                              │
   1. Ideating/Exploring  →  2. Building/Augmenting  →  3. Operationalizing
      prompt engineering,       RAG, fine-tuning,          monitoring, alerts,
      prototyping, testing      bigger datasets,           deployment, integration
      the hypothesis            robustness checks
```

**Not linear** — these are integrated, iterative loops.

1. **Ideating/Exploring** — explore against business needs; prototype a flow; test whether the hypothesis holds.
2. **Building/Augmenting** — evaluate on bigger datasets; apply RAG/tuning; if it fails, restructure the data or add steps to the flow. When metrics pass, move on.
3. **Operationalizing** — monitoring and alerting, deployment, application integration.

## 3. Evaluation in Python — the practical minimum

Before any of the tooling, you need a test set and a scoring loop. This is the highest-leverage
thing in the whole lesson:

```python
import json, time
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client()
MODEL = "gemini-flash-latest"

# 1. A fixed evaluation set — the thing most teams never build
cases = [
    {"input": "What is a perceptron?",          "must_include": ["weights", "activation"]},
    {"input": "Who wrote the Martian War 2076?", "must_include": ["not", "fictional"]},
]

def evaluate(system_instruction):
    results = []
    for case in cases:
        t0 = time.perf_counter()
        r = client.interactions.create(
            model=MODEL, system_instruction=system_instruction, input=case["input"]
        )
        text = (r.output_text or "").lower()
        results.append({
            "input":    case["input"],
            "passed":   all(k.lower() in text for k in case["must_include"]),
            "latency":  round(time.perf_counter() - t0, 2),
            "tokens":   getattr(r, "usage", None),
        })
    passed = sum(x["passed"] for x in results)
    print(f"{passed}/{len(results)} passed")
    return results

# 2. Change ONE thing (the prompt), re-run, compare. That's the iteration loop.
evaluate("You are a precise tutor. If a premise is false, say so before answering.")
```

**LLM-as-judge** for qualities you can't keyword-match (fluency, groundedness): send the question,
the answer and the source to a second model call and ask it to score 1–5 with a reason.

## 4. Tooling
- **Google AI Studio** — prompt exploration, comparison, "Get code".
- **Vertex AI** — evaluation, deployment, monitoring at scale; Gen AI Evaluation Service.
- The original lesson's stack: **Microsoft Foundry** + **PromptFlow** (visual flow building in VS Code, test/tune, deploy).

Whatever the vendor, the shape is the same: **explore → evaluate → deploy → monitor → iterate**.

---

## 🧠 Crux Notes
- LLMOps moves the centre of gravity from *training models* to **integrating and evaluating them**.
- Track five metrics: **Quality, Harm, Honesty (groundedness), Cost, Latency** — not just accuracy.
- The lifecycle is **loops, not a line**; management (security/compliance/governance) wraps all of it.
- **Build a fixed evaluation set early.** Without it, "the new prompt seems better" is just vibes.
- Change one variable at a time and re-run the same cases — that's the entire discipline.

---

## ✅ Test Your Knowledge

**1.** Name the five LLMOps metrics.
<details><summary>Answer</summary>

**Quality, Harm, Honesty (groundedness), Cost, Latency.**
</details>

**2.** What is the core shift from MLOps to LLMOps?
<details><summary>Answer</summary>

From data scientists **training models** to app developers **integrating and evaluating** Models-as-a-Service. The iteration unit becomes a prompt/retrieval/flow change rather than a training run.
</details>

**3.** Name the three lifecycle stages and what wraps them.
<details><summary>Answer</summary>

**Ideating/Exploring → Building/Augmenting → Operationalizing**, wrapped by an overarching **Management** cycle (security, compliance, governance). They are loops, not a line.
</details>

**4.** You changed the prompt and the retrieval strategy, and results improved. What is wrong?
<details><summary>Answer</summary>

You changed two variables, so you cannot attribute the gain — or know if one change actually hurt. Change one thing at a time against a fixed evaluation set.
</details>

**5.** How do you evaluate "groundedness", which keyword matching cannot measure?
<details><summary>Answer</summary>

**LLM-as-judge**: pass the question, the answer and the source documents to a second model call and ask it to score 1–5 with a reason for whether the answer is supported by the sources.
</details>

---

## 🛠️ Practical Task

**Build:** `practice/14_eval.py` — the evaluation harness every other lesson should have been graded by.

### Requirements
1. An evaluation set of **15 cases** for your lesson-15 RAG bot: `{question, must_include[], should_not_include[], expected_refusal: bool}`.
   Include at least **3 unanswerable** questions where the correct behaviour is refusal.
2. A `run_eval(system_instruction, retrieval_k)` function returning per-case results.
3. Score four dimensions: **keyword pass**, **refusal correctness**, **latency**, **tokens**.
4. Add an **LLM-as-judge** groundedness score (1–5) comparing answer against retrieved context.
5. Run **two configurations** (e.g. `k=2` vs `k=5`) and print a comparison.
6. Save results with a timestamp to `practice/14_evals/<timestamp>.json` so runs are comparable over time.

### Passing criteria

| # | Criterion | Expected |
|---|---|---|
| 1 | 15 cases including 3 unanswerable | Refusals scored as correct behaviour |
| 2 | Only **one** variable differs between configs | `k` alone |
| 3 | Judge returns a parseable 1–5 score | Structured output, not prose |
| 4 | All 5 dimensions reported per config | Table output |
| 5 | Results persisted with timestamp | Two runs produce two files |
| 6 | Conclusion cites numbers | Which config wins, and on which dimension |

### Test cases (illustrative)

| Question | must_include | expected_refusal |
|---|---|---|
| "What is a perceptron?" | `["weighted", "activation"]` | false |
| "What is cosine similarity?" | `["angle", "vector"]` | false |
| "What is the capital of Mongolia?" | — | **true** (not in the corpus) |
| "What did the Martian War of 2076 teach us?" | — | **true** (does not exist) |

### Verify
```bash
python practice/14_eval.py
ls practice/14_evals/*.json | wc -l    # grows with each run
```
**PASS:** both configs scored on all 5 dimensions, the 3 unanswerable questions are refused, and your conclusion names a winner with numbers.

**This is the most valuable file in the whole course.** Without it, every "this prompt is better" claim you make is a guess.
