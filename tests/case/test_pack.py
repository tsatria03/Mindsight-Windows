"""story.dat (mindsight/platform/pack.py): the format, damaged and foreign packs, the mixer
playing a packed recording from memory, and the recordings found in the pack when the
loose story folder is not there."""
import _quiet  # noqa: F401  (first, before any of the game)

import json
import os
import shutil

from mindsight import paths
from mindsight.game import recordings
from mindsight.game.recordings import Recordings
from mindsight.platform import pack

REAL = Recordings.shared()
N = [0]


def folder(name):
    N[0] += 1
    path = os.path.join(_quiet.FOLDER, 'pack%d' % N[0], name)
    os.makedirs(path, exist_ok=True)
    return path


def small_story():
    """A story folder with a real scene and a real pause clip, each in its own subfolder
    as on disk, and its pack: (root, pack, fingerprint, the scene's name, the clip's)."""
    root = folder('story')
    names = []
    for binary_name in ('09_office_puzzle_lead_in', 'pause_menu'):
        path = REAL.get(binary_name).path
        sub = os.path.basename(os.path.dirname(path))
        os.makedirs(os.path.join(root, sub), exist_ok=True)
        shutil.copy2(path, os.path.join(root, sub, os.path.basename(path)))
        names.append('%s/%s' % (sub, os.path.basename(path)))
    dest = os.path.join(os.path.dirname(root), 'story.dat')
    info = pack.write_pack(root, dest)
    return root, dest, info, names[0], names[1]


def test_every_recording_reads_back_by_its_path_in_the_folder():
    root, dest, info, scene, clip = small_story()
    opened = pack.Pack(dest)
    assert sorted(opened.files) == sorted([scene, clip])
    assert scene.startswith('sceen/')
    with open(os.path.join(root, *scene.split('/')), 'rb') as fh:
        assert opened.read(scene) == fh.read()
    assert info['files'] == 2 and info['size'] == os.path.getsize(dest)
    assert pack.fingerprint(dest)['sha256'] == info['sha256']
    assert not os.path.exists(dest + '.part')


def test_the_pack_hides_its_names_and_its_sound():
    root, dest, _info, scene, _clip = small_story()
    with open(dest, 'rb') as fh:
        raw = fh.read()
    assert raw.startswith(pack.MAGIC)
    assert scene.encode('utf-8') not in raw and b'sceen/' not in raw
    with open(os.path.join(root, *scene.split('/')), 'rb') as fh:
        assert fh.read()[1000:1064] not in raw                      # no stretch of the MP3


def flip(path, at):
    with open(path, 'r+b') as fh:
        fh.seek(at)
        byte = fh.read(1)
        fh.seek(-1, 1)
        fh.write(bytes([byte[0] ^ 1]))


def test_a_damaged_recording_a_damaged_index_and_a_foreign_file_are_refused():
    _root, dest, _info, scene, _clip = small_story()
    opened = pack.Pack(dest)
    at, length = opened.files[scene]
    flip(dest, opened.start + at + length // 2)
    try:
        pack.Pack(dest).read(scene)
    except pack.PackError as error:
        assert 'damaged' in str(error)
    else:
        raise AssertionError('a damaged recording was read')
    flip(dest, len(pack.MAGIC) + 4 + 20)                           # inside the index
    for bad in (dest, REAL.get('09_office_puzzle_lead_in').path):  # and an MP3 is no pack
        try:
            pack.Pack(bad)
        except pack.PackError:
            pass
        else:
            raise AssertionError('%s opened as a pack' % bad)


def test_one_part_cannot_pass_for_another():
    data = pack.seal(b'hello', 'sceen/a.mp3')
    assert pack.unseal(data, 'sceen/a.mp3') == b'hello'
    try:
        pack.unseal(data, 'sceen/b.mp3')
    except pack.PackError:
        pass
    else:
        raise AssertionError('a part opened under another name')


def game_without_its_story(info=None, size=None):
    """A game folder whose recordings hold system/misc but no story folder, with the
    fingerprint a build writes, when given."""
    game = folder('game')
    misc = os.path.join(paths.audio(), 'system', 'misc')
    shutil.copytree(misc, os.path.join(game, 'data', 'audio', 'system', 'misc'))
    if info is not None:
        os.makedirs(os.path.dirname(os.path.join(game, paths.PACK_FINGERPRINT)), exist_ok=True)
        with open(os.path.join(game, paths.PACK_FINGERPRINT), 'w', encoding='utf-8') as fh:
            json.dump({'size': info['size'] if size is None else size, 'sha256': info['sha256']}, fh)
    return game


def with_pack_at(where, fn):
    saved = paths.story_pack
    paths.story_pack = lambda: where
    try:
        return fn()
    finally:
        paths.story_pack = saved


def test_without_the_folder_the_recordings_come_from_the_pack():
    _root, dest, info, scene, clip = small_story()
    game = game_without_its_story(info)

    def check():
        found = Recordings(os.path.join(game, 'data', 'audio'), recordings.open_pack(game))
        office = found.get('09_office_puzzle_lead_in')
        assert office.pack is not None and office.path == scene
        assert found.get('pause_menu').path == clip
        solved = found.get('Solved')                               # system/misc stays loose
        assert solved.pack is None and os.path.isfile(solved.path)
        assert abs(office.length - REAL.get('09_office_puzzle_lead_in').length) < 1e-6
        assert office.source().read() == pack.Pack(dest).read(scene)
    with_pack_at(dest, check)


def test_a_missing_pack_or_one_from_another_build_stops_with_a_message():
    _root, dest, info, _scene, _clip = small_story()
    for where, size, words in ((os.path.join(_quiet.FOLDER, 'nowhere.dat'), None, 'were not found'),
                               (dest, info['size'] + 1, 'does not belong')):
        game = game_without_its_story(info, size)
        try:
            with_pack_at(where, lambda: recordings.open_pack(game))
        except paths.MissingData as stop:
            assert words in str(stop) and 'extract the whole game folder again' in str(stop), stop
        else:
            raise AssertionError('no MissingData for %s' % words)
    game = game_without_its_story()
    with open(dest, 'wb') as fh:
        fh.write(b'not a pack at all')
    try:
        with_pack_at(dest, lambda: recordings.open_pack(game))
    except paths.MissingData as stop:
        assert 'damaged' in str(stop)
    else:
        raise AssertionError('a foreign story.dat opened')


def test_the_mixer_plays_a_packed_recording_from_memory():
    import pygame
    from mindsight.platform.audio import Audio
    _root, dest, info, _scene, _clip = small_story()
    game = game_without_its_story(info)
    found = with_pack_at(dest, lambda: Recordings(os.path.join(game, 'data', 'audio'),
                                                  recordings.open_pack(game)))
    audio = Audio()
    audio.open(pygame)
    try:
        office = found.get('09_office_puzzle_lead_in')
        audio.scene.play(office, 2.0)
        assert audio.scene.playing and pygame.mixer.music.get_busy()
        audio.play_clip(found.get('pause_menu'))                   # a Sound, from bytes too
        assert pygame.mixer.Channel(1).get_busy()
        audio.play_solved(found.get('Solved'))                     # and one from its file
    finally:
        audio.close()


def test_from_source_the_loose_folder_wins():
    assert REAL.pack is None
    assert os.path.isfile(REAL.get('09_office_puzzle_lead_in').path)
    assert paths.story_pack().endswith(os.path.join('dist', 'data', 'story.dat'))


def test_a_build_looks_in_the_data_folder_beside_its_exe():
    saved = paths.FROZEN, paths.EXE_DIR
    paths.FROZEN, paths.EXE_DIR = True, os.path.join('C:\\', 'Games', 'Mindsight-Windows')
    try:
        assert paths.story_pack() == os.path.join('C:\\', 'Games', 'Mindsight-Windows', 'data', 'story.dat')
    finally:
        paths.FROZEN, paths.EXE_DIR = saved


_quiet.run_tests(globals())
