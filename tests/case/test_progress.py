"""The save: saves/progress.json in the save folder, the checkpoints, and what counts as
no save."""
import _quiet  # noqa: F401  (first, before any of the game)

import json
import os

from mindsight import paths
from mindsight.game import progress
from mindsight.game import scenes as S


def clear():
    for end in ('', '.bak', '.damaged', '.tmp'):
        try:
            os.remove(progress.path() + end)
        except FileNotFoundError:
            pass


def hand_written(data):
    clear()
    os.makedirs(os.path.dirname(progress.path()), exist_ok=True)
    with open(progress.path(), 'w', encoding='utf-8') as f:
        f.write(data if isinstance(data, str) else json.dumps(data))


def test_it_lives_in_the_save_folder():
    assert progress.path() == os.path.join(paths.user_dir(), 'saves', 'progress.json')
    assert progress.path().startswith(_quiet.FOLDER)


def test_the_checkpoints_are_the_original_ones():
    assert S.CHECKPOINTS == {9, 12, 13, 14, 19, 20, 22, 23, 24, 29, 30, 31, 32, 33, 34, 36,
                             38, 39, 40, 42, 43, 44, 46, 52}
    assert not S.CHECKPOINTS & S.MENUS and S.REWIND not in S.CHECKPOINTS


def test_no_file_is_no_save():
    clear()
    assert progress.load() is None and not progress.has_save()


def test_save_and_load():
    clear()
    progress.save(24)
    assert progress.load() == 24 and progress.has_save()
    with open(progress.path(), encoding='utf-8') as f:
        assert json.load(f) == {'scene': 24}
    progress.save(29)
    assert progress.load() == 29


def test_what_is_not_a_checkpoint_is_no_save():
    for data in ({'scene': 0}, {'scene': 1}, {'scene': 7}, {'scene': 55}, {'scene': 56},
                 {'scene': -1}, {'scene': 9.0}, {'scene': True}, {'scene': '9'}, {}, [9], 9):
        hand_written(data)
        assert progress.load() is None, data


def test_a_damaged_save_falls_back_on_the_one_before():
    clear()
    progress.save(9)
    progress.save(12)
    with open(progress.path(), 'w', encoding='utf-8') as f:
        f.write('{"sce')
    assert progress.load() == 9


def test_a_damaged_save_with_nothing_before_is_no_save():
    hand_written('not json at all')
    assert progress.load() is None


_quiet.run_tests(globals())
