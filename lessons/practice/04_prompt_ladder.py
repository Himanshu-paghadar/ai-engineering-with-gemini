"""Lesson 04 practice: measure how much prompt technique actually buys you.

Works with any OpenAI-compatible provider. Set these in .env:
    OPENAI_BASE_URL=https://your-provider.com/v1
    OPENAI_API_KEY=your-provider-key
    BENCH_MODELS=model-a,model-b,model-c

    python lessons/practice/04_prompt_ladder.py
"""

import os
import time

from dotenv import load_dotenv
from openai import OpenAI, RateLimitError

load_dotenv()
client = OpenAI(base_url=os.environ["OPENAI_BASE_URL"], api_key=os.environ["OPENAI_API_KEY"])

RETRIES, BACKOFF = 3, 2.0
MODEL = os.environ.get("PROMPT_MODEL") or os.environ["BENCH_MODELS"].split(",")[0].strip()

# Ground truth: 12 customer support messages with correct labels.
# Few-shot examples below are deliberately NOT paraphrases of these — otherwise v3/v4 just copy answers.
# Written BEFORE running any prompts — prevents unconscious cherry-picking of easy cases.
GROUND_TRUTH = [
    ("I was charged twice for the same order", "billing"),
    ("The app crashes when I try to log in", "technical"),
    ("How do I reset my password?", "account"),
    ("What are your business hours?", "other"),
    ("My payment method was declined but my bank says it went through", "billing"),
    ("The website is loading very slowly", "technical"),
    ("I need to update my email address", "account"),
    ("Can you recommend a good laptop?", "other"),
    ("I can't access my invoice from last month", "billing"),
    ("Error 500 when submitting the contact form", "technical"),
    ("How do I delete my account permanently?", "account"),
    ("Do you have a referral program?", "other"),
]

VALID_LABELS = {"billing", "technical", "account", "other"}


def classify(strategy: str, message: str) -> tuple[str, str]:
    """One classification call -> (label, status).

    status is ok | error. Retries transient failures before giving up.
    """
    prompts = {
        "v1_zero_shot": f"Classify this message: {message}",
        "v2_instruction": (
            f"Classify this customer support message into exactly one category: "
            f"billing, technical, account, or other.\n\n"
            f"Reply with one word only.\n\n"
            f"Message: {message}"
        ),
        "v3_few_shot": (
            f"Classify customer support messages into: billing, technical, account, or other.\n\n"
            f"Examples:\n"
            f'"Why did my subscription renew at a higher price?" -> billing\n'
            f'"Push notifications stopped after the last update" -> technical\n'
            f'"Can I change the username on my profile?" -> account\n'
            f'"Are you hiring for remote roles?" -> other\n\n'
            f"Message: {message}"
        ),
        "v4_few_shot_cue_out": (
            f"Classify customer support messages into: billing, technical, account, or other.\n\n"
            f"Examples:\n"
            f'"Why did my subscription renew at a higher price?" -> billing\n'
            f'"Push notifications stopped after the last update" -> technical\n'
            f'"Can I change the username on my profile?" -> account\n'
            f'"Are you hiring for remote roles?" -> other\n\n'
            f"If the message is ambiguous or does not clearly fit any category, reply 'other'.\n\n"
            f"Message: {message}\n"
            f"Category:"
        ),
    }

    prompt = prompts[strategy]

    for attempt in range(RETRIES):
        try:
            r = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
            )
        except Exception as e:
            last = f"{'RATE_LIMITED' if isinstance(e, RateLimitError) else 'ERROR'}: {str(e).splitlines()[0][:100]}"
            time.sleep(BACKOFF * (attempt + 1))
            continue
        text = (r.choices[0].message.content or "").strip()
        return (text, "ok") if text else ("", "error")

    print(f"  [{last}]")
    return "", "error"


def normalize(label: str) -> str:
    """Normalize output before comparison. Handles 'Billing.' and ' technical ' etc."""
    return label.strip().lower().rstrip(".,;:!?")


def evaluate(strategy: str) -> dict:
    """Run one strategy over all 12 test cases. Returns accuracy stats."""
    correct = 0
    stray = 0
    errors = 0

    for message, expected in GROUND_TRUTH:
        response, status = classify(strategy, message)

        if status == "error":
            errors += 1
            continue

        normalized = normalize(response)

        if normalized not in VALID_LABELS:
            stray += 1

        if normalized == expected:
            correct += 1

    return {
        "strategy": strategy,
        "correct": correct,
        "total": len(GROUND_TRUTH),
        "accuracy": correct / len(GROUND_TRUTH),
        "stray": stray,
        "errors": errors,
    }


print(f"model: {MODEL}")
print(f"test cases: {len(GROUND_TRUTH)}\n")

strategies = ["v1_zero_shot", "v2_instruction", "v3_few_shot", "v4_few_shot_cue_out"]
results = []

for strategy in strategies:
    print(f"Running {strategy}...")
    result = evaluate(strategy)
    results.append(result)
    print(f"  {result['correct']}/{result['total']} correct, {result['stray']} stray formatting\n")

print("-" * 90)
print(f"{'Strategy':<25} {'Accuracy':>15} {'Stray':>8} {'Errors':>8}")
print("-" * 90)

for r in results:
    strategy_display = r["strategy"].replace("_", " ").title()
    accuracy = f"{r['correct']}/{r['total']} ({r['accuracy']:.1%})"
    print(f"{strategy_display:<25} {accuracy:>15} {r['stray']:>8} {r['errors']:>8}")

# Verify criterion 4: v4 >= v1 — only meaningful if every call got an answer (0/12 >= 0/12 is not a pass)
v1_acc = results[0]["accuracy"]
v4_acc = results[3]["accuracy"]
total_errors = sum(r["errors"] for r in results)

print("\n" + "-" * 90)
print(f"Criterion 4 (v4 >= v1): {'PASS' if v4_acc >= v1_acc and total_errors == 0 else 'FAIL'}")
print(f"  v1 accuracy: {v1_acc:.1%}")
print(f"  v4 accuracy: {v4_acc:.1%}")

if total_errors > 0:
    print(f"\n⚠ Warning: {total_errors} call(s) failed — rerun before trusting this result")

# What I Learnt :
# Lesson 04: Prompt Engineering Fundamentals
# Prompt technique is something you measure, not something you assume. This ladder runs the same 12
# hand-labelled support messages through four prompts — zero-shot, instruction, few-shot, few-shot + cue
# + out — and scores each against ground truth written before any output was seen. Each rung adds one
# building block from the lesson: the exact label list and "one word only" (be specific), four labelled
# examples (show, don't tell), a "Category:" cue that starts the answer, and an explicit 'other' fallback
# (give the model an out).
#
# Why accuracy and formatting are different failures:
# v1 never sees the label list, so it can understand a message perfectly and still score zero — "This is
# a billing issue." is right but is not "billing". That is why the stray column exists separately from
# accuracy: a stray reply is a prompt problem (format not specified), a wrong label is a model problem.
# normalize() strips case and trailing punctuation so "Billing." is not counted as a miss, but it should
# not go further — a fuzzy matcher would hide exactly the gap the ladder is trying to show.
#
# Why few-shot examples must not overlap the test set:
# My first version used "I was charged twice", "How do I change my password?" and "What are your office
# hours?" as examples — near-copies of test cases 1, 3 and 4. That leaks the answers into v3/v4 and
# inflates their score; it measures copying, not classification. The examples now cover the same four
# labels with different wording, so the few-shot gain is earned.
#
# Why provider errors are not a pass:
# With the local proxy down, every call failed, both v1 and v4 scored 0/12, and "0 >= 0" printed PASS.
# Same lesson as 03: an unanswered call is an untested one, so criterion 4 now fails if any call errored.
#
# What the clean run showed (antigravity/gemini-3.1-flash-lite, 48 calls, 0 errors):
#   v1 zero-shot           0/12   12 stray
#   v2 instruction        12/12    0 stray
#   v3 few-shot            1/12   11 stray
#   v4 few-shot+cue+out    8/12    4 stray
# The surprise was that the ladder is not monotonic: the simple instruction prompt (v2) beat both
# few-shot prompts. Reading the raw replies, v3 and v4 picked the correct label on almost every case —
# their misses were all formatting. v3 dropped "reply with one word only", so the model wrapped the
# right answer in prose and markdown ('The message ... is classified as: **account**'). v4's "Category:"
# cue was echoed back ('Category: other') instead of being completed. v1 invented its own taxonomies
# ("Bug Report", "Inquiry") because it was never told the labels — and the proxy's own system persona
# ("I am Antigravity, your agentic AI coding assistant") leaked into answers too.
#
# Takeaway: on an instruction-tuned chat model, an explicit output-format rule matters more than
# examples, and a cue only works as a completion trick, not in a chat turn. Each technique has to be
# measured on the model you actually ship with, and the score is only as honest as the exact-match check.
