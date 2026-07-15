# vibe-learn — reference (v1.2)

Deeper material for the `vibe-learn` skill. Load when sharpening questions, teaching
something heavy, running `review` / `diagnose` / `recap`, or writing `.vibe-learn/progress.md`.

`SKILL.md` is the source of truth for behaviour. This file makes the teaching better.

---

## 1. Teaching methodology — ground-up / recursive

**Never leave jargon undefined.** When a takeaway uses a term the user may not know,
explain that term — and if *that* explanation needs another term, explain it too — until
you hit ground the user already stands on. Go one or two levels deep, not infinitely.

Good teaching here is:

1. **Anchored to the real code.** Use actual names (`fetchUser`, `debounce`, the
   `useEffect` you just wrote) — not generic `foo`/`bar`.
2. **Major-ideas-first.** 1–3 things that, if remembered alone, unlock the code.
3. **The "why", not just the "what".** "We `await` so the next line sees data, not a
   pending Promise" beats "this awaits the promise."
4. **Honest about trade-offs.** One line on when someone might do it differently.
5. **Failure-aware.** What breaks if inputs are null, network fails, or order flips.

---

## 2. Question-design patterns

Mix types. Don't ask three of the same kind.

| Type | Tests | Example shape |
|------|-------|---------------|
| **Recall** | Did the concept land? | "What does `useMemo` save us from re-doing here?" |
| **Application** | Can they transfer it? | "If this list had 10,000 rows, what would you change and why?" |
| **Debugging-trap** | Failure modes | "What happens if `user` is `null` when this runs?" |
| **Compare** | Trade-offs | "Why a `Map` here instead of a plain object?" |
| **Predict** | Mental model | "What does this log on the *second* render?" |
| **Interview** | Explainability | "Walk me through why you structured it this way and what you'd change at 10× traffic." |

Avoid: yes/no, verbatim re-read trivia, pure syntax "gotchas", trick questions.

### Density mapping

- `quiet` → prefer one **Predict** over a 3-question quiz.
- `normal` → 2–3 mixed.
- `dense` → include at least one application/trap; interview mode adds design narrative.

---

## 3. Level calibration (same feature, three depths)

Feature: debounced search input.

### beginner

> 🎓 Learn — Debouncing  
> • "Debounce" = wait until the user **stops** typing before doing work. Here we wait
>   300ms after the last keystroke before calling the API.  
> • Without it, every letter fires a network request — slow and wasteful.  
> Why it matters: fewer requests, smoother typing.
>
> 📝 1. In your own words, what does debouncing prevent?

### intermediate

> 🎓 Learn — Debounce + cleanup  
> • `setTimeout` is cancelled on each keystroke (`clearTimeout` in cleanup), so only the
>   last timer survives — that's the debounce.  
> • Cleanup runs before the next effect **and** on unmount, preventing a stale call after
>   the component is gone.  
> Why it matters: standard React pattern for "react to input, but not too often".
>
> 📝 1. Why does cleanup matter on unmount specifically?  
> 2. What breaks if we forget the dependency array?

### advanced

> 🎓 Learn — Debounce edge cases  
> • Closure captures `query` per render; cleanup closes over the *previous* timeout id.  
> • A `useRef` for the timer survives renders without re-subscribing the effect —
>   trade-off: less idiomatic, but avoids re-creating timers on unrelated re-renders.  
> Why it matters: naive versions leak calls under fast unmount/remount.
>
> 📝 1. Where does this leak a request, and how would `AbortController` help?  
> 2. Effect-based vs ref-based debounce — when does the difference actually bite?

---

## 4. Full worked example (intermediate) — fetch helper

```js
async function getUser(id) {
  const res = await fetch(`/api/users/${id}`);
  if (!res.ok) throw new Error(`User ${id} failed: ${res.status}`);
  return res.json();
}
```

> 🎓 Learn — async/await + error handling  
> • `await` pauses inside this function until `fetch` resolves, so `res` is the real
>   response, not a pending Promise. The function still returns a Promise to *its* caller.  
> • `res.ok` is `false` for 4xx/5xx. `fetch` does **not** throw on those — only on network
>   failure — so we throw manually so callers handle bad statuses.  
> Why it matters: forgetting `res.ok` is the classic bug where a 404 becomes "undefined data".
>
> 📝 Quick check (optional — answer, or say skip/next)  
> 1. Why doesn't `fetch` throw on a 404 by itself?  
> 2. Caller does `const u = await getUser(5)` — what happens if the user doesn't exist?  
> 3. How would you add a timeout so this can't hang forever?

Feedback if they answer Q2 with "it returns null":

> 🟡 Close — it doesn't return null, it **throws**. The caller needs `try/catch` (or
> `.catch`) or the error bubbles. Returning null would need an explicit
> `if (!res.ok) return null`.

---

## 5. Bug-class worked example

Bug: React effect fetches on every keystroke; race shows stale results.

> 🐛 Bug class — async race / stale response  
> • Root cause: older requests can finish **after** newer ones; last-write-wins on
>   `setState` is not guaranteed by network order.  
> • Fix idea: abort previous request (`AbortController`) or ignore results whose request
>   id is not the latest.  
> • Prevention: any async effect driven by rapidly changing input needs cancellation or
>   a "latest only" guard.
>
> 🔮 Predict: User types "a" then "ab" quickly. Request for "a" returns last. What does the
> UI show without a guard?

---

## 6. Mental-model worked example

> 🧠 Mental model — checkout  
> cart page → `createPaymentIntent` → Stripe confirm → webhook `payment_succeeded` → mark order paid  
> Failure points: client confirms but webhook delayed (UI must not assume paid); double-submit;
> partial refund vs full cancel.

---

## 7. Interview-style examples

- "Explain this data flow to a senior engineer in 60 seconds. What trade-off did you accept?"
- "If this endpoint got 100× traffic, what breaks first and what would you change?"
- "How would you test this without hitting the real API?"
- "What invariants must stay true for this module to be correct?"

Score generously on structure (problem → approach → trade-off → risks), not buzzwords.

---

## 8. Soft diagnostic bank

Pick **2** (stack-aware when possible). Do not run all.

**Universal**
1. "In your own words: what is the difference between an error you can recover from and one that should crash the request?"
2. "What does 'state' mean in a UI — and when does local component state become a problem?"

**JS/TS**
3. "`const` vs `let` vs immutability of objects — what can still change?"
4. "Why might `await` inside a loop be slow, and what is one alternative?"

**React**
5. "When does a component re-render, and how do you stop *unnecessary* re-renders?"
6. "What is a stale closure, in plain words?"

**Python**
7. "What does `async def` change about how the function runs?"
8. "Mutable default argument (`def f(x=[])`) — why is it a trap?"

**SQL / data**
9. "INNER JOIN vs LEFT JOIN — when does a row disappear?"
10. "What does an index speed up, and what does it cost?"

**Scoring**
- Vague / confuses basics → beginner  
- Clear basics, thin on trade-offs → intermediate  
- Names failure modes and trade-offs unprompted → advanced  

---

## 9. Progress schema & spaced review

### File location

`.vibe-learn/progress.md` at the **project root**.

Template ships at `templates/progress.md` in this skill folder.

### Concept block (canonical)

```markdown
### async-res-ok
- name: fetch res.ok vs throw
- stack: js/fetch
- first_seen: 2026-07-16
- last_seen: 2026-07-16
- times_taught: 1
- times_quizzed: 1
- last_result: partial
- next_review: 2026-07-18
- interval_days: 2
- shaky: true
- notes: thought 404 returned null
```

### Meta block

```markdown
## Meta
- version: 1.2
- level: intermediate
- density: normal
- interview: false
- last_session: 2026-07-16
- notes: ""
```

### Spaced schedule (simple, not full SM-2)

| Outcome | `interval_days` | `next_review` | `shaky` |
|---------|-----------------|---------------|---------|
| first teach (no quiz yet) | 1 | today + 1 | false |
| wrong | 1 | today + 1 | true |
| partial | 2 | today + 2 | true |
| correct | max(2, previous×2), cap 14 | today + interval | false if was re-review and correct |

On each teach of an existing concept: bump `times_taught`, set `last_seen` = today.  
On each quiz: bump `times_quizzed`, set `last_result`.

### Review selection order

1. `shaky: true` (oldest `next_review` first)  
2. `next_review` ≤ today  
3. Cap 2–4 concepts per `/vibe-learn review`  

### Session log

Keep newest ~10 lines:

```markdown
## Session log
- 2026-07-16: async/await, res.ok, AbortController; shaky: res.ok
```

### Writing hygiene

- Merge; don't clobber unknown sections.  
- Never store API keys, `.env`, or large code.  
- Slug = short kebab-case from the concept name.

---

## 10. Stack mini-examples (teach shapes)

Use as *patterns*, not scripts to paste when irrelevant.

### React / TypeScript — `useEffect` data load

Focus: dependency array, cleanup/abort, loading vs error vs data states.  
Mental model: mount/deps change → set loading → fetch → set data/error → unmount aborts.

### Next.js App Router — server vs client

Focus: where code runs, what can touch `window`, why secrets stay server-side.  
Trap: leaking server env into a client bundle.

### Python / FastAPI — dependency + status codes

Focus: dependency injection for db/auth; `HTTPException` vs unhandled 500; Pydantic validation errors as 422.

### SQL — N+1 query

Focus: loop of queries vs join/prefetch; when an index helps `WHERE`/`JOIN`.  
Predict: 100 posts × 1 author query each = 101 queries.

### Auth — sessions vs JWT (high level)

Focus: where identity lives; revocation story; XSS vs CSRF angles in one line each.  
Interview: "How would you force-logout a stolen session?"

### Git (when you teach a non-trivial recovery)

Focus: working tree vs index vs HEAD; why `restore` ≠ `reset` for beginners.  
Only when the session actually used the concept.

### Tests — assertion on behaviour

Focus: test the contract users rely on, not private implementation details.  
Trap: snapshot-everything that breaks on CSS class renames.

### Go — error wrapping

Focus: `fmt.Errorf("...: %w", err)`; caller checks with `errors.Is` / `errors.As`.  
Why it matters: stack of context without losing the root sentinel.

### Rust (advanced only) — ownership at API boundary

Focus: why a function takes `&str` vs `String`; when clone is the honest cost.  
Skip for beginners unless the code forced it.

---

## 11. Recap quality bar

A good recap is:

- **Specific** (real concepts from *this* session, not "you learned React")  
- **Honest** about shaky items (or "none spotted")  
- **Actionable** with one micro-task: e.g. "Rewrite `getUser` with a 3s timeout using `AbortController` without looking at the solution."

A bad recap: generic praise, five paragraphs, no next step.

---

## 12. Always-teach hook (companion)

Optional `PostToolUse` hook (`hooks/always-teach.sh`) injects a reminder after source
edits. It is **not** a second teacher — you still apply major/trivial rules, density, and
dedupe. v1.2 debounces same-file spam (~45s) and skips tiny payloads when length is known.

---

## 13. Anti-patterns (do not do these)

- Lecturing after every import sort  
- Blocking the build on unanswered quizzes  
- Re-teaching the same intermediate concept three times in one hour because they didn't quiz  
- Writing a progress novel after each keystroke  
- Using interview mode to humiliate ("wrong, you'd fail")  
- Inventing concepts in recap that were never taught  
- Explaining the skill's internals instead of the user's code  

---

## 14. Version map

| Version | Highlights |
|---------|------------|
| 1.0 | Learn blocks, non-blocking quizzes, levels |
| 1.1 | Optional always-teach hook |
| 1.2 | Recap, progress file, spaced review, diagnose, density, interview & predict, bug-class + mental-model first-class, hook debounce, stack examples |
