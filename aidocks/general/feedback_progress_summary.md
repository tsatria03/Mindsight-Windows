---
name: feedback_progress_summary
description: "After each plan is finished, give the dev a brief summary of the whole port's progress as a percentage, by the agreed weights per plan: 15, 15, 20, 25, 10 and 15."
metadata:
  node_type: memory
  type: feedback
---

**After each plan, give a brief summary of the overall progress.** The percentage is of the whole port, from reading the original to a released game, never of one plan.

**Why:** the dev's standing rule, taken from the reference material in `user/` on 2026-10-22. It lets the dev see how far the port has come, and what is left, at each milestone.

**How to apply:**
- Give it with the end-of-plan docs pass ([[feedback_docs_after_each_plan]]), before asking to push.
- **Keep it brief:**
  - the overall percentage
  - what the finished plan added to it
  - what is left, plan by plan
  - anything that moved the estimate
- **The weights,** proposed after plan 1 and agreed after plan 2 (the dev, 2026-10-23: "I like your proposed weights"), rough and by effort:
  - plan 1, reading the original: 15
  - plan 2, the foundation: 15
  - plan 3, the audio: 20
  - plan 4, the story engine: 25
  - plan 5, the menus and saves: 10
  - plan 6, building and releasing: 15
- **Progress so far:**
  - plan 1 finished: about 15 percent (2026-10-23).
  - plan 2 finished: about 30 percent (2026-10-23). It came in at its weight: smaller than first planned, with speech, Settings, the key binder and the volumes dropped, but with foundation_check.py and the message boxes added.
- If a plan turns out bigger or smaller than its weight, change the weights here, and say so in the summary.
- Plans added after the port is complete are reported as additions, not as a percentage.
