---
name: audio_plan
description: "Plan 3: playing the original's recordings through pygame's mixer: finding each by the binary's name, the scene player (from a point, looping, pause, position), the Solved and pause players, MP3 lengths, the cue sound in place of vibration, and audio_check.py."
metadata:
  node_type: memory
  type: project
---

**Status: being written.** Its open questions are being asked one at a time; no review or building until every plan is written ([[feedback_all_plans_first]]).

Plan 3 ([[reading_original_plan]] lists the order). It stands on [[foundation_plan]] and serves the story engine.

## What the original does

Read from the binary ([[project_original_behaviour]], [[project_original_findings]]):
- **Three `AVAudioPlayer`s, nothing else.** The scene player plays one scene at a time; starting a scene replaces the last. The pause player plays `pause_menu` and `WelcomeBack`. The Solved player plays `Solved` at volume 0.2, over the start of the next scene.
- **A scene can start partway** (`playScene:fromInterval:`, 0x100007148), for the Rewind's retry points, such as 112 s into `roof_entry_scene`.
- **Three scenes loop forever:** 10 `Beeps`, 26 `solve_guard_puzzle2` and 35 `pirahnaloop`.
- **The game reads the scene's time** every 0.1 s, for the cue times and the piranha windows, and starts again from 0 on each loop.
- **Pause** pauses the scene player and plays `pause_menu`; resuming plays on and stops the clip.
- No fades, no speed changes, no filters, no volume settings.

## Sections

1. **The recordings.** `mindsight/game/recordings.py` finds a recording by the binary's name: the number prefix dropped, the five letter-suffixed names mapped, as `.mp3` anywhere under `game/data/audio/` in any letter case ([[project_original_findings]]). `mindsight/platform/mp3.py` reads an MP3's length from its frames, since pygame cannot give a streamed MP3's length. Silent tests. Nothing to hear.
2. **The players.** `mindsight/platform/audio.py`:
   - the scene through `pygame.mixer.music`, the only pygame player that starts partway (`play(start=)`) and loops (`loops=-1`), with pause, resume, its position and its end
   - the position worked out as the start point plus `get_pos()`, wrapped by the length for a looping scene, and held still while paused
   - `Solved` as a `pygame.mixer.Sound` on its own channel at 0.2
   - the pause clips as a `pygame.mixer.Sound` on another channel
   - the mixer opened at 44,100 Hz, 16-bit, stereo, so the binaural recordings play untouched; the 22,050 Hz misc sounds are resampled by the mixer
   - `tests/interact/audio_check.py` starts here: choose any of the 56 scenes by number, play it, pause and resume, jump to a point, and hear Solved over it
3. **The cue sound and losing focus**, grown into `audio_check.py`. What they are is in the open questions.

## Decided

- **pygame's mixer plays everything** ([[project_python_only]]). Nothing else opens the audio device.
- **The scene streams; the short sounds are loaded whole.** `Solved` (1.1 s), `pause_menu` (5.1 s), `WelcomeBack` and the cue sound are `Sound`s, so they play over the scene without stopping it.
- **Volumes are the original's:** every recording at full volume except `Solved` at 0.2; the player sets the level with Windows' own volume ([[foundation_plan]]).
- **Tests stay silent:** they run on SDL's dummy audio driver, so nothing is heard ([[feedback_dont_run_or_build]]).

## Open questions

Asked one at a time; each answer moves into Decided.
1. **The cue sound in place of vibration:** what it is, and how loud against the recordings.
2. **Losing focus:** whether the game pauses when its window loses focus, and whether coming back steps back 3 s and plays `WelcomeBack`, as the original did after a phone call.
3. **No sound device:** what the game does if the mixer cannot open.
