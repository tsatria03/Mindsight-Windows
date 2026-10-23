"""The screen the game opens on until the story engine (aidocks/plans/foundation_plan.md).

It shows the last key's meaning in the window, such as "Swipe up", and writes it to the
log. It says nothing, since the game has no speech: to hear the keys, use
tests/interact/foundation_check.py.
"""
from __future__ import annotations

import logging

from ..platform import keys
from ..ui.screens import Screen

log = logging.getLogger('standin')


class StandInScreen(Screen):
    name = 'stand-in screen'

    def __init__(self, app):
        super().__init__(app)
        self.last = 'No key yet.'
        self.focus = 'The window has the keyboard.'

    def gesture(self, gesture):
        self.last = keys.LABELS[gesture] + '.'
        log.info('key: %s', keys.LABELS[gesture])

    def ignored_key(self, key, mods):
        self.last = '%s: ignored, with a modifier held.' % keys.key_label(key, mods)
        log.info('key ignored: %s', keys.key_label(key, mods))

    def focus_lost(self):
        self.focus = 'The window lost the keyboard.'
        log.info('focus lost')

    def focus_gained(self):
        self.focus = 'The window has the keyboard.'
        log.info('focus gained')

    def lines(self):
        return [
            self.app.window_title(),
            '',
            'A stand-in, until the story engine is built.',
            'The arrow keys or W, A, S and D are the four swipes.',
            'Escape, Enter or P is the double tap, which pauses and resumes.',
            '',
            'Last key: ' + self.last,
            self.focus,
            '',
            'Close the window or press Alt+F4 to quit.',
        ]
