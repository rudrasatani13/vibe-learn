<div align="center">

# 🎓 vibe-learn

**Learn while you vibe code.**

A [Claude Code](https://claude.com/claude-code) skill that turns "the AI wrote it, I don't know how" into "I shipped it *and* I understand it." After meaningful code (or a real bug fix), Claude surfaces **major concepts**, optional **mental models**, and **non-blocking quizzes** — with recap, spaced review, and cross-session progress so it still sticks tomorrow.

[![Claude Code Skill](https://img.shields.io/badge/Claude%20Code-Skill-6C3EF5)](https://code.claude.com/docs/en/skills)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![Version](https://img.shields.io/badge/version-1.3.0-blue.svg)](./CHANGELOG.md)

<br/>

<img src="assets/example.svg" alt="vibe-learn example — a Learn block with key takeaways, followed by a Quick check quiz" width="100%">

</div>

---

## The problem

Vibe coding is fast, but it has a cost: you end up with a working app you can't explain. The code becomes a black box, and you don't grow as a developer. The usual fixes are all-or-nothing — either you stop and read docs (kills the flow), or you ship blind (kills the learning).

**vibe-learn** sits in the middle. It rides *alongside* the build. Claude Code is the primary supported runtime; the package intentionally uses Claude Code skill and hook extensions:

- After a **meaningful** change → short **🎓 Learn** block (2–4 takeaways, jargon from scratch).
- After a **real bug fix** → **🐛 Bug class** (root cause, fix idea, prevention).
- After a **feature slice** → **🧠 Mental model** (how the pieces connect + failure points).
- At natural pauses → **📝 Quick check**, **🔮 Predict**, or **🎤 Interview** questions — all **non-blocking**.
- Across sessions → canonical **`.vibe-learn/state.json`**, generated **`.vibe-learn/progress.md`**, and **`/vibe-learn review`** (spaced repetition).
- When ready to practice → bounded **`/vibe-learn challenge`** and explain-it-yourself **`/vibe-learn teach-back`**.
- End of day → **`/vibe-learn recap`**.

It changes *nothing* about how the code itself gets written. It only adds teaching around it.

---

## Architecture (v1.3)

```
┌─────────────────────────────────────────────────────────────┐
│                     Session (in context)                    │
│  active · level · density · interview · concepts · shaky    │
└────────────────────────────┬────────────────────────────────┘
                             │
     triggers: major code │ bug fix │ feature checkpoint
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
   🎓 Learn            🐛 Bug class        🧠 Mental model
         │                   │                   │
         └───────────────────┼───────────────────┘
                             ▼
              📝 Quiz · 🔮 Predict · 🎤 Interview
                     (non-blocking)
                             │
                             ▼
              .vibe-learn/state.json  ←── canonical state
              .vibe-learn/progress.md ←── generated report
```

| Layer | Role |
| :--- | :--- |
| **SKILL.md** | Standing behaviour: when to teach, block formats, modes, guardrails |
| **references/** | Targeted teaching, practice, and progress guidance |
| **scripts/progress.py** | Validates, migrates, updates, and renders state atomically |
| **templates/** | Starter state and legacy-compatible report structure |
| **always-teach.sh** | Optional hook: deterministic reminder after source edits (debounced) |

---

## Demo

You ask Claude to write a data fetcher. Alongside the code, you get:

> 🎓 **Learn — async/await + error handling**  
> • `await` pauses inside this function until `fetch` resolves, so `res` is the real response, not a pending Promise.  
> • `res.ok` is `false` for 4xx/5xx. `fetch` does **not** throw on those — only on network failure — so we throw manually to catch bad statuses.  
> **Why it matters:** forgetting the `res.ok` check is the classic bug where a 404 silently becomes "undefined data" downstream.
>
> 📝 **Quick check** (optional — answer, or say skip/next)  
> 1. Why doesn't `fetch` throw on a 404 by itself?  
> 2. The caller does `const u = await getUser(5)` — what happens to them if the user doesn't exist?  
> 3. How would you add a timeout so this can't hang forever?

Answer in your own words → instant, kind feedback. End the day with `/vibe-learn recap`. Tomorrow: `/vibe-learn review` resurfaces shaky concepts.

---

## Install

> Requires Claude Code. New to skills? See the [official skills docs](https://code.claude.com/docs/en/skills).

### Option A — Copy install (recommended, clean `/vibe-learn` command)

```bash
git clone https://github.com/rudrasatani13/vibe-learn.git
cp -r vibe-learn/plugins/vibe-learn/skills/vibe-learn ~/.claude/skills/
```

One-liner:

```bash
git clone --depth 1 https://github.com/rudrasatani13/vibe-learn.git /tmp/vibe-learn && \
  cp -r /tmp/vibe-learn/plugins/vibe-learn/skills/vibe-learn ~/.claude/skills/ && \
  rm -rf /tmp/vibe-learn && echo "✅ vibe-learn installed — type /vibe-learn in Claude Code"
```

### Option B — Plugin marketplace

```text
/plugin marketplace add rudrasatani13/vibe-learn
/plugin install vibe-learn@vibe-learn
```

Command is namespaced as `/vibe-learn:vibe-learn` with this method. Update with `/plugin marketplace update vibe-learn`.

---

## Usage

| Command | What it does |
| :--- | :--- |
| `/vibe-learn` | Learn mode **ON** (level from progress, else intermediate) |
| `/vibe-learn beginner` \| `intermediate` \| `advanced` | ON at that level |
| `/vibe-learn quiet` \| `normal` \| `dense` | Teaching intensity |
| `/vibe-learn interview` | Toggle interview-style design questions |
| `/vibe-learn diagnose` | Soft 2-question level diagnostic |
| `/vibe-learn recap` | Session recap + progress update |
| `/vibe-learn review` | Spaced review of due / shaky concepts |
| `/vibe-learn status` | Show current mode state |
| `/vibe-learn challenge` | Bounded project-grounded practice task |
| `/vibe-learn teach-back` | Explain a feature in your own words and get evaluated |
| `/vibe-learn off` | Turn off |

Plain language works too: *"teach me as you build"*, *"recap what I learned"*, *"quiz me like an interview"*, *"review my shaky concepts"*.

### Levels

| Level | Takeaways | Quiz |
| :--- | :--- | :--- |
| `beginner` | Every term from zero | Recall-heavy, gentle |
| `intermediate` *(default)* | Patterns, trade-offs, why | Recall + application |
| `advanced` | Non-obvious / easy-to-get-wrong | Application + traps + interview |

### Density

| Density | Feel |
| :--- | :--- |
| `quiet` | Almost invisible — high-signal only, prefer single 🔮 Predict |
| `normal` | Balanced (default) |
| `dense` | More blocks and checkpoints; still non-blocking |

It **matches your language** — Hinglish in, Hinglish lessons out.

---

## Progress file (cross-session memory)

When useful, the skill creates/updates:

```text
.vibe-learn/state.json
.vibe-learn/progress.md
```

Stores concept names, quiz results, review dates, mistake evidence, and profile settings — **not** secrets, prompts, or source. Add `.vibe-learn/` to `.gitignore` if progress is personal. V1.2 Markdown migrates with a backup.

---

## Always-teach mode (optional, deterministic)

The skill is *soft* — Claude decides when a change is worth teaching. For a **guaranteed reminder** after source edits, install the hook. v1.3 keeps it optional, debounces same-file spam (~45s), and skips tiny payloads when length is known.

**Setup** (requires [`jq`](https://jqlang.github.io/jq/)):

```bash
mkdir -p ~/.claude/hooks
cp vibe-learn/plugins/vibe-learn/hooks/always-teach.sh ~/.claude/hooks/vibe-learn-always-teach.sh
chmod +x ~/.claude/hooks/vibe-learn-always-teach.sh
```

```jsonc
// ~/.claude/settings.json  (merge into existing "hooks")
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "$HOME/.claude/hooks/vibe-learn-always-teach.sh",
            "timeout": 15
          }
        ]
      }
    ]
  }
}
```

Not auto-enabled — default stays non-blocking.

---

## How it works

vibe-learn is a Claude Code skill. Once invoked, instructions stay in context for the session. After *major* changes Claude teaches; after trivial edits it stays silent. Teaching is **ground-up** (no undefined jargon). Challenges and teach-back add deliberate practice; progress + review close the loop across days.

```
vibe-learn/
├── .claude-plugin/
│   └── marketplace.json
├── plugins/
│   └── vibe-learn/
│       ├── .claude-plugin/
│       │   └── plugin.json
│       ├── hooks/
│       │   └── always-teach.sh      # optional, debounced (v1.3)
│       └── skills/
│           └── vibe-learn/
│               ├── SKILL.md         # behaviour, modes, guardrails
│               ├── references/      # teaching, practice, and progress guidance
│               ├── scripts/
│               │   └── progress.py  # deterministic state CLI
│               └── templates/
│                   ├── state.json
│                   └── progress.md
├── assets/
│   └── example.svg
├── README.md
├── LICENSE
└── CHANGELOG.md
```

---

## Roadmap

- [x] Optional `PostToolUse` always-teach hook *(v1.1)*
- [x] Session recap *(v1.2)*
- [x] Cross-session progress + spaced review *(v1.2)*
- [x] Soft diagnostic / level detect *(v1.2)*
- [x] Mental models, bug-class, interview & predict *(v1.2)*
- [x] Density controls + hook debounce *(v1.2)*
- [x] Multi-stack worked examples *(v1.2)*
- [x] Deterministic state and V1.2 migration *(v1.3)*
- [x] Bounded challenge and teach-back workflows *(v1.3)*
- [x] Recurring-mistake taxonomy and compact learning map *(v1.3)*
- [ ] Optional export of progress for Anki / flashcards
- [ ] Multi-agent / Cursor-oriented packaging notes

Ideas and PRs welcome.

---

## Contributing

This is a small skill package — contributions are easy. Open an issue or PR. If you change behaviour, update `SKILL.md`, the targeted files in `references/`, and the matching README section. To test: run `python3 -m unittest discover -s tests` and copy into `~/.claude/skills/` for a real session.

## License

[MIT](./LICENSE) © 2026 Rudra Satani

<div align="center">
<sub>Built with Claude Code. If vibe-learn taught you something, a ⭐ helps others find it.</sub>
</div>
