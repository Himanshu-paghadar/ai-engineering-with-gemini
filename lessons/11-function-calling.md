# Lesson 11 — Integrating with Function Calling

> Source: `11-integrating-with-function-calling` · Retargeted to Gemini tools. ✅ Code verified live.

## 🎯 Goal
Get **consistent, structured** responses and let the model reach **external data**.

---

## 1. The problem function calling solves

Two nearly identical prompts asking for JSON student records returned:

```json
{"name": "Emily Johnson", "grades": "3.7"}        // one format
{"name": "Michael Lee",   "grades": "3.8 GPA"}    // ...and another
```

Unstructured in → unstructured out. You cannot store that reliably. Two fixes, both in this lesson:

| Need | Tool |
|---|---|
| Guaranteed output **shape** | **Structured output** (`response_format` + JSON schema) |
| Model decides to **call your code / an API** | **Function calling** (`tools=[...]`) |

## 2. Structured output — when you just need clean JSON

```python
from pydantic import BaseModel
from google import genai

client = genai.Client()

class Student(BaseModel):
    name: str
    major: str
    school: str
    grades: float
    club: str

r = client.interactions.create(
    model="gemini-flash-latest",
    input=f"Extract the student information:\n{student_1_description}",
    response_format={
        "type": "text",
        "mime_type": "application/json",
        "schema": Student.model_json_schema(),
    },
)
student = Student.model_validate_json(r.output_text)
print(student.grades)     # 3.7  — a float, every single time
```

## 3. Function calling — the 3-step flow

> **The model never runs your function.** It returns a *structured request* to call it. Your code
> executes it and sends the result back.

```
1. Call the model with tools + user message
2. Read the function_call → execute YOUR Python function
3. Send the result back → model replies in natural language
```

### Step 1 — declare the tool

```python
functions = [
    {
        "type": "function",
        "name": "search_courses",
        "description": "Retrieves courses from the search index based on the parameters provided",
        "parameters": {
            "type": "object",
            "properties": {
                "role":    {"type": "string", "description": "The role of the learner (developer, data scientist, student...)"},
                "product": {"type": "string", "description": "The product the lesson covers (Azure, Power BI...)"},
                "level":   {"type": "string", "description": "beginner, intermediate, or advanced"},
            },
            "required": ["role"],
        },
    }
]
```
`description` is not documentation — it is **the prompt the model uses to decide when to call this**. Be specific.

> ⚠️ Tool definitions are sent with every request and **count against your token budget**.

### Step 2 — call, and read the function_call

```python
interaction = client.interactions.create(
    model="gemini-flash-latest",
    input="Find me a good course for a beginner student to learn Azure.",
    tools=functions,
)

fc = next(s for s in interaction.steps if s.type == "function_call")
print(fc.name)        # search_courses
print(fc.arguments)   # {'role': 'student', 'product': 'Azure', 'level': 'beginner'}
```
✅ Exactly this output was verified against the live key. Note the model extracted `student`,
`Azure` and `beginner` from free-form English into typed parameters.

> `interaction.steps` may also contain a `thought` step — always **filter by `s.type`**, never index by position.

### Step 3 — execute and return the result

```python
import json, requests

def search_courses(role, product=None, level=None):
    url = "https://learn.microsoft.com/api/catalog/"
    params = {"role": role, "product": product, "level": level}
    modules = requests.get(url, params=params).json()["modules"]
    return [{"title": m["title"], "url": m["url"]} for m in modules[:5]]

available_functions = {"search_courses": search_courses}

result = available_functions[fc.name](**fc.arguments)

final = client.interactions.create(
    model="gemini-flash-latest",
    input=[{
        "type": "function_result",
        "name": fc.name,
        "call_id": fc.id,
        "result": [{"type": "text", "text": json.dumps(result)}],
    }],
    previous_interaction_id=interaction.id,
)
print(final.output_text)   # natural-language answer built from real API data
```

## 4. A reusable loop

```python
def run_with_tools(user_message, tools, registry, model="gemini-flash-latest"):
    interaction = client.interactions.create(model=model, input=user_message, tools=tools)

    for _ in range(5):                                  # bound the loop — always
        calls = [s for s in interaction.steps if s.type == "function_call"]
        if not calls:
            return interaction.output_text
        results = []
        for call in calls:
            try:
                out = registry[call.name](**call.arguments)
            except Exception as e:                      # tell the model it failed
                out = {"error": str(e)}
            results.append({
                "type": "function_result", "name": call.name, "call_id": call.id,
                "result": [{"type": "text", "text": json.dumps(out)}],
            })
        interaction = client.interactions.create(
            model=model, input=results,
            previous_interaction_id=interaction.id, tools=tools,
        )
    return interaction.output_text
```

## 5. Built-in tools
Gemini also ships hosted tools you don't implement — e.g. Google Search grounding:

```python
r = client.interactions.create(
    model="gemini-flash-latest",
    input="Who won Euro 2024?",
    tools=[{"type": "google_search"}],
)
```
> ⚠️ On the free tier this can return **429 (quota exceeded)** — it did in testing. Handle it.

## 6. Use cases
- **Call external tools** — "Email my instructor" → `send_email(to, body)`
- **API/DB queries** — "Who completed the last assignment?" → `get_completed(...)`
- **Structured data** — turn an article into flashcards → `get_important_facts(...)`

---

## 🧠 Crux Notes
- **The model doesn't execute anything.** It emits a typed request; your code runs it and reports back.
- Need shape only → **structured output**. Need external data/actions → **function calling**.
- The function `description` *is* the prompt — vague descriptions mean the tool never gets called.
- Filter `interaction.steps` by `type`; expect `thought` steps alongside `function_call`.
- Always **bound the tool loop** and return errors to the model as results rather than crashing.
- Tool schemas consume input tokens on every call.

---

## ✅ Test Your Knowledge

**1.** When the model returns a `function_call`, has your function run?
<details><summary>Answer</summary>

**No.** The model only emits a structured *request*. Your code looks it up, executes it, and sends the result back. The model never executes anything.
</details>

**2.** You need guaranteed JSON shape but no external data. Structured output or function calling?
<details><summary>Answer</summary>

**Structured output** (`response_format` + schema). Function calling is for when the model needs to reach your code or an API.
</details>

**3.** Your tool is never called despite being declared. First thing to check?
<details><summary>Answer</summary>

The `description`. It is the prompt the model uses to decide relevance — vague descriptions mean the tool is ignored. Check the parameter descriptions too.
</details>

**4.** Why is `interaction.steps[0]` unsafe for reading a function call?
<details><summary>Answer</summary>

`steps` can contain a `thought` step before the `function_call` — verified in testing. Always filter by `s.type == "function_call"`.
</details>

**5.** Your tool raises an exception. Crash, or tell the model?
<details><summary>Answer</summary>

Tell the model — return `{"error": str(e)}` as the function result. It can often recover, retry with different arguments, or explain the failure to the user.
</details>

**6.** Why cap the tool loop?
<details><summary>Answer</summary>

A model can request tools indefinitely. Unbounded, it burns free-tier quota in seconds and can hang. Always bound the iterations.
</details>

---

## 🛠️ Practical Task

**Build:** `practice/11_agent_tools.py` — a working tool-calling assistant with three tools.

### Requirements
1. Implement three **real** Python functions:
   - `get_weather(city)` — may return canned data
   - `calculate(expression)` — safe arithmetic, **no `eval`** (use `ast.literal_eval` or a whitelist parser)
   - `search_courses(role, product, level)` — real HTTP call to the MS Learn catalog API
2. Declare all three as tool schemas with precise descriptions.
3. Write a loop (max 5 iterations) handling one *or multiple* function calls per turn.
4. Return tool errors to the model as results rather than crashing.
5. Log each tool call: name, arguments, result preview.

### Passing criteria

| # | Criterion | How to verify |
|---|---|---|
| 1 | Model picks the right tool per query | See test cases |
| 2 | Loop is bounded | `max_steps` parameter present |
| 3 | `calculate` rejects malicious input | `"__import__('os').system('ls')"` must not execute |
| 4 | Tool errors returned, not raised | Unplug the network — get a message, not a traceback |
| 5 | Filters by `s.type` | `grep 'type == "function_call"'` |
| 6 | Multiple calls per turn handled | Test case 4 |

### Test cases

| Query | Expected |
|---|---|
| "What's the weather in Paris?" | Calls `get_weather(city="Paris")` |
| "What is 847 * 23 + 19?" | Calls `calculate`, answers **19500** |
| "Find beginner Azure courses for a student" | Calls `search_courses(role='student', product='Azure', level='beginner')` |
| "Weather in Oslo, and what's 15% of 200?" | **Two** tool calls in one turn |
| "Who was Napoleon?" | **No** tool call — answers directly |
| `calculate("__import__('os').system('ls')")` | Rejected safely |

### Verify
```bash
python practice/11_agent_tools.py
# PASS: all 6 cases behave as specified; case 5 makes zero tool calls
```

**Case 5 is the one people miss.** A model that calls a tool for everything is as broken as one that never does. Knowing when *not* to act is part of the job.
