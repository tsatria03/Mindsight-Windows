"""The stack of screens the main loop drives.

The top screen gets every key and is drawn in the window. A screen can open another on top
(``stack.push``), close itself (``stack.pop``), or put another in its place
(``stack.replace``); closing the last one ends the game (aidocks/plans/foundation_plan.md).

A screen hears a key in one of three ways, from the App:

* ``gesture``: a game key with no modifier held, as the gesture it stands for
  (platform/keys.py): a swipe, or the double tap's pause;
* ``ignored_key``: a game key held with a modifier, which the game never acts on;
* ``other_key``: any other key, which the game itself never acts on, though a by-ear
  tool in tests/interact/ may.
"""
from __future__ import annotations

import logging

log = logging.getLogger('screens')


class Screen:
    """What every screen has. Subclasses fill in what they need."""

    #: A short name for the log.
    name = 'screen'

    def __init__(self, app):
        self.app = app

    @property
    def stack(self):
        return self.app.stack

    def opened(self):
        """Put on top of the stack, or back on top after the one above it closed."""

    def closed(self):
        """Taken off the stack for good."""

    def covered(self):
        """Another screen was opened on top of this one."""

    def gesture(self, gesture):
        """A swipe or the double tap: one of platform/keys.py's gestures."""

    def ignored_key(self, key, mods):
        """A game key held with a modifier: pygame's name for it, and the modifiers held."""

    def other_key(self, key, mods):
        """Any other key: pygame's name for it, and the modifiers held."""

    def update(self):
        """Called once a frame while on top."""

    def focus_lost(self):
        """The game's window lost the keyboard."""

    def focus_gained(self):
        """The game's window has the keyboard again."""

    def lines(self):
        """What the window shows, for a sighted helper."""
        return []


class ScreenStack:
    def __init__(self):
        self.screens = []

    @property
    def top(self):
        return self.screens[-1] if self.screens else None

    @property
    def empty(self):
        return not self.screens

    def push(self, screen):
        if self.top is not None:
            self.top.covered()
        self.screens.append(screen)
        log.info('opened %s', screen.name)
        screen.opened()

    def pop(self):
        """Close the top screen and reopen the one below it."""
        if not self.screens:
            return
        screen = self.screens.pop()
        log.info('closed %s', screen.name)
        screen.closed()
        if self.top is not None:
            self.top.opened()

    def replace(self, screen):
        """Put ``screen`` in place of the top one."""
        if self.screens:
            old = self.screens.pop()
            log.info('closed %s', old.name)
            old.closed()
        self.screens.append(screen)
        log.info('opened %s', screen.name)
        screen.opened()

    def reset(self, screen):
        """Close every screen and open ``screen`` alone."""
        self.clear()
        self.push(screen)

    def clear(self):
        while self.screens:
            screen = self.screens.pop()
            log.info('closed %s', screen.name)
            screen.closed()
