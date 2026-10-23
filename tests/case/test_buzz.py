"""The buzz: its length, both ears alike, its fades, its level, its shapes and pitch, made
from memory, and played on the dummy driver."""
import _quiet  # noqa: F401  (first, before any of the game)

import pygame

from mindsight.platform import buzz
from mindsight.platform.audio import BUZZ_CHANNEL, Audio


def left(s):
    return s[0::2]


def test_its_length_and_both_ears():
    s = buzz.samples()
    assert len(s) == 2 * int(buzz.RATE * buzz.LENGTH_MS / 1000) == 2 * 17640
    assert s[0::2] == s[1::2]


def test_it_starts_and_ends_silent_and_never_clips():
    s = left(buzz.samples())
    assert s[0] == 0 and s[-1] == 0
    fade = int(buzz.RATE * buzz.FADE_MS / 1000)
    assert max(abs(v) for v in s[:fade // 4]) < 0.3 * 32767 * buzz.LEVEL
    assert max(abs(v) for v in s) <= 32767 * buzz.LEVEL


def test_it_is_well_below_full():
    assert buzz.LEVEL <= 0.5


def test_it_holds_one_level_between_its_fades():
    s = left(buzz.samples(shape='square'))
    fade = int(buzz.RATE * buzz.FADE_MS / 1000)
    middle = {abs(v) for v in s[fade + 1:len(s) - fade - 1]}
    assert middle == {int(32767 * buzz.LEVEL)}


def test_each_shape_differs():
    made = {shape: bytes(buzz.samples(shape=shape)) for shape in buzz.SHAPES}
    assert len(set(made.values())) == len(buzz.SHAPES)
    try:
        buzz.samples(shape='wobble')
    except ValueError:
        pass
    else:
        raise AssertionError('an unknown shape was allowed')


def test_its_pitch_follows_the_frequency():
    for frequency in (100, 170, 400):
        s = left(buzz.samples(frequency=frequency, shape='square'))
        crossings = sum(1 for a, b in zip(s, s[1:]) if a < 0 <= b)
        expected = frequency * buzz.LENGTH_MS / 1000
        assert abs(crossings - expected) <= 2, (frequency, crossings)


def test_the_wave_shapes():
    assert abs(buzz.wave('sine', 0.25) - 1) < 1e-9
    assert buzz.wave('square', 0.1) == 1 and buzz.wave('square', 0.6) == -1
    assert buzz.wave('triangle', 0.25) == 0 and buzz.wave('triangle', 0.5) == 1
    assert buzz.wave('sawtooth', 0.0) == -1


def test_a_tool_can_make_it_at_another_level():
    audio = Audio()
    audio.open(pygame)
    try:
        audio.set_buzz_level(0.5)
        raw = audio.buzz.get_raw()
        import array
        values = array.array('h', raw)
        assert max(values) == int(32767 * 0.5)
    finally:
        audio.close()


def test_it_plays_from_memory_on_its_channel():
    audio = Audio()
    audio.open(pygame)
    try:
        assert abs(audio.buzz.get_length() - buzz.LENGTH_MS / 1000) < 0.01
        audio.play_buzz()
        assert pygame.mixer.Channel(BUZZ_CHANNEL).get_sound() is audio.buzz
    finally:
        audio.close()


_quiet.run_tests(globals())
