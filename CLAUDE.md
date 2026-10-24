# CLAUDE.md

This file guides Claude Code when it works in this repository. **It is a lean dispatcher.** It says what the project is and how it is laid out, then points to focused memory files (`[[name]]`) for the detail. When you start work in an area, read its linked memory first.

**Memory location:** all memory files (the `[[name]]` links and the `MEMORY.md` index) live in the repo's **`aidocks/`** folder, in two folders. **`aidocks/plans/`** holds every plan, planned or complete, as `aidocks/plans/<name>_plan.md` with no `project_` prefix; a finished plan stays there, marked finished. **`aidocks/general/`** holds every other note, as `aidocks/general/<name>.md`. A `[[name]]` link resolves to whichever of the two holds it ([[feedback_completed_projects]]). Read memory from there and write new or updated memory there, never to the `~/.claude` memory store. `aidocks/general/MEMORY.md` is the index, so add a one-line pointer there for every new memory. Keep this file under 40,000 characters and move detail into memory ([[feedback_memory_in_aidocks]]).

## What this is

A Windows port of **MiNDSiGHT** (`com.lukecharman.mindsight` 1.0.2, by Luke Charman), an iOS interactive audio adventure told through binaural recordings, no longer on the App Store. The player listens to the story and solves puzzles inside it by swiping up, down, left or right at the right moment; there are no choice menus. The port is played from the keyboard, entirely by ear, as the original was.

- **A solo project.** tsatria03 makes it alone ([[project_solo]]).
- **Windows only** ([[project_windows_only]]).
- **Python only**, with pygame for the window, the keys and all sound. **No FMOD**, no OpenAL, and **no speech**: the original is entirely self-voiced, so the game has no Prism, no NVDA client, no Settings screen, no key binder and no volume controls. Errors go to a Windows message box, which screen readers read by themselves ([[project_python_only]], [[foundation_plan]]).
- **The keys are fixed:** the arrows or W, A, S and D for the four swipes, and Escape, Enter or P for the double tap, which pauses and resumes ([[foundation_plan]]).
- **Developer tasks**, open and finished, are in [[project_dev_tasks]].
- **The story is code, not data.** The original's 56 scenes, what follows each, every puzzle's answer and every timing are hard-coded in its binary, so the port's scene table is written from it. What the bundle holds is in [[project_original_findings]]; how it plays, with addresses, is in [[project_original_behaviour]]. Questions waiting for later plans are in [[project_later_topics]].
- **Status:** all six plans are written, every question answered ([[feedback_all_plans_first]]). Plan 1, reading the original, is finished ([[reading_original_plan]]), which also lists the plans after it; plan 2, the foundation, is finished ([[foundation_plan]]); plan 3, the audio, is finished ([[audio_plan]]); plan 4, the story engine, is finished, and the whole game plays ([[story_engine_plan]]); plan 5, the menus and saves, is finished, saving at the checkpoints, with Continue and the dissertation ([[menus_saves_plan]]); next is plan 6, building and releasing, the last, written, with no section review, built only on the dev's word ([[build_release_plan]]). New work gets a plan of its own first ([[feedback_record_plans_first]]).

## Layout

- **`game/`**: the original app bundle, reorganized by the dev, and never written to by Claude. The binary is `game/MiNDSIGHT`. The 60 recordings are MP3, converted by the dev from the original's m4a, in `game/data/audio/story/sceen/` (45), `story/speech/` (10) and `system/misc/` (5); the original kept them in one flat folder. `game/data/text/MiNDSIGHT.pdf` is the creator's dissertation. Don't move, rename, convert or delete sound files unless the dev asks.
- **`Mindsight.py`**: the entry script, with `--debug`, `--scene N`, `-v` and `--exit-after`, the logs, `crash.txt` and the error message boxes ([[foundation_plan]]).
- **`mindsight/`**: the port's Python package.
  - `paths.py`: the recordings in `game/data/audio`, `VERSION`, and the save folder, `%APPDATA%\Mindsight` or `MINDSIGHT_USER_DIR`.
  - `app.py`: the main loop at 60 frames a second, handing each key to the top screen as a gesture, an ignored key or another key.
  - `platform/`: `msgbox.py`, the error message box; `runloop.py`, the timer loop with hold and resume; `keys.py`, the fixed keys; `audio.py`, the mixer and the original's three players (the scene, Solved at 0.2, the pause clips) with the buzz, and losing focus; `buzz.py`, the buzz made in memory, 160 Hz, sine, 20 percent; `mp3.py`, an MP3's length from its frames ([[audio_plan]]); `jsonfile.py`, the safe JSON files, with a `.bak` and a `.damaged` ([[menus_saves_plan]]).
  - `ui/screens.py`: the screen stack.
  - `game/`: `recordings.py`, each recording found by the binary's name; `scenes.py`, the whole scene table, which `tools/scenes.py` checks against the binary value by value; `story.py`, the rules as plain state, returning effects; `story_screen.py`, the story as a screen, the menus included, with pause and losing focus ([[story_engine_plan]]), saving, Continue and the dissertation; `progress.py`, the save, one checkpoint scene in `saves/progress.json` ([[menus_saves_plan]]).
- **`tests/case/`**: silent test scripts, each importing `_quiet.py` first, which keeps it silent, off the real save and free of message boxes; `tests/suite.py` runs them all, or some by name, into the gitignored `tests/results/`. **`tests/interact/`**: tools played by ear, run by the dev, each with its own save under `%APPDATA%\Mindsight\interact\` and speaking through `_nvda.py`, built on `_tool.py`, and quitting with Escape or Alt+F4: `foundation_check.py` tries the message boxes, the keys, the timer loop and focus; `audio_check.py` plays any scene, from a typed point, with Solved, the buzz and its level, WelcomeBack and focus; `buzz_check.py` tunes the buzz's frequency and shape; `story_check.py` plays the story from any scene, in debug mode, with T, I and L; `menu_check.py` plays from the main menu with its own save, with T to save at a checkpoint, C to clear and I to say it ([[feedback_test_tools_in_interact]]). Run only the tests covering what changed, in the background, and the full suite only when the dev asks ([[feedback_dont_run_or_build]]).
- **`tools/`**: scripts for reading the original, described in `tools/README.md`: `macho64.py` and `dis64.py` read and disassemble `game/MiNDSIGHT` (not encrypted), naming selectors, strings and instance variables and listing each switch's cases, citing the binary's own addresses; `scenes.py` reads the 56 scenes, checks every puzzle value against the binary and the recordings on disk, and writes the listing. They need `capstone`; the game never does.
- **`analysis/script/scenes.txt`**: every scene as plain text, written by `tools/scenes.py`; find "Scene <number>:" to jump to one. The dev keeps it in `script/`.
- **`vendor/nvda/`**: `nvdaControllerClient64.dll` (x64) and its license. The game never speaks; the by-ear tools in `tests/interact/` speak through it ([[audio_plan]]).
- **`docks/`**: the documents a player reads: `readme.txt`, `changelog.txt` and `todo list.txt` ([[feedback_changelog]], [[feedback_todo_list_format]]). The readme describes only what works in the game now.
- **`README.md`**: the developer's guide: status by plan, how it will play, requirements, the tools, the layout, credits and licences, brought up to date after each plan. **`requirements.txt`**: `pygame` and `cryptography`. **`VERSION`**: the version, such as `26.10.22-1`.
- **`build/`** and **`dist/`**: build output, gitignored.
- **`user/`** is gitignored private reference material. Read it, but never edit it. Never name the dev's other games kept in it, in any of this repo's files ([[feedback_no_other_games]]).
- **`New File*.txt`** at the root is the dev's private scratchpad. It is gitignored; never read, edit, flag or delete it.

## Working here

- **The dev runs and builds, not Claude.** Ask before running the game or anything that plays sound or speaks ([[feedback_dont_run_or_build]]).
- **All plans are written first,** one at a time, with the dev's answers, before any review or building ([[feedback_all_plans_first]]).
- **Before each plan,** review it section by section with the dev, and build only on their word ([[feedback_review_plan_sections]]). Within a plan, when the dev says a section's tests passed, mark and commit it, then build the next section without asking ([[feedback_next_section_on_pass]]).
- **Before each section,** list what the dev will test by ear, sound or speech, each test marked optional or mandatory ([[feedback_say_ear_tests_ahead]]). A plan's by-ear tool grows with each section ([[feedback_grow_check_tools]]).
- **After each plan,** bring `README.md`, `CLAUDE.md`, every note in `aidocks/` and, where there is something to say, every player doc in `docks/` up to date, give a brief progress summary ([[feedback_progress_summary]]), then ask to push ([[feedback_docs_after_each_plan]]).
- **Plans first:** an agreed plan goes into its own note in `aidocks/plans/` before any code, and is marked finished only once the dev says it works ([[feedback_record_plans_first]]).
- **Committing and pushing:** commit finished work without asking; push only once a whole plan is finished and its docs are updated; "commit/push" means both; history rewrites need a go-ahead ([[feedback_git_commits]]). Name people by GitHub username only ([[feedback_use_github_usernames]]).
- **Questions:** a question or correction from the dev is a check, answered in chat ([[feedback_questions_are_checks]]). Ask one question per reply, in plain text ([[feedback_one_question_at_a_time]], [[feedback_no_question_pickers]]).
- **Releases** are never recorded in notes or the README ([[feedback_no_release_records]]).
- **Menus:** Back is always the first row ([[feedback_back_first]]).
- **Who you're working with:** [[user_screen_reader]]. The dev uses NVDA, so prefer lists and short lines, never wide tables, and never make noise from tools.

`CLAUDE.md` and `aidocks/` are committed, not gitignored.
