"""Where things are: the game's recordings, VERSION, the vendored files and the save folder.

From source, everything is found from the repository's root. In a build made by
compiler.py, PyInstaller unpacks the code to ``sys._MEIPASS`` and the game's data
sits beside the executable, or inside it for a single exe
(aidocks/plans/build_release_plan.md).

The game never writes to ``game/``. Everything it keeps goes in
``%APPDATA%\\Mindsight``, or wherever ``MINDSIGHT_USER_DIR`` points; the tests and the
by-ear tools set it to a folder of their own, so they never touch a player's save.
"""
from __future__ import annotations

import logging
import os
import sys

log = logging.getLogger('paths')

FROZEN = getattr(sys, 'frozen', False)
if FROZEN:
    ROOT = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(sys.executable)))
    EXE_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    EXE_DIR = ROOT

VENDOR = os.path.join(ROOT, 'vendor')

#: The save folder's name under %APPDATA% (aidocks/plans/foundation_plan.md).
SAVE_FOLDER = 'Mindsight'
#: Set by the tests and the by-ear tools to a folder of their own, never by the game.
USER_DIR_ENV = 'MINDSIGHT_USER_DIR'

#: The recordings, inside game/: story/sceen, story/speech and system/misc.
AUDIO_FOLDER = os.path.join('data', 'audio')


class MissingData(Exception):
    """The game's recordings are not where they should be; its text is the player's message."""


def _game_folders() -> list[str]:
    """Where game/ may be: beside the executable in a folder build, inside it in a single
    exe, or the repository's own ``game/`` from source."""
    out = []
    for folder in (os.path.join(EXE_DIR, 'game'), os.path.join(ROOT, 'game')):
        if folder not in out:
            out.append(folder)
    return out


def game() -> str:
    """The folder holding the game's data, the first of :func:`_game_folders` that has
    its recordings; :class:`MissingData` when none has."""
    tried = _game_folders()
    for folder in tried:
        if os.path.isdir(os.path.join(folder, AUDIO_FOLDER)):
            return folder
    raise MissingData(missing_data_message(tried))


def missing_data_message(tried: list[str] | None = None) -> str:
    """What the player is told when the recordings are missing, naming where the game looked."""
    tried = tried or _game_folders()
    places = '\n'.join(os.path.join(f, AUDIO_FOLDER) for f in tried)
    return ("Mindsight's recordings were not found, so the game cannot start.\n\n"
            "It looked for them in:\n%s\n\n"
            "Please extract the whole game folder again." % places)


def audio() -> str:
    """``game/data/audio``: the recordings."""
    return os.path.join(game(), AUDIO_FOLDER)


#: The story's recordings inside the recordings folder: what story.dat packs
#: (platform/pack.py, aidocks/plans/build_release_plan.md).
STORY_FOLDER = 'story'
STORY_PACK = 'story.dat'
#: The folder beside the executable that holds story.dat, in either kind of build.
PACK_FOLDER = 'data'
#: The pack's size and SHA-256, which compiler.py writes into a build's game\data\, so the
#: game knows its own pack.
PACK_FINGERPRINT = os.path.join('data', 'story_pack.json')


def story_pack() -> str:
    """Where story.dat is: data\\story.dat beside the executable in a build, or
    dist\\data\\story.dat from source, used there only when the loose story folder is not."""
    if FROZEN:
        return os.path.join(EXE_DIR, PACK_FOLDER, STORY_PACK)
    return os.path.join(ROOT, 'dist', PACK_FOLDER, STORY_PACK)


def dissertation() -> str:
    """``game/data/text/MiNDSIGHT.pdf``: the creator's dissertation, which the credits'
    left swipe opens (aidocks/plans/menus_saves_plan.md)."""
    return os.path.join(game(), 'data', 'text', 'MiNDSIGHT.pdf')


def version() -> str:
    """The port's version from ``VERSION``, beside the executable or at the repository's
    root; 'unknown' when it is missing."""
    for folder in (EXE_DIR, ROOT):
        try:
            with open(os.path.join(folder, 'VERSION'), 'r', encoding='utf-8-sig') as f:
                value = f.read().strip()
            if value:
                return value
        except OSError:
            pass
    return 'unknown'


def user_dir() -> str:
    """The save folder, made if it is not there yet."""
    folder = os.environ.get(USER_DIR_ENV)
    if not folder:
        base = os.environ.get('APPDATA') or os.path.expanduser('~')
        folder = os.path.join(base, SAVE_FOLDER)
    os.makedirs(folder, exist_ok=True)
    return folder


def user_path(*parts: str) -> str:
    """A path inside the save folder, such as ``user_path('saves', 'progress.json')``."""
    return os.path.join(user_dir(), *parts)


def logs_dir() -> str:
    folder = user_path('logs')
    os.makedirs(folder, exist_ok=True)
    return folder
