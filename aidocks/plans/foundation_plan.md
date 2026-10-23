---
name: foundation_plan
description: "Plan 2: the mindsight package, the Mindsight.py entry script and screen loop, save-folder paths, logs and crash files, screen reader speech, the timer loop, settings and keys files, the F1 screen, the spoken menu and the silent tests."
metadata:
  node_type: memory
  type: project
---

**Status: being written.** Its open questions are being asked one at a time; no review or building until every plan is written ([[feedback_all_plans_first]]).

Plan 2 ([[reading_original_plan]] lists the order). Everything else stands on it: the audio, the story engine, the menus and the saves all use its paths, speech, timers and screen loop.

## Sections

1. The entry script, paths, logs and the crash file.
2. Speech and the timer loop, with `tests/interact/speech_check.py`.
3. The settings and keys files, the screen stack, the spoken menu and the F1 screen, with a stand-in menu until the menus plan.
4. The silent test setup: `tests/case/_quiet.py`, `tests/suite.py` and the first test files.

## Decided

- **The name is "Mindsight" everywhere,** following the folders the dev made:
  - the window title: Mindsight
  - the entry script: `Mindsight.py` at the repo root
  - the package: `mindsight/`
  - the built game: `Mindsight.exe`
  - the save folder: `%APPDATA%\Mindsight`, or `MINDSIGHT_USER_DIR` when set
- **The package is split in three:**
  - `mindsight/platform/`: the parts that talk to Windows (speech, timers, files, settings, keys, and later the audio)
  - `mindsight/ui/`: keyboard input, menus and screens
  - `mindsight/game/`: the scenes, the puzzles and what is particular to Mindsight
- **Windows only, Python 3.12 or newer, 64-bit** ([[project_windows_only]], [[project_python_only]]).
- **Adapted from the reference material in the gitignored `user/` folder,** renamed and cut down, never naming where it came from ([[feedback_no_other_games]]). These are the dev's standing choices there, carried over as they are:
  - **Speech:** NVDA through its own client first, then any other screen reader through Prism, then a Windows voice. It has `speak(text, interrupt)` and `stop()`, rechecks which screen reader is running every few seconds, and loads Prism only when NVDA is not running. `MINDSIGHT_SILENT` turns it off for tests.
  - **Timer loop:** delayed calls and repeating timers, pumped once a frame on wall-clock time, with `hold()` and `resume()` that shift every waiting timer by the pause. A call made while the loop is held counts its delay from the moment the clock stopped. The cue times, the input lock and the scene changes run on it.
  - **Settings files:** short JSON files written safely (a temporary file first, then a `.bak` of the old one, then a swap). A damaged file is kept as `.damaged` and the backup loaded instead; with no backup, it is replaced with the defaults at once. Every setting is written from the first start, and a bad value is put back to its default.
  - **Logs:** every run writes `logs/log.txt` in the save folder and keeps the run before as `log.old.txt`. An error that stops the game writes `logs/crash.txt` and is spoken aloud, so a blind player knows why the game closed.
  - **Screen loop:** a stack of screens at 60 frames a second. A screen can open another on top, close itself, or replace the stack. Switching away from the window is passed to the top screen.
  - **The spoken menu,** for the list menus the port adds, such as Settings: rows read without their place; Up, Down, Left and Right all move, wrapping round; Home and End jump to the first and last row; Back first ([[feedback_back_first]]).
  - **F1 key bindings screen:** every action rebindable, spoken in full, from anywhere in the game, with the timers held while it is open. F1 and Escape are fixed. A binding is one key with exact modifiers, saved in `config/keys.json`. The key map's actions are grouped by where they work, and a key clashes only within its group.
  - **Master volume:** Shift+Home raises it and Shift+End lowers it, from anywhere in the game, each press saying the new level.
- **What interrupts what,** for screen reader speech:
  - Each move in a menu cuts off what was being said.
  - A key the player presses speaks at once, cutting off earlier speech but never the recordings, which keep playing underneath.
  - Important messages, such as an error, are never cut off by background events, only by the player pressing a key.
  - Speech never pauses the story. Only the pause key does.
- **The data counts as found** only when `game/data/audio/` is there; if it is missing, the player is told where the game looked.
- **Tests stay silent and off the real save** ([[feedback_dont_run_or_build]]): every test imports `_quiet.py` first, which points the save at a throwaway folder, turns speech off, and gives SDL dummy video and audio drivers.
- `tests/suite.py` runs each test file as its own process, several at once, runs a failed file again alone, writes `tests/results/results-<date>-<n>.txt`, exits 1 on a failure, and takes names with or without `test_`.

## Open questions

Asked one at a time; each answer moves into Decided.
1. The keys for the four swipes and for the double tap's pause.
2. Whether there is a debug mode for source runs, to jump to any scene, and its command-line options.
3. Whether the window shows plain text for a sighted helper.
4. Which volumes there are, beyond the master, and their keys.
5. Until the menus plan, the stand-in menu the game opens on.
