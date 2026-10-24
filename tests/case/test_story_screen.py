"""The story screen, on a stand-in for the audio: opening on the main menu, the rules done
on the audio, the input lock and the cue, Solved and the buzz, --scene, Escape in the
menus, the window's lines, failing and the Rewind's retries, the piranha windows on a
real looping player, and a silent run of the game."""
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

    def pause(self):
        if self.playing:
            self.paused = True
            self.log.append(('pause',))

    def resume(self):
        if self.paused:
            self.paused = False
            self.log.append(('resume', self.at))

    def step_back(self, seconds=3.0):
        if self.paused:
            self.at = max(0.0, self.at - seconds)

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

    def play_clip(self, recording):
        self.log.append(('clip', recording.name))

    def stop_clip(self):
        self.log.append(('stop clip',))

    def focus_gained(self, welcome_back):
        self.scene.step_back()
        self.play_clip(welcome_back)

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


def test_failing_a_street_round_and_the_rewind():
    app, audio, s = screen(start_scene=15)
    audio.scene.at = 10.5
    app.key_down('down', [])
    assert audio.log[-1] == ('play', '16_street_puzzle_fail', 0.0, False)
    audio.scene.end()
    assert audio.log[-1] == ('play', 'Rewind', 0.0, False)
    audio.scene.end()
    assert audio.log[-1] == ('play', '11_street_puzzle_leadin2', 20.4, False)


def test_a_roof_round_running_out():
    app, audio, s = screen(start_scene=47)
    audio.scene.end()
    assert audio.log[-1] == ('play', '41_roof_puzzle_fail', 0.0, False)
    audio.scene.end()
    audio.scene.end()
    assert audio.log[-1] == ('play', '36_roof_entry_scene', 112.0, False)


def test_the_piranha_windows_on_a_real_looping_player():
    import pygame
    from mindsight.platform import runloop
    from mindsight.platform.audio import Audio

    class Clock:
        now = 500.0

        def __call__(self):
            return self.now
    real_clock = runloop.clock
    clock = runloop.clock = Clock()
    audio = Audio()
    audio.open(pygame)
    try:
        app = App(loop=RunLoop())
        s = StoryScreen(app, audio, start_scene=35)
        app.stack.push(s)
        loop_length = audio.scene.recording.length
        clock.now += loop_length + 16           # once round, then inside the first window
        assert abs(s.position() - 16) < 1e-6
        app.key_down('a', [])
        assert s.story.scene == 36 and audio.scene.recording.name == '28_pirahna_puzzle_pass'
        s2 = StoryScreen(App(loop=RunLoop()), audio, start_scene=35)
        s2.app.stack.push(s2)
        clock.now += 21                         # outside every window
        s2.gesture('up')
        assert s2.story.scene == 37 and s2.story.failure == 35
    finally:
        audio.close()
        runloop.clock = real_clock


def test_pause_and_resume_in_the_story():
    app, audio, s = screen(start_scene=19)
    audio.scene.at = 10.0
    app.key_down('escape', [])
    assert s.paused and app.loop.held and audio.log[-2:] == [('pause',), ('clip', 'pause_menu')]
    assert 'Paused' in s.lines()
    audio.scene.at = 21.5
    app.key_down('right', [])                       # a swipe while paused does nothing
    s.update()                                      # nor does the cue
    assert audio.log[-1] == ('clip', 'pause_menu') and s.story.scene == 19
    app.key_down('p', [])
    assert not s.paused and not app.loop.held and audio.log[-2:] == [('stop clip',), ('resume', 21.5)]
    app.key_down('right', [])
    assert s.story.scene == 20


def test_enter_and_p_pause_in_the_menus_and_escape_quits():
    app, audio, s = screen()
    app.key_down('return', [])
    assert s.paused and audio.log[-1] == ('clip', 'pause_menu')
    app.key_down('return', [])
    assert not s.paused and app.running
    app.key_down('escape', [])
    assert not app.running


def test_pausing_a_waiting_scene_only_plays_the_clip():
    app, audio, s = screen()
    audio.scene.end()
    audio.scene.recording = None                    # its recording is over: it waits
    app.key_down('p', [])
    assert audio.log[-1] == ('clip', 'pause_menu')
    app.key_down('p', [])
    assert audio.log[-1] == ('stop clip',)
    audio.scene.recording = object()


def test_losing_focus_and_coming_back():
    app, audio, s = screen(start_scene=46)
    audio.scene.at = 100.0
    s.focus_lost()
    assert s.paused and app.loop.held and audio.log[-1] == ('pause',)
    s.focus_gained()
    assert s.paused and audio.scene.at == 97.0 and audio.log[-1] == ('clip', 'WelcomeBack')
    app.key_down('return', [])
    assert not s.paused and audio.log[-1] == ('resume', 97.0)
    s.focus_gained()                                # not paused: nothing more
    assert audio.log[-1] == ('resume', 97.0)


def test_the_ending_goes_to_the_credits():
    app, audio, s = screen(start_scene=54)
    s.story.failure = 49                            # a failure this run, as the original kept
    audio.scene.end()
    assert audio.log[-1] == ('play', '43_end_game_congrats', 0.0, False)
    audio.scene.end()
    assert audio.log[-2:] == [('play', '04_credits_menu_choice', 0.0, False), ('buzz',)]
    assert s.escape_quits


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
