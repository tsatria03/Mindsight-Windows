---
name: project_python_only
description: "The port is written entirely in Python, with pygame for the window, the keys, the frame loop and all sound (no FMOD, no OpenAL), and Prism or the NVDA client for speech. The recordings are MP3, converted from m4a by the dev; Claude never runs a conversion."
metadata:
  node_type: memory
  type: project
---

The port is written entirely in Python, in the `mindsight/` package:
- **pygame** (not pygame-ce) for the window, the keyboard, the frame loop **and all sound**, through `pygame.mixer`
- `prismatoid` (Prism) for speech through any screen reader or a Windows voice
- NVDA's own controller client, `vendor/nvda/nvdaControllerClient64.dll`, through ctypes

Don't propose moving parts to another language or engine.

**No FMOD** (the dev, 2026-10-22: "I do not want this game using the fmod library. It doesn't need it. It can just use pygame instead."). **No OpenAL** either. Nothing but pygame's mixer opens the audio device.

**Why it fits:** the original itself used only plain `AVAudioPlayer`s, with no speed changes, filters or fades ([[project_original_findings]]). What it does, pygame's mixer can do: start a recording partway through, loop it, pause and resume it, and play a short sound over it.

**Audio formats:**
- Every recording is MP3, converted from the original's `.m4a` by the dev on their own machine, so pygame plays them with no conversion at run time (the dev, 2026-10-22). Claude never runs a conversion.
- The binary names every recording with `m4a`; the port looks each one up by its name as `.mp3`, and never edits the original to match.
- The recordings are binaural, so they are played in stereo, as they are, with nothing mixed down.

**How to apply:**
- Write any new code in Python, inside `mindsight/`.
- `requirements.txt` holds `pygame`, `prismatoid` and `cryptography`; what `cryptography` is for is still to be decided ([[project_later_topics]]).
- Don't move, rename, convert or delete sound files unless the dev asks.
