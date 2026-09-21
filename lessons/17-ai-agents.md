# Lesson 17 — AI Agents

> Source: `17-ai-agents` · Extended with Gemini-native agent patterns.

## 🎯 Goal
Understand what an agent is, and build one on top of function calling.

---

## 1. Definition

> **AI Agents let LLMs perform tasks by giving them access to a _state_ and _tools_.**

| Term | Meaning |
|---|---|
| **LLM** | The reasoning engine — `gemini-flash-latest`, Gemma, Llama... |
| **State** | The context the model works in: past actions + current situation, guiding the next decision |
| **Tools** | What it can act with: a database, an API, an external app, or another LLM |

Agent = **LLM + state + tools + a loop**. Lesson 11 gave you tools; the loop makes it an agent.

## 2. Build one yourself (no framework)

```python
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client()
MODEL = "gemini-flash-latest"

def get_weather(location: str) -> str:
    return f"The weather in {location} is sunny with a high of 22°C."

TOOLS = [{
    "type": "function",
    "name": "get_weather",
    "description": "Get the current weather for a given location.",
    "parameters": {
        "type": "object",
        "properties": {"location": {"type": "string", "description": "City name"}},
        "required": ["location"],
    },
}]
REGISTRY = {"get_weather": get_weather}

def agent(task: str, max_steps: int = 5) -> str:
    interaction = client.interactions.create(
        model=MODEL,
        system_instruction="You are a helpful assistant. Use tools when you need real data.",
        input=task,
        tools=TOOLS,
    )
    for _ in range(max_steps):                      # ← the agent loop, always bounded
        calls = [s for s in interaction.steps if s.type == "function_call"]
        if not calls:
            return interaction.output_text
        results = []
        for c in calls:
            try:
                out = REGISTRY[c.name](**c.arguments)
            except Exception as e:
                out = {"error": str(e)}
            print(f"  ↳ tool: {c.name}({c.arguments})")
            results.append({"type": "function_result", "name": c.name, "call_id": c.id,
                            "result": [{"type": "text", "text": json.dumps(out)}]})
        interaction = client.interactions.create(
            model=MODEL, input=results,
            previous_interaction_id=interaction.id, tools=TOOLS,
        )
    return interaction.output_text

print(agent("What's the weather in Amsterdam, and should I take a jacket?"))
```

**State** here = `previous_interaction_id` (server-side history). **Tools** = `TOOLS` + `REGISTRY`.
**The loop** = keep going while the model keeps asking for tools.

## 3. Built-in / hosted tools
Some tools you don't implement at all:

```python
r = client.interactions.create(model=MODEL, input="What happened in tech this week?",
                               tools=[{"type": "google_search"}])
```
Also available to this key: `deep-research-*` models (multi-step research agents) and
`gemini-2.5-computer-use-preview` (UI-driving agents). ⚠️ Free-tier quota applies.

## 4. The framework landscape

| Framework | State | Tools | Distinctive |
|---|---|---|---|
| **Google ADK** (`pip install google-adk`) | Sessions | Python functions, MCP servers | Google's agent SDK; multi-agent, ships with eval + deploy |
| **LangChain Agents** | `AgentExecutor` holds chat history | Large community tool catalog | LangSmith gives visibility into which tool ran and why |
| **AutoGen** (Microsoft) | Conversation between agents | Assistant generates Python to act | **Conversable + customizable**: `AssistantAgent`, `UserProxyAgent` for human feedback |
| **Microsoft Agent Framework** | **Threads** (persistable, resumable) | Type-annotated Python functions → auto schema; MCP; code interpreter | Successor to AutoGen + Semantic Kernel; OpenTelemetry tracing; `SequentialBuilder` / `ConcurrentBuilder` |
| **TaskWeaver** | A `Planner` LLM maps request → tasks | `Plugins` (Python classes, code interpreter), stored as embeddings | **Code-first**: works with pandas DataFrames, not just strings. `experience` persists context to YAML |
| **JARVIS** | An LLM manages state | **Other AI models** are the tools | Routes to specialist models (object detection, transcription, captioning) and merges results |

```python
# Google ADK — tools are just annotated Python functions
from google.adk.agents import Agent

def get_weather(location: str) -> str:
    """Get the current weather for a given location."""
    return f"The weather in {location} is sunny with a high of 22°C."

root_agent = Agent(
    name="weather_agent",
    model="gemini-flash-latest",
    instruction="You are a helpful assistant that answers weather questions.",
    tools=[get_weather],
)
```

**Visibility matters.** Developers must be able to see *which* tool the model used and *why* —
LangSmith, OpenTelemetry tracing, or your own logging.

## 5. Multi-agent orchestration
- **Sequential** — each agent passes context down the chain (researcher → writer → editor).
- **Concurrent** — fan out to several agents in parallel, then aggregate (analyst A/B/C).
- **Conversational** — agents talk to each other until a termination condition ("Reply TERMINATE when done").

## 6. Assignment
Simulate a business meeting across departments of an education startup: give each agent a persona
and priorities via system instructions, let the user pitch a product idea, and have each department
generate follow-up questions to refine it.

---

## 🧠 Crux Notes
- **Agent = LLM + state + tools + a bounded loop.** You already have all four pieces from lesson 11.
- **Always cap the loop.** An unbounded agent burns your free-tier quota in seconds.
- State on Gemini = `previous_interaction_id`; in frameworks = threads/sessions/executors.
- Modern frameworks turn **type-annotated Python functions into tool schemas automatically**.
- **Observability is not optional** — you must be able to answer "why did it call that?"
- Return tool errors to the model as results; it can often recover on its own.

---

## ✅ Test Your Knowledge

**1.** Complete the definition: an AI agent is an LLM plus ___ and ___.
<details><summary>Answer</summary>

**State** (the context of past actions and the current situation) and **tools** (a database, API, external app, or another LLM). Plus a loop — that is what turns lesson 11's tool calling into an agent.
</details>

**2.** What is "state" on the Gemini API, concretely?
<details><summary>Answer</summary>

`previous_interaction_id` — server-side conversation history. In frameworks it appears as threads (Microsoft Agent Framework), sessions (ADK) or an `AgentExecutor` (LangChain).
</details>

**3.** What makes TaskWeaver "code-first" and why does it matter?
<details><summary>Answer</summary>

It works with **pandas DataFrames** rather than only strings, which suits data analysis and generation — charts, computed results — instead of passing data around as text.
</details>

**4.** How is JARVIS's approach to tools different?
<details><summary>Answer</summary>

Its tools are **other AI models** — specialists for object detection, transcription, image captioning. The LLM routes the request, formats it for each specialist, then merges the results.
</details>

**5.** Why is observability non-negotiable for agents?
<details><summary>Answer</summary>

You must be able to answer "which tool did it use and why?" — for debugging, cost control and trust. LangSmith, OpenTelemetry tracing, or your own logging.
</details>

**6.** What is the single most important safety rail in an agent loop?
<details><summary>Answer</summary>

**A bounded iteration count.** Unbounded, an agent can loop indefinitely, exhausting quota and hanging the app.
</details>

---

## 🛠️ Practical Task

**Build:** `practice/17_research_agent.py` — an agent that plans, acts and reports.

### Goal
Given a topic, the agent researches it using tools and produces a structured brief.

### Requirements
1. Tools: `search_notes(query)` (reuse your lesson-15 RAG retriever), `calculate(expr)`, `save_note(title, content)` (writes to `practice/17_notes/`).
2. A bounded loop (`max_steps=8`) handling multiple calls per turn.
3. **Log every step** to `practice/17_trace.jsonl`: step number, type, tool name, arguments, result preview, elapsed time.
4. Final output as a structured schema: `{topic, findings[], sources[], confidence}`.
5. Graceful stop when `max_steps` is hit — report partial results, do not crash.

### Passing criteria

| # | Criterion | How to verify |
|---|---|---|
| 1 | Completes a multi-tool task | Uses 2+ different tools in one run |
| 2 | Trace is complete and valid JSONL | Every step logged, file parses |
| 3 | Loop bounded | Set `max_steps=1` — it stops gracefully with partial results |
| 4 | Output matches schema | Parses with Pydantic |
| 5 | Tool errors recovered | Break `search_notes` deliberately — the agent reports rather than crashing |
| 6 | No infinite loop | Runs terminate in every test case |

### Test cases

| Task | Expected |
|---|---|
| "Summarize what my notes say about RAG and save it as a note" | `search_notes` → `save_note`; file appears in `practice/17_notes/` |
| "What do my notes say about quantum tunnelling?" | Searches, finds nothing relevant, reports low confidence — does **not** invent |
| "How many lessons mention embeddings, and what is that as a % of 22?" | `search_notes` + `calculate` |
| *(with `max_steps=1`)* | Stops cleanly, reports partial progress |

### Verify
```bash
python practice/17_research_agent.py "RAG and vector databases"
python -c "import json;[json.loads(l) for l in open('practice/17_trace.jsonl')];print('trace valid')"
```
**PASS:** all 4 cases terminate, trace is valid JSONL, case 2 reports low confidence rather than fabricating.

**Case 2 is the real test.** An agent that invents findings when tools return nothing is worse than no
agent — it launders a fabrication through an authoritative-looking process.
