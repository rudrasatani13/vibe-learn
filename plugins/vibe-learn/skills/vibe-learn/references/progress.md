# Progress reference

`.vibe-learn/state.json` is canonical machine state. `.vibe-learn/progress.md` is generated for humans. Use `scripts/progress.py`; do not hand-edit generated Markdown during normal operation.

## Commands

```text
progress.py init --project <path>
progress.py migrate --project <path> --dry-run
progress.py teach --project <path> --concept <name> --stack <stack>
progress.py result --project <path> --concept <slug> --outcome correct|partial|wrong
progress.py mistake --project <path> --class <class> --evidence <short safe note>
progress.py profile --project <path> --level <level> --density <density>
progress.py due --project <path> --limit 4
progress.py recap --project <path>
progress.py validate --project <path>
progress.py render --project <path>
```

The script validates dates and schema, normalizes concept slugs, caps history at 20 sessions, rejects bounded evidence that resembles secrets, and writes JSON atomically. A failed read never overwrites malformed state; continue with session-only learning.

## Review schedule

First teach and wrong: one day. Partial: two days. Correct: double the previous interval, minimum two and maximum fourteen days. Wrong and partial are shaky; a stable correct review clears shaky.

## Mistake taxonomy

`missing-error-handling`, `null-state-assumption`, `async-race-or-stale-result`, `missing-cleanup`, `sequential-work-that-can-be-parallel`, `authorization-vs-authentication-confusion`, `implementation-coupled-test`, `unvalidated-input`, `state-ownership-confusion`, `unsafe-secret-boundary`.

Record only concrete evidence in user-written code or answers. First occurrence stays private; mention the pattern at two occurrences; prioritize a challenge or review item at three.

## Migration

When a V1.2 `progress.md` exists without `state.json`, run dry-run first. A successful migration backs up the Markdown as `progress.v1.2.backup.md`, writes JSON atomically, and regenerates the report. Unknown Markdown is ignored; malformed recognized values fail safely.

