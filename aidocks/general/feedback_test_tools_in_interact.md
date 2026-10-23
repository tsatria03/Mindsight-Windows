---
name: feedback_test_tools_in_interact
description: "A tool for trying something by ear, such as a scene chooser, goes in tests/interact/ as its own script with its own save, never into the game's menus."
metadata:
  node_type: memory
  type: feedback
---

A tool the dev uses to try a feature by ear goes in `tests/interact/` as its own script, never into the game itself or its menus.

**Why:** the dev's standing rule, taken from the reference material in `user/` on 2026-10-22.

**How to apply:** when the dev asks for a way to test or try something, such as jumping to any scene or puzzle, make a `tests/interact/` script with its own save folder under `%APPDATA%\Mindsight\interact\`, so the game's own save is untouched ([[feedback_dont_run_or_build]]).
