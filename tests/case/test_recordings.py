"""Finding the recordings by the binary's names: all 59, the renamed six, any letter case,
any folder, and a missing one."""
import _quiet  # noqa: F401  (first, before any of the game)

import os
import shutil

from mindsight.game import scenes
from mindsight.game.recordings import RENAMED, Recordings, disk_name

#: Every recording the binary names, as it names them: the 56 scenes, from the game's own
#: table, which tools/scenes.py checks against the binary, then the three played outside it.
BINARY_NAMES = list(scenes.NAMES) + [scenes.PAUSE_MENU, scenes.WELCOME_BACK, scenes.SOLVED]


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
