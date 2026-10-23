---
name: story_engine_plan
description: "Plan 4: the original's 56 scenes and rules played on the audio: the scene table, what follows each scene, the input lock and cue times, the buzz cues, every puzzle's answer, failing and the Rewind's retry points, the piranha windows, pause, debug's --scene, and story_check.py."
metadata:
  node_type: memory
  type: project
---

**Status: written,** every question answered on 2026-10-22. Its section review waits until every plan is written ([[feedback_all_plans_first]]).

Plan 4 ([[reading_original_plan]] lists the order). It stands on [[foundation_plan]] and [[audio_plan]]. Every rule it plays is in [[project_original_behaviour]], with the binary's addresses.

## Sections

1. **The scene table and the rules, silent.** `mindsight/game/scenes.py`: the 56 scenes by the original's numbers, each with its recording, what follows it, whether it saves, whether it loops, and its cue time. `mindsight/game/story.py`: the rules as plain state, with no sound: the current scene, the failure, the input lock, each puzzle's answer, the piranha windows, and the Rewind's retry points. Silent tests check every scene, every answer and every retry against the behaviour note. Nothing to hear.
2. **The story screen.** `mindsight/game/story_screen.py` plays the rules on the audio: each scene's recording, what follows when it ends, the swipe keys, the input lock, the cue times, the buzz at each cue and when a waiting scene ends, and Solved over the next scene. `tests/interact/story_check.py` starts here: choose any scene by number, play from it with the game's own keys, and hear its state spoken through the NVDA client: the scene, the failure, and whether a swipe counts yet.
3. **Failing, the Rewind and the piranhas.** The fail scenes, timed rounds running out, the Rewind and each retry point, and the piranha windows, grown into `story_check.py`.
4. **Pause, losing focus and debug.** Escape, Enter or P pausing with `pause_menu`, losing focus as [[audio_plan]] says, and `--scene N` in debug mode ([[foundation_plan]]).

## Decided

- **The original's rules, as read from the binary,** unless a decision below changes one ([[project_original_behaviour]]):
  - the scene order, the saves and the three looping scenes
  - every puzzle's answer and cue time, and the guard puzzle going on either way
  - the piranha windows, strictly between their start and end, counted from 0 on each loop
  - failing: a fail scene or a timed round running out leads to the Rewind, then the retry point
  - Solved at 0.2 over the start of the next scene
- **The input lock is kept exactly as the original's, and an ignored key is silent** (the dev, 2026-10-22: "yes", to the proposal):
  - A swipe key does nothing until the recording playing has finished, wherever the original locked input: after every swipe it acted on, and for the whole of scenes 39 and 43, the tones and the safe. It turns on as a recording ends and stays on into the next scene; scene 35, the piranha loop, turns it on at once.
  - Before a timed scene's cue time, a swipe key does nothing.
  - An ignored key is never a failure and makes no sound, so nothing can be mistaken for the buzz.
- **The ending's quirk is fixed: the credits always follow the ending** (the dev, 2026-10-22: "I want this fixed."). A departure from the original, where `whichFailure` is never cleared, so after a run with any failure, scene 55 ending sent the player to that failure's retry point instead of the credits (0x100006d24, [[project_original_behaviour]]). In the port, the failure is cleared when scene 55 begins, so its end always leads to scene 5, the credits. Every other use of the failure, the Rewind's retry points, is unchanged.
- **The swipe keys are ignored while paused** (the dev, 2026-10-22: "Yes, it should ignore them."). A departure from the original, whose `pushDirection:` (0x1000055c8) checks only the input lock, never `isPaused`, so a swipe while paused still acted. In the port, while paused, only Escape, Enter or P does anything, resuming; a swipe key is silent, as an ignored key is. The original has no pause-menu options of its own, so nothing else is lost.
- **The window's text during the story** (the dev, 2026-10-22: "agreed", to the proposal), for a sighted helper ([[foundation_plan]]), three short lines:
  - the scene's number and its recording's plain name, such as "Scene 47: roof puzzle iteration 1"
  - whether a swipe counts yet: "Listening", or "Your turn" once the lock is off and any cue time has passed
  - "Paused" while paused
  - It never shows a puzzle's answer, and everything in it can also be heard.
- **The buzz** plays at each timed scene's cue and when a waiting scene's recording ends, where the original vibrated, once per recording ([[audio_plan]]).
- **The keys** are the four swipes and the double tap, as [[foundation_plan]] fixes them.
- **The story's timers run on the timer loop**, held while paused.
- **`--scene N`** starts at scene N with no failure set, and saves nothing from the jump.

## Open questions

Asked one at a time; each answer moves into Decided.
1. Answered: the input lock, kept, with ignored keys silent.
2. Answered: the ending's quirk, fixed.
3. Answered: swipes while paused, ignored.
4. Answered: the window's text during the story.
