---
name: feedback_docs_after_each_plan
description: "When a plan is finished, bring every doc up to date, developer and player alike: README.md, requirements.txt, tools/README.md, CLAUDE.md, every note and plan in aidocks/ with its index, and docks/readme.txt, changelog.txt and todo list.txt. Only then push."
metadata:
  node_type: memory
  type: feedback
---

**After each plan is finished, update every doc it touches, so none falls behind.**

**Why:** the dev's standing rule, taken from the reference material in `user/` on 2026-10-22, and asked for again after plan 1 (the dev, 2026-10-23: "Please also make a propper readme.md file for the project. Make sure to update it after each plan, same for the aidocks folder, the player facing docks folder when possible, and of course claude.md."). Docs left until the end fall behind and need a catch-up.

**`README.md` is a proper developer's guide,** written after plan 1 (2026-10-23): what the port is, status by plan, how it will play, requirements, the tools, the layout, credits and licences. As each plan lands it gains running, tests, the by-ear tools and building, as they come to exist.

**How to apply:**
- When the dev confirms a plan finished, before offering the next plan's review ([[feedback_review_plan_sections]]), go through:
  - **Developer docs:**
    - `README.md`: status by plan, requirements, running, options, files, tests, by-ear tools, layout, credits, licences.
    - `requirements.txt`, when a package is added.
    - `tools/README.md`, when a tool changed.
    - `CLAUDE.md`'s layout and status.
    - **All of `aidocks/`:** the finished plan's own note, every later plan its build changed, the project notes such as [[project_dev_tasks]] and [[project_later_topics]], and the `MEMORY.md` index.
  - **Player docs, in `docks/`:**
    - `readme.txt`: describes only what works in the game now, never what is planned.
    - `changelog.txt`: one line per noticeable change, if any were missed ([[feedback_changelog]]).
    - `todo list.txt`: move what the plan finished, and add what it left ([[feedback_todo_list_format]]).
- Say what changed in each doc, and commit them, one commit per kind of doc.
- Give the progress summary ([[feedback_progress_summary]]).
- **Then ask to push.** A plan is complete only once its docs are updated, and that is when its commits go up ([[feedback_git_commits]]).
- Keep the changelog and todo list up to date as changes land, too. This catch-up is a safety net, not a replacement.
- Never name another game from `user/` ([[feedback_no_other_games]]), and never record a release ([[feedback_no_release_records]]).
