---
name: audio_plan
description: "Plan 3: playing the original's recordings through pygame's mixer: finding each by the binary's name, the scene player (from a point, looping, pause, position), the Solved and pause players, MP3 lengths, the cue sound in place of vibration, and audio_check.py."
metadata:
  node_type: memory
  type: project
---

**Status: FINISHED 2026-10-23,** its last section's by-ear tests passed (the dev: "Also section 3 tests past."). Built one section at a time, reviewed in one message the same day.

## Progress

- **Section 3, FINISHED 2026-10-23,** its by-ear tests passed, the buzz set to the dev's 160 Hz, sine, at 20 percent. Built the same day:
  - `mindsight/platform/buzz.py`: the buzz made in memory with `array` and turned into a `pygame.mixer.Sound` from its buffer, never a file, in about a hundredth of a second: 170 Hz, sine, 400 ms, 10 ms fades and a steady level between them (first built pulsed 30 times a second, which the dev turned down), both ears alike, at 0.3 of full scale. Its numbers are the module's first lines; its four shapes are sine, square, triangle and sawtooth.
  - `mindsight/platform/audio.py`: the buzz on a third reserved channel (`play_buzz()`); `focus_lost()` pausing the scene; `focus_gained(welcome_back)` stepping it back 3 s, never before its start, keeping it paused, and playing WelcomeBack, which alone plays when nothing was. Resuming after a step back plays on from that point. The game's own screens use these once the story engine exists.
  - `tests/interact/buzz_check.py`: Up or W, Down or S for the frequency, 5 Hz a step since the dev asked (10 at first), 20 to 2000; Left and Right for the shape; Space to play; I for the values; H for the keys; Escape to quit; each change spoken, such as "180 hertz, square". `audio_check.py` grew: 2 plays the buzz, and switching away pauses the scene, coming back stepping it back with WelcomeBack.
  - `tests/case/test_buzz.py`, 7 tests, and three more in `test_audio.py` for losing focus: 69 silent tests in all, each passing. `test_paths.py`'s import check now reads the code with `ast`, after a docstring line starting "from memory" was taken for an import.
  - Checked silently: every tool started through its real entry point and closed cleanly; driven by hand, `buzz_check.py` stepped the frequency and the four shapes and played, and `audio_check.py` played the buzz over a scene and stepped back on coming back.
- **Section 2, FINISHED 2026-10-23,** all five by-ear tests passed (the dev: "section 2 past. all 5 tests"). Built the same day (the dev: "ready for section 2"):
  - `mindsight/platform/audio.py`: the mixer at 44,100 Hz, 16-bit stereo, with two reserved channels; `ScenePlayer` through `pygame.mixer.music`, starting partway, looping, pausing, its position timed on the game's clock from its start point, held while paused and wrapped by the length when looping, and its end noticed only after a quarter of a second, never for a loop, a pause or a stop; Solved at 0.2 on channel 0; the pause clips on channel 1. `NoSound` carries the player's message.
  - `Mindsight.py` opens the sound before the window and closes it after; no sound device shows its message box, writes `crash.txt` and closes the game ([[foundation_plan]]).
  - `mindsight/game/scenes.py`, begun early: the 56 scenes' recordings by number and the three looping scenes, which `audio_check.py` needs; the story engine adds the rest. `tools/scenes.py` now fails if either differs from the binary, and `test_recordings.py` takes its names from it.
  - `tests/interact/_tool.py`, what every tool shares: its own save, Escape quitting before the game's keys, and `run()`, which never closes silently on an error; `foundation_check.py` moved onto it, unchanged to the ear.
  - `tests/interact/audio_check.py`, with the agreed keys and one more, **I, saying where the playing scene is,** to check a typed point such as 112 seconds; a scene ending of itself is spoken.
  - `tests/case/test_audio.py`, 11 tests: the mixer's settings, starting partway, pause, a loop's wrap, the end and its grace, Solved at 0.2 and the clip channel, a real scene on the dummy driver, no sound device, and the scene table. 59 silent tests in all, each passing.
  - Checked silently: `audio_check.py` and `foundation_check.py` started through their real entry points and closed cleanly; driven by hand, `audio_check.py` chose scenes, played scene 46 from a typed 112 seconds, moved 5 seconds each way, paused, played Solved and WelcomeBack, looped scene 35, and quit on Escape.
- **Section 1, FINISHED 2026-10-23,** with nothing to test by ear; the dev moved on to section 2 on it (the dev: "Now you can build section 1."):
  - `mindsight/platform/mp3.py`: an MP3's length from its frames, from a path or bytes, past any ID3 tag. Moved here from `tools/scenes.py`, which now imports it, so the game and the tool never disagree about a length.
  - `mindsight/game/recordings.py`: `disk_name()` and the six renamed names, `Recordings`, every MP3 under `game/data/audio/` by its lower-case name, and `Recording`, with `source()` (a path now; bytes once plan 6 packs the story) and its `length`. `tools/scenes.py` imports the same lookup; its listing came out unchanged.
  - `tests/case/test_mp3.py` (5: built MPEG-1 and MPEG-2 frames, an ID3 tag skipped, a path or bytes, and four real recordings' lengths) and `tests/case/test_recordings.py` (5: the names on disk, all 59 found with their lengths, only FanRadio unnamed, any folder and letter case, and a missing one). 48 silent tests in all, each passing.

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

1. **The recordings.** `mindsight/game/recordings.py` finds a recording by the binary's name: the number prefix dropped, the six letter-suffixed names mapped, as `.mp3` anywhere under `game/data/audio/` in any letter case ([[project_original_findings]]). `mindsight/platform/mp3.py` reads an MP3's length from its frames, since pygame cannot give a streamed MP3's length. Silent tests. Nothing to hear.
2. **The players.** `mindsight/platform/audio.py`:
   - the scene through `pygame.mixer.music`, the only pygame player that starts partway (`play(start=)`) and loops (`loops=-1`), with pause, resume, its position and its end
   - the position worked out as the start point plus `get_pos()`, wrapped by the length for a looping scene, and held still while paused
   - `Solved` as a `pygame.mixer.Sound` on its own channel at 0.2
   - the pause clips as a `pygame.mixer.Sound` on another channel
   - the mixer opened at 44,100 Hz, 16-bit, stereo, so the binaural recordings play untouched; the 22,050 Hz misc sounds are resampled by the mixer
   - `tests/interact/audio_check.py` starts here: choose any of the 56 scenes by number, play it, pause and resume, jump to a point, and hear Solved over it
3. **The cue sound and losing focus:** `mindsight/platform/buzz.py`, the buzz, with `tests/interact/buzz_check.py` to tune it by ear; and losing focus, as the open questions settle it, grown into `audio_check.py`.

## Decided

- **pygame's mixer plays everything** ([[project_python_only]]). Nothing else opens the audio device.
- **The scene streams; the short sounds are loaded whole.** `Solved` (1.1 s), `pause_menu` (5.1 s), `WelcomeBack` and the cue sound are `Sound`s, so they play over the scene without stopping it.
- **Volumes are the original's:** every recording at full volume except `Solved` at 0.2; the player sets the level with Windows' own volume ([[foundation_plan]]).
- **The cue sound is a buzz the game makes itself,** in place of the original's vibration (the dev, 2026-10-22: "Do you mind making the buzzz? I don't want it to be saved as an audio file. I also want an interactive test to control the freq of it, along with the wave shape."):
  - **What the original did:** `AudioServicesPlaySystemSound(0xfff)` (`vibrate`, 0x1000076f0), iOS's standard vibration, with no frequency, strength or length of the game's own; commonly about 400 ms on the phone.
  - **Made in code, never saved as a file:** `mindsight/platform/buzz.py` computes the samples once at startup with the standard `array` module and turns them into a `pygame.mixer.Sound` from that buffer. Nothing is written to disk, and no file joins `game/data/audio/`.
  - **Its starting shape, to be tuned by ear:** a steady low tone of about 170 Hz, 400 ms long with about 10 ms of fade at each end so it never clicks, the same in both ears, and well below the voices. **No pulse** (the dev, 2026-10-23, hearing the first build: "Why does the tone generator paulce? I don't like that.", then "Yes please." to taking it out): it was first pulsed 30 times a second for a motor's rattle, which sounded like an envelope. It starts on its first sample, so the cue lands exactly when a swipe starts to count.
  - **Its level, tried over a scene in `audio_check.py`** (the dev, 2026-10-23: "Can you make the volume adjustable? I mean the buzz volume. Put it either in audio check or the buzz check script."): E or Page Up raises it and Q or Page Down lowers it (Q and E added at the dev's word, 2026-10-23: "I also want q/e to adjust the volume as well"), 5 percent of full scale a step, from 5 to 100, starting at `buzz.py`'s 30, saying the level and playing the buzz at it; put in `audio_check.py`, since the level only means something against a voice. `Audio.set_buzz_level()` makes it again for the tool; the game's own level stays `buzz.LEVEL` until the dev chooses one.
  - **The dev's final choice, by ear: 160 Hz, sine, at 20 percent of full scale** (2026-10-23: "I'd say put the volume to 20percent. And the freq to 160hz."), after first liking 170 Hz in `buzz_check.py` and trying levels over a scene in `audio_check.py`. `buzz.py`'s `FREQUENCY` and `LEVEL` hold them.
  - **Its numbers live in one place** in `buzz.py`, so a value the dev chooses by ear is a one-line change.
  - **`tests/interact/buzz_check.py`,** a by-ear tool of its own, sets the buzz's frequency and its wave shape (sine, square, triangle or sawtooth) and plays it on demand, so the dev can choose by ear. Like every tool there, it never changes the game: the dev says which values they like, and they go into `buzz.py` ([[feedback_test_tools_in_interact]]).
  - **Its keys** (agreed 2026-10-22, with W and S added at the review, 2026-10-23): Up or W and Down or S move the frequency up or down by 5 Hz (10 at first; the dev, 2026-10-23: "Please make it so the freq keys goes by 5 hurts, not 10"); Left and Right change the wave shape; Space plays the buzz; Escape or Alt+F4 quits ([[feedback_test_tools_in_interact]]). Each change says the new value, such as "180 hertz, square".
  - Hearing the buzz is a mandatory by-ear test; only the dev can judge it.
- **Losing focus works like the original's interruption** (the dev, 2026-10-22: "I like that.", to the proposal), from `interruptedPlayer:` (0x100007b64):
  - When the window loses focus, the scene and every timer pause at once, so no cue time or timed puzzle runs on unheard.
  - When it gets focus back, the scene steps back 3 s and `WelcomeBack` plays, and the game stays paused until Escape, Enter or P resumes it.
  - If no recording was playing, such as a menu waiting for its swipe, coming back plays `WelcomeBack` only, with nothing to step back; to be confirmed at the section review.
- **No sound device closes the game with a message box** (the dev, 2026-10-22: "I agree with that.", to the proposal). If the mixer cannot open, the game shows a Windows message box, read by the screen reader, saying that no sound device could be opened and the game needs one; it writes the reason to the log and closes. Every part of the game is a recording, so carrying on silently would leave a blind player with nothing.
- **`audio_check.py`'s keys** (agreed at the review, 2026-10-23, the dev choosing O for Solved, "O can be for solved.", and T for the typed point):
  - Up or W, Down or S: the scene before or after, saying its number and name
  - Enter: play that scene from its start
  - Left and Right: back or forward 5 seconds in the playing scene
  - T: play from the point typed, in seconds, then Enter (the dev, 2026-10-23: "Pressing t should open the typed point thing, not j.")
  - Space: pause or resume
  - O: Solved
  - 2: the buzz, once section 3 builds it
  - 3: WelcomeBack
  - Escape or Alt+F4: quit ([[feedback_test_tools_in_interact]])
- **Every by-ear tool speaks through the NVDA client** (the dev, 2026-10-22: "Yes, keep the nvda client for all interactive tests."): `vendor/nvda/nvdaControllerClient64.dll` through ctypes, from a small helper in `tests/interact/`, used by the tools only and never by the game, which stays without speech ([[foundation_plan]]). Each line is printed in the console as well, and when NVDA is not running the tool only prints. So `vendor/nvda/` stays in the repo.
- **Tests stay silent:** they run on SDL's dummy audio driver, so nothing is heard ([[feedback_dont_run_or_build]]).

## Open questions

Asked one at a time; each answer moves into Decided.
1. Answered: the cue sound, a buzz the game makes, with `buzz_check.py`.
4. Answered: `buzz_check.py`'s keys, and the NVDA client for every by-ear tool.
2. Answered: losing focus, as the original's interruption.
3. Answered: no sound device, a message box and close.
