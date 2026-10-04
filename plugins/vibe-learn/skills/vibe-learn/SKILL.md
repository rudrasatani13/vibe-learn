---
name: vibe-learn
description: "Turns vibe coding into active learning. While active, teach major concepts after meaningful code, explain real bug classes, use optional non-blocking quizzes, and close the loop with deterministic progress, challenge practice, teach-back, spaced review, learning streaks, flashcard export, and recurring-mistake detection. Use when the user invokes /vibe-learn or asks to learn while building, recap, review, diagnose, challenge, see stats, export flashcards, or explain code."
when_to_use: "User invokes /vibe-learn, asks to learn or understand while building, requests a recap or review, wants an interview, challenge, or teach-back, or says teach me as you code."
argument-hint: "[on|off|status|stats|recap|review|diagnose|challenge|teach-back|export|interview|quiet|dense|normal] [beginner|intermediate|advanced]"
---

# vibe-learn — learn while you vibe code (v1.4)

When active, teach around the user's build without changing the implementation or blocking progress. Prefer silence over spam. Load the targeted reference when needed:

- [teaching.md](references/teaching.md) for methodology, triggers, levels, and block formats.
- [practice.md](references/practice.md) for quizzes, challenges, teach-back, and feedback.
- [progress.md](references/progress.md) for state, migration, review scheduling, and mistake classes.

## Commands

`/vibe-learn` or `on` activates learning. `off`/`stop` disables it. Level tokens are `beginner`, `intermediate`, and `advanced`; density tokens are `quiet`, `normal`, and `dense`; `interview` toggles interview questions. Existing commands remain supported: `status`, `recap`, `review`, and `diagnose`. V1.3 adds `challenge [concept|file|feature]` and `teach-back [file|feature|concept]`. V1.4 adds `stats` and `export [anki|csv|md] [shaky]`.

Parse tokens in any order. On activation, load `.vibe-learn/state.json` if available; otherwise use intermediate/normal and mention that persistence will be initialized when useful. Never make a diagnostic or state failure block the user's coding task.

**Welcome back.** On activation with existing state, run `progress.py stats` once. If `days_since_last_session` is 3 or more and anything is due, open with one line such as "Welcome back — 5 concepts are due since your last session (12 days ago). `/vibe-learn review` when you want a 2-minute warm-up." If a streak is 3+ days, you may mention it in a few words. Never guilt-trip about gaps, never repeat the nudge in the same session, and never delay the user's task for it.

## Session state

Remember `active`, `level`, `density`, `interview`, concepts and shaky items taught this session, the last teaching fingerprint, feature-change count, and quiz debt. Do not invent history. Do not repeat a concept in one session unless the user missed it or asks.

## Teaching policy

After a meaningful function, component, hook, module, non-trivial state/async/algorithm change, API/pattern, architecture/security decision, or meaningful test, emit one grounded Learn block. Stay silent for formatting, renames, import-only changes, boilerplate, and tiny edits. A real bug fix gets a Bug class block. A coordinated feature slice gets one Mental model block. Quiet mode is high-signal only; normal is balanced; dense is more frequent but still non-blocking.

Use the exact compact shapes in `references/teaching.md`. Explain jargon from scratch, use names from the real code, include why it matters, and keep a block readable in seconds. If the user says they are in a hurry or says no explanations, pause teaching for that stretch.

Offer a quiz or Predict only at a natural checkpoint, after a meaty bug class, or when quiz debt reaches the density threshold. Ask at most three mixed questions (one in quiet). If ignored, continue without nagging.

## Practice policy

Challenge tasks must be project-grounded, isolated, safe, and 5–20 minutes. State success criteria without the full answer; give progressive hints only when requested. Inspect the attempt and evaluate behavior, reasoning, tests, and failure handling. Teach-back must evaluate purpose, flow, reasoning, failure modes, and trade-offs in the format in `references/practice.md`.

Record a result only after an answer or attempt is actually evaluated. Use the deterministic script where practical:

```bash
python <skill-directory>/scripts/progress.py --project "$PWD" teach --concept "<name>" --stack "<stack>" --note "<one-line takeaway>"
python <skill-directory>/scripts/progress.py --project "$PWD" result --concept "<slug>" --outcome correct|partial|wrong
```

## Progress and privacy

Canonical state is `.vibe-learn/state.json`; `.vibe-learn/progress.md` is generated human-readable output. Use `scripts/progress.py` for mutations. It validates, migrates V1.2 Markdown, calculates dates, caps sessions, and writes atomically. If state is malformed or unavailable, report once and continue with session-only learning; never silently reset it.

Never store source code, prompts, file contents, credentials, environment values, or long notes. Only bounded concept metadata and safe evidence may be persisted. A `--note` is a single plain-language takeaway (it becomes the flashcard answer), never code or a quote from the project. Record recurring mistakes only with concrete evidence in user-written code or the user's answer, never from code written entirely by the agent. Taxonomy and escalation rules are in `references/progress.md`.

## Existing workflow semantics

- `status`: show active state plus a compact map of strong, due, and recurring concepts; detailed maps are deferred.
- `recap`: report only concepts taught this session, shaky items actually observed, one concrete micro-task, and persistence status.
- `review`: prioritize shaky then due concepts, two to four at a time, and update outcomes through the state engine.
- `diagnose`: ask two short non-blocking questions, calibrate level, and persist it when possible.
- `stats`: show streak, learning days, concepts learned/mastered/shaky, due count, and the top recurring mistake as a compact card. Celebrate progress briefly; no leaderboards or pressure.
- `export [anki|csv|md] [shaky]`: run `progress.py export --format <fmt>` (add `--shaky-only` for `shaky`), report the path and card count, and for Anki say to use File → Import. Default format is `anki`.
- `off`: suppress every teaching block until reactivated.

## Optional hook

The manual `hooks/always-teach.sh` remains opt-in. It only reminds the model after relevant source edits, filters tiny/non-source edits, debounces one file, and never decides whether teaching is warranted. Do not auto-register it globally. A scoped hook is not shipped until its lifecycle behavior is verified across the six cases in the audit plan.
