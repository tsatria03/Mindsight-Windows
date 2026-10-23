"""The story screen, on a stand-in for the audio: opening on the main menu, the rules done
on the audio, the input lock and the cue, Solved and the buzz, --scene, Escape in the
menus, the window's lines, and a silent run of the game."""
import _quiet  # noqa: F401  (first, before any of the game)

import logging
import types

from mindsight.app import App
from mindsight.game import scenes as S
from mindsight.game.story_screen import StoryScreen
from mindsight.platform.runloop import RunLoop


class FakeScene:
    """The scene player: what it plays, where it is, and its end, by hand."""
    def __init__(self, log):
        self.log = log
        self.recording, self.loop, self.at, self.on_end = None, False, 0.0, None
        self.paused = False

    def play(self, recording, start=0.0, loop=False, on_end=None):
        self.recording, self.loop, self.at, self.on_end = recording, loop, start, on_end
        self.log.append(('play', recording.name, start, loop))

    def stop(self):
        self.recording = None

    @property
    def playing(self):
        return self.recording is not None

    def position(self):
        return self.at

    def end(self):
        callback, self.on_end = self.on_end, None
        callback()


class FakeAudio:
    def __init__(self):
        self.log = []
        self.scene = FakeScene(self.log)
        self.ok = True

    def play_solved(self, recording):
        self.log.append(('solved', recording.name))

    def play_buzz(self):
        self.log.append(('buzz',))

    def update(self):
        pass


def screen(start_scene=None):
    app = App(loop=RunLoop())
    audio = FakeAudio()
    s = StoryScreen(app, audio, start_scene=start_scene)
    app.stack.push(s)
    return app, audio, s


def test_it_opens_on_the_main_menu_and_waits():
    app, audio, s = screen()
    assert audio.log == [('play', '01_main_menu_list', 0.0, False)]
    app.key_down('up', [])
    assert len(audio.log) == 1                       # locked until the menu ends
    audio.scene.end()
    assert audio.log[-1] == ('buzz',)
    app.key_down('w', [])
    assert audio.log[-1] == ('play', '02_new_game_menu_choice', 0.0, False)


def test_the_new_game_and_on_into_the_story():
    app, audio, s = screen()
    audio.scene.end()
    app.key_down('up', [])
    audio.scene.end()
    app.key_down('up', [])
    assert audio.log[-1][1] == '02b_new_game_confirmation'
    audio.scene.end()
    assert audio.log[-1] == ('play', '08_introductory_scene', 0.0, False)


def test_the_office_puzzle():
    app, audio, s = screen(start_scene=11)
    assert audio.log == [('play', '10_solve_office_puzzle', 0.0, False)]
    audio.scene.at = 21.0
    app.key_down('right', [])
    s.update()
    assert len(audio.log) == 1                       # before the gate: nothing, no buzz yet
    audio.scene.at = 22.0
    s.update()
    s.update()
    assert audio.log[1:] == [('buzz',)]              # once
    audio.scene.at = 22.5
    app.key_down('d', [])
    assert audio.log[2:] == [('solved', 'Solved'), ('play', '11_street_puzzle_leadin', 0.0, False)]


def test_loops_play_looping():
    app, audio, s = screen(start_scene=34)
    audio.scene.end()
    assert audio.log[-2:] == [('play', 'pirahnaloop', 0.0, True), ('buzz',)]


def test_a_scene_run_never_saves_and_a_full_run_would(caplog=None):
    records = []
    handler = logging.Handler()
    handler.emit = records.append
    logging.getLogger('story').addHandler(handler)
    logging.getLogger('story').setLevel(logging.INFO)
    try:
        app, audio, s = screen(start_scene=8)
        audio.scene.end()
        app2, audio2, s2 = screen()
        s2.save(9)
    finally:
        logging.getLogger('story').removeHandler(handler)
    text = [r.getMessage() for r in records]
    assert any('not saving scene 9' in t for t in text)
    assert any('would save scene 9' in t for t in text)


def test_escape_quits_in_the_menus_only():
    app, audio, s = screen()
    assert s.escape_quits
    app.key_down('escape', [])
    assert not app.running
    app, audio, s = screen(start_scene=8)
    assert not s.escape_quits
    app.key_down('escape', [])
    assert app.running


def test_the_window_lines():
    app, audio, s = screen(start_scene=47)
    assert 'Scene 47: roof puzzle iteration 1' in s.lines()
    assert 'Listening' in s.lines()
    audio.scene.at = 7.5
    assert 'Your turn' in s.lines()


def test_the_game_runs_silently_on_the_story_screen():
    import Mindsight
    root = logging.getLogger()
    assert Mindsight.main(['--exit-after', '0.5']) == 0
    for h in list(root.handlers):
        if isinstance(h, logging.FileHandler):
            root.removeHandler(h)
            h.close()
    from mindsight import paths
    with open(paths.user_path('logs', 'log.txt'), encoding='utf-8') as f:
        text = f.read()
    assert 'opened story' in text and 'scene 1, main menu list' in text and 'Mindsight closed' in text


_quiet.run_tests(globals())
