"""Try plan 3's sound by ear (aidocks/plans/audio_plan.md).

    python tests/interact/audio_check.py

It plays the original's recordings through the game's own players, and speaks through
NVDA, as every tool here does; the game itself never speaks. It keeps its own save under
%APPDATA%\\Mindsight\\interact\\audio_check.

Keys:
    Up or W, Down or S   the scene before or after, saying its number, name and length
    Enter                play that scene from its start; scenes 10, 26 and 35 loop
    Left and Right       5 seconds back or on in the playing scene
    T                    type a point in seconds, such as 112 or 20.4, then Enter to play from it;
                         Backspace takes back a digit
    Space                pause or resume the scene
    I                    say where the scene is, in seconds
    O                    Solved, at a fifth of full volume, over whatever is playing
    2                    the buzz, over whatever is playing, where the original vibrated
    E or Page Up         the buzz's level up, 5 percent of full scale a step, playing it at once
    Q or Page Down       the buzz's level down; it starts at buzz.py's level, and never changes
                         the game
    3                    WelcomeBack, as after an interruption
    H                    say the keys again
    Escape               quit, as does Alt+F4

A scene ending of itself is spoken, so the end can be heard to come at the right time.
Switching away from the window pauses the scene, as the game will; coming back steps it
back 3 seconds and plays WelcomeBack, and Space resumes it from there.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _tool  # noqa: E402
_tool.own_save('audio_check')

from mindsight.game import scenes  # noqa: E402
from mindsight.game.recordings import Recordings, disk_name  # noqa: E402
from mindsight.platform import buzz  # noqa: E402
from mindsight.platform.audio import Audio  # noqa: E402
from mindsight.ui.screens import Screen  # noqa: E402
import _nvda  # noqa: E402

KEYS = ('Audio check. Up and Down choose a scene, Enter plays it, Left and Right move 5 seconds, '
        'T types a point to play from, Space pauses, I says where it is, O plays Solved, '
        '2 plays the buzz, E and Q or Page Up and Page Down change its level, 3 plays WelcomeBack, '
        'H says the keys again, and Escape quits.')
NUDGE = 5.0
#: The buzz's level, in percent of full scale: a step, and the lowest and highest.
LEVEL_STEP, LEVEL_LOWEST, LEVEL_HIGHEST = 5, 5, 100


def spoken_name(scene):
    return disk_name(scenes.name(scene)).replace('_', ' ')


class AudioCheckScreen(Screen):
    name = 'audio check'

    def __init__(self, app, audio=None, recordings=None):
        super().__init__(app)
        self.audio = audio or Audio.shared()
        self.recordings = recordings or Recordings.shared()
        self.scene = 1
        self.typing = None          # the digits typed after T, or None
        self.last = 'Nothing yet.'
        self.buzz_level = round(buzz.LEVEL * 100)

    def say(self, text):
        self.last = text
        _nvda.say(text)

    def quit(self):
        _nvda.say('Quitting the audio check.')
        self.app.quit()

    def opened(self):
        self.say(KEYS)

    def recording(self, scene=None):
        return self.recordings.get(scenes.name(self.scene if scene is None else scene))

    def describe(self):
        return 'Scene %d, %s, %.1f seconds%s.' % (self.scene, spoken_name(self.scene), self.recording().length,
                                                ', looping' if self.scene in scenes.LOOPING else '')

    # ---- playing --------------------------------------------------------------
    def play(self, start=0.0):
        rec = self.recording()
        start = max(0.0, min(start, rec.length - 0.5)) if self.scene not in scenes.LOOPING else max(0.0, start)
        scene = self.scene
        self.audio.scene.play(rec, start, loop=scene in scenes.LOOPING,
                              on_end=lambda: self.say('Scene %d ended.' % scene))

    def nudge(self, seconds):
        player = self.audio.scene
        if player.recording is None:
            self.say('Nothing is playing.')
            return
        self.play(player.position() + seconds)
        self.say('%.0f seconds.' % self.audio.scene.position())

    def pause_or_resume(self):
        player = self.audio.scene
        if not player.playing:
            self.say('Nothing is playing.')
        elif player.paused:
            player.resume()
            self.say('Resumed.')
        else:
            player.pause()
            self.say('Paused at %.1f seconds.' % player.position())

    # ---- keys -----------------------------------------------------------------
    def gesture(self, gesture):
        if self.typing is not None and gesture == 'pause':
            self.play_typed()               # Enter ends what was typed
            return
        if gesture == 'up':
            self.scene = (self.scene - 1) % scenes.COUNT
            self.say(self.describe())
        elif gesture == 'down':
            self.scene = (self.scene + 1) % scenes.COUNT
            self.say(self.describe())
        elif gesture == 'left':
            self.nudge(-NUDGE)
        elif gesture == 'right':
            self.nudge(NUDGE)
        elif gesture == 'pause':
            self.say('Playing s' + self.describe()[1:])
            self.play()

    def other_key(self, key, mods):
        if mods:
            return
        if self.typing is not None:
            self.type_key(key)
            return
        if key == 't':
            self.typing = ''
            self.say('Type the point in seconds, then Enter.')
        elif key == 'space':
            self.pause_or_resume()
        elif key == 'i':
            player = self.audio.scene
            self.say('%.1f seconds into scene %d.' % (player.position(), self.scene) if player.playing
                     else 'Nothing is playing.')
        elif key == 'o':
            self.audio.play_solved(self.recordings.get(scenes.SOLVED))
            self.say('Solved.')
        elif key in ('2', '[2]'):
            self.audio.play_buzz()
        elif key in ('page up', 'page down', 'e', 'q'):
            step = LEVEL_STEP if key in ('page up', 'e') else -LEVEL_STEP
            self.buzz_level = max(LEVEL_LOWEST, min(LEVEL_HIGHEST, self.buzz_level + step))
            self.audio.set_buzz_level(self.buzz_level / 100)
            self.say('Buzz level %d percent.' % self.buzz_level)
            self.audio.play_buzz()
        elif key in ('3', '[3]'):
            self.audio.play_clip(self.recordings.get(scenes.WELCOME_BACK))
        elif key == 'h':
            self.say(KEYS)

    def type_key(self, key):
        digit = key.strip('[]')
        if digit.isdigit() or (digit in ('.', 'period') and '.' not in self.typing):
            self.typing += '.' if digit == 'period' else digit
            _nvda.say(digit if digit.isdigit() else 'point')
        elif key == 'backspace':
            self.typing = self.typing[:-1]
            _nvda.say(self.typing or 'Empty.')

    def play_typed(self):
        typed, self.typing = self.typing, None
        try:
            start = float(typed)
        except ValueError:
            self.say('Nothing was typed.')
            return
        self.play(start)
        self.say('Playing scene %d from %s seconds.' % (self.scene, typed))

    def update(self):
        self.audio.update()

    def focus_lost(self):
        self.audio.focus_lost()

    def focus_gained(self):
        player = self.audio.scene
        was = player.position() if player.playing else None
        self.audio.focus_gained(self.recordings.get(scenes.WELCOME_BACK))
        if was is not None:
            self.last = 'Back: paused, stepped back from %.1f to %.1f seconds. Space resumes.' % (
                was, player.position())

    def lines(self):
        player = self.audio.scene
        state = 'Nothing playing.'
        if player is not None and player.playing:
            state = '%s at %.1f s%s' % (player.recording.name, player.position(), ', paused' if player.paused else '')
        return ['Mindsight audio check', '', self.describe(), state, 'Buzz level: %d percent' % self.buzz_level,
                'Typing: ' + self.typing if self.typing is not None else '', '', 'Last: ' + self.last]


def main(argv=None):
    audio = Audio.shared()
    return _tool.run('Mindsight audio check', AudioCheckScreen, argv,
                     before=audio.open, after=audio.close)


if __name__ == '__main__':
    sys.exit(main())
