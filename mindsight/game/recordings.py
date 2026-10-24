"""Finding the original's recordings by the names its binary gives them.

The binary asks for each sound by a bare name, such as ``08_introductory_scene``, from one
flat folder, as an m4a. The dev converted every one to MP3 and sorted them into folders
under ``game/data/audio/``, dropping the number prefixes
(aidocks/general/project_original_findings.md). So a recording is found:

* by its name without the number prefix, ``introductory_scene``, or, for the six names
  whose letter suffix became a number on disk, by :data:`RENAMED`;
* as ``.mp3``, anywhere under ``game/data/audio/``, in any letter case.

Moving files between the folders never breaks the lookup.

The story's recordings, ``story/``, are loose from source, and in a build come from
``data\\story.dat`` (platform/pack.py, aidocks/plans/build_release_plan.md): the loose
folder wins when it is there; without it, the pack is opened, and checked against the
size the build wrote for it. A :class:`Recording` gives the players its file's path, or
its bytes from the pack, decrypted in memory, through the same ``source()``.
"""
from __future__ import annotations

import io
import json
import logging
import os
import re

from .. import paths
from ..platform import mp3
from ..platform import pack as story_pack

log = logging.getLogger('recordings')

MISSING_PACK = ("Mindsight's story recordings were not found, so the game cannot start.\n\n"
                "They belong in story.dat, in the data folder beside Mindsight.exe. The game "
                "looked for:\n%s\n\n"
                "Please extract the whole game folder again.")
WRONG_PACK = ("Mindsight's story.dat is damaged, or does not belong to this copy of the game "
              "(%s), so the game cannot start.\n\n"
              "Please extract the whole game folder again.")

#: The six names whose letter suffix became a number on disk (the dev's renaming).
RENAMED = {
    '26b_tower_entry_scene': 'tower_entry_scene2',
    '26c_tower_entry_scene': 'tower_entry_scene3',
    '26d_tower_entry_scene': 'tower_entry_scene4',
    '26e_tower_entry_scene': 'tower_entry_scene5',
    '30b_third_floor_scene': 'third_floor_scene2',
    '33b_fourth_floor_scene': 'fourth_floor_scene2',
}


def disk_name(binary_name: str) -> str:
    """The file name, without .mp3, that the binary's name is on disk."""
    return RENAMED.get(binary_name) or re.sub(r'^\d+[a-z]?_', '', binary_name)


def open_pack(game_folder: str):
    """story.dat, opened and checked against the size a build wrote for it in
    game\\data\\text\\story_pack.json; :class:`paths.MissingData`, with the player's message,
    when it is missing, damaged or from another build."""
    where = paths.story_pack()
    if not os.path.isfile(where):
        raise paths.MissingData(MISSING_PACK % where)
    expected = os.path.join(game_folder, paths.PACK_FINGERPRINT)
    if os.path.isfile(expected):
        try:
            with open(expected, encoding='utf-8') as f:
                size = json.load(f)['size']
        except (OSError, ValueError, KeyError, TypeError):
            size = None
        if size is not None and os.path.getsize(where) != size:
            raise paths.MissingData(WRONG_PACK % ('it is %d bytes, not %d' % (os.path.getsize(where), size)))
    try:
        opened = story_pack.Pack(where)
    except story_pack.PackError as error:
        raise paths.MissingData(WRONG_PACK % error) from None
    return opened


class Recording:
    """One recording: the binary's name for it, and where it is: a file, or a name in
    story.dat."""

    def __init__(self, name: str, path: str, pack=None):
        self.name = name
        #: The file's path, or, with ``pack``, the recording's name in it.
        self.path = path
        self.pack = pack
        self._length = None

    def source(self):
        """What the players open: the file's path, or its bytes from the pack."""
        if self.pack is None:
            return self.path
        return io.BytesIO(self.pack.read(self.path))

    @property
    def length(self) -> float:
        """Its length in seconds, read from its MP3 frames once."""
        if self._length is None:
            self._length = mp3.length(self.path if self.pack is None else self.pack.read(self.path))
        return self._length

    def __repr__(self):
        return 'Recording(%r, %r)' % (self.name, self.path)


class Recordings:
    """Every MP3 under the recordings folder, found by the binary's names."""

    _shared = None

    @classmethod
    def shared(cls) -> 'Recordings':
        if cls._shared is None:
            folder = paths.audio()
            pack = None
            if not os.path.isdir(os.path.join(folder, paths.STORY_FOLDER)):
                pack = open_pack(paths.game())
            cls._shared = cls(folder, pack)
        return cls._shared

    def __init__(self, folder: str, pack=None):
        self.folder = folder
        self.pack = pack
        self.files = {}         # file name without .mp3, in lower case -> path, or name in the pack
        for d, _, names in os.walk(folder):
            for n in names:
                stem, ext = os.path.splitext(n)
                if ext.lower() == '.mp3':
                    self.files[stem.lower()] = os.path.join(d, n)
        self.packed = set()
        if pack is not None:
            for name in pack.files:
                stem, ext = os.path.splitext(name.rsplit('/', 1)[-1])
                if ext.lower() == '.mp3':
                    self.files[stem.lower()] = name
                    self.packed.add(name)
        self._found = {}
        log.info('%d recordings found in %s', len(self.files), folder)
        # compiler.py --test looks for this line, to know a build played from story.dat.
        log.info('story recordings: %s', pack.path if pack is not None
                 else os.path.join(folder, paths.STORY_FOLDER))

    def find(self, name: str) -> Recording | None:
        """The recording the binary names ``name``, or None when it is not on disk."""
        if name in self._found:
            return self._found[name]
        path = self.files.get(disk_name(name).lower())
        found = None
        if path:
            found = Recording(name, path, self.pack if path in self.packed else None)
        if found is None:
            log.warning('the recording %s is not on disk as %s.mp3', name, disk_name(name))
        self._found[name] = found
        return found

    def get(self, name: str) -> Recording:
        """Like :meth:`find`, but a missing recording is an error, naming it."""
        found = self.find(name)
        if found is None:
            raise KeyError('the recording %s is not on disk as %s.mp3' % (name, disk_name(name)))
        return found
