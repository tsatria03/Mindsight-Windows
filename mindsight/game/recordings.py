"""Finding the original's recordings by the names its binary gives them.

The binary asks for each sound by a bare name, such as ``08_introductory_scene``, from one
flat folder, as an m4a. The dev converted every one to MP3 and sorted them into folders
under ``game/data/audio/``, dropping the number prefixes
(aidocks/general/project_original_findings.md). So a recording is found:

* by its name without the number prefix, ``introductory_scene``, or, for the six names
  whose letter suffix became a number on disk, by :data:`RENAMED`;
* as ``.mp3``, anywhere under ``game/data/audio/``, in any letter case.

Moving files between the folders never breaks the lookup. A :class:`Recording` gives its
path to the players; once plan 6 packs the story's recordings, it will give their bytes
instead, through the same ``source()`` (aidocks/plans/build_release_plan.md).
"""
from __future__ import annotations

import logging
import os
import re

from .. import paths
from ..platform import mp3

log = logging.getLogger('recordings')

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


class Recording:
    """One recording: the binary's name for it, and where it is."""

    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path
        self._length = None

    def source(self):
        """What the players open: the file's path."""
        return self.path

    @property
    def length(self) -> float:
        """Its length in seconds, read from its MP3 frames once."""
        if self._length is None:
            self._length = mp3.length(self.path)
        return self._length

    def __repr__(self):
        return 'Recording(%r, %r)' % (self.name, self.path)


class Recordings:
    """Every MP3 under the recordings folder, found by the binary's names."""

    _shared = None

    @classmethod
    def shared(cls) -> 'Recordings':
        if cls._shared is None:
            cls._shared = cls(paths.audio())
        return cls._shared

    def __init__(self, folder: str):
        self.folder = folder
        self.files = {}         # file name without .mp3, in lower case -> path
        for d, _, names in os.walk(folder):
            for n in names:
                stem, ext = os.path.splitext(n)
                if ext.lower() == '.mp3':
                    self.files[stem.lower()] = os.path.join(d, n)
        self._found = {}
        log.info('%d recordings found in %s', len(self.files), folder)

    def find(self, name: str) -> Recording | None:
        """The recording the binary names ``name``, or None when it is not on disk."""
        if name in self._found:
            return self._found[name]
        path = self.files.get(disk_name(name).lower())
        found = Recording(name, path) if path else None
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
