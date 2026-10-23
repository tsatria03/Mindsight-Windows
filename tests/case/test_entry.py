"""Mindsight.py: its options, the logs, crash.txt, the message boxes, and a silent run."""
import _quiet  # noqa: F401  (first, before any of the game)

import logging
import os

import Mindsight
from mindsight import app as app_module
from mindsight import paths
from mindsight.platform import msgbox


def logs():
    return paths.logs_dir()


def read(name):
    with open(os.path.join(logs(), name), encoding='utf-8') as f:
        return f.read()


def drop_log_handlers():
    """Each main() adds a log file of its own; take them off between runs."""
    root = logging.getLogger()
    for handler in list(root.handlers):
        if isinstance(handler, logging.FileHandler):
            root.removeHandler(handler)
            handler.close()


def test_options():
    o = Mindsight.parse_args(['--debug', '--scene', '47', '-v', '--exit-after', '1.5'])
    assert o.debug and o.scene == 47 and o.verbose and o.exit_after == 1.5
    o = Mindsight.parse_args([])
    assert not o.debug and o.scene is None and not o.verbose and o.exit_after is None


def test_scene_needs_debug_and_a_real_scene():
    assert Mindsight.scene_from_options(Mindsight.parse_args(['--scene', '47']), False) is None
    assert Mindsight.scene_from_options(Mindsight.parse_args(['--scene', '47']), True) == 47
    assert Mindsight.scene_from_options(Mindsight.parse_args(['--scene', '0']), True) == 0
    assert Mindsight.scene_from_options(Mindsight.parse_args(['--scene', '55']), True) == 55
    assert Mindsight.scene_from_options(Mindsight.parse_args(['--scene', '56']), True) is None
    assert Mindsight.scene_from_options(Mindsight.parse_args(['--scene', '-1']), True) is None


def test_debug_only_from_source():
    options = Mindsight.parse_args(['--debug'])
    assert Mindsight.debug_from_options(options) is True
    saved = paths.FROZEN
    try:
        paths.FROZEN = True
        assert Mindsight.debug_from_options(options) is False
    finally:
        paths.FROZEN = saved


def test_crash_file():
    path = Mindsight.write_crash('Traceback: something broke\n')
    text = read('crash.txt')
    assert path == os.path.join(logs(), 'crash.txt')
    assert text.startswith('Mindsight stopped because of an error.')
    assert 'Version: %s' % paths.version() in text and 'Running from: source' in text
    assert text.endswith('Traceback: something broke\n')


def test_crash_message_names_the_folder():
    assert logs() in Mindsight.crash_message()
    assert 'crash.txt' in Mindsight.crash_message()


def test_a_silent_run_and_the_log_before_it():
    drop_log_handlers()
    assert Mindsight.main(['--exit-after', '0.3']) == 0
    first = read('log.txt')
    assert 'game data: ' in first and 'Mindsight closed' in first
    drop_log_handlers()
    assert Mindsight.main(['--debug', '--scene', '12', '--exit-after', '0.3']) == 0
    assert read('log.old.txt') == first
    second = read('log.txt')
    assert 'debug mode is on' in second and 'start at scene 12' in second
    drop_log_handlers()


def test_missing_recordings_show_their_message_box():
    msgbox.shown.clear()
    saved = paths.EXE_DIR, paths.ROOT
    try:
        paths.EXE_DIR = paths.ROOT = os.path.join(_quiet.FOLDER, 'nowhere')
        assert Mindsight.main(['--exit-after', '0.3']) == 1
    finally:
        paths.EXE_DIR, paths.ROOT = saved
        drop_log_handlers()
    assert len(msgbox.shown) == 1 and "recordings were not found" in msgbox.shown[0]
    assert "recordings were not found" in read('crash.txt')


def test_an_error_shows_the_crash_message_box():
    msgbox.shown.clear()
    saved = app_module.App.run

    def broken(self, first_screen, pygame):
        raise RuntimeError('a test error')
    try:
        app_module.App.run = broken
        assert Mindsight.main([]) == 1
    finally:
        app_module.App.run = saved
        drop_log_handlers()
    assert msgbox.shown == [Mindsight.crash_message()]
    assert 'RuntimeError: a test error' in read('crash.txt')


def test_message_boxes_stay_shut_in_tests():
    msgbox.shown.clear()
    msgbox.error('A test message.')
    assert msgbox.shown == ['A test message.']


_quiet.run_tests(globals())
