# tools

Scripts for reading the original app. None of them is part of the game, none is shipped in a build, and none writes anything under `game/`; the only file any of them writes is `analysis/script/scenes.txt`. None plays sound or speaks.

- `macho64.py`: reads the arm64 code of `game/MiNDSIGHT`, the original's binary. It lists the segments and sections, the three Objective-C classes with their methods and instance variables, the selector references, the string constants and the imported functions. Run on its own, it prints the layout and whether the code is encrypted (it is not: `cryptid` 0). Standard library only.
- `dis64.py`: disassembles methods from that code, naming the selectors, imported functions, classes, string constants and instance variables each instruction refers to, and showing the value of each number loaded as a time, such as 112 seconds. It follows the `adr` and literal `ldr` loads this binary uses for nearly every string and selector, lists each switch's jump table as its cases, and marks every load or store through an instance variable, as `-> _currentScene`. It can also find every method that uses an address or calls a selector, and every store to an instance variable. It needs `capstone` (`pip install capstone`), which the game itself does not.
- `scenes.py`: reads the 56 scenes from the binary, each with its recording, what follows it, whether it saves and whether it loops, and checks a table of the puzzles' answers, cue times, piranha windows and retry points against the binary's own constants. It finds each recording on disk the way the game will, checks that every recording the binary names is there, and writes the whole story as `analysis/script/scenes.txt`. It needs `capstone` too.

Examples, from the repo root:

    python tools/macho64.py
    python tools/macho64.py --ivars MSViewController
    python tools/macho64.py --strings
    python tools/macho64.py --imports
    python tools/dis64.py --list MSViewController
    python tools/dis64.py --find puzzle
    python tools/dis64.py MSViewController pushDirection:
    python tools/dis64.py --brief MSViewController handleSafe:
    python tools/dis64.py --full --brief MSViewController playNextScene
    python tools/dis64.py --at 0x100006d2c
    python tools/dis64.py --refs 0x10000e9f8
    python tools/dis64.py --refs playSolvedSound
    python tools/dis64.py --writes whichFailure
    python tools/scenes.py
    python tools/scenes.py --check

Notes:
- Addresses are the binary's own virtual addresses, as the plans and notes cite them.
- A class method is named with a + in front; this binary has none of its own.
- A listing stops at a method's first `ret` unless `--full` is given, which reads on to where the next method begins; many methods return early and carry on after. `--refs` and `--writes` always read in full.
- A switch's cases are listed right after its `br`, each with its target; the table's data, which sits after the code, is skipped.
- A class from the system frameworks, such as `AVAudioPlayer`, shows as `class@0`, since the binary names it only when it is loaded. The selector sent to it says which it is.
- `MINDSIGHT_BINARY` sets the path of the binary to read.
