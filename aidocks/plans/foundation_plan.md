---
name: foundation_plan
description: "Plan 2: the mindsight package, the Mindsight.py entry script and screen loop, save-folder paths, logs, crash files and error message boxes, the timer loop, the fixed keys (arrows and WASD for the swipes; Escape, Enter and P for the double tap), the window's text and the silent tests. No speech, Settings, key binder or volumes."
metadata:
  node_type: memory
  type: project
---

**Status: written,** every question answered on 2026-10-22. Its section review waits until every plan is written ([[feedback_all_plans_first]]).

Plan 2 ([[reading_original_plan]] lists the order). Everything else stands on it: the audio, the story engine, the menus and the saves all use its paths, timers, keys and screen loop.

## Sections

1. The entry script, paths, logs, the crash file and the error message boxes.
2. The timer loop and the screen loop, with the fixed keys and the window's text, and a stand-in screen until the story engine.
3. The silent test setup: `tests/case/_quiet.py`, `tests/suite.py` and the first test files.

## Decided

- **The name is "Mindsight" everywhere,** following the folders the dev made:
  - the window title: Mindsight
  - the entry script: `Mindsight.py` at the repo root
  - the package: `mindsight/`
  - the built game: `Mindsight.exe`
  - the save folder: `%APPDATA%\Mindsight`, or `MINDSIGHT_USER_DIR` when set
- **The package is split in three:**
  - `mindsight/platform/`: the parts that talk to Windows (timers, files, keys, message boxes, and later the audio)
  - `mindsight/ui/`: the screen stack and the window's text
  - `mindsight/game/`: the scenes, the puzzles and what is particular to Mindsight
- **Windows only, Python 3.12 or newer, 64-bit** ([[project_windows_only]], [[project_python_only]]).
- **No speech, no Settings screen, no key binder and no volume controls** (the dev, 2026-10-22, asked whether they were needed: "I feel like this game doesn't need it because there's no tts what so ever, and it's not nearly as complex"; "it does not need any volume controls what so ever. It wouldn't need the prism library if that's the case."; then, to the summary: "Yes please."). Why it holds:
  - The original is entirely self-voiced: every word is a recording, and it never uses text to speech or the screen reader ([[project_original_behaviour]]). The port has nothing of its own to say.
  - The original has no settings and no volume controls; the player used the phone's own volume. On Windows, the system volume and the volume mixer do that.
  - So the game has no speech module, no Prism, no NVDA client, no settings file, no keys file, no F1 screen and no spoken menu.
- **The keys, fixed, never rebound** (the dev, 2026-10-22: the arrows and Escape, "Enter can be for the double tap if it asks for it", then "it can use the 4 arrow keys plus w/a/s/d keys for swipes", then "add p to that list for pausing/resuming. So escape/enter/p."). This replaces the dev's earlier "All should be rebindable", since there is no key binder:
  - **Up arrow or W:** swipe up.
  - **Down arrow or S:** swipe down.
  - **Left arrow or A:** swipe left.
  - **Right arrow or D:** swipe right.
  - **Escape, Enter or P:** the double tap, which pauses and resumes. Enter covers wherever a recording asks the player to double tap; the original's only double tap is the pause.
  - The swipe keys answer the original's spoken menus and its puzzles alike.
  - A key works with no modifier held; with Shift, Control or Alt held, it does nothing, so a screen reader's own commands never reach the game.
  - Closing the window, or Alt+F4, quits.
- **Errors are shown in a Windows message box** (agreed 2026-10-22), through ctypes' `MessageBoxW`, which NVDA and every other screen reader read aloud by themselves, with no library:
  - when `game/data/audio/` is missing, saying where the game looked
  - when an error stops the game, saying it closed and that `crash.txt` says why
  - when no sound device can be opened, saying the game needs one ([[audio_plan]])
  - nowhere else; the game itself never shows one
- **The window shows plain text for a sighted helper** (the dev, 2026-10-22: "yes, show a window for sited users."): during the story, the scene playing and which keys work there; while paused, that it is paused. It is secondary: the recordings are the real interface, and nothing is only in the window.
- **Adapted from the reference material in the gitignored `user/` folder,** renamed and cut down, never naming where it came from ([[feedback_no_other_games]]). These standing choices carry over:
  - **Timer loop:** delayed calls and repeating timers, pumped once a frame on wall-clock time, with `hold()` and `resume()` that shift every waiting timer by the pause. A call made while the loop is held counts its delay from the moment the clock stopped. The cue times, the input lock and the scene changes run on it.
  - **Safe JSON files,** for the save: a temporary file first, then a `.bak` of the old one, then a swap. A damaged file is kept as `.damaged` and the backup loaded instead; with no backup, it is replaced at once ([[menus_saves_plan]]).
  - **Logs:** every run writes `logs/log.txt` in the save folder and keeps the run before as `log.old.txt`. An error that stops the game writes `logs/crash.txt`, and shows the message box above.
  - **Screen loop:** a stack of screens at 60 frames a second. A screen can open another on top, close itself, or replace the stack. Switching away from the window is passed to the top screen.
- **Debug mode is command-line only** (the dev, 2026-10-22: "The debugger should be commandline only. How ever you activate it."), for runs from source only, never in a built game, and never remembered between runs:
  - `--debug` turns it on for that run; the window title says "Mindsight (debug)".
  - `--scene N`, in debug mode only, starts the game at scene N, from 0 to 55, by the original's numbering ([[project_original_behaviour]]), and that run never writes the save ([[menus_saves_plan]]). A number outside that range is logged and ignored.
  - Its use in the story, such as what a jump sets up, is settled in the story engine plan.
- **Two more options,** for any run:
  - `-v` writes a more detailed log.
  - `--exit-after SECONDS` quits by itself after that many seconds, so the build test can start a built game silently and check it runs.
- **The data counts as found** only when `game/data/audio/` is there.
- **Until the story engine,** the game opens on a stand-in screen that names the key pressed in the window, so the window, the keys and the logs can be tried. Escape, Enter and P there say nothing, since there is no speech; the window shows them.
- **Tests stay silent and off the real save** ([[feedback_dont_run_or_build]]): every test imports `_quiet.py` first, which points the save at a throwaway folder, gives SDL dummy video and audio drivers, and stops the message boxes from opening.
- `tests/suite.py` runs each test file as its own process, several at once, runs a failed file again alone, writes `tests/results/results-<date>-<n>.txt`, exits 1 on a failure, and takes names with or without `test_`.
- **`requirements.txt` loses `prismatoid`** when this plan is built. `vendor/nvda/` stays: the by-ear tools in `tests/interact/` speak through it, never the game ([[audio_plan]]).

## Open questions

Asked one at a time; each answer moves into Decided.
1. Answered: the keys.
2. Answered: debug mode, command-line only, after the dev first put it off.
3. Answered: the window's text.
4. Answered: no volumes at all.
5. The stand-in screen: proposed in Decided as following from having no menus of the port's own; to be confirmed at the section review.
