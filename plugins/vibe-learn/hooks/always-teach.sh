#!/usr/bin/env bash
# vibe-learn — always-teach hook (optional, opt-in / "hard mode") v1.2
#
# PostToolUse hook for Write|Edit. After a source-code file is written or
# edited, injects a factual reminder so the model reliably considers a 🎓 Learn
# block — the deterministic counterpart to the soft /vibe-learn skill.
#
# v1.2 polish:
#   - Still filters to source extensions only.
#   - Debounces: same file within ~45s does not re-remind (avoids spam on
#     multi-step edits of one file).
#   - Skips obviously tiny writes when new_string / content length is known
#     and very small (pure one-liners / empty).
#   - Reminder text stresses major-vs-trivial judgment (skill is source of truth).
#
# Contract (Claude Code hooks):
#   - Reads hook payload JSON on STDIN.
#   - stdout must contain ONLY the JSON object below.
#   - Must exit 0 (JSON ignored on non-zero).
#   - additionalContext is factual state, not an imperative command.
#
# Requires: jq. Without jq the hook stays silent (exit 0), never errors.

input=$(cat)

# Tool + path
file_path=$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty' 2>/dev/null)
[ -z "$file_path" ] && exit 0

# Only source code; stay silent for docs, config, data, lockfiles, etc.
case "$file_path" in
  *.ts|*.tsx|*.js|*.jsx|*.mjs|*.cjs|*.py|*.go|*.rs|*.rb|*.java|*.kt|*.swift\
  |*.c|*.h|*.cpp|*.cc|*.hpp|*.cs|*.php|*.vue|*.svelte|*.scala|*.ex|*.exs|*.sh|*.sql\
  |*.dart|*.lua|*.r|*.R|*.jl|*.zig|*.toml) ;;
  *) exit 0 ;;
esac

# Skip lockfiles / generated-ish names even if extension matched
base=$(basename "$file_path")
case "$base" in
  package-lock.json|pnpm-lock.yaml|yarn.lock|Cargo.lock|go.sum|composer.lock|poetry.lock)
    exit 0 ;;
esac

# Tiny-edit skip when we can see the written payload length
# (Write often has .content; Edit often has .new_string)
content_len=$(printf '%s' "$input" | jq -r '
  (.tool_input.content // .tool_input.new_string // "") | length
' 2>/dev/null)
# If length is known and very small, likely trivial — stay silent
if [ -n "$content_len" ] && [ "$content_len" -gt 0 ] 2>/dev/null; then
  if [ "$content_len" -lt 40 ]; then
    exit 0
  fi
fi

# Debounce: same file within 45s
state_dir="${XDG_CACHE_HOME:-$HOME/.cache}/vibe-learn"
mkdir -p "$state_dir" 2>/dev/null || true
# Hash path to a safe filename
path_hash=$(printf '%s' "$file_path" | shasum 2>/dev/null | awk '{print $1}')
[ -z "$path_hash" ] && path_hash=$(printf '%s' "$file_path" | cksum | awk '{print $1}')
state_file="$state_dir/last-$path_hash"
now=$(date +%s)
if [ -f "$state_file" ]; then
  last=$(cat "$state_file" 2>/dev/null || echo 0)
  if [ -n "$last" ] && [ "$last" -gt 0 ] 2>/dev/null; then
    delta=$((now - last))
    if [ "$delta" -lt 45 ]; then
      exit 0
    fi
  fi
fi
printf '%s' "$now" > "$state_file" 2>/dev/null || true

ctx="vibe-learn 'always-teach' mode is active (v1.2). The user opted in to learning while they build. \
A change to ${base} was just written. Per the vibe-learn skill: if this change is non-trivial \
(new logic, API/pattern, architecture, or a real bug fix), add a short 🎓 Learn block \
(2-4 takeaways grounded in the code, jargon from scratch) or a 🐛 Bug class block for fixes; \
at a feature checkpoint consider a 🧠 Mental model; at a natural pause offer a non-blocking \
quiz / 🔮 Predict. Trivial edits (renames, formatting, imports-only, one-liners) need nothing. \
Update .vibe-learn/progress.md when a solid new concept lands. Density/level rules from the skill still apply."

jq -nc --arg ctx "$ctx" \
  '{hookSpecificOutput: {hookEventName: "PostToolUse", additionalContext: $ctx}}'
exit 0
