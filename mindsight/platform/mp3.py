"""An MP3's length, read from its frames, since pygame cannot give a streamed MP3's length.

The game needs it to wrap a looping scene's position, such as the piranha loop's 124
seconds, and to know where a recording ends (aidocks/plans/audio_plan.md). It counts every
MPEG audio layer III frame after any ID3 tag, so it is exact for constant and variable bit
rates alike. tools/scenes.py uses it too, so the game and the tools never disagree.
"""
from __future__ import annotations

import struct

#: Bit rates in kbit/s, by version (1 for MPEG-1, 2 for MPEG-2 and 2.5) and index.
BITRATES = {1: [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320],
            2: [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160]}
#: Sample rates in Hz, by the header's version bits (3 MPEG-1, 2 MPEG-2, 0 MPEG-2.5) and index.
RATES = {3: [44100, 48000, 32000], 2: [22050, 24000, 16000], 0: [11025, 12000, 8000]}


def length(source) -> float:
    """Seconds of audio in an MP3, given its path or its bytes."""
    if isinstance(source, (bytes, bytearray, memoryview)):
        b = bytes(source)
    else:
        with open(source, 'rb') as f:
            b = f.read()
    i = 0
    if b[:3] == b'ID3' and len(b) >= 10:
        i = 10 + ((b[6] & 127) << 21 | (b[7] & 127) << 14 | (b[8] & 127) << 7 | (b[9] & 127))
    seconds = 0.0
    while i + 4 <= len(b):
        h = struct.unpack('>I', b[i:i + 4])[0]
        ver, layer, bri, sri, pad = (h >> 19) & 3, (h >> 17) & 3, (h >> 12) & 15, (h >> 10) & 3, (h >> 9) & 1
        if (h >> 21) & 0x7FF != 0x7FF or layer != 1 or bri in (0, 15) or sri == 3 or ver == 1:
            i += 1
            continue
        rate = RATES[ver][sri]
        kbps = BITRATES[1 if ver == 3 else 2][bri]
        seconds += (1152 if ver == 3 else 576) / rate
        i += (144 if ver == 3 else 72) * kbps * 1000 // rate + pad
    return seconds
