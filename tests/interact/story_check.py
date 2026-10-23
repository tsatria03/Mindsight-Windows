"""Play the story by ear, from any scene (aidocks/plans/story_engine_plan.md).

    python tests/interact/story_check.py
    python tests/interact/story_check.py --scene 47

It always runs in the game's debug mode (the dev, 2026-10-23), its window titled "Mindsight
story check (debug)", and like the game's ``--debug --scene N``, ``--scene N`` starts it at
scene N, 0 to 55.

It is the game's own story screen, with the game's own keys, plus a few of its own to get
around, and it speaks through NVDA, as every tool here does; the game itself never speaks.
It keeps its own save under %APPDATA%\\Mindsight\\interact\\story_check, and never saves.

The game's keys, passed straight through:
    Arrow keys, or W, A, S and D    the four swipes
    Enter or P                      the double tap, which pauses and resumes; Escape quits here

The tool's own keys:
    T        type a scene number, then Enter, to jump there, as if the scene before had ended
    I        say the state: the scene, where it is, the failure, and whether a swipe counts
    L        skip to 5 seconds before the playing scene's end
    H        say the keys again
    Escape   quit, as does Alt+F4
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _tool  # noqa: E402
_tool.own_save('story_check')

from mindsight.game import scenes as S  # noqa: E402
from mindsight.game.story_screen import StoryScreen, plain_name  # noqa: E402
from mindsight.platform.audio import Audio  # noqa: E402
import _nvda  # noqa: E402

KEYS = ('Story check. The game\'s keys play as in the game, with Enter or P to pause. '
        'T then a number and Enter jumps to a scene, I says the state, L skips near the end, '
        'H says the keys again, and Escape quits.')
NEAR_END = 5.0


class StoryCheckScreen(StoryScreen):
    name = 'story check'

    def __init__(self, app, audio=None, start_scene=None):
        super().__init__(app, audio, start_scene=start_scene)
        self.saving = False             # a tool never saves
        self.typing = None

    def opened(self):
        _nvda.say(KEYS)
        super().opened()

    def quit(self):
        _nvda.say('Quitting the story check.')
        self.app.quit()

    @property
    def escape_quits(self):
        return True                     # as in every tool

    def gesture(self, gesture):
        if self.typing is not None and gesture == 'pause':
            self.jump_typed()           # Enter ends what was typed
            return
        super().gesture(gesture)

    def other_key(self, key, mods):
        if mods:
            return
        if self.typing is not None:
            digit = key.strip('[]')
            if digit.isdigit() and len(self.typing) < 2:
                self.typing += digit
                _nvda.say(digit)
            elif key == 'backspace':
                self.typing = self.typing[:-1]
                _nvda.say(self.typing or 'Empty.')
            return
        if key == 't':
            self.typing = ''
            _nvda.say('Type a scene number, 0 to 55, then Enter.')
        elif key == 'i':
            _nvda.say(self.state())
        elif key == 'l':
            self.skip_near_end()
        elif key == 'h':
            _nvda.say(KEYS)

    def jump_typed(self):
        typed, self.typing = self.typing, None
        if not typed or not 0 <= int(typed) < S.COUNT:
            _nvda.say('There is no scene %s.' % (typed or 'typed'))
            return
        scene = int(typed)
        _nvda.say('Scene %d, %s.' % (scene, plain_name(scene)))
        self.perform(self.story.jump(scene))

    def skip_near_end(self):
        player = self.audio.scene
        scene = self.story.scene
        if scene in S.LOOPING:
            _nvda.say('Scene %d loops, so it has no end.' % scene)
            return
        if not player.playing:
            _nvda.say('Nothing is playing.')
            return
        start = max(0.0, player.recording.length - NEAR_END)
        player.play(player.recording, start, loop=False, on_end=self.ended)
        _nvda.say('5 seconds before the end of scene %d.' % scene)

    def state(self):
        scene = self.story.scene
        where = '%.1f seconds in' % self.position() if self.audio.scene.playing else 'not playing'
        failure = 'failure %d' % self.story.failure if self.story.failure is not None else 'no failure'
        turn = 'a swipe counts now' if self.story.counts(self.position()) else 'a swipe does nothing yet'
        return 'Scene %d, %s, %s, %s, %s.' % (scene, plain_name(scene), where, failure, turn)


def scene_from(argv):
    """The scene ``--scene N`` names, when it is one; or None."""
    if '--scene' not in argv:
        return None
    try:
        scene = int(argv[argv.index('--scene') + 1])
    except (IndexError, ValueError):
        return None
    return scene if 0 <= scene < S.COUNT else None


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    audio = Audio.shared()
    scene = scene_from(argv)
    return _tool.run('Mindsight story check', lambda app: StoryCheckScreen(app, audio, start_scene=scene), argv,
                     before=audio.open, after=audio.close, debug=True)


if __name__ == '__main__':
    sys.exit(main())
