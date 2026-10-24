"""The safe JSON files: writing through a temporary file with a backup, and reading a
damaged or missing file from its backup."""
import _quiet  # noqa: F401  (first, before any of the game)

import os
import tempfile

from mindsight.platform import jsonfile


def fresh(name='save.json'):
    return os.path.join(tempfile.mkdtemp(dir=_quiet.FOLDER), 'saves', name)


def test_a_missing_file_reads_as_nothing():
    assert jsonfile.read(fresh()) is None


def test_write_then_read():
    path = fresh()
    jsonfile.write(path, {'scene': 9})
    assert jsonfile.read(path) == {'scene': 9}
    assert not os.path.exists(path + '.tmp') and not os.path.exists(path + '.bak')


def test_the_file_before_is_kept_as_the_backup():
    path = fresh()
    jsonfile.write(path, {'scene': 9})
    jsonfile.write(path, {'scene': 12})
    assert jsonfile.read(path) == {'scene': 12}
    assert jsonfile.read(path + '.bak') == {'scene': 9}


def test_a_damaged_file_is_kept_and_the_backup_read():
    path = fresh()
    jsonfile.write(path, {'scene': 9})
    jsonfile.write(path, {'scene': 12})
    with open(path, 'w', encoding='utf-8') as f:
        f.write('{"scene": 1')
    assert jsonfile.read(path) == {'scene': 9}
    assert os.path.exists(path + '.damaged') and not os.path.exists(path)


def test_a_damaged_file_with_no_backup_reads_as_nothing_and_is_replaced():
    path = fresh()
    os.makedirs(os.path.dirname(path))
    with open(path, 'wb') as f:
        f.write(b'\x00\xff not json')
    assert jsonfile.read(path) is None
    jsonfile.write(path, {'scene': 13})
    assert jsonfile.read(path) == {'scene': 13}


def test_a_write_cut_off_between_its_swaps_reads_the_backup():
    path = fresh()
    jsonfile.write(path, {'scene': 9})
    jsonfile.write(path, {'scene': 12})
    os.remove(path)                             # as if cut off after the backup was made
    assert jsonfile.read(path) == {'scene': 9}


_quiet.run_tests(globals())
