# Contributing

Thanks for your interest. This is a learning repository, so contributions that
make the material **more accurate** or **easier to learn from** are the most valuable.

## Ways to contribute

| Type | Examples |
|---|---|
| 🐛 **Correctness fixes** | Code that no longer runs, a wrong model ID, a broken link, an API that changed |
| 📝 **Clarity** | A confusing explanation, a missing step, a better worked example |
| ✅ **Task improvements** | A sharper passing criterion, a test case that exposes a real failure mode |
| 🌍 **Translations** | A lesson translated into another language |
| ⭐ **Solutions** | A reference solution for a practical task, in `lessons/practice/` |

## The one rule that matters

**Verify before you write.** This repo's whole premise is that every API claim was
executed against a live endpoint rather than copied from documentation — that is how
we caught that fine-tuning no longer exists on the Gemini API and that reasoning
tokens can be 25× the visible cost.

If you change a code sample or state how an API behaves, **run it first** and say so
in the pull request. A PR that says *"docs say X"* will be asked for evidence. A PR
that says *"ran this on 2026-09-21 against gemini-flash-latest, here is the output"*
gets merged.

## Setup

```bash
git clone https://github.com/Himanshu-paghadar/ai-engineering-with-gemini
cd ai-engineering-with-gemini

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env    # add your free key: https://aistudio.google.com/app/api-keys
python lessons/practice/00_setup_check.py
```

## Lesson structure

Every lesson follows the same shape. Keep it:

```
# Lesson NN — Title
> Source attribution

## 🎯 Goal              one sentence
## 1..N                 concepts, each with runnable Python
## 🧠 Crux Notes        5-6 bullets — the revision summary
## ✅ Test Your Knowledge   5-6 questions, answers in <details> blocks
## 🛠️ Practical Task    deliverable + passing-criteria table + test cases
```

Conventions:
- Prefer `-latest` model aliases (`gemini-flash-latest`) so samples don't rot
- Load keys with `load_dotenv()` and `os.environ` — **never** hardcode one
- Show the failure path too: blocked responses, rate limits, empty input
- Keep Crux Notes to bullets a reader can revise from in under a minute

## Pull requests

1. Fork and branch: `git checkout -b fix/lesson-11-tool-schema`
2. Make focused changes — one concern per PR
3. Run any code you touched, and **paste the output in the PR description**
4. Confirm no secrets: `git diff --staged | grep -iE 'AIza|AQ\.|api[_-]?key\s*='`
5. Open the PR describing what changed and how you verified it

**Commit messages:** imperative subject under 72 characters, body explaining *why*.

```
fix: correct tool schema format in lesson 11

The `parameters` block was nested one level too deep, so the model never
received the function description. Verified against gemini-flash-latest.
```

## Reporting issues

For a broken lesson, include: the lesson number, what you ran, what you expected,
what happened, and your `google-genai` version (`pip show google-genai`).

For anything security-related, see [SECURITY.md](SECURITY.md) — do not open a
public issue.

## Code of conduct

Participation is governed by the [Code of Conduct](CODE_OF_CONDUCT.md).
