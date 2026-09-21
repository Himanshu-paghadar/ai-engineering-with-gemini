# Lesson 07 — Building Chat Applications

> Source: `07-building-chat-applications` · Retargeted to the Gemini API.

## 🎯 Goal

Move from one-shot text generation to a stateful, monitored, responsible chat app.

---

## 1. Chatbot vs AI-powered chat application

| Chatbot                              | Generative AI chat application |
| ------------------------------------ | ------------------------------ |
| Task-focused, rule-based             | Context-aware                  |
| Often embedded in a larger system    | May host one or many chatbots  |
| Limited to programmed functions      | Incorporates generative models |
| Specialized, structured interactions | Open-domain discussion         |

## 2. Why use an SDK

- **Faster development** — focus on business logic, not HTTP plumbing.
- **Better performance** — scaling concerns already solved.
- **Easier maintenance** — upgrade a library, not your own transport code.
- **Cutting-edge models** — without training them.

```python
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client()

response = client.interactions.create(
    model="gemini-flash-latest",
    input="Suggest two titles for an instructional lesson on chat applications for generative AI.",
)
print(response.output_text)
```

## 3. Managing conversation state — three patterns

**A. Chain by interaction ID (Gemini-native, cheapest)**

```python
r1 = client.interactions.create(model=MODEL, input="I have 2 dogs in my house.")
r2 = client.interactions.create(
    model=MODEL,
    input="How many paws are in my house?",
    previous_interaction_id=r1.id,       # server keeps the context
)
print(r2.output_text)     # 8
```

**B. Send the full message list (portable, explicit)**

```python
history = [
    {"role": "user",  "content": "I have 2 dogs in my house."},
    {"role": "model", "content": "That's lovely! Two dogs make a lively home."},
    {"role": "user",  "content": "How many paws are in my house?"},
]
r = client.interactions.create(model=MODEL, input=history)
```

**C. A minimal REPL chat loop**

```python
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client()
MODEL = "gemini-flash-latest"

SYSTEM = ("You are a patient tutor for high-school students. "
          "Answer in at most 5 sentences. If unsure, say so.")

last_id = None
while True:
    user = input("\nYou: ")
    if user.strip().lower() in {"exit", "quit"}:
        break
    r = client.interactions.create(
        model=MODEL,
        system_instruction=SYSTEM,
        input=user,
        previous_interaction_id=last_id,
    )
    last_id = r.id
    print("\nBot:", r.output_text or "[response blocked by safety filters]")
```

## 4. UX considerations specific to AI chat

- **Handle ambiguity** — let users ask for clarification.
- **Context retention** — valuable, but retaining user data is a privacy risk. Set a retention policy.
- **Personalization** — user profiles / custom instructions tailor answers (like ChatGPT "Custom instructions").

### System message framework (4 parts)

1. Define **who the model is**, its capabilities and limitations.
2. Define the **output format**.
3. Provide **examples** of intended behaviour.
4. Provide **behavioural guardrails**.

### Accessibility

| Impairment | Features                                             |
| ---------- | ---------------------------------------------------- |
| Visual     | High contrast, resizable text, screen-reader support |
| Auditory   | Text-to-speech / speech-to-text, visual cues         |
| Motor      | Keyboard navigation, voice commands                  |
| Cognitive  | Simplified language options                          |

## 5. Customization for a domain

- **DSL model** — a model trained/tuned for one field.
- **Fine-tuning** — retrain on your data. _(Not available on the Gemini API — lesson 18. Use system instruction + few-shot + RAG instead.)_

Scenario: a medical reference chat. A general model handles basic questions but fails on
"best practices for drug-resistant epilepsy in pediatric patients" and lacks recent advances.
Ground it in a curated corpus (RAG, lesson 15) rather than trusting the base model.

## 6. Metrics to monitor

| Metric            | Definition                                     |
| ----------------- | ---------------------------------------------- |
| Uptime            | Time the app is operational                    |
| Response time     | Latency to reply                               |
| Precision         | True positives ÷ all positive predictions      |
| Recall            | True positives ÷ actual positives              |
| F1                | Harmonic mean of precision & recall            |
| Perplexity        | How well predicted distribution matches actual |
| User satisfaction | Survey / thumbs up-down                        |
| Error rate        | Rate of misunderstanding or wrong output       |
| Retraining cycles | How often the model/prompts are updated        |
| Anomaly detection | Unusual patterns vs expected behaviour         |

## 7. Responsible AI in chat

Fairness · Reliability & Safety · Privacy & Security · Inclusiveness · Transparency · Accountability
— each maps to a concrete developer duty (no discrimination on user data; fail-safes; encryption;
accessible UI; documented reasoning; an audit process).

---

## 🧠 Crux Notes

- Chat = text generation **+ state**. `previous_interaction_id` is the state primitive on Gemini.
- Always handle the empty/blocked response — a safety filter returns no text.
- The **system instruction** carries persona, format, examples and guardrails: write it deliberately.
- Context retention is a feature _and_ a privacy liability — decide a retention policy up front.
- You cannot improve what you don't measure: instrument latency, error rate and satisfaction from day one.

---

## ✅ Test Your Knowledge

**1.** Two differences between a chatbot and a generative AI chat application?

<details><summary>Answer</summary>

A chatbot is task-focused and rule-based with limited programmed functions; a generative chat app is context-aware, open-domain, and may host multiple chatbots.

</details>

**2.** Name the four parts of the system message framework.

<details><summary>Answer</summary>

1. Who the model is — capabilities and limitations. 2) Output format. 3) Examples of intended behaviour. 4) Behavioural guardrails.

</details>

**3.** Context retention improves UX. What is the cost?

<details><summary>Answer</summary>

Privacy risk from retaining potentially sensitive user information. Balance it with a retention policy and user control over stored context.

</details>

**4.** What does F1 score balance, and when do you care?

<details><summary>Answer</summary>

The harmonic mean of precision and recall. It matters when both false positives and false negatives are costly — e.g. routing support tickets.

</details>

**5.** Your chat loop crashes on turn 4 with `TypeError: NoneType`. Most likely cause?

<details><summary>Answer</summary>

A safety filter returned an empty response and you passed `None` onward. Guard `output_text` on **every** turn, not just the first.

</details>

---

## 🛠️ Practical Task

**Build:** `practice/07_chat.py` — a multi-turn tutor bot with real state.

### Requirements

1. A system instruction using all **four** framework parts.
2. A REPL loop maintaining context via `previous_interaction_id`.
3. Commands: `exit` (quit), `reset` (clear context), `history` (show turn count).
4. Handle blocked/empty responses with a friendly fallback.
5. Log every turn to `practice/07_chatlog.jsonl` — timestamp, user text, response, latency.

### Passing criteria

| #   | Criterion                          | How to verify                                                                        |
| --- | ---------------------------------- | ------------------------------------------------------------------------------------ |
| 1   | **Context is retained**            | Say "My name is Sam", then "What is my name?" — it answers Sam                       |
| 2   | `reset` genuinely clears it        | After`reset`, "What is my name?" no longer knows                                     |
| 3   | 5+ turns without crashing          | Includes at least one deliberately odd input                                         |
| 4   | Empty response handled             | Never prints`None`                                                                   |
| 5   | Log file is valid JSONL            | `python -c "import json;[json.loads(l) for l in open('practice/07_chatlog.jsonl')]"` |
| 6   | System instruction has all 4 parts | Read it — role, format, example, guardrail                                           |

### Test script

```bash
printf 'My name is Sam\nWhat is my name?\nreset\nWhat is my name?\nexit\n' | python practice/07_chat.py
```

**PASS:** turn 2 says "Sam"; turn 4 does **not**.

**The trap:** it is easy to "pass" turn 2 by accident because the model guesses from phrasing. Prove real state by asking something it could not infer — a number you invented, like "remember the code 7741".
