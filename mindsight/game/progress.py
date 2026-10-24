"""The save: one scene number, as the original kept (aidocks/plans/menus_saves_plan.md).

``saves/progress.json`` in the save folder holds ``{"scene": N}``, written through the
safe JSON files at the original's checkpoints, and read by Continue. Nothing is saved on
quitting, and a new game clears nothing: the old save is overwritten at the first
checkpoint. A missing or damaged file, or a scene that is not a checkpoint, counts as no
save, so a file edited by hand cannot leave the game stuck on the Rewind or a menu.
"""
from __future__ import annotations

import logging

from . import scenes as S
from .. import paths
from ..platform import jsonfile

log = logging.getLogger('progress')


def path() -> str:
    return paths.user_path('saves', 'progress.json')


def load() -> int | None:
    """The saved scene, or None when there is no save to continue from."""
    data = jsonfile.read(path())
    if data is None:
        return None
    scene = data.get('scene') if isinstance(data, dict) else None
    if type(scene) is not int or scene not in S.CHECKPOINTS:
        log.warning('the save holds %r, which is not a checkpoint: no save', data)
        return None
    return scene


def has_save() -> bool:
    return load() is not None


def save(scene: int) -> None:
    """Save ``scene`` as the place to continue from. Raises OSError when it cannot."""
    jsonfile.write(path(), {'scene': scene})
