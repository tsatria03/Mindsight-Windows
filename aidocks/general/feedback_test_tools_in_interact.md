---
name: feedback_test_tools_in_interact
description: "A tool for trying something by ear, such as a scene chooser, goes in tests/interact/ as its own script with its own save, never into the game's menus."
metadata:
  node_type: memory
  type: feedback
---

A tool the dev uses to try a feature by ear goes in `tests/interact/` as its own script, never into the game itself or its menus.

**Why:** the dev's standing rule, taken from the reference material in `user/` on 2026-10-22.

**Every tool quits with Escape or Alt+F4, and W and S work as Up and Down** (the dev, 2026-10-23, at plan 3's review: "I want alt f4 and or escape to quit for all interact tests. Also w/s for up/down arrows. So the user can press either or."):
- Escape quits, as does Alt+F4 or closing the window. No tool uses Escape for anything else, so `foundation_check.py` reports the game's pause from Enter and P, while Escape quits it.
- Wherever a tool uses Up or Down, W or S does the same, so S is never given another job in a tool.

**How to apply:** when the dev asks for a way to test or try something, such as jumping to any scene or puzzle, make a `tests/interact/` script with its own save folder under `%APPDATA%\Mindsight\interact\`, so the game's own save is untouched ([[feedback_dont_run_or_build]]).
