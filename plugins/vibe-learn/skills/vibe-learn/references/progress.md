# Progress reference

`.vibe-learn/state.json` is canonical machine state. `.vibe-learn/progress.md` is generated for humans. Use `scripts/progress.py`; do not hand-edit generated Markdown during normal operation.

## Commands

```text
progress.py --project <path> init
progress.py --project <path> migrate --dry-run
progress.py --project <path> teach --concept <name> --stack <stack> [--note <one-line takeaway>]
progress.py --project <path> result --concept <slug> --outcome correct|partial|wrong
progress.py --project <path> mistake --class <class> --evidence <short safe note>
progress.py --project <path> profile --level <level> --density <density>
progress.py --project <path> due --limit 4
progress.py --project <path> recap
progress.py --project <path> stats
progress.py --project <path> export [--format anki|csv|md] [--shaky-only] [--out <file>]
progress.py --project <path> validate
progress.py --project <path> render
```

`--project` is a global option and must come before the subcommand.

The script validates dates and schema, normalizes concept slugs, keeps one session entry per day (capped at 60 days), keeps at most three notes per concept, rejects bounded evidence that resembles secrets, and writes JSON atomically. A failed read never overwrites malformed state; continue with session-only learning.

## Review schedule

First teach and wrong: one day. Partial: two days. Correct: double the previous interval, minimum two and maximum fourteen days. Wrong and partial are shaky; a stable correct review clears shaky.

## Stats and streaks

`stats` returns concept, mastered (not shaky with an interval of at least eight days), shaky, due, and quiz counts plus `streak_days` (consecutive learning days ending today or yesterday), `learning_days`, `last_session`, `days_since_last_session`, and the top recurring mistake. The generated report includes the same summary.

## Export

`export` writes to `.vibe-learn/export/flashcards.<ext>` unless `--out` is given. `anki` is a tab-separated file with Anki import headers (front, back, tags); `csv` includes schedule columns; `md` uses collapsible answers. The card back is the concept's notes, or an explain-it-yourself prompt when there are none. Shaky concepts come first and are tagged `shaky`. Exports contain only stored concept metadata.

## Mistake taxonomy

`missing-error-handling`, `null-state-assumption`, `async-race-or-stale-result`, `missing-cleanup`, `sequential-work-that-can-be-parallel`, `authorization-vs-authentication-confusion`, `implementation-coupled-test`, `unvalidated-input`, `state-ownership-confusion`, `unsafe-secret-boundary`.

Record only concrete evidence in user-written code or answers. First occurrence stays private; mention the pattern at two occurrences; prioritize a challenge or review item at three.

## Migration

When a V1.2 `progress.md` exists without `state.json`, run dry-run first. A successful migration backs up the Markdown as `progress.v1.2.backup.md`, writes JSON atomically, and regenerates the report. Unknown Markdown is ignored; malformed recognized values fail safely.

