---
name: feedback_progress_summary
description: "After each plan is finished, give the dev a brief summary of the whole port's progress as a percentage, using weights per plan agreed with the dev."
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
- **The weights** are not set yet. Propose them, rough and by effort, once the plan order is agreed ([[project_later_topics]]), and record them here when the dev agrees.
- If a plan turns out bigger or smaller than its weight, change the weights here, and say so in the summary.
- Plans added after the port is complete are reported as additions, not as a percentage.
