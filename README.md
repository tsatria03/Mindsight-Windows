# Mindsight-Windows

A Windows port, in Python, of **MiNDSiGHT** (`com.lukecharman.mindsight` 1.0.2, by Luke Charman), an interactive audio adventure for iPhone that is no longer on the App Store. It is told entirely through binaural recordings: you listen to the story and solve the puzzles inside it by swiping up, down, left or right at the right moment.

The original was played by swiping, and every word it says is a recording, with no text to speech. This port plays the same recordings and takes the keyboard in place of the swipes, so it can be played entirely by ear, as the original was.

**Headphones are needed.** The recordings were made with a dummy-head microphone, so their 3D sound only works in headphones.

## Status

**Plans 1 to 4 of 6 are finished. The whole game can be played,** from its main menu, through every puzzle, to its ending and credits. It does not save yet, so Continue always finds no saved game, and the credits' left swipe does not open the dissertation yet; plan 5 adds both. The work is split into six plans, in `aidocks/plans/`, each written in full, with every question answered, before any was built:

1. **Reading the original: finished.** Tools that read the original's binary, a check of every puzzle value against it and of every recording on disk, and a plain-text listing of all 56 scenes in `analysis/script/scenes.txt`.
2. **The foundation: finished.** `Mindsight.py`, its logs, its crash file and its error message boxes, the timer loop, the screens, the fixed keys, the window's text, debug mode on the command line, a by-ear tool, and its silent tests.
3. **The audio: finished.** The recordings through pygame's mixer, the Solved sound, the pause clips, a buzz the game makes itself in place of the original's vibration (160 Hz, sine, at 20 percent, chosen by ear), and pausing when the window loses focus.
4. **The story engine: finished.** The 56 scenes and the original's rules, the menus included: the input lock, the cues and the buzz, every puzzle, failing and the Rewind's retry points, pause and losing focus, with five changes from the original, below.
5. **The menus and saves: next.** The original's recorded menus, the dissertation PDF from the credits, and the one saved scene.
6. **Building and releasing.** `compiler.py` and `releaser.py`, with the story's recordings packed into an encrypted `data\story.dat`.

## How it plays

- **The swipes:** the arrow keys, or W, A, S and D.
- **The double tap,** which pauses and resumes: Escape, Enter or P.
- **Before the story starts,** in the menus and on today's stand-in screen, Escape quits the game instead, while Enter and P still pause.
- A key held with Shift, Control, Alt or the Windows key does nothing, so your screen reader's own commands never reach the game.
- **No speech, no settings, no volume controls.** The original had none of them; set the level with Windows' own volume. An error that stops the game shows a Windows message box, which your screen reader reads.
- **Pause** plays the original's pause message and holds everything; the swipes do nothing while paused. Switching to another window pauses by itself; coming back steps back 3 seconds and plays the welcome back, waiting for the double tap.
- **Five changes from the original:** a buzz where it vibrated; swipes ignored while paused; the credits always following the ending; street rounds 2 and 3 buzzing at their cue; and a buzz as a scene begins only for the two loops, the guard and the piranhas.

If Windows can open no sound device, the game says so in a message box and closes, since every part of it is a recording.

## Requirements

- Windows, 64-bit, and Python 3.12 or newer.
- For the game: `pip install -r requirements.txt`, which holds `pygame` and `cryptography`.
- For the tools in `tools/`: `pip install capstone`. The game never needs it.

## Running it

From the repo root:

    python Mindsight.py
    python Mindsight.py --debug
    python Mindsight.py --debug --scene 47
    python Mindsight.py -v
    python Mindsight.py --exit-after 5

- `--debug` turns on debug mode for that run, from source only; the window title says "Mindsight (debug)".
- `--scene N`, in debug mode only, starts at scene N, 0 to 55, by the original's numbering, as if the scene before had just ended; that run never saves. `analysis/script/scenes.txt` lists every scene.
- `-v` writes a more detailed log.
- `--exit-after SECONDS` quits by itself, for the build's own test.

The game opens on the original's main menu, or with `--debug --scene N` on scene N. The window shows the scene, "Listening" or "Your turn", and "Paused", for anyone helping who can see the screen. Until plan 5, saving only writes to the log where it would save.

Every run writes `logs\log.txt` in the save folder, `%APPDATA%\Mindsight`, keeping the run before as `log.old.txt`. An error that stops the game writes `logs\crash.txt` there and shows a message box saying so.

## Tests

    python tests/suite.py
    python tests/suite.py keys runloop

The silent tests are in `tests/case/`, 102 of them in eleven files: `test_paths`, `test_entry`, `test_runloop`, `test_keys`, `test_screens`, `test_mp3`, `test_recordings`, `test_audio`, `test_buzz`, `test_story` and `test_story_screen`. Each file imports `_quiet.py` first, which gives it a throwaway save, keeps every message box shut, and uses SDL's dummy video and sound, so nothing is heard, nothing opens and your own save is never touched. `tests/suite.py` runs them eight at once, runs a failed file again alone, and writes the results to `tests/results/`, which git ignores.

## Trying it by ear

The tools in `tests/interact/` are for trying things by ear. Each speaks through NVDA, using the NVDA client in `vendor/nvda/`, prints every line too, and keeps its own save under `%APPDATA%\Mindsight\interact\`. The game itself never speaks.

    python tests/interact/foundation_check.py
    python tests/interact/audio_check.py
    python tests/interact/buzz_check.py
    python tests/interact/story_check.py
    python tests/interact/story_check.py --scene 47

Every tool quits with Escape or Alt+F4, and wherever a tool uses Up or Down, W or S does the same.

- `foundation_check.py`: the game's own keys and timers, each key spoken with its meaning and a key with a modifier spoken as ignored; the pause is Enter or P here, since Escape quits. 1 and 2 show the game's two message boxes for real, T starts a countdown, Space holds or resumes it, switching windows is spoken, and H says the keys again.
- `audio_check.py`: any of the 56 scenes through the game's own players. Up or W and Down or S choose a scene, Enter plays it, Left and Right move 5 seconds, T types a point to play from, Space pauses, I says the position, O plays Solved, 2 the buzz, E and Q or Page Up and Page Down try the buzz's level, and 3 plays WelcomeBack. Switching windows pauses the scene; coming back steps it back 3 seconds with WelcomeBack.
- `story_check.py`: the game's own story screen, in debug mode, never saving, with the game's keys and Enter or P to pause. `--scene N` starts it at scene N; T then a number and Enter jumps to a scene; I says the scene, where it is, the failure and where the Rewind will go, whether a swipe counts, and in the piranha loop whether it is inside a window; L skips to 5 seconds before the scene's end.
- `buzz_check.py`: tunes the buzz. Up or W and Down or S move its frequency 5 Hz, Left and Right change its shape, Space plays it, and I says its values. It never changes the game.

## The tools

Scripts for reading the original, described in full in `tools/README.md`. None plays sound or speaks, and the only file they write is `analysis/script/scenes.txt`. From the repo root:

    python tools/macho64.py
    python tools/dis64.py --list MSViewController
    python tools/dis64.py --brief MSViewController handleSafe:
    python tools/dis64.py --writes whichFailure
    python tools/scenes.py
    python tools/scenes.py --check

- `macho64.py` lists the binary's layout, classes, instance variables, strings and imports.
- `dis64.py` disassembles its methods, naming what each instruction refers to and listing each switch's cases.
- `scenes.py` reads the 56 scenes from the binary, checks every puzzle value against it and every recording on disk, and writes the listing. `--check` prints only problems.

## Layout

- `game/`: the original app bundle, reorganized by the dev; never changed by the port.
  - `game/MiNDSIGHT`: the original's binary, a thin arm64 file, not encrypted. The whole story is code in it, not data.
  - `game/data/audio/`: the 60 recordings, MP3, converted from the original's m4a: `story/sceen/` (45), `story/speech/` (10) and `system/misc/` (5).
  - `game/data/text/MiNDSIGHT.pdf`: the creator's 2009 dissertation on the game.
- `Mindsight.py`: the entry script.
- `mindsight/`: the port's Python package: `paths.py`, `app.py` (the main loop), `platform/` (the message box, the timer loop, the keys, the sound, the buzz and the MP3 reader), `ui/` (the screen stack) and `game/` (the recordings, the scene table, the rules in `story.py` and the story screen).
- `tools/`: the scripts for reading the original.
- `analysis/script/scenes.txt`: every scene as plain text; find "Scene <number>:" to jump to one.
- `tests/case/`: the silent tests, with `tests/suite.py` to run them, and `tests/interact/`: the tools to try things by ear.
- `vendor/nvda/`: the NVDA controller client, which only the by-ear tools use.
- `docks/`: the documents a player reads: the readme, the changelog and the todo list.
- `aidocks/`: the project's notes and plans.
- `VERSION`: the version, by date and that day's number, such as `26.10.22-1`.

## Credits

**[tsatria03](https://github.com/tsatria03)** makes the port, on their own.

MiNDSiGHT itself is Luke Charman's game, made as a research project at SAE Institute London in 2009. Its cast and crew are named in its own credits recording, which the port plays as it is.

## Licence

The port's code is under the MIT License, in `LICENSE`. Everything under `game/` belongs to the original's makers and is not covered by it.

The third-party pieces keep their own licences:

- pygame, LGPL 2.1: <https://github.com/pygame/pygame/blob/main/docs/LGPL.txt>
- the NVDA controller client, LGPL 2.1, in `vendor/nvda/license.txt`
- capstone, for the tools only, BSD: <https://github.com/capstone-engine/capstone/blob/next/LICENSE.TXT>
