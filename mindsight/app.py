"""The game's main loop: the window, the keys, the timers and the stack of screens.

``Mindsight.py`` builds an ``App`` and runs it. Every frame, sixty a second, it:

1. reads the window's events: closing the window quits, losing or regaining the keyboard
   tells the top screen, and a key goes to the top screen (ui/screens.py), as a gesture,
   an ignored key or another key (platform/keys.py);
2. runs the timers that are due (platform/runloop.py);
3. draws the top screen's text in the window, for a sighted helper. The game says
   nothing of its own: the recordings are the real interface.
"""
from __future__ import annotations

import logging

from .platform import keys
from .platform.runloop import RunLoop
from .ui.screens import ScreenStack

log = logging.getLogger('app')

TITLE = 'Mindsight'
WINDOW_SIZE = (800, 500)
FPS = 60
#: The window's text, in lines from the top; the rest is cut.
MAX_LINES = 22


class App:
    def __init__(self, options=None, debug=False, start_scene=None, loop=None, title=TITLE):
        self.options = options
        self.debug = bool(debug)
        #: The scene --scene named, in debug mode; the story engine starts there.
        self.start_scene = start_scene
        self.loop = loop or RunLoop.main()
        self.stack = ScreenStack()
        self.running = True
        self.pygame = None          # pygame, once run() has opened the window
        self.title = title

    def window_title(self):
        return '%s (debug)' % self.title if self.debug else self.title

    def quit(self):
        self.running = False

    # ---- keys -----------------------------------------------------------
    def key_down(self, key, mods):
        """A key pressed: pygame's name for it, and the modifiers held."""
        if key in keys.MODIFIER_KEYS:
            return                          # Shift and the rest only go with another key
        top = self.stack.top
        if top is None:
            return
        gesture = keys.gesture(key, mods)
        if gesture is not None:
            log.debug('key %s: %s', key, gesture)
            top.gesture(gesture)
        elif keys.is_game_key(key):
            log.debug('key %s ignored, with %s held', key, '+'.join(mods))
            top.ignored_key(key, mods)
        else:
            top.other_key(key, mods)

    # ---- running --------------------------------------------------------
    def run(self, first_screen, pygame):
        """The main loop. Returns when the game quits or the last screen closes."""
        pygame.display.init()
        pygame.font.init()
        pygame.display.set_caption(self.window_title())
        screen = pygame.display.set_mode(WINDOW_SIZE)
        self.pygame = pygame
        font = pygame.font.SysFont('consolas', 18) or pygame.font.Font(None, 22)
        clock = pygame.time.Clock()
        exit_after = getattr(self.options, 'exit_after', None)
        if exit_after:
            self.loop.after(exit_after, self.quit)
            log.info('quitting by itself after %g seconds', exit_after)
        self.stack.push(first_screen)
        try:
            while self.running and not self.stack.empty:
                for event in pygame.event.get():
                    self.handle_event(event, pygame)
                if self.stack.top is not None:
                    self.stack.top.update()
                self.loop.pump()
                self.draw(screen, font, pygame)
                clock.tick(FPS)
        finally:
            self.stack.clear()
            pygame.display.quit()

    def handle_event(self, event, pygame):
        if event.type == pygame.QUIT:
            self.quit()
        elif event.type == getattr(pygame, 'WINDOWFOCUSLOST', None):
            if self.stack.top is not None:
                self.stack.top.focus_lost()
        elif event.type == getattr(pygame, 'WINDOWFOCUSGAINED', None):
            if self.stack.top is not None:
                self.stack.top.focus_gained()
        elif event.type == pygame.KEYDOWN:
            self.key_down(pygame.key.name(event.key), keys.mods_from_pygame(event.mod, pygame))

    def draw(self, screen, font, pygame):
        """The top screen's text, for a sighted helper."""
        screen.fill((0, 0, 0))
        lines = list(self.stack.top.lines() if self.stack.top is not None else [])[:MAX_LINES]
        y = 10
        for line in lines:
            if line:
                screen.blit(font.render(str(line), True, (230, 230, 230)), (12, y))
            y += font.get_linesize()
        pygame.display.flip()
