# Lesson 10 — Low-Code AI Applications

> Source: `10-building-low-code-ai-applications` · The original is Microsoft Power Platform. Below: the
> transferable concepts, the Google-ecosystem equivalents, and the Python fallback.

## 🎯 Goal
Know when *not* to write code — and what the low-code tools actually do under the hood.

---

## 1. The low-code idea
A visual builder generates the app (UI, data model, automation) from a natural-language description.
You describe the app; the platform emits the schema, screens and logic. Generative AI is the
translation layer between "what I want" and "the app definition".

Original lesson's stack:
- **Copilot in Power Apps** — describe an app, get tables + screens.
- **Copilot in Power Automate** — describe a workflow, get the flow.
- **Copilot Studio** — build intelligent agents over your knowledge sources.
- **AI Builder** — prebuilt models (invoice processing, sentiment, OCR, text generation) you drop into flows.

## 2. Prebuilt vs custom AI models

| | Prebuilt | Custom |
|---|---|---|
| Training | Already trained by the vendor | You train on your data |
| Setup | Use immediately | Collect, label, train, evaluate |
| Fit | Common tasks (invoices, receipts, sentiment, OCR) | Your specific documents/labels |
| Cost | Low | Higher (data + compute + expertise) |

**Rule:** try the prebuilt model first; go custom only when it measurably fails your data.

## 3. Google-ecosystem equivalents

| Need | Tool |
|---|---|
| No-code prompt prototyping | **Google AI Studio** — build, test and share prompts, then "Get code" |
| Custom no-code assistant | **Gems** (custom Gemini assistants with your instructions + files) |
| Workflow automation | **Apps Script** + Gemini API, or Google Workspace flows |
| Enterprise agents | **Vertex AI Agent Builder** / Gemini Enterprise |

**The realistic low-code workflow:** prototype the prompt in AI Studio → click **Get code** → paste
the generated Python into your app. You get the iteration speed of low-code and the control of code.

## 4. Structured extraction — the Python version of "AI Builder invoice processing"

The single highest-value low-code feature is document → structured data. Here it is in ~20 lines:

```python
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel
from typing import List

load_dotenv()
client = genai.Client()

class LineItem(BaseModel):
    description: str
    quantity: int
    unit_price: float

class Invoice(BaseModel):
    invoice_number: str
    vendor: str
    invoice_date: str
    total: float
    line_items: List[LineItem]

interaction = client.interactions.create(
    model="gemini-flash-latest",
    input=f"Extract the invoice fields from this document:\n\n{document_text}",
    response_format={
        "type": "text",
        "mime_type": "application/json",
        "schema": Invoice.model_json_schema(),
    },
)

invoice = Invoice.model_validate_json(interaction.output_text)
print(invoice.vendor, invoice.total)
```
> ✅ Verified working against this project's key. This is the same pattern as lesson 11 — a schema
> turns an unstructured document into typed Python objects you can put straight in a database.

## 5. When to choose which

| Use low-code when | Use code when |
|---|---|
| Internal tool, non-developer owners | Custom logic, custom UX |
| Standard CRUD + approvals | Version control, tests, CI/CD needed |
| Speed matters more than control | Cost/performance tuning matters |
| The prebuilt model fits your data | You need your own retrieval, evals, or pipeline |

---

## 🧠 Crux Notes
- Low-code platforms are a **generative front-end over an app definition** — same LLM ideas, different surface.
- **Prebuilt first, custom only on measured failure** — that rule survives any platform.
- AI Studio → "Get code" is the practical bridge from no-code prototype to Python app.
- The transferable skill from this lesson is **structured extraction**: schema in, typed object out.
- Choose low-code for speed and ownership by non-developers; choose code for control, tests and scale.

---

## ✅ Test Your Knowledge

**1.** When do you choose a prebuilt AI model over a custom one?
<details><summary>Answer</summary>

Always try prebuilt first — invoices, receipts, sentiment, OCR are solved problems. Go custom only when you have **measured** the prebuilt model failing on your data.
</details>

**2.** What is the transferable engineering skill behind "AI Builder invoice processing"?
<details><summary>Answer</summary>

**Structured extraction** — unstructured document in, schema-validated typed object out. Same pattern as lesson 11's structured output.
</details>

**3.** Give two reasons to write code instead of using a low-code platform.
<details><summary>Answer</summary>

Any two of: custom logic/UX, version control and tests, CI/CD, cost and performance tuning, custom retrieval or evaluation pipelines.
</details>

**4.** What is the practical bridge from an AI Studio prototype to a Python app?
<details><summary>Answer</summary>

Prototype the prompt in AI Studio, then use **"Get code"** to export it and paste it into your app — low-code iteration speed, code-level control.
</details>

**5.** Why does a JSON schema beat "return JSON" in the prompt?
<details><summary>Answer</summary>

A schema is enforced, so the shape is guaranteed and parses into typed objects every time. "Return JSON" in prose gives you `3.7` one call and `"3.7 GPA"` the next (lesson 11).
</details>

---

## 🛠️ Practical Task

**Build:** `practice/10_invoice_extract.py` — the code version of a low-code document processor.

### Requirements
1. Define Pydantic models: `LineItem(description, quantity, unit_price)` and `Invoice(invoice_number, vendor, invoice_date, total, line_items)`.
2. Extract from **3 messy invoice texts** you write by hand — vary the wording, ordering and date formats deliberately.
3. Use `response_format` with `Invoice.model_json_schema()`.
4. Validate with `Invoice.model_validate_json()`.
5. **Cross-check the arithmetic in Python**: does `sum(qty * unit_price)` match the extracted `total`? Flag mismatches.
6. Write all results to `practice/10_invoices.json`.

### Passing criteria

| # | Criterion | Expected |
|---|---|---|
| 1 | All 3 parse without a `ValidationError` | Schema holds across varied wording |
| 2 | `total` is a **float**, not a string | `type(inv.total) is float` |
| 3 | Dates normalised to one format | Despite three input formats |
| 4 | Arithmetic cross-check runs | Prints OK or MISMATCH per invoice |
| 5 | Output JSON is valid | `python -c "import json;json.load(open('practice/10_invoices.json'))"` |

### Test cases

| Input quirk | Expected |
|---|---|
| Total written `"$1,234.50"` | Parsed as `1234.5` (float, no comma or symbol) |
| Date `"3rd March 2026"` vs `"03/03/26"` | Both normalised identically |
| An invoice whose stated total is **deliberately wrong** | Your Python check flags MISMATCH |

### Verify
```bash
python practice/10_invoice_extract.py && python -c "import json;d=json.load(open('practice/10_invoices.json'));print(len(d),'invoices')"
# PASS: 3 invoices, and the wrong-total one flagged
```

**Why case 3 matters:** the model will happily return the stated (wrong) total. Lesson 01 said models are bad at arithmetic — so the *model extracts* and *Python verifies*. Never let the LLM be your calculator.
