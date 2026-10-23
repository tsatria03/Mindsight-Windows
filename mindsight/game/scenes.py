"""The original's 56 scenes, by the numbers its binary gives them
(aidocks/general/project_original_behaviour.md).

For now, each scene's recording, by the binary's own name for it, and which scenes loop.
The story engine (aidocks/plans/story_engine_plan.md) adds what follows each scene, the
saves, the cue times and the puzzles. tools/scenes.py checks this list against the
binary, -[MSSceneURLStore urlForScene:] at 0x100008b58.
"""
from __future__ import annotations

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

#: The scenes that loop forever (setNumberOfLoops: -1 in playScene:fromInterval:,
#: 0x100007148): the beeps, the guard and the piranhas.
LOOPING = frozenset({10, 26, 35})

#: The recordings played outside the scene table: the pause clip, the welcome back after
#: an interruption, and the Solved sound.
PAUSE_MENU, WELCOME_BACK, SOLVED = 'pause_menu', 'WelcomeBack', 'Solved'


def name(scene: int) -> str:
    """The binary's name for a scene's recording."""
    return NAMES[scene]
