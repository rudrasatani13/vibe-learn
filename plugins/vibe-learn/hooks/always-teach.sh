#!/usr/bin/env bash
# vibe-learn — always-teach hook (optional, opt-in / "hard mode")
#
# A PostToolUse hook for Write|Edit. After a source-code file is written or
# edited, it injects a factual reminder so Claude reliably adds a 🎓 Learn block
# for non-trivial changes — the deterministic counterpart to the soft, model-
# driven /vibe-learn skill. Pair it with the skill for the full teaching style.
#
# Contract (from Claude Code hooks):
#   - Reads the hook payload as JSON on STDIN.
#   - stdout must contain ONLY the JSON object below.
#   - Must exit 0 (JSON is ignored on non-zero exit).
#   - additionalContext is phrased as factual state, not an imperative command.
#
# Requires: jq. Without jq the hook does nothing (stays silent), never errors.

input=$(cat)

# What file did the tool touch? (Write/Edit both put it in tool_input.file_path)
file_path=$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty' 2>/dev/null)
[ -z "$file_path" ] && exit 0

# Only teach on source code; stay silent for docs, config, data, lockfiles, etc.
case "$file_path" in
  *.ts|*.tsx|*.js|*.jsx|*.mjs|*.cjs|*.py|*.go|*.rs|*.rb|*.java|*.kt|*.swift\
  |*.c|*.h|*.cpp|*.cc|*.hpp|*.cs|*.php|*.vue|*.svelte|*.scala|*.ex|*.exs|*.sh|*.sql) ;;
  *) exit 0 ;;
esac

base=$(basename "$file_path")

ctx="vibe-learn 'always-teach' mode is active. The user has opted in to learning while they build. \
Per the vibe-learn skill, a non-trivial change to ${base} is a good moment for a short 🎓 Learn block: \
2-4 key takeaways grounded in the code just written, with any jargon explained from scratch, then a brief \
optional non-blocking quiz at a natural checkpoint. Trivial edits (renames, formatting, imports, one-liners) \
do not need one."

# stdout: ONLY this JSON. Exit 0.
jq -nc --arg ctx "$ctx" \
  '{hookSpecificOutput: {hookEventName: "PostToolUse", additionalContext: $ctx}}'
exit 0
