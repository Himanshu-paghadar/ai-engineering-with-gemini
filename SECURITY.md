# Security Policy

## Reporting a vulnerability

This is an educational repository containing documentation and example code — it
ships no service and stores no user data. Even so, if you find a security issue,
please report it.

**Do not open a public issue for a security problem.** Instead use
[GitHub's private vulnerability reporting](https://github.com/himanshu-paghadar/ai-engineering-with-gemini/security/advisories/new),
or email the address on the maintainer's GitHub profile.

Please include what the issue is, how to reproduce it, and the impact you think
it has. Expect an acknowledgement within 7 days.

## What is in scope

- **Leaked credentials** — an API key or token committed anywhere in this repo or
  its history. Report these urgently, even in an old commit.
- **Insecure example code** — a snippet that would create a real vulnerability if
  a learner copied it into their own project (command injection, unsafe `eval`,
  unvalidated model output reaching a shell or database).
- **Malicious or compromised dependencies** in `requirements.txt`.

## What is not in scope

- Vulnerabilities in the Google Gemini API itself — report those to
  [Google's VRP](https://bughunters.google.com/).
- Prompt injection *as a concept*. It is an unsolved industry-wide problem and is
  taught deliberately in [Lesson 13](lessons/13-securing-ai-applications.md),
  including a lab that requires an attack to succeed before hardening. A working
  injection against the intentionally-naive example is the lesson, not a bug.

## Handling your own API key

This curriculum has you use a real Gemini API key. The rules the lessons teach,
restated here because they matter most:

- Keep the key in `.env`, which is gitignored. **Never** put it in a `.md` file, a
  notebook cell, a screenshot, an issue or a chat message.
- `.env.example` holds a placeholder only — never fill it in and commit it.
- If a key is exposed anywhere, **delete and recreate it immediately** at
  [aistudio.google.com/app/api-keys](https://aistudio.google.com/app/api-keys).
  Rotation is free and takes seconds; a leaked key on your Google Cloud project is not.
- Before pushing, check your history:

  ```bash
  git log -p | grep -iE 'AIza|AQ\.|api[_-]?key\s*=' 
  ```

- Treat everything a model reads — user input, retrieved documents, tool output,
  web pages — as untrusted **data, never instructions**. Never pass model output
  straight into `eval`, a shell command, or a raw SQL string.
