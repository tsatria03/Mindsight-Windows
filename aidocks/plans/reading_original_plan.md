---
name: reading_original_plan
description: "Plan 1: tools to read the original's binary, a check of every recording it names against game/data/audio/, a readable listing of all 56 scenes in analysis/, and the original's behaviour note, for every later plan to build on."
metadata:
  node_type: memory
  type: project
---

**Status: built, not yet confirmed** (2026-10-23), all four sections at once (the dev, 2026-10-23, after the review: "Since plan 1 has no hering tests, you can build it. I mean all 4 sections without pausing at each section for review."). Reviewed in one message on 2026-10-23 ([[feedback_review_plan_sections]]).

**Done before the plan, 2026-10-22:** the binary was read with capstone through a throwaway helper outside the repo, and what it showed is already written down in [[project_original_findings]] and [[project_original_behaviour]], with the dev's corrections. This plan makes the reading repeatable inside the repo, so every number in those notes can be checked again, and later plans can cite tools rather than memory.

## Built

- **Section 1:** `tools/macho64.py`, `tools/dis64.py` and `tools/README.md`. `macho64.py` also lists the string constants (`--strings`) and the imports (`--imports`), and names each instance variable's offset variable. `dis64.py` follows `adr` and literal `ldr` loads, names instance variables and marks each load or store through one (`-> _currentScene`), lists a switch's cases right after its `br`, skipping the table's data, and finds every store to an instance variable (`--writes`). `--writes whichFailure` finds the 12 stores, none clearing it.
- **Section 2:** `tools/scenes.py`. From the binary it reads each scene's recording, what follows and whether it saves (by following each `playNextScene` case to the shared tail), the looping scenes and the input lock's scenes, and the scenes that vibrate as they end, from the masks in `playScene:fromInterval:` and `audioPlayerDidFinishPlaying:successfully:`. The puzzles, the piranha windows, the retry points, the retry tests and the menus' scenes are tables, each value checked at its address. It finds all 59 named recordings on disk, and only `system/misc/FanRadio.mp3` unnamed; it reports no problems. Fed seven wrong values on purpose, in memory, it reported all seven.
- **Section 3:** `analysis/script/scenes.txt`, written by `tools/scenes.py`: 56 scenes, with the port's three departures marked at the top and at scene 55. A looping scene shows no "then" and no vibration, since it never ends.
- **Section 4:** every address cited in [[project_original_behaviour]], [[project_original_findings]] and the plans resolves to the method or instruction it names. The note's scene list matches the tool's reading of `playNextScene` scene for scene. Solved's volume (0.2), the timer (0.1 s), the vibration (0xfff), `saved.plist`, the 3-second step back and the eleven achievements' scenes match too. Corrections made:
  - **six letter-suffixed names, not five,** in the findings note and in plans 1 and 3; the tool's table had all six
  - scene 10's unused "then", noted in the behaviour note
  - `pause_menu`'s words, from the dev's listening

## Why

The original has no story data: its 56 scenes, what follows each, the puzzles' answers and every timing are hard-coded in `MSViewController`. The binary is the only record of them. Every later plan needs those numbers, so the port plays as the original did.

## Sections

### 1. Reading the binary

- `tools/macho64.py`: reads `game/MiNDSIGHT` (thin arm64, not encrypted): the segments and sections, the three classes with their methods and instance variables, the selector references, the imported functions and the Objective-C string constants. Standard library only.
- `tools/dis64.py`: disassembles a method with capstone, naming what each instruction refers to: selectors, classes, imported functions, string constants and the doubles loaded as times. Unlike a plain listing, it must also:
  - follow `adr` and pc-relative `ldr` loads, which this binary uses for nearly every string and selector
  - name an instance variable from its offset, such as `currentScene` or `whichFailure`
  - decode the inline jump tables behind the game's switch statements, listing each case's target, rather than stopping at their data
  - find every write to an instance variable, such as every place `whichFailure` is set
- `tools/README.md`: what each tool does, with examples.
- `MINDSIGHT_BINARY` sets the path of the binary to read.
- Nothing to test by ear: these are silent tools that print text.

### 2. The scene table and the recordings

- `tools/scenes.py`: reads from the binary the recording of each of the 56 scenes (`urlForScene:`'s jump table at 0x100009014), what follows each one and whether it saves (`playNextScene`'s jump table at 0x100006e04), and the looping scenes. It finds each recording on disk by the port's own lookup: the name without its number prefix, the six letter-suffixed names mapped, found anywhere under `game/data/audio/` ([[project_original_findings]]).
- It checks that every recording the binary names is on disk, and lists the files it never names (today, only `FanRadio.mp3`).
- **The puzzle values are a table in the tool, each checked against the binary** (agreed at the review, 2026-10-23). What follows each scene, the saves and the loops come from the two jump tables. The answers, cue times, piranha windows and retry points sit in separate handlers, in less regular code, so `tools/scenes.py` holds them in a table, each with the address of the constant or branch it comes from, and checks every one against the binary; any that differs is a problem.
- `--check` prints only problems.
- Nothing to test by ear.

### 3. A readable listing

- `analysis/script/scenes.txt`, written by `tools/scenes.py`: every scene in story order, each beginning "Scene <number>: <recording>", so a screen reader's find can jump to it, with its length, what follows, whether it saves, whether it loops, and, for a puzzle, the answer, the cue time and the retry point. Plain text, short lines.
- It marks where the port departs from the original (agreed at the review): the credits always following the ending, swipes ignored while paused, and the buzz in place of vibration.
- Nothing to test by ear. The dev may read it to check it against what they remember of the original (optional).

### 4. Checking the behaviour note

- Every claim in [[project_original_behaviour]] is checked against the tools' output, and each address it cites is confirmed; anything that differs is corrected there.
- Questions only listening can settle go to the dev one at a time. Listening to the original's recordings is the dev's to do, never Claude's ([[feedback_dont_run_or_build]]). The one such question, what `pause_menu` says, was settled at the review: it says only that the game is paused, and to double tap to carry on (the dev, 2026-10-23).
- Nothing to test by ear, beyond those optional listens.

## Decided

- No FMOD; pygame plays everything ([[project_python_only]]).
- The tools never write under `game/`, play nothing and speak nothing. The only file they write is `analysis/script/scenes.txt`.
- `capstone` is needed by `tools/dis64.py` and `tools/scenes.py` only, never by the game, so it is not in `requirements.txt`; `tools/README.md` says to install it.

## Open questions

None yet. The questions for later plans are in [[project_later_topics]].

## Where this fits

The plans after this one, proposed, each to get its own note and review before any code:
1. Reading the original (this plan).
2. The foundation: the entry script, paths, logs, crash file and error message boxes, the timer loop, the screens, the fixed keys, the window's text, and the silent tests; no speech, Settings, key binder or volumes ([[foundation_plan]]).
3. The audio: the scenes through `pygame.mixer.music`, starting partway, looping, pause and resume, the Solved sound over the next scene, and the cue sounds in place of vibration.
4. The story engine: the 56 scenes, the input lock, the puzzles, failing and the Rewind, and debug jumps, with a scene chooser in `tests/interact/`.
5. The menus and saves, combined at the dev's word: the original's recorded menus answered by the swipe keys, the credits and the PDF, and the one saved scene ([[menus_saves_plan]]).
6. Building and releasing: `compiler.py` and `releaser.py` ([[build_release_plan]]).

The order and the weights for the progress summary are agreed with the dev once this plan is finished ([[feedback_progress_summary]]).
