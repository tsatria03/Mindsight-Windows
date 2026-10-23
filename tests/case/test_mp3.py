"""The MP3 length reader: built frames, an ID3 tag, bytes or a path, and real recordings."""
import _quiet  # noqa: F401  (first, before any of the game)

import os
import struct

from mindsight import paths
from mindsight.platform import mp3


def frame(version='1', kbps=128, rate=44100, pad=0):
    """One MPEG audio layer III frame of silence: its header, then zeros to its size."""
    ver_bits = {'1': 3, '2': 2}[version]
    br_table = mp3.BITRATES[1 if version == '1' else 2]
    sr_index = mp3.RATES[ver_bits].index(rate)
    header = (0x7FF << 21) | (ver_bits << 19) | (1 << 17) | (1 << 16) | (br_table.index(kbps) << 12) \
        | (sr_index << 10) | (pad << 9)
    size = (144 if version == '1' else 72) * kbps * 1000 // rate + pad
    return struct.pack('>I', header) + bytes(size - 4)


def test_frames_are_counted():
    data = frame() * 100
    assert abs(mp3.length(data) - 100 * 1152 / 44100) < 1e-9


def test_mpeg2_frames_at_22050():
    data = frame('2', 64, 22050) * 50
    assert abs(mp3.length(data) - 50 * 576 / 22050) < 1e-9


def test_an_id3_tag_is_skipped():
    tag_body = b'\xff\xfb' * 50          # looks like frame headers, but is inside the tag
    tag = b'ID3\x04\x00\x00' + bytes([0, 0, 0, len(tag_body)]) + tag_body
    assert abs(mp3.length(tag + frame() * 10) - 10 * 1152 / 44100) < 1e-9


def test_a_path_or_bytes():
    path = os.path.join(_quiet.FOLDER, 'test.mp3')
    with open(path, 'wb') as f:
        f.write(frame() * 20)
    assert mp3.length(path) == mp3.length(frame() * 20)


def test_real_recordings():
    audio = paths.audio()
    for rel, seconds in (('system/misc/pirahnaloop.mp3', 124.0), ('system/misc/Rewind.mp3', 6.4),
                         ('story/sceen/roof_puzzle_iteration_1.mp3', 9.5),
                         ('story/sceen/roof_entry_scene.mp3', 141.8)):
        got = mp3.length(os.path.join(audio, *rel.split('/')))
        assert abs(got - seconds) < 0.05, (rel, got)


_quiet.run_tests(globals())
