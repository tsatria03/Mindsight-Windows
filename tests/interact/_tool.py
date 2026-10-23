"""What every by-ear tool in tests/interact/ shares (aidocks/general/feedback_test_tools_in_interact.md).

* Its own save, ``%APPDATA%\\Mindsight\\interact\\<tool>``, set before any of the game is
  imported, so the game's own save and logs are untouched. :func:`own_save` sets it.
* The game's main loop, in :class:`ToolApp`, where Escape quits, as it does in every
  tool, before the game's keys see it; Alt+F4 or closing the window quits too.
* :func:`run`, which starts the log, runs the tool, and never closes silently on an error:
  it writes crash.txt and says why, through NVDA.
* ``--exit-after SECONDS``, for starting a tool silently before it is handed over.
"""
from __future__ import annotations

import os
import sys
import traceback

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def own_save(tool):
    """Point the save folder at this tool's own, unless the caller already set one, and
    put the repository on the path. Call it before importing any of the game."""
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
    if not os.environ.get('MINDSIGHT_USER_DIR'):
        base = os.environ.get('APPDATA') or os.path.expanduser('~')
        os.environ['MINDSIGHT_USER_DIR'] = os.path.join(base, 'Mindsight', 'interact', tool)


def tool_app_class():
    from mindsight.app import App

    class ToolApp(App):
        """The game's App, but Escape quits, before the game's keys see it."""

        def key_down(self, key, mods):
            if key == 'escape' and not mods and self.stack.top is not None:
                quit_ = getattr(self.stack.top, 'quit', None)
                if quit_ is not None:
                    quit_()
                else:
                    self.quit()
                return
            super().key_down(key, mods)
    return ToolApp


def run(title, make_screen, argv=None, before=None, after=None, debug=False):
    """Run a tool: ``make_screen(app)`` is its first screen. ``before(pygame)`` runs once
    the log has started and ``after()`` once the window has closed, such as opening and
    closing the sound. ``debug`` runs it in the game's debug mode, its title saying so."""
    import Mindsight
    import _nvda
    from mindsight import paths
    argv = sys.argv[1:] if argv is None else argv
    exit_after = float(argv[argv.index('--exit-after') + 1]) if '--exit-after' in argv else None
    Mindsight.start_log(verbose=False)
    Mindsight.log.info('%s starting; save folder %s', title, paths.user_dir())
    try:
        import pygame
        if before is not None:
            before(pygame)
        try:
            app = tool_app_class()(Mindsight.parse_args(['--exit-after', str(exit_after)] if exit_after else []),
                                   title=title, debug=debug)
            app.run(make_screen(app), pygame)
        finally:
            if after is not None:
                after()
        Mindsight.log.info('%s closed', title)
        return 0
    except Exception:
        text = traceback.format_exc()
        Mindsight.log.error('%s stopped because of an error:\n%s', title, text)
        path = Mindsight.write_crash(text)
        _nvda.say('%s stopped because of an error. The details are in %s.' % (title, path))
        return 1
