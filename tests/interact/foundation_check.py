"""Try plan 2's foundation by ear (aidocks/plans/foundation_plan.md).

    python tests/interact/foundation_check.py

It runs on the game's own main loop, keys and timer loop, and speaks through NVDA, as
every tool here does; the game itself never speaks. It keeps its own save under
%APPDATA%\\Mindsight\\interact\\foundation_check, so the game's own save and logs are
untouched.

The game's keys, each spoken with its meaning:
    Arrow keys, or W, A, S and D    the four swipes
    Escape, Enter or P              the double tap, which pauses and resumes
    Any of them with Shift, Control, Alt or the Windows key held: ignored, as in the game

The tool's own keys:
    1        show the message box for missing recordings, as the game would
    2        show the message box for an error that stops the game, as the game would
    T        start a 10-second countdown on the timer loop, spoken each second
    Space    hold the timer loop, or resume it
    H        say the keys again
    F10      quit

Switching away from the window, and back, is spoken too. The message boxes are the
game's own, with the game's own text: only their cause is pretend. Key 2 writes a
crash.txt in this tool's logs folder, saying the game did not really stop, so the file
the message names is there to open.
"""
from __future__ import annotations

import os
import sys
import traceback

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
if not os.environ.get('MINDSIGHT_USER_DIR'):
    base = os.environ.get('APPDATA') or os.path.expanduser('~')
    os.environ['MINDSIGHT_USER_DIR'] = os.path.join(base, 'Mindsight', 'interact', 'foundation_check')

import Mindsight  # noqa: E402
from mindsight import paths  # noqa: E402
from mindsight.app import App  # noqa: E402
from mindsight.platform import keys, msgbox, runloop  # noqa: E402
from mindsight.ui.screens import Screen  # noqa: E402
import _nvda  # noqa: E402

KEYS = ('Foundation check. The arrow keys or W, A, S and D are the swipes, and Escape, Enter or P '
        'is the pause. Press 1 for the missing recordings message, 2 for the crash message, '
        'T for a countdown, Space to hold or resume the timers, H to hear the keys again, '
        'or F10 to quit.')
COUNTDOWN = 10
#: Seconds after a message box closes in which focus changes are not spoken: the box
#: itself takes the keyboard and gives it back, and NVDA has just read it.
QUIET_AFTER_BOX = 1.0


class CheckScreen(Screen):
    name = 'foundation check'

    def __init__(self, app):
        super().__init__(app)
        self.last = 'No key yet.'
        self.countdown = None
        self.left = 0
        self.quiet_until = 0.0

    def opened(self):
        _nvda.say(KEYS)

    def say(self, text):
        self.last = text
        _nvda.say(text)

    # ---- the game's keys --------------------------------------------------
    def gesture(self, gesture):
        self.say(keys.LABELS[gesture] + '.')

    def ignored_key(self, key, mods):
        self.say('%s, ignored.' % keys.key_label(key, mods))

    # ---- the tool's keys --------------------------------------------------
    def other_key(self, key, mods):
        if mods:
            return
        if key in ('1', '[1]'):
            self.show(paths.missing_data_message, 'the missing recordings message')
        elif key in ('2', '[2]'):
            Mindsight.write_crash('This crash.txt was written by foundation_check.py, to try the '
                                  'crash message. The game did not really stop.\n')
            self.show(Mindsight.crash_message, 'the crash message')
        elif key == 't':
            self.start_countdown()
        elif key == 'space':
            self.hold_or_resume()
        elif key == 'h':
            self.say(KEYS)
        elif key == 'f10':
            _nvda.say('Quitting the foundation check.')
            self.app.quit()

    def show(self, message, what):
        self.say('Showing %s.' % what)
        msgbox.error(message())
        self.quiet_until = runloop.clock() + QUIET_AFTER_BOX
        self.say('The message box closed.')

    def start_countdown(self):
        if self.countdown is not None:
            self.countdown.cancel()
        self.left = COUNTDOWN
        self.say('Counting down from %d.' % COUNTDOWN)
        self.countdown = self.app.loop.every(1.0, self.tick)

    def tick(self):
        self.left -= 1
        if self.left > 0:
            self.say(str(self.left))
        else:
            self.countdown.cancel()
            self.countdown = None
            self.say('The countdown has finished.')

    def hold_or_resume(self):
        if self.app.loop.held:
            self.app.loop.resume()
            self.say('The timers are running again.')
        else:
            self.app.loop.hold()
            self.say('The timers are held.')

    # ---- the window ---------------------------------------------------------
    def focus_lost(self):
        if runloop.clock() >= self.quiet_until:
            self.say('The window lost the keyboard.')

    def focus_gained(self):
        if runloop.clock() >= self.quiet_until:
            self.say('The window has the keyboard again.')

    def lines(self):
        return ['Mindsight foundation check', '', 'Last: ' + self.last,
                'Timers held.' if self.app.loop.held else 'Timers running.']


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    exit_after = float(argv[argv.index('--exit-after') + 1]) if '--exit-after' in argv else None
    Mindsight.start_log(verbose=False)
    Mindsight.log.info('foundation check starting; save folder %s', paths.user_dir())
    try:
        import pygame
        app = App(Mindsight.parse_args(['--exit-after', str(exit_after)] if exit_after else []),
                  title='Mindsight foundation check')
        app.run(CheckScreen(app), pygame)
        Mindsight.log.info('foundation check closed')
        return 0
    except Exception:
        # A tool never closes silently on an error: it writes crash.txt and says why.
        text = traceback.format_exc()
        Mindsight.log.error('the foundation check stopped because of an error:\n%s', text)
        path = Mindsight.write_crash(text)
        _nvda.say('The foundation check stopped because of an error. The details are in %s.' % path)
        return 1


if __name__ == '__main__':
    sys.exit(main())
