"""Finding the recordings by the binary's names: all 59, the renamed six, any letter case,
any folder, and a missing one."""
import _quiet  # noqa: F401  (first, before any of the game)

import os
import shutil

from mindsight.game.recordings import RENAMED, Recordings, disk_name

#: Every recording the binary names, as it names them: the 56 scenes, then the three
#: played outside the scene table (aidocks/general/project_original_behaviour.md).
#: tools/scenes.py reads this list from the binary itself.
BINARY_NAMES = [
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
    'pause_menu', 'WelcomeBack', 'Solved',
]


def test_the_names_on_disk():
    assert disk_name('08_introductory_scene') == 'introductory_scene'
    assert disk_name('02b_new_game_confirmation') == 'new_game_confirmation'
    assert disk_name('21b_flashback_scene2') == 'flashback_scene2'
    assert disk_name('11_street_puzzle_leadin2') == 'street_puzzle_leadin2'
    assert disk_name('Rewind') == 'Rewind'
    assert disk_name('26c_tower_entry_scene') == 'tower_entry_scene3'
    assert disk_name('30b_third_floor_scene') == 'third_floor_scene2'
    assert len(RENAMED) == 6


def test_all_59_are_found_with_their_lengths():
    rec = Recordings.shared()
    assert len(BINARY_NAMES) == 59 and len(set(BINARY_NAMES)) == 59
    paths_found = set()
    for name in BINARY_NAMES:
        found = rec.get(name)
        assert os.path.isfile(found.source()), name
        assert found.length > 1.0, name
        paths_found.add(found.path)
    assert len(paths_found) == 59          # no two names share a file


def test_only_fanradio_is_never_named():
    rec = Recordings.shared()
    named = {disk_name(n).lower() for n in BINARY_NAMES}
    assert sorted(set(rec.files) - named) == ['fanradio']
    assert len(rec.files) == 60


def test_any_folder_and_any_letter_case():
    folder = os.path.join(_quiet.FOLDER, 'audio')
    os.makedirs(os.path.join(folder, 'elsewhere', 'deeper'))
    shutil.copy(Recordings.shared().get('Rewind').path, os.path.join(folder, 'elsewhere', 'deeper', 'REWIND.MP3'))
    rec = Recordings(folder)
    assert rec.get('Rewind').path.endswith('REWIND.MP3')


def test_a_missing_recording():
    rec = Recordings(os.path.join(_quiet.FOLDER, 'empty'))
    assert rec.find('08_introductory_scene') is None
    try:
        rec.get('08_introductory_scene')
    except KeyError as error:
        assert 'introductory_scene.mp3' in str(error)
    else:
        raise AssertionError('no KeyError')


_quiet.run_tests(globals())
