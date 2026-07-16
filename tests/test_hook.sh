#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOOK="$ROOT/plugins/vibe-learn/hooks/always-teach.sh"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
export HOME="$tmp/home" XDG_CACHE_HOME="$tmp/cache"
mkdir -p "$HOME"
payload='{"tool_input":{"file_path":"/tmp/project/app.ts","new_string":"function meaningfulChange() { return Promise.resolve(1); }"}}'
printf '%s' "$payload" | "$HOOK" | jq -e '.hookSpecificOutput.additionalContext | contains("always-teach")' >/dev/null
printf '%s' '{"tool_input":{"file_path":"/tmp/project/README.md","new_string":"A long documentation update that should remain silent."}}' | "$HOOK" | test ! -s /dev/stdin
printf '%s' '{"tool_input":{"file_path":"/tmp/project/app.ts","new_string":"function anotherMeaningfulChange() { return Promise.resolve(2); }"}}' | "$HOOK" | test ! -s /dev/stdin
echo "hook tests passed"
