---
name: feedback_use_github_usernames
description: "Name people by GitHub username (tsatria03), never real names, in commit authors, commit messages and everything committed to the repo; the original's own credits are cited as they are."
metadata:
  node_type: memory
  type: feedback
---

Identify people by their GitHub username, never their real name. The dev is **tsatria03**. This applies to commit authors and committers, commit messages, and everything committed to the repo, which is public on GitHub as `tsatria03/Mindsight-Windows`.

**Why:** the dev's standing rule, taken from the reference material in `user/` on 2026-10-22. The repo's git identity is `tsatria03`, with the noreply address `156674543+tsatria03@users.noreply.github.com`.

**How to apply:**
- Check `git config user.name` before committing. If it has drifted, pass `--author="tsatria03 <156674543+tsatria03@users.noreply.github.com>"`.
- Emails stay the GitHub noreply address.
- `LICENSE` reads "Copyright (c) 2026 tsatria03".
- The people credited by the original game itself, such as its creator Luke Charman and its cast, are part of the original and are cited from it ([[project_solo]]).
