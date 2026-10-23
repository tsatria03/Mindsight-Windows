"""The fixed keys: every swipe and pause key, modifiers, and their names."""
import _quiet  # noqa: F401  (first, before any of the game)

import pygame

from mindsight.platform import keys


def test_every_agreed_key():
    want = {'up': 'up', 'w': 'up', 'down': 'down', 's': 'down', 'left': 'left', 'a': 'left',
            'right': 'right', 'd': 'right', 'escape': 'pause', 'return': 'pause', 'enter': 'pause',
            'p': 'pause'}
    for key, gesture in want.items():
        assert keys.gesture(key, []) == gesture, key
    assert set(keys.KEYS) == set(want)


def test_the_names_are_pygames_own():
    for name in ('K_UP', 'K_DOWN', 'K_LEFT', 'K_RIGHT', 'K_w', 'K_a', 'K_s', 'K_d',
                 'K_ESCAPE', 'K_RETURN', 'K_KP_ENTER', 'K_p'):
        assert pygame.key.name(getattr(pygame, name)) in keys.KEYS, name


def test_a_modifier_stops_every_key():
    for key in keys.KEYS:
        for mods in (['shift'], ['control'], ['alt'], ['windows'], ['shift', 'control']):
            assert keys.gesture(key, mods) is None, (key, mods)
            assert keys.is_game_key(key)


def test_other_keys_are_not_game_keys():
    for key in ('x', 'space', 'f1', 'f10', 'tab', '1'):
        assert keys.gesture(key, []) is None and not keys.is_game_key(key)


def test_modifiers_from_pygame():
    assert keys.mods_from_pygame(0, pygame) == []
    assert keys.mods_from_pygame(pygame.KMOD_LSHIFT, pygame) == ['shift']
    assert keys.mods_from_pygame(pygame.KMOD_RCTRL | pygame.KMOD_LALT, pygame) == ['control', 'alt']
    assert keys.mods_from_pygame(pygame.KMOD_CAPS | pygame.KMOD_NUM, pygame) == []


def test_modifier_keys_named_as_pygame_names_them():
    for name in ('K_LSHIFT', 'K_RSHIFT', 'K_LCTRL', 'K_RCTRL', 'K_LALT', 'K_RALT', 'K_LGUI', 'K_CAPSLOCK'):
        assert pygame.key.name(getattr(pygame, name)) in keys.MODIFIER_KEYS, name


def test_labels():
    assert keys.LABELS[keys.UP] == 'Swipe up'
    assert keys.LABELS[keys.PAUSE] == 'Pause or resume'
    assert keys.key_label('up', ['shift']) == 'Shift plus Up'
    assert keys.key_label('w', ['control']) == 'Control plus W'


_quiet.run_tests(globals())
