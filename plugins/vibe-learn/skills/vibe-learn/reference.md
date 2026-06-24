# vibe-learn — reference

Deeper material for the `vibe-learn` skill. Load when sharpening questions or teaching
something conceptually heavy. `SKILL.md` is the source of truth for behavior; this file
makes the teaching better.

## Teaching methodology — ground-up / recursive

The core principle: **never leave jargon undefined.** When a takeaway uses a term the
user may not know, explain that term — and if *that* explanation needs another term,
explain it too, until you hit ground the user already stands on. Go one or two levels
deep, not infinitely; stop when the explanation rests on everyday concepts.

Good teaching here is:
1. **Anchored to the real code.** Use the actual names (`fetchUser`, `debounce`, the
   `useEffect` you just wrote) — not generic `foo`/`bar`. The user remembers *their* code.
2. **Major-ideas-first.** Pick the 1-3 things that, if the user only remembered those,
   they'd understand the code. Skip the obvious.
3. **The "why", not just the "what".** "We `await` here so the next line sees the data,
   not a pending Promise" beats "this awaits the promise."
4. **Honest about trade-offs.** If there's a reason someone might do it differently, name
   it in one line. That's where real understanding lives.

## Question-design patterns

Mix these. Don't ask three of the same type.

| Type | Tests | Example shape |
|------|-------|---------------|
| **Recall** | Did the concept land? | "What does `useMemo` save us from re-doing here?" |
| **Application** | Can they transfer it? | "If this list had 10,000 rows, what would you change and why?" |
| **Debugging-trap** | Do they see failure modes? | "What happens if `user` is `null` when this runs? How would you guard it?" |
| **Compare** | Do they get the trade-off? | "Why a `Map` here instead of a plain object?" |
| **Predict** | Mental model check | "What does this log on the *second* render?" |

Avoid: yes/no questions, questions answerable by re-reading one line verbatim, and
trick questions about syntax trivia. Aim for questions whose answer proves understanding.

## Level calibration (concrete)

Same code — a debounced search input — taught three ways:

**beginner**
> 🎓 Learn — Debouncing
> • "Debounce" = wait until the user stops typing before doing work. Here we wait 300ms
>   after the last keystroke before calling the API.
> • Without it, every single letter fires a network request — slow and wasteful.
> Why it matters: fewer requests, smoother typing.
>
> 📝 1. In your own words, what does debouncing prevent?

**intermediate**
> 🎓 Learn — Debounce + cleanup
> • The `setTimeout` is cancelled on each keystroke (`clearTimeout` in the cleanup), so
>   only the last one survives — that's the debounce.
> • The cleanup function runs before the next effect AND on unmount, preventing a stale
>   call firing after the component is gone.
> Why it matters: this is the standard React pattern for any "react to input, but not too often".
>
> 📝 1. Why does the cleanup matter on unmount specifically?
> 2. What would break if we forgot the dependency array?

**advanced**
> 🎓 Learn — Debounce edge cases
> • Closure captures `query` per render; the cleanup closes over the *previous* timeout id,
>   which is why the cancel targets the right pending call.
> • A `useRef` for the timer would survive renders without re-subscribing the effect —
>   trade-off: less idiomatic, but avoids re-creating the timeout on unrelated re-renders.
> Why it matters: the naive version leaks calls under fast unmount/remount.
>
> 📝 1. Where does this leak a request, and how would `AbortController` help?
> 2. Effect-based vs ref-based debounce — when does the difference actually bite?

## Full worked example (intermediate)

Code just written:

```js
async function getUser(id) {
  const res = await fetch(`/api/users/${id}`);
  if (!res.ok) throw new Error(`User ${id} failed: ${res.status}`);
  return res.json();
}
```

Ideal Learn block:

> 🎓 Learn — async/await + error handling
> • `await` pauses inside this function until `fetch` resolves, so `res` is the real
>   response, not a pending Promise. The function returns a Promise to *its* caller.
> • `res.ok` is `false` for 4xx/5xx. `fetch` does NOT throw on those — only on network
>   failure — so we throw manually to make callers handle bad statuses.
> Why it matters: forgetting the `res.ok` check is the classic bug where a 404 silently
> becomes "undefined data" downstream.

Then at the checkpoint:

> 📝 Quick check (optional — answer, or say skip/next)
> 1. Why doesn't `fetch` throw on a 404 by itself?
> 2. The caller does `const u = await getUser(5)` — what happens to them if the user doesn't exist?
> 3. How would you add a timeout so this can't hang forever?

Feedback example, if they answer Q2 with "it returns null":

> 🟡 Close — it doesn't return null, it **throws** (our `throw new Error`). So the caller
> needs a `try/catch` (or `.catch`) or the error bubbles up. Returning null would need an
> explicit `if (!res.ok) return null` instead.
