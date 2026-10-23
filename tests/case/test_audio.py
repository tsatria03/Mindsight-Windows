"""The sound, on SDL's dummy driver: the mixer, the scene player's position, pause, loops
and end, Solved at 0.2, the pause clips, and no sound device."""
import _quiet  # noqa: F401  (first, before any of the game)

import pygame

from mindsight.game import scenes
from mindsight.game.recordings import Recordings
from mindsight.platform import audio as audio_module
from mindsight.platform import runloop
from mindsight.platform.audio import Audio, NoSound, ScenePlayer


class Clock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


class FakeMusic:
    """pygame.mixer.music, without the sound: what it was told, and whether it is busy."""
    def __init__(self):
        self.calls = []
        self.busy = False

    def load(self, source):
        self.calls.append(('load', source))

    def play(self, loops=0, start=0.0):
        self.calls.append(('play', loops, start))
        self.busy = True

    def stop(self):
        self.busy = False

    def pause(self):
        self.calls.append(('pause',))

    def unpause(self):
        self.calls.append(('unpause',))

    def get_busy(self):
        return self.busy


class FakePygame:
    def __init__(self):
        self.mixer = type('mixer', (), {})()
        self.mixer.music = FakeMusic()


def player():
    clock = Clock()
    runloop.clock = clock
    fake = FakePygame()
    return ScenePlayer(fake), fake.mixer.music, clock


def rec(name):
    return Recordings.shared().get(name)


def test_the_mixer_opens_as_planned():
    audio = Audio()
    audio.open(pygame)
    try:
        assert pygame.mixer.get_init() == (44100, -16, 2)
        assert audio.ok
    finally:
        audio.close()
    assert not audio.ok


def test_a_scene_starts_partway_and_its_position_moves():
    p, music, clock = player()
    p.play(rec('36_roof_entry_scene'), 112)
    assert music.calls[-2:] == [('load', rec('36_roof_entry_scene').path), ('play', 0, 112.0)]
    assert p.position() == 112.0
    clock.now += 3.5
    assert abs(p.position() - 115.5) < 1e-9


def test_pause_holds_the_position():
    p, music, clock = player()
    p.play(rec('36_roof_entry_scene'))
    clock.now += 10
    p.pause()
    clock.now += 60
    assert p.paused and abs(p.position() - 10) < 1e-9
    p.resume()
    clock.now += 2
    assert not p.paused and abs(p.position() - 12) < 1e-9
    assert ('pause',) in music.calls and ('unpause',) in music.calls


def test_a_loop_wraps_by_its_length():
    p, music, clock = player()
    loop = rec('pirahnaloop')
    p.play(loop, loop=True)
    assert music.calls[-1] == ('play', -1, 0.0)
    clock.now += loop.length + 16
    assert abs(p.position() - 16) < 1e-6        # inside the first window again, 15 to 19


def test_the_end_is_noticed_once_after_the_grace():
    p, music, clock = player()
    ended = []
    p.play(rec('16_street_puzzle_fail'), on_end=lambda: ended.append(1))
    music.busy = False                          # slow to start: not an end yet
    p.update()
    assert ended == [] and p.playing
    clock.now += 0.3
    p.update()
    assert ended == [1] and not p.playing
    p.update()
    assert ended == [1]


def test_a_paused_or_looping_scene_never_ends():
    p, music, clock = player()
    ended = []
    p.play(rec('Beeps'), loop=True, on_end=lambda: ended.append(1))
    clock.now += 100
    music.busy = False
    p.update()
    p.play(rec('16_street_puzzle_fail'), on_end=lambda: ended.append(2))
    clock.now += 1
    p.pause()
    music.busy = False
    p.update()
    assert ended == []


def test_stop_never_calls_on_end():
    p, music, clock = player()
    ended = []
    p.play(rec('16_street_puzzle_fail'), on_end=lambda: ended.append(1))
    clock.now += 1
    p.stop()
    p.update()
    assert ended == [] and not p.playing


def test_solved_at_a_fifth_and_the_clips_on_their_channels():
    runloop.clock = Clock()
    audio = Audio()
    audio.open(pygame)
    try:
        audio.play_solved(rec(scenes.SOLVED))
        assert audio._sounds['Solved'].get_volume() == audio_module.SOLVED_VOLUME == 0.2 or \
            abs(audio._sounds['Solved'].get_volume() - 0.2) < 0.01
        assert pygame.mixer.Channel(audio_module.SOLVED_CHANNEL).get_sound() is audio._sounds['Solved']
        audio.play_clip(rec(scenes.WELCOME_BACK))
        assert pygame.mixer.Channel(audio_module.CLIP_CHANNEL).get_sound() is audio._sounds['WelcomeBack']
        audio.stop_clip()
        assert not pygame.mixer.Channel(audio_module.CLIP_CHANNEL).get_busy()
    finally:
        audio.close()


def test_a_real_scene_plays_on_the_dummy_driver():
    runloop.clock = Clock()
    audio = Audio()
    audio.open(pygame)
    try:
        audio.scene.play(rec('36_roof_entry_scene'), 112)
        assert pygame.mixer.music.get_busy() and audio.scene.playing
    finally:
        audio.close()


def test_no_sound_device():
    audio = Audio()
    saved = pygame.mixer.init

    def broken(*args, **kwargs):
        raise pygame.error('no audio device')
    try:
        pygame.mixer.init = broken
        try:
            audio.open(pygame)
        except NoSound as error:
            assert 'could not open a sound device' in str(error)
        else:
            raise AssertionError('no NoSound')
    finally:
        pygame.mixer.init = saved
    assert not audio.ok


def test_the_scene_table_so_far():
    assert scenes.COUNT == 56 and scenes.LOOPING == {10, 26, 35}
    for k in range(scenes.COUNT):
        assert Recordings.shared().find(scenes.name(k)) is not None, k


_quiet.run_tests(globals())
