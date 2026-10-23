"""Try plan 2's foundation by ear (aidocks/plans/foundation_plan.md).

    python tests/interact/foundation_check.py

It speaks through NVDA, as every tool here does; the game itself never speaks. It keeps
its own save under %APPDATA%\\Mindsight\\interact\\foundation_check, so the game's own
save and logs are untouched.

Keys:
    1        show the message box for missing recordings, as the game would
    2        show the message box for an error that stops the game, as the game would
    H        say the keys again
    Escape   quit

The message boxes are the game's own, with the game's own text: only their cause is
pretend. Key 2 writes a crash.txt in this tool's logs folder, saying the game did not
really stop, so the file the message names is there to open.
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
from mindsight.platform import msgbox  # noqa: E402
import _nvda  # noqa: E402

KEYS = ('Foundation check. Press 1 for the missing recordings message, 2 for the crash '
        'message, H to hear the keys again, or Escape to quit.')


def show_missing():
    _nvda.say('Showing the missing recordings message.')
    msgbox.error(paths.missing_data_message())
    _nvda.say('The message box closed.')


def show_crash():
    Mindsight.write_crash('This crash.txt was written by foundation_check.py, to try the crash '
                          'message. The game did not really stop.\n')
    _nvda.say('Showing the crash message.')
    msgbox.error(Mindsight.crash_message())
    _nvda.say('The message box closed.')


def run(exit_after=None):
    import pygame
    pygame.display.init()
    try:
        pygame.display.set_caption('Mindsight foundation check')
        screen = pygame.display.set_mode((640, 360))
        clock = pygame.time.Clock()
        started = pygame.time.get_ticks()
        _nvda.say(KEYS)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type != pygame.KEYDOWN:
                    continue
                if event.key == pygame.K_ESCAPE:
                    _nvda.say('Quitting the foundation check.')
                    return
                if event.key in (pygame.K_1, pygame.K_KP1):
                    show_missing()
                elif event.key in (pygame.K_2, pygame.K_KP2):
                    show_crash()
                elif event.key == pygame.K_h:
                    _nvda.say(KEYS)
            if exit_after is not None and pygame.time.get_ticks() - started >= exit_after * 1000:
                return
            screen.fill((0, 0, 0))
            pygame.display.flip()
            clock.tick(60)
    finally:
        pygame.display.quit()


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    exit_after = float(argv[argv.index('--exit-after') + 1]) if '--exit-after' in argv else None
    Mindsight.start_log(verbose=False)
    Mindsight.log.info('foundation check starting; save folder %s', paths.user_dir())
    try:
        run(exit_after)
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
