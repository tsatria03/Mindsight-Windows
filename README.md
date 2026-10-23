# Mindsight-Windows

A Windows port, in Python, of **MiNDSiGHT** (`com.lukecharman.mindsight` 1.0.2, by Luke Charman), an interactive audio adventure for iPhone that is no longer on the App Store. It is told entirely through binaural recordings: you listen to the story and solve the puzzles inside it by swiping up, down, left or right at the right moment.

The original was played by swiping, and every word it says is a recording, with no text to speech. This port plays the same recordings and takes the keyboard in place of the swipes, so it can be played entirely by ear, as the original was.

**Headphones are needed.** The recordings were made with a dummy-head microphone, so their 3D sound only works in headphones.

## Status

**Plan 1 of 6 is finished.** Nothing can be played yet: the plans after it build the game. The work is split into six plans, in `aidocks/plans/`, each written in full, with every question answered, before any was built:

1. **Reading the original: finished.** Tools that read the original's binary, a check of every puzzle value against it and of every recording on disk, and a plain-text listing of all 56 scenes in `analysis/script/scenes.txt`.
2. **The foundation: next.** `Mindsight.py`, its logs, its crash file and its error message boxes, the timer loop, the screens, the fixed keys, the window's text, debug mode on the command line, and the silent tests.
3. **The audio.** The recordings through pygame's mixer, the Solved sound, the pause clips, a buzz the game makes itself in place of the original's vibration, and pausing when the window loses focus.
4. **The story engine.** The 56 scenes and the original's rules: the input lock, the puzzles, failing and the Rewind's retry points.
5. **The menus and saves.** The original's recorded menus, the dissertation PDF from the credits, and the one saved scene.
6. **Building and releasing.** `compiler.py` and `releaser.py`, with the story's recordings packed into an encrypted `data\story.dat`.

## How it will play

From the plans, so far unbuilt:

- **The swipes:** the arrow keys, or W, A, S and D.
- **The double tap,** which pauses and resumes: Escape, Enter or P.
- **No speech, no settings, no volume controls.** The original had none of them; set the level with Windows' own volume. An error that stops the game shows a Windows message box, which your screen reader reads.
- **Three changes from the original:** a buzz where it vibrated, swipes ignored while paused, and the credits always following the ending.

## Requirements

- Windows, 64-bit, and Python 3.12 or newer.
- For the game, from plan 2 on: `pip install -r requirements.txt`, which holds `pygame`, `prismatoid` and `cryptography`. `prismatoid` goes when the foundation is built, since the game never speaks.
- For the tools in `tools/`: `pip install capstone`. The game never needs it.

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
- `mindsight/`: the port's Python package, from plan 2.
- `tools/`: the scripts for reading the original.
- `analysis/script/scenes.txt`: every scene as plain text; find "Scene <number>:" to jump to one.
- `tests/case/`: silent tests, and `tests/interact/`: tools to try things by ear, from plan 2.
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
