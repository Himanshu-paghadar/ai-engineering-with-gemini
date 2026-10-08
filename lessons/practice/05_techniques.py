"""Lesson 05 practice: zero-shot vs chain-of-thought on multi-step word problems.

Works with any OpenAI-compatible provider. Set these in .env:
    OPENAI_BASE_URL=https://your-provider.com/v1
    OPENAI_API_KEY=your-provider-key
    BENCH_MODELS=model-a,model-b,model-c

    python lessons/practice/05_techniques.py
"""

import os
import re
import time

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(base_url=os.environ["OPENAI_BASE_URL"], api_key=os.environ["OPENAI_API_KEY"])
MODEL = os.environ.get("PROMPT_MODEL") or os.environ["BENCH_MODELS"].split(",")[0].strip()

# 8 word problems with answers worked out by hand before running anything.
PROBLEMS = [
    ("Alice has 5 apples, throws 3, gives 2 to Bob, and Bob gives one back. How many apples does Alice have?", 1),
    ("A baker makes 24 cupcakes, sells 15, bakes 12 more, then gives away 7. How many cupcakes are left?", 14),
    ("Tom has 3 boxes of 8 pencils. He gives away 5 pencils, then buys 2 more boxes. How many pencils does he have?", 35),
    ("A train has 120 passengers. At the first stop 40 get off and 20 get on. At the second stop half of them get off. How many are still on the train?", 50),
    ("Sara earns $15 an hour. She works 6 hours on Monday and 4 hours on Tuesday, then spends $45 on groceries. How many dollars does she have left?", 105),
    ("A parking lot has 4 rows of 12 spaces. 29 cars are parked, then 8 leave and 13 arrive. How many spaces are empty?", 14),
    ("Jake reads 12 pages a day for 5 days, then 20 pages a day for 3 days. His book has 150 pages. How many pages are left?", 30),
    ("A farmer has 17 sheep. All but 9 run away. He buys 4 more, then sells 3. How many sheep does he have?", 10),
]

COT_EXAMPLE = """Lisa has 7 apples, throws 1 apple, gives 4 apples to Bart and Bart gives one back:
7 - 1 = 6
6 - 4 = 2
2 + 1 = 3
ANSWER: 3

"""

STRATEGIES = {
    "A": lambda q: q,
    "B": lambda q: COT_EXAMPLE + q,
    "C": lambda q: q + "\nShow your steps, then give the final answer on the last line as `ANSWER: <n>`.",
}


def ask(prompt: str) -> tuple[str, float, int]:
    """One call -> (reply, seconds, output tokens). Returns an empty reply on error."""
    start = time.time()
    try:
        r = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
    except Exception as e:
        print(f"    [ERROR: {str(e).splitlines()[0][:80]}]")
        return "", time.time() - start, 0
    tokens = r.usage.completion_tokens if r.usage else 0
    return r.choices[0].message.content or "", time.time() - start, tokens


def extract(reply: str) -> int | None:
    """Prefer the `ANSWER: n` line; otherwise take the last integer in the reply."""
    reply = reply.replace(",", "")
    match = re.search(r"ANSWER:\s*\$?(-?\d+)", reply, re.IGNORECASE)
    if match:
        return int(match.group(1))
    numbers = re.findall(r"-?\d+", reply)
    return int(numbers[-1]) if numbers else None


print(f"model: {MODEL}\n")
results = {}

for name, build in STRATEGIES.items():
    correct, seconds, tokens = 0, 0.0, 0
    for question, expected in PROBLEMS:
        reply, secs, toks = ask(build(question))
        got = extract(reply)
        correct += got == expected
        seconds += secs
        tokens += toks
        print(f"  {name}  expected {expected:>4}  got {str(got):>4}  {'✓' if got == expected else '✗'}")
    results[name] = (correct, seconds / len(PROBLEMS), tokens / len(PROBLEMS))
    print()

print("-" * 50)
print(f"{'Strategy':<10} {'Accuracy':>10} {'Avg latency':>14} {'Avg tokens':>12}")
print("-" * 50)
for name, (correct, latency, tokens) in results.items():
    print(f"{name:<10} {f'{correct}/{len(PROBLEMS)}':>10} {latency:>13.2f}s {tokens:>12.0f}")
print("\n" + "  ".join(f"{name}: {r[0]}/{len(PROBLEMS)}" for name, r in results.items()))

# What I Learnt :
# Lesson 05: Advanced Prompting Techniques
# Same 8 hand-solved word problems, three prompts: A zero-shot, B one worked chain-of-thought example,
# C "show your steps + ANSWER: <n>". Answers are pulled from the ANSWER: line, else the last integer.
#
# What the run showed (antigravity/gemini-3.1-flash-lite, 24 calls, 0 errors):
#   A zero-shot      6/8   5.42s   214 tokens
#   B CoT example    8/8   4.50s    44 tokens
#   C steps+ANSWER   8/8   4.43s   168 tokens
#
# A's two "misses" were not wrong maths. Reading the raw replies, the model solved both correctly
# (14 and 105) and then tacked on an unrequested Python snippet — so "last integer" grabbed a 7 and a
# 2 from the code. The model reasons internally, so the arithmetic was never the problem; the
# unconstrained output format was. That is the real finding: zero-shot accuracy here is an
# extraction failure, not a reasoning failure.
#
# The surprise was cost. The lesson expects CoT to cost more, but B was the cheapest: the worked
# example showed a terse "a - b = c" format, and the model copied that format — 44 tokens vs 214 for
# zero-shot, which rambled into markdown and code. C asked for steps, so it paid for them (168).
#
# When is CoT worth it?
# - On a reasoning model, not for accuracy on simple arithmetic — it already gets these right.
# - It IS worth it for format control (B doubles as a few-shot example) and for auditability: C's
#   steps let you check *where* an answer went wrong, which a bare number never does.
# - It is worth it most for domain logic the model was never trained on, where showing the method is
#   the only way to teach it.
# - An explicit ANSWER: line is the cheapest robustness win — it made extraction exact for B and C.
