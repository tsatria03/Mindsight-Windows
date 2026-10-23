# CLAUDE.md

This file guides Claude Code when it works in this repository. **It is a lean dispatcher.** It says what the project is and how it is laid out, then points to focused memory files (`[[name]]`) for the detail. When you start work in an area, read its linked memory first.

**Memory location:** all memory files (the `[[name]]` links and the `MEMORY.md` index) live in the repo's **`aidocks/`** folder, in two folders. **`aidocks/plans/`** holds every plan, planned or complete, as `aidocks/plans/<name>_plan.md` with no `project_` prefix; a finished plan stays there, marked finished. **`aidocks/general/`** holds every other note, as `aidocks/general/<name>.md`. A `[[name]]` link resolves to whichever of the two holds it ([[feedback_completed_projects]]). Read memory from there and write new or updated memory there, never to the `~/.claude` memory store. `aidocks/general/MEMORY.md` is the index, so add a one-line pointer there for every new memory. Keep this file under 40,000 characters and move detail into memory ([[feedback_memory_in_aidocks]]).

## What this is

A Windows port of **MiNDSiGHT** (`com.lukecharman.mindsight` 1.0.2, by Luke Charman), an iOS interactive audio adventure told through binaural recordings, no longer on the App Store. The player listens to the story and solves puzzles inside it by swiping up, down, left or right at the right moment; there are no choice menus. The port is for the keyboard and screen readers.

- **A solo project.** tsatria03 makes it alone ([[project_solo]]).
- **Windows only** ([[project_windows_only]]).
- **Python only**, with pygame for the window, the keys and all sound, and Prism and the NVDA client for speech. **No FMOD** and no OpenAL ([[project_python_only]]).
- **Developer tasks**, open and finished, are in [[project_dev_tasks]].
- **The story is code, not data.** The original's 56 scenes, what follows each, every puzzle's answer and every timing are hard-coded in its binary, so the port's scene table is written from it. What the bundle holds is in [[project_original_findings]]; how it plays, with addresses, is in [[project_original_behaviour]]. Questions waiting for later plans are in [[project_later_topics]].
- **Status:** plan 1, reading the original, is planned and waiting for its section review ([[reading_original_plan]]). The plans after it are proposed there. New work gets a plan of its own first ([[feedback_record_plans_first]]).

## Layout

- **`game/`**: the original app bundle, reorganized by the dev, and never written to by Claude. The binary is `game/MiNDSIGHT`. The 60 recordings are MP3, converted by the dev from the original's m4a, in `game/data/audio/story/sceen/` (45), `story/speech/` (10) and `system/misc/` (5); the original kept them in one flat folder. `game/data/text/MiNDSIGHT.pdf` is the creator's dissertation. Don't move, rename, convert or delete sound files unless the dev asks.
- **`mindsight/`**: the port's Python package, empty until plan 2.
- **`tests/case/`**: silent test scripts, to come. **`tests/interact/`**: tools played by ear, run by the dev, each with its own save under `%APPDATA%\Mindsight\interact\` ([[feedback_test_tools_in_interact]]). Run only the tests covering what changed, in the background, and the full suite only when the dev asks ([[feedback_dont_run_or_build]]).
- **`tools/`**: scripts for reading the original, to come in plan 1. **`analysis/`**: what they write, for reference.
- **`vendor/nvda/`**: `nvdaControllerClient64.dll` (x64) and its license.
- **`docks/`**: the documents a player reads: `readme.txt`, `changelog.txt` and `todo list.txt` ([[feedback_changelog]], [[feedback_todo_list_format]]). The readme describes only what works in the game now.
- **`README.md`**: the developer's guide. **`requirements.txt`**: `pygame`, `prismatoid` and `cryptography`. **`VERSION`**: the version, such as `26.10.22-1`.
- **`build/`** and **`dist/`**: build output, gitignored.
- **`user/`** is gitignored private reference material. Read it, but never edit it. Never name the dev's other games kept in it, in any of this repo's files ([[feedback_no_other_games]]).
- **`New File*.txt`** at the root is the dev's private scratchpad. It is gitignored; never read, edit, flag or delete it.

## Working here

- **The dev runs and builds, not Claude.** Ask before running the game or anything that plays sound or speaks ([[feedback_dont_run_or_build]]).
- **Before each plan,** review it section by section with the dev, and build only on their word ([[feedback_review_plan_sections]]). Within a plan, when the dev says a section's tests passed, mark and commit it, then build the next section without asking ([[feedback_next_section_on_pass]]).
- **Before each section,** list what the dev will test by ear, sound or speech, each test marked optional or mandatory ([[feedback_say_ear_tests_ahead]]). A plan's by-ear tool grows with each section ([[feedback_grow_check_tools]]).
- **After each plan,** bring every developer doc, `aidocks/` included, and every player doc up to date, give a brief progress summary ([[feedback_progress_summary]]), then ask to push ([[feedback_docs_after_each_plan]]).
- **Plans first:** an agreed plan goes into its own note in `aidocks/plans/` before any code, and is marked finished only once the dev says it works ([[feedback_record_plans_first]]).
- **Committing and pushing:** commit finished work without asking; push only once a whole plan is finished and its docs are updated; "commit/push" means both; history rewrites need a go-ahead ([[feedback_git_commits]]). Name people by GitHub username only ([[feedback_use_github_usernames]]).
- **Questions:** a question or correction from the dev is a check, answered in chat ([[feedback_questions_are_checks]]). Ask one question per reply, in plain text ([[feedback_one_question_at_a_time]], [[feedback_no_question_pickers]]).
- **Releases** are never recorded in notes or the README ([[feedback_no_release_records]]).
- **Menus:** Back is always the first row ([[feedback_back_first]]).
- **Who you're working with:** [[user_screen_reader]]. The dev uses NVDA, so prefer lists and short lines, never wide tables, and never make noise from tools.

`CLAUDE.md` and `aidocks/` are committed, not gitignored.
