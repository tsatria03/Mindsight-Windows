---
name: feedback_grow_check_tools
description: "When a plan has a by-ear check tool in tests/interact/, start it in the first section that can be heard and grow it with every section; start it silently through its real entry point before handing it over."
metadata:
  node_type: memory
  type: feedback
---

**A plan's by-ear check tool grows section by section.**

**Why:** the dev's standing rule, taken from the reference material in `user/` on 2026-10-22. A tool written only in a plan's last section leaves every mandatory ear test until the end, so a problem is heard late, when it is harder to fix.

**How to apply:**
- At a plan's review ([[feedback_review_plan_sections]]), if it has a `tests/interact/` tool, plan it to start in the first section with anything to hear.
- **Each section adds that section's part to the tool.** The plan's last tool section only rounds it off.
- Each section's ear tests ([[feedback_say_ear_tests_ahead]]) name the tool's keys for that section.
- Each tool keeps its own save under `%APPDATA%\Mindsight\interact\` ([[feedback_test_tools_in_interact]]).
- **Before handing a tool over, start it silently through its real entry point:** `python tests\interact\<tool>.py` with speech and sound switched off, SDL's dummy video and audio drivers and a throwaway save folder, for a few seconds, then read its log. Driving the tool's pieces by hand is not enough, since a tool can fail on its own start-up order.
- **A tool never closes silently on an error.** It writes `crash.txt` and says why, as the game does.
