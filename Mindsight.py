"""Mindsight for Windows.

    python Mindsight.py

Options (aidocks/plans/foundation_plan.md):

    --debug               debug mode for this run (source runs only)
    --scene N             start at scene N, 0 to 55, in debug mode only; that run never saves
    -v                    a more detailed log
    --exit-after SECONDS  quit by itself after that many seconds

Every run writes logs/log.txt in the save folder, %APPDATA%\\Mindsight, keeping the run
before as log.old.txt. An error that stops the game writes logs/crash.txt and shows a
Windows message box, which the screen reader reads, so a player who cannot see the
screen knows why the game closed: missing recordings, no sound device, or any other error.
"""
from __future__ import annotations

import argparse
import datetime
import logging
import os
import platform
import sys
import traceback

os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')

from mindsight import paths  # noqa: E402
from mindsight.platform import msgbox  # noqa: E402
from mindsight.platform.audio import NoSound  # noqa: E402

log = logging.getLogger('mindsight')

#: The scenes, by the original's numbering (aidocks/general/project_original_behaviour.md).
FIRST_SCENE, LAST_SCENE = 0, 55


def crash_message() -> str:
    """What the player is told when an error stops the game, naming crash.txt."""
    return ('Mindsight has stopped because of an error.\n\n'
            'The details are in crash.txt, in this folder:\n%s' % paths.logs_dir())


def parse_args(argv=None):
    parser = argparse.ArgumentParser(prog='Mindsight', description='Mindsight for Windows')
    parser.add_argument('--debug', action='store_true', help='debug mode for this run (source runs only)')
    parser.add_argument('--scene', metavar='N', type=int,
                        help='start at scene N, 0 to 55, in debug mode only; that run never saves')
    parser.add_argument('-v', '--verbose', action='store_true', help='a more detailed log')
    parser.add_argument('--exit-after', metavar='SECONDS', type=float,
                        help='quit by itself after that many seconds')
    return parser.parse_args(argv)


def start_log(verbose):
    """logs/log.txt for this run, keeping the run before as log.old.txt."""
    folder = paths.logs_dir()
    current = os.path.join(folder, 'log.txt')
    old = os.path.join(folder, 'log.old.txt')
    try:
        if os.path.exists(current):
            os.replace(current, old)
    except OSError:
        pass
    handler = logging.FileHandler(current, encoding='utf-8')
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-7s %(name)-9s %(message)s',
                                           '%H:%M:%S'))
    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(logging.DEBUG if verbose else logging.INFO)
    return current


def write_crash(error_text):
    """logs/crash.txt, for the last error that stopped the game."""
    path = os.path.join(paths.logs_dir(), 'crash.txt')
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write('Mindsight stopped because of an error.\n')
            f.write('When: %s\n' % datetime.datetime.now().isoformat(timespec='seconds'))
            f.write('Version: %s\n' % paths.version())
            f.write('Python: %s\n' % sys.version.replace('\n', ' '))
            f.write('System: %s\n' % platform.platform())
            f.write('Running from: %s\n\n' % ('a build' if paths.FROZEN else 'source'))
            f.write(error_text)
    except OSError:
        pass
    return path


def debug_from_options(options) -> bool:
    """Debug mode, which only a run from source can have."""
    if options.debug and paths.FROZEN:
        log.warning('--debug works only when running from source, so it is ignored')
        return False
    return bool(options.debug)


def scene_from_options(options, debug):
    """The scene ``--scene`` names, when it is allowed and in range; or None."""
    if options.scene is None:
        return None
    if not debug:
        log.warning('--scene works only in debug mode, so it is ignored')
        return None
    if not FIRST_SCENE <= options.scene <= LAST_SCENE:
        log.warning('there is no scene %d, only %d to %d, so --scene is ignored',
                    options.scene, FIRST_SCENE, LAST_SCENE)
        return None
    return options.scene


def main(argv=None):
    options = parse_args(argv)
    start_log(options.verbose)
    log.info('Mindsight %s starting, from %s', paths.version(), 'a build' if paths.FROZEN else 'source')
    try:
        # compiler.py --test looks for this line, to know a build found its data.
        log.info('game data: %s', paths.game())
        debug = debug_from_options(options)
        if debug:
            log.info('debug mode is on')
        scene = scene_from_options(options, debug)
        if scene is not None:
            log.info('the game will start at scene %d, and this run will never save', scene)
        import pygame
        from mindsight.app import App
        from mindsight.game.story_screen import StoryScreen
        from mindsight.platform.audio import Audio
        audio = Audio.shared()
        audio.open(pygame)
        try:
            app = App(options, debug=debug, start_scene=scene)
            app.run(StoryScreen(app, audio, start_scene=scene), pygame)
        finally:
            audio.close()
        log.info('Mindsight closed')
        return 0
    except NoSound as missing:
        log.error('%s', missing)
        write_crash(str(missing) + '\n')
        msgbox.error(str(missing))
        return 1
    except paths.MissingData as missing:
        text = str(missing)
        log.error('%s', text)
        write_crash(text + '\n')
        msgbox.error(text)
        return 1
    except Exception:
        text = traceback.format_exc()
        log.error('the game stopped because of an error:\n%s', text)
        write_crash(text)
        msgbox.error(crash_message())
        return 1
    finally:
        logging.shutdown()


if __name__ == '__main__':
    sys.exit(main())
