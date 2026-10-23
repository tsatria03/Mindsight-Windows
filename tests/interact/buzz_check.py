"""Tune the buzz by ear (aidocks/plans/audio_plan.md).

    python tests/interact/buzz_check.py

The buzz is the game's own sound in place of the original's vibration, made in memory by
mindsight/platform/buzz.py. This tool changes its frequency and its wave shape and plays
it, speaking each value through NVDA. It never changes the game: tell Claude the values
you like, and they go into buzz.py. It keeps its own save under
%APPDATA%\\Mindsight\\interact\\buzz_check.

Keys:
    Up or W, Down or S   the frequency, 10 Hz up or down
    Left and Right       the wave shape: sine, square, triangle or sawtooth
    Space                play the buzz
    I                    say the frequency and shape
    H                    say the keys again
    Escape               quit, as does Alt+F4
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _tool  # noqa: E402
_tool.own_save('buzz_check')

from mindsight.platform import buzz  # noqa: E402
from mindsight.platform.audio import BUZZ_CHANNEL, Audio  # noqa: E402
from mindsight.ui.screens import Screen  # noqa: E402
import _nvda  # noqa: E402

KEYS = ('Buzz check. Up and Down change the frequency by 10 hertz, Left and Right the wave shape, '
        'Space plays the buzz, I says its values, H says the keys again, and Escape quits.')
STEP = 10
LOWEST, HIGHEST = 20, 2000


class BuzzCheckScreen(Screen):
    name = 'buzz check'

    def __init__(self, app, audio=None):
        super().__init__(app)
        self.audio = audio or Audio.shared()
        self.frequency = buzz.FREQUENCY
        self.shape = buzz.SHAPE
        self.sound = None
        self.last = 'Nothing yet.'

    def say(self, text):
        self.last = text
        _nvda.say(text)

    def quit(self):
        _nvda.say('Quitting the buzz check.')
        self.app.quit()

    def opened(self):
        self.say(KEYS + ' ' + self.values())

    def values(self):
        return '%d hertz, %s.' % (self.frequency, self.shape)

    def changed(self):
        self.sound = None
        self.say(self.values())

    def gesture(self, gesture):
        if gesture == 'up':
            self.frequency = min(HIGHEST, self.frequency + STEP)
            self.changed()
        elif gesture == 'down':
            self.frequency = max(LOWEST, self.frequency - STEP)
            self.changed()
        elif gesture in ('left', 'right'):
            k = buzz.SHAPES.index(self.shape) + (1 if gesture == 'right' else -1)
            self.shape = buzz.SHAPES[k % len(buzz.SHAPES)]
            self.changed()
        elif gesture == 'pause':
            self.say(KEYS)

    def other_key(self, key, mods):
        if mods:
            return
        if key == 'space':
            self.play()
        elif key == 'i':
            self.say(self.values())
        elif key == 'h':
            self.say(KEYS)

    def play(self):
        if self.sound is None:
            self.sound = buzz.sound(self.audio.pygame, frequency=self.frequency, shape=self.shape)
        self.audio.pygame.mixer.Channel(BUZZ_CHANNEL).play(self.sound)

    def lines(self):
        return ['Mindsight buzz check', '', 'Frequency: %d Hz' % self.frequency, 'Shape: ' + self.shape,
                '%d ms, level %.2f, no pulse' % (buzz.LENGTH_MS, buzz.LEVEL), '',
                'Last: ' + self.last]


def main(argv=None):
    audio = Audio.shared()
    return _tool.run('Mindsight buzz check', BuzzCheckScreen, argv, before=audio.open, after=audio.close)


if __name__ == '__main__':
    sys.exit(main())
