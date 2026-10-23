"""A Windows message box for the errors that stop the game.

The game has no speech of its own (aidocks/plans/foundation_plan.md), so an error is
shown with Windows' own ``MessageBoxW``, which NVDA and every other screen reader read
aloud by themselves. It is shown only when the recordings are missing, when an error
stops the game, and, from the audio plan, when no sound device can be opened.

``MINDSIGHT_NO_MESSAGEBOX`` stops it from opening, for the silent tests; the text is
then only logged, and :data:`shown` keeps it, so a test can check what would have shown.
"""
from __future__ import annotations

import ctypes
import logging
import os

log = logging.getLogger('msgbox')

#: Set by the tests, so a message box never opens during them.
OFF_ENV = 'MINDSIGHT_NO_MESSAGEBOX'
TITLE = 'Mindsight'

MB_OK = 0x0
MB_ICONERROR = 0x10
MB_SETFOREGROUND = 0x10000
MB_TOPMOST = 0x40000

#: Every message that would have been shown while message boxes are off.
shown: list[str] = []


def error(text: str) -> None:
    """Show ``text`` in an error box, and wait until the player closes it."""
    log.info('message box: %s', text.replace('\n', ' '))
    if os.environ.get(OFF_ENV):
        shown.append(text)
        return
    try:
        ctypes.windll.user32.MessageBoxW(None, text, TITLE,
                                         MB_OK | MB_ICONERROR | MB_SETFOREGROUND | MB_TOPMOST)
    except Exception:
        log.exception('the message box could not be shown')
