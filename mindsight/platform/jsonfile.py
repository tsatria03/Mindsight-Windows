"""Safe JSON files, for the save (aidocks/plans/foundation_plan.md).

Writing never leaves a half-written file where the save should be: the new contents go
to ``<name>.tmp`` first, the old file becomes ``<name>.bak``, and the temporary file then
takes its place. Reading falls back on the backup: a damaged file is kept as
``<name>.damaged`` and the backup read instead; with no backup, there is nothing to
read, and the next write replaces it. A file missing with its backup there, as after a
write cut off between its two swaps, reads the backup too.
"""
from __future__ import annotations

import json
import logging
import os

log = logging.getLogger('jsonfile')


def _load(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def read(path: str):
    """The data in ``path``, or in its backup when it is damaged or missing; None when
    neither can be read."""
    backup = path + '.bak'
    if os.path.exists(path):
        try:
            return _load(path)
        except (OSError, ValueError) as error:
            log.warning('%s is damaged (%s); kept as .damaged', path, error)
            try:
                os.replace(path, path + '.damaged')
            except OSError:
                log.exception('could not keep the damaged %s', path)
    if os.path.exists(backup):
        try:
            data = _load(backup)
            log.info('read the backup of %s', path)
            return data
        except (OSError, ValueError) as error:
            log.warning('the backup of %s is damaged too (%s)', path, error)
    return None


def write(path: str, data) -> None:
    """Write ``data`` to ``path`` as JSON, keeping the file before as ``.bak``. Raises
    OSError when it cannot be written; the old file is then left as it was."""
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    temporary = path + '.tmp'
    with open(temporary, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=1)
        f.flush()
        os.fsync(f.fileno())
    if os.path.exists(path):
        os.replace(path, path + '.bak')
    os.replace(temporary, path)
