---
name: feedback_git_commits
description: "One commit per change. Commit without asking; raise pushing only when a whole plan is finished and its docs are updated. 'Commit' means commit only; 'commit/push' means both. History rewrites need an explicit go-ahead. Use git commit -F with a message file, from Git Bash, and never hide git's errors."
metadata:
  node_type: memory
  type: feedback
---

**"Commit" means commit only; "commit/push" means commit and push.** Commits pile up locally by default, because the dev tests batches before pushing.

**Commit without asking; ask before pushing.** When a change is done, commit it straight away.

**Push once a whole plan is complete, after its docs are updated.** While a plan is being built, commit quietly and never bring up pushing, however many commits wait. When the plan is finished and every doc is brought up to date ([[feedback_docs_after_each_plan]]), say how many commits wait and ask to push. The dev can still ask for a push at any time.

**Make multiple commits when possible.** Split a batch into one commit per logical change.

**Fetching is fine without asking; bringing commits in is not.** Never pull, merge, rebase, cherry-pick or reset onto incoming commits without the dev's go-ahead.

**Rewriting published history needs an explicit go-ahead every time.** That covers force pushes, amending or rebasing pushed commits, and changing authors. When approved, push with `--force-with-lease`, and keep a backup branch, never pushed, until the dev says to delete it.

**Why:** the dev's standing rules, taken from the reference material in `user/` on 2026-10-22. The dev approves what goes into a commit, and history rewrites can lose work.

**How to apply:**
- Write the message to a file in the scratchpad with the Write tool, then run `git commit -F <file>`. Run git from Git Bash, the dev's standing shell preference for every project.
- Keep git commands plain and never send git's error output away; a failed commit must be visible.
- **One commit per fix or change.** Each commit carries its own todo, changelog, docs and memory lines.
- **Mark the work finished before committing it**, so the finished line goes in the same commit as the work.
- Stage files by name when the commit should hold exactly what the dev approved. Check `git status` first.
- Never commit work the dev made by hand (such as a reorganization of `game/`) without asking first.
- Format: a short summary line, a blank line, then a plain-text description wrapped at about 72 characters, ending with the Claude attribution line.
- The author is always tsatria03, with no `Co-authored-by:` lines for people ([[project_solo]], [[feedback_use_github_usernames]]).
- Never add large binaries casually; they stay in git history forever.
- After pushing, confirm with `git ls-remote origin refs/heads/main` and report the new commit.
- Committing isn't building or running; [[feedback_dont_run_or_build]] still applies.
