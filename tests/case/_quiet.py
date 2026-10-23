"""Keep the tests off the real save, and silent, and run them.

Every test file imports this first, before any of the game. It:

* points ``MINDSIGHT_USER_DIR`` at a fresh folder of its own, so logs and saves are
  written there and never to ``%APPDATA%\\Mindsight``, and deletes that folder when the
  run ends;
* sets ``MINDSIGHT_NO_MESSAGEBOX``, so a message box never opens: its text is only kept
  in ``msgbox.shown``, for a test to check;
* sets ``MINDSIGHT_SILENT``, so a by-ear tool's speech (tests/interact/_nvda.py) only
  prints, never reaching NVDA;
* gives SDL a dummy audio driver and a dummy display, so nothing is heard and no window
  opens for a screen reader to announce.

Each is set outright, whatever the shell has set, so a test is silent and off the real
save wherever it is run from. ``test_paths.py`` fails if a test file does not import this.
It is not a test itself; the leading underscore keeps it apart.

``run_tests(globals())`` at the end of a test file runs its ``test_`` functions in name
order and prints one line for each, then the total.
"""
from __future__ import annotations

import atexit
import logging
import os
import shutil
import sys
import tempfile
import traceback

FOLDER = tempfile.mkdtemp(prefix='mindsight_test_save_')
QUIET = {
    'MINDSIGHT_USER_DIR': FOLDER,
    'MINDSIGHT_NO_MESSAGEBOX': '1',
    'MINDSIGHT_SILENT': '1',
    'SDL_AUDIODRIVER': 'dummy',
    'SDL_VIDEODRIVER': 'dummy',
    'PYGAME_HIDE_SUPPORT_PROMPT': '1',
}
os.environ.update(QUIET)
atexit.register(shutil.rmtree, FOLDER, True)
# The game's log goes nowhere in a test, so the errors tests cause on purpose do not
# crowd out the test lines.
logging.getLogger().addHandler(logging.NullHandler())

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def run_tests(namespace):
    """Run every ``test_`` function in ``namespace``; exit 1 if any failed."""
    tests = [(name, fn) for name, fn in sorted(namespace.items())
             if name.startswith('test_') and callable(fn)]
    bad = 0
    for name, fn in tests:
        try:
            fn()
            print('ok    %s' % name)
        except AssertionError as error:
            bad += 1
            print('FAIL  %s: %s' % (name, error or traceback.format_exc().strip().splitlines()[-2]))
        except Exception as error:
            bad += 1
            print('ERROR %s: %r' % (name, error))
            traceback.print_exc()
    print('%d/%d passed' % (len(tests) - bad, len(tests)))
    sys.exit(1 if bad else 0)
