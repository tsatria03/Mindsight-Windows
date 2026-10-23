"""The game's fixed keys, standing for the original's gestures (aidocks/plans/foundation_plan.md).

    Up arrow or W        swipe up
    Down arrow or S      swipe down
    Left arrow or A      swipe left
    Right arrow or D     swipe right
    Escape, Enter or P   the double tap, which pauses and resumes

The keys are never rebound. A key works only with no modifier held: with Shift, Control,
Alt or the Windows key down, it does nothing, so a screen reader's own commands, such as
NVDA's, never reach the game as a swipe. Keys are named as pygame names them.
"""
from __future__ import annotations

UP, DOWN, LEFT, RIGHT, PAUSE = 'up', 'down', 'left', 'right', 'pause'
SWIPES = (UP, DOWN, LEFT, RIGHT)

#: Each key, by pygame's name, and the gesture it stands for. "enter" is the keypad's Enter.
KEYS = {
    'up': UP, 'w': UP,
    'down': DOWN, 's': DOWN,
    'left': LEFT, 'a': LEFT,
    'right': RIGHT, 'd': RIGHT,
    'escape': PAUSE, 'return': PAUSE, 'enter': PAUSE, 'p': PAUSE,
}

#: What each gesture is called, for the window and the log.
LABELS = {UP: 'Swipe up', DOWN: 'Swipe down', LEFT: 'Swipe left', RIGHT: 'Swipe right',
          PAUSE: 'Pause or resume'}

#: The modifiers, by pygame's names for the keys themselves; pressed alone, they do nothing.
MODIFIER_KEYS = {'left shift', 'right shift', 'left ctrl', 'right ctrl', 'left alt', 'right alt',
                 'left meta', 'right meta', 'left gui', 'right gui', 'caps lock', 'num lock',
                 'scroll lock', 'mode'}

_MODS = (('KMOD_SHIFT', 'shift'), ('KMOD_CTRL', 'control'), ('KMOD_ALT', 'alt'), ('KMOD_GUI', 'windows'))


def mods_from_pygame(mod: int, pygame) -> list[str]:
    """The modifiers held, as names, from a pygame key event's ``mod``; Caps Lock and Num
    Lock never count."""
    return [name for flag, name in _MODS if mod & getattr(pygame, flag, 0)]


def gesture(key: str, mods: list[str]) -> str | None:
    """The gesture a key stands for with these modifiers held, or None."""
    if mods:
        return None
    return KEYS.get(key)


def is_game_key(key: str) -> bool:
    """Whether a key stands for a gesture at all, held with a modifier or not."""
    return key in KEYS


def key_label(key: str, mods: list[str]) -> str:
    """A key and its modifiers as words, such as "Shift plus Up"."""
    words = [m.capitalize() for m in mods] + [key.capitalize() if len(key) > 1 else key.upper()]
    return ' plus '.join(words)
