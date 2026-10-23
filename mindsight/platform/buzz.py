"""The buzz, the game's own sound in place of the original's vibration
(aidocks/plans/audio_plan.md).

The original vibrated with iOS's standard vibration, AudioServicesPlaySystemSound(0xfff)
(vibrate, 0x1000076f0), to say a swipe counts now. The port plays a short buzz instead,
made here in memory once at startup, never saved as a file: a steady low tone, faded in
and out so it never clicks, the same in both ears, and well below the voices. It has no
pulse: the dev turned it down (2026-10-23). It starts on its first sample, so it lands
exactly when a swipe starts to count.

Its numbers are all here, in one place, so a value the dev chooses by ear in
tests/interact/buzz_check.py is a one-line change.
"""
from __future__ import annotations

import array
import math

#: The tone's frequency, in Hz.
FREQUENCY = 170
#: The tone's wave shape: one of SHAPES.
SHAPE = 'sine'
#: The whole buzz, in milliseconds: about the length of iOS's vibration.
LENGTH_MS = 400
#: The fade in and the fade out, in milliseconds, so it never clicks.
FADE_MS = 10
#: Its loudest, as a share of full scale, well below the voices.
LEVEL = 0.3

SHAPES = ('sine', 'square', 'triangle', 'sawtooth')
RATE = 44100


def wave(shape: str, phase: float) -> float:
    """One wave shape's value, from -1 to 1, at ``phase`` cycles."""
    p = phase % 1.0
    if shape == 'sine':
        return math.sin(2 * math.pi * p)
    if shape == 'square':
        return 1.0 if p < 0.5 else -1.0
    if shape == 'triangle':
        return 4 * p - 1 if p < 0.5 else 3 - 4 * p
    if shape == 'sawtooth':
        return 2 * p - 1
    raise ValueError('no wave shape %r; the shapes are %s' % (shape, ', '.join(SHAPES)))


def samples(frequency=FREQUENCY, shape=SHAPE, length_ms=LENGTH_MS, fade_ms=FADE_MS,
            level=LEVEL, rate=RATE) -> array.array:
    """The buzz as 16-bit stereo samples, left and right alike, interleaved."""
    count = int(rate * length_ms / 1000)
    fade = max(1, int(rate * fade_ms / 1000))
    out = array.array('h', bytes(4 * count))
    peak = 32767 * level
    for i in range(count):
        t = i / rate
        # Only the fades in and out, so it never clicks; between them, a steady level.
        envelope = min(1.0, i / fade, (count - 1 - i) / fade)
        value = int(peak * envelope * wave(shape, frequency * t))
        out[2 * i] = out[2 * i + 1] = value
    return out


def sound(pygame, **settings):
    """The buzz as a ``pygame.mixer.Sound``, made from memory; the mixer must be open at
    44,100 Hz stereo (platform/audio.py)."""
    return pygame.mixer.Sound(buffer=samples(**settings).tobytes())
