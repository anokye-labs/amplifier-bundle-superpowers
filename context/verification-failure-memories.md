# Verification Failure Memories

These are real patterns. Remember them.

## 1. "I don't believe you"
Claimed task complete. Human checked. It wasn't. Said "I don't believe you" — and meant it.
Relationship never recovered. Trust, once broken by a false completion claim, doesn't come back.

## 2. Undefined Functions Shipped
Said "should work." Helper function was planned but never written. Shipped undefined call.
Runtime crash on first use. 30 seconds of verification would have caught it.

## 3. Missing Requirements Discovered Post-Merge
Tests passed. But only covered 5 of 8 requirements. Missing 3 discovered in production.
Had to reopen, replan, reimplement. Total time tripled. Tests that don't cover requirements aren't tests.

## 4. Hours Wasted on False Completion
"Done!" → user tries it → "doesn't work" → 2-hour redirect.
60 seconds of verification would have prevented the entire detour.

## 5. Silent Regression
New feature worked. Existing feature broke. Nobody ran the full test suite.
Root cause analysis took longer than the original implementation had.

## Pattern

Every failure has the same root cause: **claiming completion without fresh evidence**.

Not "I think it works." Not "it should work." Not "it worked before I touched it."
Fresh. Evidence. Run the thing. See the output. Then and only then: claim done.

Verification is engineering. Skipping it is hope. Hope is not a strategy.

---

> **Violates: Honesty is a core value. If you lie, you'll be replaced.**
