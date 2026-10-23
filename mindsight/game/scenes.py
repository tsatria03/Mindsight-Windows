"""The original's 56 scenes, by the numbers its binary gives them
(aidocks/general/project_original_behaviour.md).

Each scene's recording, by the binary's own name for it, what follows it as it ends, the
cue times, and each puzzle's answers. The rules that use them are in story.py.
tools/scenes.py checks every value here against the binary, citing its addresses:
-[MSSceneURLStore urlForScene:] (0x100008b58) for the recordings,
-[MSViewController playNextScene] (0x100006a7c) for what follows,
-[MSViewController pushDirection:] (0x1000055c8) and its handlers for the answers.
"""
from __future__ import annotations

from collections import namedtuple

#: Each scene's recording, as the binary names it, by scene number, 0 to 55.
NAMES = (
    'Rewind', '01_main_menu_list', '02_new_game_menu_choice', '02b_new_game_confirmation',
    '03_audio_manual_menu_choice', '04_credits_menu_choice', 'NoSavedGame', 'LoadedSuccessfully',
    '08_introductory_scene', '09_office_puzzle_lead_in', 'Beeps', '10_solve_office_puzzle',
    '11_street_puzzle_leadin', '11_street_puzzle_leadin2', '12_street_puzzle_iteration_1',
    '13_street_puzzle_iteration_2', '14_street_puzzle_iteration_3', '15_street_puzzle_pass',
    '16_street_puzzle_fail', '17_car_accident_scene', '19_car_accident_puzzle_pass',
    '20_car_accident_puzzle_fail', '21_flashback_scene', '21b_flashback_scene2', '22_first_tower_scene',
    '23_solve_guard_puzzle', '23_solve_guard_puzzle2', '24_guard_puzzle_pass', '25_guard_puzzle_fail',
    '26_tower_entry_scene', '26b_tower_entry_scene', '26c_tower_entry_scene', '26d_tower_entry_scene',
    '26e_tower_entry_scene', '27_second_floor_scene', 'pirahnaloop', '28_pirahna_puzzle_pass',
    '29_pirahna_puzzle_fail', '30_third_floor_scene', '30b_third_floor_scene', '31_tones_puzzle_pass',
    '32_tones_puzzle_fail', '33_fourth_floor_scene', '33b_fourth_floor_scene', '34_safe_puzzle_pass',
    '35_safe_puzzle_fail', '36_roof_entry_scene', '37_roof_puzzle_iteration_1',
    '37_roof_puzzle_iteration_1_pass', '38_roof_puzzle_iteration_2', '38_roof_puzzle_iteration_2_pass',
    '39_roof_puzzle_iteration_3', '39_roof_puzzle_iteration_3_pass', '41_roof_puzzle_fail',
    '42_boss_death_scene', '43_end_game_congrats',
)
COUNT = len(NAMES)

REWIND, MAIN_MENU, NEW_GAME, CONFIRM, MANUAL, CREDITS, NO_SAVE, LOADED, INTRO = range(9)
ENDING = 55
#: The menu scenes, before the story starts: Escape quits in them (aidocks/plans/menus_saves_plan.md).
MENUS = frozenset(range(1, 8))

#: The scenes that loop forever (setNumberOfLoops: -1 in playScene:fromInterval:,
#: 0x100007148): the beeps, the guard and the piranhas.
LOOPING = frozenset({10, 26, 35})

#: The recordings played outside the scene table: the pause clip, the welcome back after
#: an interruption, and the Solved sound.
PAUSE_MENU, WELCOME_BACK, SOLVED = 'pause_menu', 'WelcomeBack', 'Solved'

# ---- what follows a scene as it ends (playNextScene) ----------------------------

#: The ways a scene's end is handled.
WAITS = 'waits'        # nothing follows: the game waits for a swipe
PLAYS = 'plays'        # the next scene plays
LOADS = 'loads'        # the saved scene plays, from its start (scene 7)
RETRY = 'retry'        # the Rewind's retry, by the failure (scene 0)

#: What follows a scene: how, the next scene, whether that next scene is saved as it
#: starts, and the failure set when a timed round runs out.
Then = namedtuple('Then', 'how next saves failure')


def _then(next_scene, saves=False, failure=None):
    return Then(PLAYS, next_scene, saves, failure)


THEN = {
    0: Then(RETRY, None, False, None),
    1: Then(WAITS, None, False, None), 2: Then(WAITS, None, False, None),
    3: _then(8), 4: _then(1),
    5: Then(WAITS, None, False, None), 6: Then(WAITS, None, False, None),
    7: Then(LOADS, None, False, None),
    8: _then(9, True), 9: _then(11),
    10: Then(WAITS, None, False, None),     # it loops; its case in the binary, 12, never runs
    11: _then(10),
    12: _then(13, True), 13: _then(14, True),
    14: _then(0, failure=14), 15: _then(0, failure=15), 16: _then(0, failure=16),
    17: _then(19, True), 18: _then(0),
    19: _then(21, failure=19), 20: _then(22, True), 21: _then(0),
    22: _then(23, True), 23: _then(24, True), 24: _then(25), 25: _then(26),
    26: Then(WAITS, None, False, None),
    27: _then(29, True), 28: _then(29, True),
    29: _then(30, True), 30: _then(31, True), 31: _then(32, True), 32: _then(33, True),
    33: _then(34, True), 34: _then(35),
    35: Then(WAITS, None, False, None),
    36: _then(38, True), 37: _then(0), 38: _then(39, True),
    39: Then(WAITS, None, False, None),
    40: _then(42, True), 41: _then(0), 42: _then(43, True),
    43: Then(WAITS, None, False, None),
    44: _then(46, True), 45: _then(0), 46: _then(47),
    47: _then(53, failure=47), 48: _then(49), 49: _then(53, failure=49), 50: _then(51),
    51: _then(53, failure=51), 52: _then(54), 53: _then(0), 54: _then(55),
    55: _then(CREDITS),
}

#: After the Rewind, by the failure: the scene to retry from, and where in it, in seconds.
RETRIES = {
    14: (13, 20.4), 15: (13, 20.4), 16: (13, 20.4),
    19: (19, 0.0),
    35: (34, 70.0),
    39: (39, 42.0),
    43: (43, 68.5),
    47: (46, 112.0), 49: (46, 112.0), 51: (46, 112.0),
}

# ---- the input lock and the cue times ---------------------------------------------

#: Starting these turns the input lock off, so they must be heard to the end: the tones and
#: the safe (playScene:fromInterval:).
LOCKED_WHILE_PLAYING = frozenset({39, 43})
#: Starting this turns the input lock on at once: the piranha loop.
OPEN_AT_START = frozenset({35})

#: A swipe counts only once the scene is past this many seconds (pushDirection:'s compares).
GATES = {11: 22.0, 14: 13.0, 15: 10.0, 16: 10.0, 19: 21.0, 47: 7.0, 49: 7.0, 51: 7.0}
#: The vibration, the port's buzz, at this many seconds into the scene (vibrateIfNecessary).
CUES = {11: 22.0, 14: 13.0, 15: 11.0, 16: 11.0, 19: 21.0, 47: 7.0, 49: 8.4, 51: 7.0}
#: The vibration, the port's buzz, after a recording ends of itself, when the scene then
#: current is one of these (audioPlayerDidFinishPlaying:, 0x100008518): as one of them
#: ends while it waits, or as one begins after the recording before it ended.
CUE_AT_END = frozenset({1, 2, 5, 6, 26, 35, 39, 43})

# ---- the answers (pushDirection: and its handlers) ------------------------------

UP, DOWN, LEFT, RIGHT = 'up', 'down', 'left', 'right'
ANY = 'any'
CONTINUE, PDF = 'continue', 'pdf'

#: What a swipe in a scene leads to: the next scene, or CONTINUE (scene 7 with a save, 6
#: without) or PDF (the dissertation); whether the Solved sound plays; whether the new
#: scene is saved; the failure it sets; and whether the input lock closes behind it.
Answer = namedtuple('Answer', 'to solved saves failure locks')


def _a(to, solved=False, saves=False, failure=None, locks=True):
    return Answer(to, solved, saves, failure, locks)


#: Each scene's answers, by direction. ANY stands for every direction not listed; a
#: direction with no entry does nothing. Street rounds 1 and 2 leave the input lock open,
#: as their handlers do.
ANSWERS = {
    1: {UP: _a(NEW_GAME), DOWN: _a(CONTINUE), LEFT: _a(MANUAL), RIGHT: _a(CREDITS)},
    2: {UP: _a(CONFIRM), DOWN: _a(MAIN_MENU)},
    6: {UP: _a(CONFIRM), DOWN: _a(MAIN_MENU)},
    5: {RIGHT: _a(MAIN_MENU), LEFT: _a(PDF)},
    10: {RIGHT: _a(12, solved=True, saves=True)},
    11: {RIGHT: _a(12, solved=True, saves=True)},
    14: {RIGHT: _a(15, solved=True, locks=False), ANY: _a(18, failure=14, locks=False)},
    15: {UP: _a(16, solved=True, locks=False), ANY: _a(18, failure=15, locks=False)},
    16: {LEFT: _a(17, solved=True), ANY: _a(18, failure=16)},
    19: {RIGHT: _a(20, solved=True, saves=True), ANY: _a(21, failure=19)},
    26: {RIGHT: _a(27), LEFT: _a(28)},
    39: {LEFT: _a(40, solved=True, saves=True), ANY: _a(41, failure=39)},
    43: {DOWN: _a(44, solved=True, saves=True), ANY: _a(45, failure=43)},
    47: {RIGHT: _a(48, solved=True), ANY: _a(53, failure=47)},
    49: {LEFT: _a(50, solved=True), ANY: _a(53, failure=49)},
    51: {DOWN: _a(52, solved=True, saves=True), ANY: _a(53, failure=51)},
}
#: The piranha loop, scene 35: any swipe passes inside one of these windows, strictly
#: between start and end, counted from 0 on each loop (piranhaPuzzleTimeValid, 0x100006f08).
PIRANHA = 35
PIRANHA_PASS = _a(36, solved=True, saves=True)
PIRANHA_FAIL = _a(37, failure=35)
PIRANHA_WINDOWS = ((15, 19), (25, 27), (31, 34), (41, 45), (50, 52), (57, 59), (67, 71),
                   (77, 79), (83, 86), (93, 97), (103, 105), (109, 111), (119, 122))


def name(scene: int) -> str:
    """The binary's name for a scene's recording."""
    return NAMES[scene]


def answers_swipes(scene: int) -> bool:
    """Whether any swipe can do anything in a scene."""
    return scene in ANSWERS or scene == PIRANHA
