# Teaching reference

Use ground-up explanations anchored to the user's real code. Explain one to three major ideas, define jargon in place, state why the idea matters, and name an important failure mode or trade-off. Match the user's language.

## Trigger judgment

Teach after new functions, components, hooks, modules, non-trivial state or async logic, new APIs or patterns, architecture decisions, security-sensitive code, and meaningful tests. Stay silent for formatting, renames, import-only changes, and tiny edits. A real bug fix gets a Bug class block; a coordinated feature gets one Mental model block.

## Output shapes

```text
🎓 Learn — <topic>
• <major idea, defined from scratch and grounded in this code>
• <major idea>
Why it matters: <one line>
```

```text
🐛 Bug class — <name>
• Root cause: <why it broke>
• Fix idea: <why the fix works>
• Prevention: <how to spot it next time>
```

```text
🧠 Mental model — <flow>
<3–6 short steps or arrows>
Failure points: <one to three risks>
```

Keep blocks scannable. Quiet mode is one or two bullets; normal mode is two to four; dense mode may include one trade-off. Never let teaching block the user's build.

## Levels

- Beginner: define every term and favor recall.
- Intermediate: explain patterns, reasons, trade-offs, and failure modes.
- Advanced: focus on non-obvious behavior, traps, invariants, and scale.

