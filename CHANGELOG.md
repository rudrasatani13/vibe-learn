# Changelog

All notable changes to this project are documented here. This project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html) and the format of
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.3.0] - 2026-07-17

### Added
- Deterministic `.vibe-learn/state.json` progress engine with atomic writes, validation, rendering, and V1.2 migration backups.
- Bounded `/vibe-learn challenge` and `/vibe-learn teach-back` workflows.
- Recurring-mistake taxonomy with concrete evidence and recurrence counts.
- Split teaching, practice, and progress references for progressive disclosure.
- State-engine and hook regression tests.

### Changed
- Claude Code is now stated as the primary supported runtime.
- Plugin and marketplace metadata updated to 1.3.0.

## [1.2.0] - 2026-07-16

### Added
- **Session recap** via `/vibe-learn recap` — learned concepts, shaky items, one micro-task.
- **Cross-session progress** at `.vibe-learn/progress.md` with concept metadata and session log.
- **Spaced review** via `/vibe-learn review` (due + shaky concepts, simple interval schedule).
- **Soft diagnostic** via `/vibe-learn diagnose` for level auto-detect.
- **Density modes**: `quiet` / `normal` / `dense`.
- **Interview mode** toggle (`/vibe-learn interview`) for design-walkthrough questions.
- **Predict checks** (🔮) — single non-blocking mental-model questions.
- **Bug-class blocks** (🐛) as a first-class trigger after non-trivial fixes.
- **Mental-model blocks** (🧠) at feature / multi-file checkpoints.
- **`/vibe-learn status`** for session state.
- Progress **template** at `skills/vibe-learn/templates/progress.md`.
- Multi-stack worked examples in `reference.md` (React, Next, FastAPI, SQL, auth, Go, tests, …).
- Diagnostic question bank and spaced-review rules in `reference.md`.

### Changed
- `SKILL.md` restructured as v1.2 architecture: triggers, formats, modes, progress, guardrails.
- Always-teach hook **debounced** (~45s per file), skips tiny payloads when length known,
  expands language extensions, stronger major-vs-trivial reminder text.
- README documents full command surface, architecture diagram, and progress file.
- Plugin version bumped to **1.2.0**.

### Fixed
- Hook spam on multi-step edits of the same file (debounce + tiny-write skip).

## [1.1.0] - 2026-06-24

### Added
- **Always-teach mode** (optional, opt-in): a `PostToolUse` hook
  (`plugins/vibe-learn/hooks/always-teach.sh`) that deterministically reminds
  Claude to add a 🎓 Learn block after every source-code edit. Filters to code
  files, stays silent on docs/config/data, and is **not** auto-enabled — the
  default experience stays non-blocking. Requires `jq`.
- Illustrative example graphic (`assets/example.svg`) shown in the README.

## [1.0.0] - 2026-06-24

### Added
- Initial release of the **vibe-learn** Claude Code skill.
- Toggle-based learn mode: `/vibe-learn`, `/vibe-learn off`, and level switches
  (`beginner` / `intermediate` / `advanced`).
- 🎓 Learn blocks after *major* code changes — 2–4 key takeaways with jargon
  explained ground-up; silent on trivial edits.
- 📝 Non-blocking quizzes at natural checkpoints (recall / application /
  debugging-trap questions) with kind, per-question feedback.
- Language matching (e.g. teaches in Hinglish when the user writes Hinglish).
- `reference.md` with teaching methodology, question-design patterns, level
  calibration, and a full worked example.
- Plugin marketplace packaging for one-command install + auto-updates.

[1.3.0]: https://github.com/rudrasatani13/vibe-learn/releases/tag/v1.3.0
[1.2.0]: https://github.com/rudrasatani13/vibe-learn/releases/tag/v1.2.0
[1.1.0]: https://github.com/rudrasatani13/vibe-learn/releases/tag/v1.1.0
[1.0.0]: https://github.com/rudrasatani13/vibe-learn/releases/tag/v1.0.0
