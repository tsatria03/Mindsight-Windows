"""The paths: the throwaway save, the recordings found, the missing-data message, VERSION,
and that every test file imports _quiet first."""
import _quiet  # noqa: F401  (first, before any of the game)

import ast
import os
import tempfile

from mindsight import paths

HERE = os.path.dirname(os.path.abspath(__file__))


def test_save_folder_is_the_throwaway_one():
    assert paths.user_dir() == _quiet.FOLDER
    assert not paths.user_dir().lower().startswith(os.environ.get('APPDATA', '?').lower())


def test_logs_folder_is_made_inside_the_save():
    folder = paths.logs_dir()
    assert os.path.isdir(folder)
    assert folder == os.path.join(_quiet.FOLDER, 'logs')


def test_user_path_joins_inside_the_save():
    assert paths.user_path('saves', 'progress.json') == os.path.join(_quiet.FOLDER, 'saves', 'progress.json')


def test_recordings_found_in_the_repository():
    assert paths.game() == os.path.join(paths.ROOT, 'game')
    assert os.path.isdir(os.path.join(paths.audio(), 'story', 'sceen'))


def test_missing_recordings_raise_with_where_it_looked():
    empty = tempfile.mkdtemp(prefix='mindsight_no_game_')
    saved = paths.EXE_DIR, paths.ROOT
    try:
        paths.EXE_DIR = paths.ROOT = empty
        try:
            paths.game()
        except paths.MissingData as missing:
            text = str(missing)
        else:
            raise AssertionError('no MissingData')
    finally:
        paths.EXE_DIR, paths.ROOT = saved
    assert os.path.join(empty, 'game', 'data', 'audio') in text
    assert 'extract the whole game folder again' in text


def test_version_read_from_the_repository():
    with open(os.path.join(paths.ROOT, 'VERSION'), encoding='utf-8-sig') as f:
        assert paths.version() == f.read().strip()


def test_every_test_file_imports_quiet_first():
    for name in sorted(os.listdir(HERE)):
        if not name.endswith('.py') or name.startswith('_'):
            continue
        with open(os.path.join(HERE, name), encoding='utf-8') as f:
            tree = ast.parse(f.read())
        # The first import statement in the code, never a line of a docstring.
        first = next(node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom)))
        ok = isinstance(first, ast.Import) and first.names[0].name == '_quiet'
        assert ok, '%s does not import _quiet first' % name


_quiet.run_tests(globals())
