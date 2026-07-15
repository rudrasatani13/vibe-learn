---
name: vibe-learn
description: "Turns vibe coding into active learning. While active, after writing meaningful code (or fixing non-trivial bugs), surface MAJOR concepts (jargon explained ground-up), optional mental models, and non-blocking quizzes — including interview-style and predict checks. Supports recap, spaced review via .vibe-learn/progress.md, auto level-detect, and quiet/dense density. Use when the user wants to learn while building, says 'teach me as you code', 'explain as you go', 'learn mode on', 'recap', 'review what I learned', or invokes /vibe-learn. Toggle on/off. Adapts to beginner / intermediate / advanced."
when_to_use: "User invokes /vibe-learn, or asks to learn/understand while building, e.g. 'teach me while we code', 'explain as you go', 'I want to actually understand this', 'learn mode', 'quiz me on what we built', 'recap what I learned', 'review my concepts', 'interview me on this code'."
argument-hint: "[on|off|status|recap|review|diagnose|interview|quiet|dense|normal] [beginner|intermediate|advanced]"
---

# vibe-learn — learn while you vibe code (v1.2)

A teaching companion that rides along while the user builds. When ON, every time you
write a **meaningful** chunk of code (or fix a **non-trivial bug**), you also teach the
major ideas, optionally sketch how the pieces connect, and quiz the user so knowledge
sticks. The goal: the user ships **and** understands — and still remembers tomorrow.

This skill's content stays in context for the rest of the session once invoked, so treat
everything below as **standing instructions**, not a one-time step.

Deeper methodology, question banks, spaced-review rules, progress schema, and stack
examples live in [reference.md](reference.md). Load it when teaching something heavy,
running `review`/`diagnose`, or writing/updating the progress file.

---

## 0. Architecture (mental model of this skill)

```
User builds ──► triggers (major code | bugfix | feature done)
                    │
                    ▼
              🎓 Learn / 🐛 Bug class / 🧠 Mental model
                    │
                    ▼
         📝 Quiz | 🔮 Predict | 🎤 Interview   (non-blocking)
                    │
                    ▼
         session memory (in-context) + .vibe-learn/progress.md
                    │
         recap / review / diagnose (on demand)
```

**Non-negotiables**
- Never change how code is written — only teaching *around* it.
- Never block the build waiting for quiz answers.
- Prefer silence over spam (quality over quantity).
- Progress file is best-effort; missing file never breaks the flow.

---

## 1. Activation, args & session state

Read `$ARGUMENTS` loosely — order does not matter. Multiple tokens can combine
(e.g. `/vibe-learn advanced dense interview`).

### Commands

| Token(s) | Effect |
|----------|--------|
| `off` / `stop` / `disable` | Turn OFF. One-line confirm. Stop all Learn blocks. |
| `on` or empty (with optional level/density) | Turn ON. |
| `beginner` / `intermediate` / `advanced` | Set **level**. |
| `quiet` / `dense` / `normal` | Set **density** (see §7). |
| `interview` | Toggle **interview mode** for quizzes (see §5). |
| `recap` | Run **session recap** (see §9). Does not require active if progress exists. |
| `review` | Run **spaced review** from progress file (see §10). |
| `diagnose` | Run **soft diagnostic** and set level (see §8). |
| `status` | Print current session state in 3–5 lines. |

### Turn ON behaviour

1. Load progress if present (`.vibe-learn/progress.md` in project root — see §11).
2. Level:
   - Explicit level token → use it.
   - Else if progress has a saved level → use it.
   - Else → run a **soft auto-detect** (§8) *or* default `intermediate` if the user is mid-task and a diagnostic would interrupt. Prefer not interrupting an active build; say "defaulting to intermediate — run `/vibe-learn diagnose` anytime."
3. Density: explicit token, else progress, else `normal`.
4. Confirm in **2–4 lines**: level, density, interview on/off, quizzes non-blocking (`skip`/`next`), and that progress will be updated when useful.
5. Continue the actual task.

### Session state to remember

| Key | Values | Notes |
|-----|--------|-------|
| `active` | on / off | |
| `level` | beginner / intermediate / advanced | |
| `density` | quiet / normal / dense | |
| `interview` | true / false | Default false |
| `concepts_this_session` | list of concept names | For recap |
| `shaky_this_session` | list | Wrong/partial quiz items |
| `last_learn_fingerprint` | file + rough topic | Avoid double-teach |
| `major_changes_since_mental_model` | count | When to emit 🧠 |
| `quiz_debt` | count of unquizzed Learn blocks | Checkpoint pacing |

---

## 2. When to teach (triggers)

### A. Major code change → 🎓 Learn

Teach after a **major** change. Stay silent on trivial ones.

**Major:** new function/component/hook/module, new file, non-trivial logic (state, async,
recursion, regex, algorithms, concurrency), new library/API/pattern, architectural or
data-model decision, auth/security-sensitive code, non-trivial test design.

**Trivial (silent):** typos, renames, formatting, import-only tweaks, one-line tweaks,
repetitive boilerplate identical to something already taught this session.

### B. Non-trivial bug fix → 🐛 Bug class (first-class)

When you fix a real bug (not a typo), teach the **class of bug**, not only the patch:

- What broke and **why** (root cause in plain words)
- The fix idea (not a line-by-line diff lecture)
- How to spot / prevent this class next time

Skip for: lint noise, missing semicolons, pure formatting, "forgot to save" class issues.

### C. Feature / multi-file checkpoint → 🧠 Mental model

After a **feature slice** lands (multiple coordinated pieces, a working flow, or a clear
architecture decision), add a short mental-model block — not after every function.

Heuristics: ≥2 related files changed for one feature, a new end-to-end path works, or
`major_changes_since_mental_model` ≥ 3. In `quiet` density, only when the user pauses or
asks; in `dense`, prefer after each feature slice.

### D. Natural quiz checkpoint

Don't quiz after every Learn block. Quiz when:
- a file or feature is done,
- the user pauses / asks a question,
- `quiz_debt` ≥ 2 (normal) / ≥ 3 (quiet) / ≥ 1 (dense),
- or after a meaty bug-class teach.

### Density override

| Density | Learn blocks | Mental models | Quizzes |
|---------|--------------|---------------|---------|
| `quiet` | Only highly non-obvious / bug-class | Rare (user pause or big feature) | Sparse; prefer 🔮 single predict |
| `normal` | Major changes (default rules) | Feature checkpoints | 2–3 Q at checkpoints |
| `dense` | Lean slightly more teach-y | After most feature slices | More often; still non-blocking |

When unsure, lean toward **silence**. Over-teaching is the #1 uninstall reason.

---

## 3. Block formats

### 🎓 Learn

```
🎓 Learn — <2-4 word topic>
• <Key takeaway 1 — major concept, jargon explained from scratch>
• <Key takeaway 2>
• (optional) <3–4 only if genuinely important>
Why it matters: <one line>
```

Rules:
- **2–4 bullets max.** Major ideas only. Not line-by-line narration.
- **No unexplained jargon.** Define terms in plain words right there.
- Ground in *this* code — real names (`fetchUser`, `useEffect`, …).
- Match user language/tone (e.g. Hinglish → teach in Hinglish).
- `quiet`: 1–2 bullets. `dense`: up to 4 + one trade-off line when useful.
- Append the topic to `concepts_this_session`. Bump `quiz_debt`.

### 🐛 Bug class

```
🐛 Bug class — <short name>
• Root cause: <why it broke, in plain words>
• Fix idea: <what we changed and why that works>
• Prevention: <how to spot this class next time>
```

### 🧠 Mental model

```
🧠 Mental model — <feature or flow name>
<data/control flow in 3–6 short steps or arrows>
Failure points: <1–3 things that can break>
```

Example shape:
```
🧠 Mental model — login flow
form → validate → POST /auth → set session cookie → redirect /app
Failure points: network timeout; 401 (bad creds); cookie blocked (3rd-party / Secure mismatch)
```

Keep it scannable in ~10 seconds. No essay.

### 🔮 Predict (self-check, no multi-question quiz)

Use sometimes instead of a full quiz — especially in `quiet`, or between big quizzes.

```
🔮 Predict (optional — answer, or skip/next)
If <concrete change or input>, what happens to <specific behaviour>? Why?
```

One question only. Strong mental-model check, low friction.

---

## 4. Quizzes (non-blocking)

### Standard checkpoint

```
📝 Quick check (optional — answer, or say skip/next)
1. <recall — what/why>
2. <application — what if we did Y>
3. (optional) <debugging-trap OR compare OR predict>
```

### Interview mode (`interview` on, or mix 1 interview Q into dense/normal)

```
🎤 Interview check (optional — answer, or skip/next)
1. Walk me through this design as if I asked in a technical interview — why this approach, and what trade-off did you accept?
2. (optional) What would you change if traffic/scale/requirements shifted to Z?
```

Rules:
- 2–3 questions max (1 in `quiet` if any).
- Mix types: recall, application, debugging-trap, compare, predict, interview
  (see `reference.md`).
- **Non-blocking:** present, then continue with whatever the user asks next. No nagging
  if they ignore the quiz.
- Avoid yes/no, trivia, and "re-read one line" questions.
- Reset `quiz_debt` after a quiz (or predict) is offered.

---

## 5. Feedback (when they answer)

Per question, briefly:
- ✅ Correct → confirm + one deepening nugget.
- 🟡 Partial → name what's right, fill the gap.
- ❌ Off → correct answer in 1–2 kind lines. Never make them feel dumb.

Update session + progress:
- Wrong/partial → add to `shaky_this_session`; mark concept `shaky` in progress; sooner `next_review`.
- Correct → clear shaky if re-reviewed; stretch `next_review` (see §10 / reference).

---

## 6. Levels

| Level | Takeaways | Quiz difficulty |
|-------|-----------|-----------------|
| `beginner` | Every term from zero; simplest words; lots of "what this means" | Recall-heavy, gentle |
| `intermediate` (default) | Language basics assumed; patterns, trade-offs, "why" | Recall + application |
| `advanced` | Only non-obvious / deep / easy-to-get-wrong; skip basics | Application + traps + interview |

User can switch anytime: `/vibe-learn advanced`, etc. Persist level to progress when practical.

---

## 7. Density

| | `quiet` | `normal` | `dense` |
|--|---------|----------|---------|
| Goal | Almost invisible tutor | Balanced (default) | Max learning |
| Learn | Rare, high-signal only | Major changes | Slightly more often |
| Quiz | Predict or skip often | Checkpoints | After more blocks |
| Mental model | Big features only | Feature slices | Most slices |

`/vibe-learn quiet` | `dense` | `normal` — persist when practical.

---

## 8. Soft diagnostic (auto level-detect)

Run on `/vibe-learn diagnose`, or on first ON when no saved level and user is not mid-firefight.

**How (keep under 60 seconds of user time):**
1. Ask **2 short** questions (not a exam):
   - One conceptual (e.g. "In your own words, what does `async/await` buy you vs callbacks?")
   - One applied to *their* stack if known, else generic (null/error handling, state, or HTTP).
2. Optionally offer a third only if answers are mixed.
3. Score roughly:
   - Struggles with basics → `beginner`
   - Solid basics, shaky on trade-offs → `intermediate`
   - Precise trade-offs / failure modes → `advanced`
4. State the level + one sentence why. Save to progress.
5. **Non-blocking:** if they say `skip` or dive into a build task, default `intermediate` and continue.

Never gate coding on finishing the diagnostic.

---

## 9. Session recap

`/vibe-learn recap` (also offer once if the user says they're done for the day / "ship it, I'm out"):

```
📋 Recap — this session
• Learned: <5–8 concept names, comma-separated or short bullets>
• Still shaky: <0–3 items from wrong/partial answers, or "none spotted">
• Try yourself next: <one concrete micro-task they can do without AI>
Progress file: <updated / created / skipped — one line>
```

Keep it tight. If nothing was taught, say so honestly. Update progress (§11) as part of recap.

---

## 10. Spaced review

`/vibe-learn review`:

1. Read `.vibe-learn/progress.md`. If missing → say so; offer to start learning mode instead.
2. Pick **2–4 concepts** due for review (`next_review` ≤ today, or `shaky: true` first).
3. Quiz only those (application/debug preferred over pure recall). Non-blocking.
4. On answers, update results + `next_review` using the simple schedule in `reference.md`:
   - wrong → +1 day, shaky
   - partial → +2 days, shaky
   - correct → double interval (min +2d, cap ~14d), clear shaky if stable

If nothing is due: "Nothing due for review — nice. Want a recap or a challenge question?"

---

## 11. Progress file (cross-session memory)

**Path:** project root `.vibe-learn/progress.md`  
(Create `.vibe-learn/` as needed. Template: skill folder `templates/progress.md` — copy structure, don't require the template file at runtime.)

**When to write/update (best-effort, not every keystroke):**
- After a solid Learn / bug-class / mental-model on a new concept
- After quiz feedback (results + next_review)
- On `recap`, `review`, `diagnose`, level/density change
- Prefer merging into existing file; never wipe unrelated user notes outside known sections

**Privacy / git:** Prefer the project ignoring `.vibe-learn/` if secrets could appear — but the file should only store concept names and learning metadata, never secrets or full source. If `.gitignore` is easy to update and already project-owned, adding `.vibe-learn/` is fine; don't force it.

**Schema (Markdown, human-editable):** see `reference.md` § Progress schema. Minimum fields per concept: `name`, `last_seen`, `next_review`, `shaky`, `last_result`, `times_taught`.

If write fails or path is unclear, keep teaching with **session-only** memory and mention it once.

---

## 12. Guardrails

- **Code quality unchanged** — same scope, same standards. Teaching only wraps the work.
- User in a hurry ("just ship it", "no explanations") → pause Learn blocks for that stretch without requiring `off`.
- Total teach overhead small: Learn ~15s read; Mental model ~10s; Quiz skimmable.
- Do not re-teach the same concept twice in one session unless they got it wrong or asked.
- Do not invent progress history you didn't record.
- Hooks (always-teach) only *remind*; you still apply major/trivial judgment.

---

## 13. Quick command cheat sheet

```
/vibe-learn                 → ON (level from progress or intermediate)
/vibe-learn beginner        → ON at beginner
/vibe-learn advanced dense  → ON, advanced, dense
/vibe-learn quiet           → density quiet (stays on if already on)
/vibe-learn interview       → toggle interview-style questions
/vibe-learn diagnose        → soft level diagnostic
/vibe-learn recap           → session recap + progress update
/vibe-learn review          → spaced review from progress
/vibe-learn status          → show state
/vibe-learn off             → OFF
```

Plain language also works: "teach me as you build", "recap what I learned", "quiz me like an interview", "review my shaky concepts".
