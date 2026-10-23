---
name: reading_original_plan
description: "Plan 1: tools to read the original's binary, a check of every recording it names against game/data/audio/, a readable listing of all 56 scenes in analysis/, and the original's behaviour note, for every later plan to build on."
metadata:
  node_type: memory
  type: project
---

**Status: written,** with no open questions. Its section review waits until every plan is written ([[feedback_all_plans_first]], [[feedback_review_plan_sections]]).

**Done before the plan, 2026-10-22:** the binary was read with capstone through a throwaway helper outside the repo, and what it showed is already written down in [[project_original_findings]] and [[project_original_behaviour]], with the dev's corrections. This plan makes the reading repeatable inside the repo, so every number in those notes can be checked again, and later plans can cite tools rather than memory.

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

- `tools/scenes.py`: reads from the binary the recording of each of the 56 scenes (`urlForScene:`'s jump table at 0x100009014), what follows each one and whether it saves (`playNextScene`'s jump table at 0x100006e04), and the looping scenes. It finds each recording on disk by the port's own lookup: the name without its number prefix, the five letter-suffixed names mapped, found anywhere under `game/data/audio/` ([[project_original_findings]]).
- It checks that every recording the binary names is on disk, and lists the files it never names (today, only `FanRadio.mp3`).
- `--check` prints only problems.
- Nothing to test by ear.

### 3. A readable listing

- `analysis/scenes.txt`, written by `tools/scenes.py`: every scene in story order, each beginning "Scene <number>: <recording>", so a screen reader's find can jump to it, with its length, what follows, whether it saves, whether it loops, and, for a puzzle, the answer, the cue time and the retry point. Plain text, short lines.
- Nothing to test by ear. The dev may read it to check it against what they remember of the original (optional).

### 4. Checking the behaviour note

- Every claim in [[project_original_behaviour]] is checked against the tools' output, and each address it cites is confirmed; anything that differs is corrected there.
- Questions only listening can settle go to the dev one at a time, such as what `pause_menu` says. Listening to the original's recordings is the dev's to do, never Claude's ([[feedback_dont_run_or_build]]).
- Nothing to test by ear, beyond those optional listens.

## Decided

- No FMOD; pygame plays everything ([[project_python_only]]).
- The tools never write under `game/`, play nothing and speak nothing. The only file they write is `analysis/scenes.txt`.
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
