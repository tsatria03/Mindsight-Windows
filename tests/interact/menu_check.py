"""Try the menus around the story by ear: Continue, and the dissertation
(aidocks/plans/menus_saves_plan.md).

    python tests/interact/menu_check.py

It is the game's own story screen, from the main menu, with the game's own keys, and it
saves as the game does, but in its own save under %APPDATA%\\Mindsight\\interact\\menu_check,
never the game's. It speaks through NVDA, as every tool here does; the game itself never
speaks.

The game's keys, passed straight through:
    Arrow keys, or W, A, S and D    the four swipes
    Enter or P                      the double tap, which pauses and resumes; Escape quits here

The tool's own keys:
    T        type a scene number, then Enter, to save there; only a checkpoint is taken
    C        clear the save, to try Continue with none
    I        say what the save holds, or that there is none
    H        say the keys again
    Escape   quit, as does Alt+F4
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _tool  # noqa: E402
_tool.own_save('menu_check')

from mindsight.game import progress  # noqa: E402
from mindsight.game import scenes as S  # noqa: E402
from mindsight.game.story_screen import StoryScreen, plain_name  # noqa: E402
from mindsight.platform.audio import Audio  # noqa: E402
import _nvda  # noqa: E402

KEYS = ('Menu check. The game\'s keys play as in the game, with Enter or P to pause. '
        'T then a number and Enter saves at that scene, C clears the save, I says the save, '
        'H says the keys again, and Escape quits.')


def saved():
    scene = progress.load()
    if scene is None:
        return 'There is no save.'
    return 'The save is scene %d, %s.' % (scene, plain_name(scene))


class MenuCheckScreen(StoryScreen):
    name = 'menu check'

    def __init__(self, app, audio=None):
        super().__init__(app, audio)
        self.typing = None

    def opened(self):
        _nvda.say(KEYS + ' ' + saved())
        super().opened()

    def quit(self):
        _nvda.say('Quitting the menu check.')
        self.app.quit()

    @property
    def escape_quits(self):
        return True                     # as in every tool

    def gesture(self, gesture):
        if self.typing is not None and gesture == 'pause':
            self.save_typed()           # Enter ends what was typed
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
            _nvda.say('Type a scene number to save at, then Enter.')
        elif key == 'c':
            progress.clear()
            _nvda.say('Cleared the save.')
        elif key == 'i':
            _nvda.say(saved())
        elif key == 'h':
            _nvda.say(KEYS)

    def save_typed(self):
        typed, self.typing = self.typing, None
        if not typed:
            _nvda.say('Nothing typed.')
            return
        scene = int(typed)
        if scene not in S.CHECKPOINTS:
            _nvda.say('Scene %d is not a checkpoint, so it was not saved. The checkpoints are %s.'
                      % (scene, ', '.join(str(n) for n in sorted(S.CHECKPOINTS))))
            return
        progress.save(scene)
        _nvda.say('Saved at scene %d, %s.' % (scene, plain_name(scene)))

    def open_dissertation(self):
        super().open_dissertation()
        if self.in_viewer:
            _nvda.say('Opened the dissertation. Come back to this window for the main menu.')
        else:
            _nvda.say('The dissertation could not be opened; the log says why.')


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    audio = Audio.shared()
    return _tool.run('Mindsight menu check', lambda app: MenuCheckScreen(app, audio), argv,
                     before=audio.open, after=audio.close)


if __name__ == '__main__':
    sys.exit(main())
