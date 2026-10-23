---
name: story_engine_plan
description: "Plan 4: the original's 56 scenes and rules played on the audio: the scene table, what follows each scene, the input lock and cue times, the buzz cues, every puzzle's answer, failing and the Rewind's retry points, the piranha windows, pause, debug's --scene, and story_check.py."
metadata:
  node_type: memory
  type: project
---

**Status: being built,** one section at a time, since it has by-ear tests ([[feedback_next_section_on_pass]]); reviewed in one message on 2026-10-23, its two questions answered.

## Progress

- **Section 3, built 2026-10-23, waiting for the dev's by-ear tests** (the dev: "tests past", for section 2):
  - Failing, the Rewind, the timed rounds running out and the piranha windows were already in section 1's rules and played by section 2's screen, so this section proves them end to end and grows the tool.
  - `tests/case/test_story_screen.py` grew three tests: a wrong street round to its fail, the Rewind and scene 13 from 20.4 s; a roof round running out to its fail, the Rewind and scene 46 from 112 s; and the piranha windows on a real looping player on the dummy driver, a swipe inside the first window after a whole loop passing, one outside failing with failure 35. The test now puts the real clock back. 97 silent tests in all, each passing.
  - `story_check.py`'s I now says, after a failure, where the Rewind goes back to, such as "failure 35, the Rewind goes back to scene 34 from 70 seconds", and in the piranha loop whether the position is inside a window, naming it, or outside every window.
- **Section 2, FINISHED 2026-10-23,** its by-ear tests passed (the dev: "tests past"). Built the same day (the dev: "yes, continue"):
  - `mindsight/game/story_screen.py`, `StoryScreen`: opens on scene 1, or jumps to `--scene`'s; each frame hands the position to `Story.tick` for the cue's buzz; a swipe goes to `Story.swipe` with the position; a recording's end to `Story.ended`; and it does what they return: `Play` on the scene player, looping for 10, 26 and 35, Solved, the buzz. `Save` only logs where it would save until plan 5, and never in a `--scene` run; the PDF and Continue's load only log. `escape_quits` is true in scenes 1 to 7. The window shows "Scene 47: roof puzzle iteration 1", then "Your turn" or "Listening", and "Paused".
  - `Mindsight.py` now opens the story screen; **the stand-in screen is gone**, as plan 2 said it would be, with its tests.
  - The pause gesture only logs until section 4, so in the story, Escape, Enter and P do nothing yet; Alt+F4 quits.
  - `tests/interact/story_check.py`, on the game's own story screen, never saving: the agreed keys, T, I and L, with Escape quitting. **It always runs in debug mode** (the dev, 2026-10-23: "Can you make it so story check puts the game on debug mode?"), its title saying "(debug)", and takes `--scene N` to start at any scene, as the game's `--debug --scene N` does; `_tool.run()` gained `debug`.
  - `tests/case/test_story_screen.py`, 8 tests on a stand-in audio: opening on the menu and its lock, the new game into the story, the office puzzle's gate, cue and Solved, the loop, saving never in a `--scene` run, Escape in the menus only, the window's lines, and a silent run of `Mindsight.py`. 94 silent tests in all, each passing.
  - Checked silently: all four tools started through their real entry points and closed cleanly; driven by hand, `story_check.py` said the state, jumped to scene 11, skipped near its end, refused to skip a loop and a scene 99, and quit on Escape.
- **Section 1, FINISHED 2026-10-23,** with nothing to test by ear (the dev: "yes go ahead."); the dev moved on to section 2 on it:
  - `mindsight/game/scenes.py`, the whole table: each scene's recording; `THEN`, what follows as it ends (waits, plays the next, loads the save, or the Rewind's retry), whether that next scene is saved, and the failure a timed round sets as it runs out; `RETRIES`; the input lock's scenes; `GATES`, after which a swipe counts, and `CUES`, at which the buzz plays; `CUE_AT_END`; `ANSWERS`, each scene's swipes, with Solved, the save, the failure and whether the lock closes; the piranha windows; and `MENUS`, scenes 1 to 7, where Escape quits.
  - `mindsight/game/story.py`, `Story`, the rules with no sound: `start`, `jump` (as if the scene before had ended, for `--scene` and the tools), `counts` (the window's "Your turn"), `swipe`, `tick` (the cue's buzz) and `ended`, each returning effects: `Play`, `Save`, `SOLVED`, `BUZZ`, `PDF`, `LOAD`. Continue asks `has_save`, false until plan 5. The credits follow the ending: the failure is cleared as scene 55 starts.
  - `tools/scenes.py` checks the whole table against the binary, every scene's `THEN`, the retries, the gates and cues, the right and wrong answers and the menus; fed five wrong values, it reported all five.
  - `tests/case/test_story.py`, 17 tests walking the menus, Continue, every puzzle, failing and running out, the Rewind's retries, the piranha windows' edges, the tones and safe, the roof and the ending. 88 silent tests in all, each passing.
  - **Two corrections to the behaviour note, found building it** ([[project_original_behaviour]]): the buzz after a recording ends is tested on the scene current once the next has started, so it also buzzes as 26, 35, 39 and 43 begin after the scene before ends, and as the main menu begins after the manual and the credits after the ending; and `justVibrated` is cleared only as a recording ends of itself, so **street rounds 2 and 3, reached by answering, never buzz at their cue**. The first is built as the original has it; the second the dev chose to fix (below).

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
- **The story engine plays the menus too** (the dev, 2026-10-23, at the review: "I completely agree with that."): scenes 1 to 7, the main menu, New game, the audio manual, the credits and No saved game, are in the same table, so the story screen plays them and their swipes, and `Mindsight.py` opens on scene 1, as the original did. Until plan 5 ([[menus_saves_plan]]):
  - Continue, down on the main menu, always answers scene 6, `NoSavedGame`, since there is no save yet.
  - The credits' left swipe, which opens the dissertation, does nothing.
  - Escape quits in scenes 1 to 7 and pauses from scene 8 on, through `Screen.escape_quits` ([[menus_saves_plan]]).
- **`story_check.py`'s keys** (the dev, 2026-10-23, at the review: "Yes. I like that."):
  - the game's own keys, passed straight through: the arrows or W, A, S and D for the swipes, and Enter or P for the pause, since Escape quits the tool
  - T: type a scene number, then Enter, to jump there
  - I: say the state: the scene, its position, the failure, and whether a swipe counts yet
  - L: skip to 5 seconds before the playing scene's end, to hear endings and what follows quickly
  - Escape or Alt+F4: quit ([[feedback_test_tools_in_interact]])
- **Every scene can buzz at its cue: the buzz resets whenever a scene starts** (the dev, 2026-10-23: "yes please", to the proposal after section 1). A departure from the original, whose `justVibrated` was cleared only as a recording ended of itself (0x100008578), so street rounds 2 and 3, reached by answering the round before, never vibrated at their 11-second cue ([[project_original_behaviour]]). In the port they buzz there; nothing else changes, since no other scene reached by an answer has a cue.
- **The buzz** plays at each timed scene's cue and when a waiting scene's recording ends, where the original vibrated, once per recording ([[audio_plan]]).
- **The keys** are the four swipes and the double tap, as [[foundation_plan]] fixes them.
- **The story's timers run on the timer loop**, held while paused.
- **`--scene N`** starts at scene N with no failure set, and that run never writes the save ([[menus_saves_plan]]).

## Open questions

Asked one at a time; each answer moves into Decided.
1. Answered: the input lock, kept, with ignored keys silent.
2. Answered: the ending's quirk, fixed.
3. Answered: swipes while paused, ignored.
4. Answered: the window's text during the story.
5. Answered at the review: the menus played by the story engine.
6. Answered at the review: `story_check.py`'s keys.
