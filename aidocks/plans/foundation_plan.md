---
name: foundation_plan
description: "Plan 2: the mindsight package, the Mindsight.py entry script and screen loop, save-folder paths, logs, crash files and error message boxes, the timer loop, the fixed keys (arrows and WASD for the swipes; Escape, Enter and P for the double tap), the window's text and the silent tests. No speech, Settings, key binder or volumes."
metadata:
  node_type: memory
  type: project
---

**Status: FINISHED 2026-10-23,** confirmed by the dev ("Yes. It looks good."). Built one section at a time, since it has by-ear tests ([[feedback_next_section_on_pass]]); reviewed in one message on 2026-10-23.

## Progress

- **Section 3, FINISHED 2026-10-23,** with nothing to test by ear:
  - `tests/case/_quiet.py`: a throwaway save, deleted at the end; `MINDSIGHT_NO_MESSAGEBOX`, `MINDSIGHT_SILENT` and SDL's dummy drivers, set outright; `run_tests(globals())`.
  - `tests/suite.py`: each file in its own process, eight at once, a failed file run again alone, the results in the gitignored `tests/results/`, and names with or without `test_`.
  - **36 silent tests in five files,** all passing on their first run: `test_paths` (7: the throwaway save, the recordings found, the missing-data message naming where it looked, `VERSION`, and every test file importing `_quiet` first), `test_entry` (9: the options, `--scene` and `--debug`'s rules, `crash.txt`, two silent runs of `main()` with the log before kept, and both message boxes, missing data and an error), `test_runloop` (7), `test_keys` (7: every agreed key, pygame's own names, modifiers, the labels) and `test_screens` (6: the stack, the three ways a key reaches a screen, focus and quit events, a silent run, and the stand-in screen).
  - The dev's own `log.txt` was checked after the run, untouched by it.
- **Section 2, FINISHED 2026-10-23,** its by-ear tests passed (the dev: "The tests for section 2 past."). Built the same day:
  - `mindsight/platform/runloop.py`, the timer loop, with `hold()` and `resume()`.
  - `mindsight/platform/keys.py`, the fixed keys: each pygame key name to its gesture, `up`, `down`, `left`, `right` or `pause`, with the keypad's Enter as the double tap too; a game key with Shift, Control, Alt or the Windows key held stands for nothing.
  - `mindsight/ui/screens.py`, the screen stack. A screen hears a game key as `gesture()`, a game key with a modifier as `ignored_key()`, and any other key as `other_key()`, which only the by-ear tools use.
  - `mindsight/app.py`, the main loop at 60 frames a second: events, focus changes, the timers, `--exit-after` on the timer loop, and the top screen's lines in the window.
  - `mindsight/game/standin.py`, the stand-in screen `Mindsight.py` now opens on: the keys, the last key's meaning and whether the window has the keyboard, in the window and the log, saying nothing.
  - `foundation_check.py` grew onto the game's own App and keys: each gesture spoken, a key with a modifier spoken as ignored, T a 10-second countdown on the timer loop, Space holding or resuming it, and focus changes spoken, quiet for a second after a message box, which takes the keyboard and gives it back. **F10 now quits, since Escape is the game's pause.**
  - Checked silently: pygame's names for every key match the map; the tool started through its real entry point and closed cleanly; driven by hand, it spoke every gesture, three keys with modifiers as ignored, the countdown, nothing while held, and the focus changes.
- **Section 1, FINISHED 2026-10-23,** all four by-ear tests passed (the dev: "Perfect. All of the section 1 tests past."). Built the same day (the dev: "build section 1 first."):
  - `Mindsight.py`: the four options, `logs/log.txt` with `log.old.txt`, `logs/crash.txt`, and a plain window titled "Mindsight", or "Mindsight (debug)" with `--debug`, which closing the window or Alt+F4 shuts. `--scene N` is checked for debug mode and the range 0 to 55, and logged; the story engine will use it. A missing recordings folder or any error that stops the game writes `crash.txt` and shows its message box.
  - `mindsight/paths.py`: the recordings in `game/data/audio`, beside the executable or in the repository; `VERSION`; and the save folder, `%APPDATA%\Mindsight` or `MINDSIGHT_USER_DIR`. `paths.MissingData` carries the player's message, naming where the game looked.
  - `mindsight/platform/msgbox.py`: `MessageBoxW` with an error icon, on top; `MINDSIGHT_NO_MESSAGEBOX` keeps it shut for the tests, keeping the text in `msgbox.shown`.
  - The empty `platform/`, `ui/` and `game/` packages; `prismatoid` out of `requirements.txt`.
  - `tests/interact/_nvda.py`, the tools' speech through the NVDA client, printing every line too, and only printing with `MINDSIGHT_SILENT` or no NVDA; and `tests/interact/foundation_check.py`, with 1 for the missing recordings message, 2 for the crash message (writing a crash.txt that says the game did not really stop), H for the keys and Escape to quit.
  - Checked silently: the tool started through its real entry point with speech, message boxes, video and sound off and a throwaway save, ran 2 seconds and closed cleanly, writing its log; its two keys' actions gave the game's own texts. `Mindsight.py` itself is compiled but not yet run, since running the game waits for the dev's word ([[feedback_dont_run_or_build]]).

Plan 2 ([[reading_original_plan]] lists the order). Everything else stands on it: the audio, the story engine, the menus and the saves all use its paths, timers, keys and screen loop.

## Sections

1. **The entry script, paths, logs, the crash file and the error message boxes.** `Mindsight.py` with its four options; `mindsight/paths.py`; `logs/log.txt`, `log.old.txt` and `logs/crash.txt`; the missing-data and crash message boxes; `prismatoid` out of `requirements.txt`; a plain window titled "Mindsight", or "Mindsight (debug)", until section 2. `tests/interact/foundation_check.py` starts here, with keys to show each message box for real. To test by ear:
   1. Mandatory: the missing-data message box is read by NVDA, and Enter closes it.
   2. Mandatory: the crash message box is read, naming `crash.txt`.
   3. Optional: `python Mindsight.py` opens a window NVDA announces as Mindsight, and Alt+F4 closes it.
   4. Optional: with `--debug`, NVDA announces "Mindsight (debug)".
2. **The timer loop, the screens and the keys.** `mindsight/platform/runloop.py`, `mindsight/ui/screens.py` and `mindsight/platform/keys.py`, the window's text, and the stand-in screen. `foundation_check.py` grows here: the game's own keys and timer loop, each key's meaning spoken, a countdown, and focus changes. To test by ear:
   1. Mandatory: each swipe key and each pause key is spoken with its meaning in `foundation_check.py`, and Shift+Up or Control+W is spoken as ignored.
   2. Optional: a timer counts down and stops while held.
   3. Optional: Alt+Tab is reported as losing and regaining focus.
3. **The silent tests.** `tests/case/_quiet.py`, `tests/suite.py` and the first test files: the paths, the options, the logs and crash file, the message boxes, the timer loop, the screens and the keys. Nothing to test by ear; running `python tests/suite.py` is optional.

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
- **Until the story engine,** the game opens on a stand-in screen that shows the last key's meaning in the window, such as "Swipe up", and writes it to the log; it says nothing, since the game has no speech. Confirmed at the review (2026-10-23).
- **`tests/interact/foundation_check.py`,** a by-ear tool (the dev, 2026-10-23: "Yes please.", to the proposal at the review), speaking through the NVDA client like every tool, with its own save under `%APPDATA%\Mindsight\interact\foundation_check` ([[feedback_test_tools_in_interact]], [[feedback_grow_check_tools]]). Section 1 gives it keys to show each message box for real, so they can be heard without moving files or crashing the game; section 2 adds the game's own keys and timer loop.
- **Tests stay silent and off the real save** ([[feedback_dont_run_or_build]]): every test imports `_quiet.py` first, which points the save at a throwaway folder, gives SDL dummy video and audio drivers, and stops the message boxes from opening.
- `tests/suite.py` runs each test file as its own process, several at once, runs a failed file again alone, writes `tests/results/results-<date>-<n>.txt`, exits 1 on a failure, and takes names with or without `test_`.
- **`requirements.txt` loses `prismatoid`** when this plan is built. `vendor/nvda/` stays: the by-ear tools in `tests/interact/` speak through it, never the game ([[audio_plan]]).

## Open questions

Asked one at a time; each answer moves into Decided.
1. Answered: the keys.
2. Answered: debug mode, command-line only, after the dev first put it off.
3. Answered: the window's text.
4. Answered: no volumes at all.
5. Answered at the review: the stand-in screen, with `foundation_check.py` to hear the keys.
