"""Speech for the by-ear tools in tests/interact/, never for the game, which never speaks.

It speaks through NVDA's own controller client, vendor/nvda/nvdaControllerClient64.dll,
and prints every line as well; when NVDA is not running, or the client cannot load, it
only prints (aidocks/plans/audio_plan.md). ``MINDSIGHT_SILENT`` makes it only print, for
starting a tool silently before it is handed over.
"""
from __future__ import annotations

import ctypes
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DLL = os.path.join(ROOT, 'vendor', 'nvda', 'nvdaControllerClient64.dll')
SILENT_ENV = 'MINDSIGHT_SILENT'

_client = None
_loaded = False


def _load():
    global _client, _loaded
    if _loaded:
        return _client
    _loaded = True
    if os.environ.get(SILENT_ENV):
        return None
    try:
        client = ctypes.WinDLL(DLL)
        client.nvdaController_speakText.argtypes = [ctypes.c_wchar_p]
        _client = client
    except Exception as error:
        print('(The NVDA client could not load: %s. Lines are only printed.)' % error)
    return _client


def running() -> bool:
    """Whether NVDA is running, so speech will be heard."""
    client = _load()
    try:
        return client is not None and client.nvdaController_testIfRunning() == 0
    except Exception:
        return False


def say(text: str, interrupt: bool = True) -> None:
    """Print a line, and speak it through NVDA when it is running."""
    print(text)
    sys.stdout.flush()
    if not running():
        return
    try:
        if interrupt:
            _client.nvdaController_cancelSpeech()
        _client.nvdaController_speakText(text)
    except Exception:
        pass
