# Progress Tracker

Tick a lesson only when **both** the quiz and the practical task pass. Deliverables land in `practice/`.

| # | Lesson | Quiz | Task file | Task | Notes |
|---|---|:---:|---|:---:|---|
| 00 | Course Setup | ☐ | `00_setup_check.py` | ☐ | |
| 01 | Intro to GenAI | ☐ | `01_tokens.py` | ☐ | |
| 02 | Comparing Models | ☐ | `02_model_bench.py` | ☐ | |
| 03 | Responsible AI | ☐ | `03_safety_harness.py` | ☐ | |
| 04 | Prompt Fundamentals | ☐ | `04_prompt_ladder.py` | ☐ | |
| 05 | Advanced Prompts | ☐ | `05_techniques.py` | ☐ | |
| 06 | Text Generation Apps | ☐ | `06_recipe_app.py` | ☐ | |
| 07 | Chat Applications | ☐ | `07_chat.py` | ☐ | |
| 08 | Search Applications | ☐ | `08_search.py` | ☐ | |
| 09 | Image Applications | ☐ | `09_monuments.py` | ☐ | |
| 10 | Low-Code AI | ☐ | `10_invoice_extract.py` | ☐ | |
| 11 | Function Calling | ☐ | `11_agent_tools.py` | ☐ | ⭐ core |
| 12 | Designing UX | ☐ | `12_improved_chat.py` + `12_ux_review.md` | ☐ | |
| 13 | Securing AI Apps | ☐ | `13_injection_lab.py` | ☐ | |
| 14 | App Lifecycle | ☐ | `14_eval.py` | ☐ | ⭐ reused by 15–19 |
| 15 | RAG & Vector DBs | ☐ | `15_rag.py` | ☐ | ⭐ core |
| 16 | Open Source Models | ☐ | `16_open_vs_hosted.py` | ☐ | |
| 17 | AI Agents | ☐ | `17_research_agent.py` | ☐ | ⭐ core |
| 18 | Fine-Tuning | ☐ | `18_no_finetune.py` | ☐ | Part B optional |
| 19 | Small Language Models | ☐ | `19_size_tiers.py` | ☐ | |
| 20 | Mistral Models | ☐ | `20_tokenizer_economics.py` | ☐ | |
| 21 | Meta Llama Models | ☐ | `21_multimodal.py` | ☐ | |

## Dependencies between tasks

```
08_search.py ──► 15_rag.py ──► 17_research_agent.py
                     │
                     └────────► 14_eval.py (grades 15)
07_chat.py ──► 12_improved_chat.py
11_agent_tools.py ──► 17_research_agent.py
```
Do **08 → 15 → 14 → 17** in that order; the rest stand alone.

## Free-tier budget

Task 02 (~9 calls), 04 (~48), 05 (~24), 18A (~60), 19 (~75) are the heavy ones.
Spread them out, use `gemini-flash-lite-latest` where the task allows, and always wrap calls so a
`429` records `RATE_LIMITED` instead of destroying a half-finished run.

## Self-grading standard

A task passes only when **every** row in its criteria table passes — including the awkward ones
(empty input, blocked response, rate limit, nonsense query). Those rows are where the actual learning is.
