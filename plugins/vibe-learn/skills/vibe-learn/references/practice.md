# Practice reference

Practice is optional, project-grounded, and bounded. Continue normal project work if the user skips.

## Challenge

`/vibe-learn challenge [concept|file|feature]` selects one current or due concept and gives a 5–20 minute isolated implementation or debugging task. State success criteria without revealing the solution. Use progressive hints: direction, pattern, then a partial scaffold. Avoid deployment, destructive operations, credentials, and broad rewrites. Evaluate behavior, reasoning, tests, and failure handling, then record `correct`, `partial`, or `wrong` through `scripts/progress.py result`.

## Teach-back

`/vibe-learn teach-back [file|feature|concept]` asks the user to explain the code in their own words. Evaluate purpose, flow, reasoning, failure modes, and trade-offs:

```text
Teach-back result
- Correctly understood: ...
- Missing or unclear: ...
- Correction: ...
- Stronger 30-second explanation: ...
- Progress result: correct | partial | wrong
```

Evaluate understanding, not vocabulary or confidence. A missing important failure mode is at least partial. Record the result against the relevant concept.

## Questions and feedback

Use recall, application, debugging-trap, compare, predict, and interview questions. Ask at most three, one in quiet mode. Quizzes are non-blocking and should not repeat when ignored. Correct answers get one deepening nugget; partial answers name what is right and fill the gap; wrong answers get a concise correction.

