# Changelog

All notable changes to this project are documented here. This project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html) and the format of
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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

[1.1.0]: https://github.com/rudrasatani13/vibe-learn/releases/tag/v1.1.0
[1.0.0]: https://github.com/rudrasatani13/vibe-learn/releases/tag/v1.0.0
