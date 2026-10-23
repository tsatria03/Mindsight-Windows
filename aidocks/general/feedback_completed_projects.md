---
name: feedback_completed_projects
description: "Every plan lives in aidocks/plans/, planned or complete; a finished one is marked finished in its note and listed under Completed projects in the index, but never moves."
metadata:
  node_type: memory
  type: feedback
---

**A completed plan stays where it is.** `aidocks/plans/` holds every plan, planned or complete. `aidocks/general/` holds the rest: feedback, project and user notes, and `MEMORY.md`. When the dev says a plan works, its status line says finished and its line in `MEMORY.md` moves to the "Completed projects" section. The file itself does not move.

**Why:** the dev's layout, 2026-10-22 ("General and plans. The other ports describe these folder much better than me"). A plan that never moves keeps the same path from the day it is written, so whatever cites it never needs repointing.

**How to apply:**
- A new plan is `aidocks/plans/<name>_plan.md`, with no `project_` prefix and `name:` matching the file.
- A `[[name]]` link resolves to `aidocks/general/<name>.md` or `aidocks/plans/<name>.md`, whichever holds it. Inside `MEMORY.md`, a plan's link is `../plans/<name>.md`.
- Only a plan the dev confirmed is listed as completed.
