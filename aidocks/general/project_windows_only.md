---
name: project_windows_only
description: "The port is strictly for Windows: no Linux or macOS builds, no GitHub Actions release workflow. Releases are built, zipped and uploaded from the dev's own machine."
metadata:
  node_type: memory
  type: project
---

**The port is strictly for Windows.** There are no Linux or macOS runs, builds or releases, and no GitHub Actions release workflow.

**Why:** the repo is Mindsight-Windows, and on 2026-10-22 the dev had the working rules taken from the reference material in the gitignored `user/` folder, which are Windows only.

**How to apply:**
- Write platform code for Windows only: `%APPDATA%\Mindsight` for the save, and the NVDA client and Prism for speech. No per-system tables, Linux libraries or macOS bundles.
- `compiler.py` and `releaser.py`, when they come, build and release from the dev's own machine, and need their own plan first ([[feedback_record_plans_first]]).
