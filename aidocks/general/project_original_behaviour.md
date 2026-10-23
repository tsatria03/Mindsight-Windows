---
name: project_original_behaviour
description: "How the original plays, read from the binary with addresses: the four swipes and the double tap, the input lock, the 56 scenes and what follows each, every puzzle's answer and timing, the vibration cues, failing and the Rewind, saving, pause and interruptions, and the ending's quirk."
metadata:
  node_type: memory
  type: project
---

How `game/MiNDSIGHT` plays, read on 2026-10-22 with capstone from its arm64 code. What the bundle holds is in [[project_original_findings]].

**Why:** the story is code, not data, so the binary is the only record of what follows what, which swipe answers each puzzle, and when. Every later plan builds on these numbers.

**How to apply:** treat this note as the original's rules. When the port departs from one, say so in the plan that does it, with the dev's words. Scene numbers below are the binary's own (`currentScene`).

## Input

- **Four swipes and a double tap** (`setUpGestureRecognizers`, 0x1000052c8). `swiped:` (0x1000054fc) turns each swipe into a direction for `pushDirection:` (0x1000055c8): **0 up, 1 down, 2 left, 3 right.**
- **The double tap toggles pause** (`pauseGameMenu:`, 0x100007938).
- **The input lock** (`userInputAvailable`):
  - It starts off, so the main menu must finish before a swipe counts.
  - It turns on when the scene player finishes a recording (`audioPlayerDidFinishPlaying:successfully:`, 0x100008518), before the next scene starts, so it stays on into the next scene.
  - Almost every handler turns it off when it acts, so the next recording must finish before another swipe counts. The street rounds 1 and 2 leave it on, but their cue times hold the next swipe back anyway.
  - Starting scene 39 or 43 turns it off, so those two must be heard to the end (`playScene:fromInterval:`, 0x100007148). Starting scene 35 turns it on, so the piranha loop takes a swipe at once.
  - `pushDirection:` checks only this lock, never the pause.
- **Timed scenes ignore a swipe until a cue time**, `currentTime >` the number below. Before it, the swipe does nothing.

## The vibration cues

- The phone vibrates once (`vibrate`, 0x1000076f0, system sound 0xfff) to say "answer now". `justVibrated` keeps it to once per recording and is cleared when a recording ends.
- **At a cue time** (`vibrateIfNecessary`, 0x100007738, run every 0.1 s by `incrementalUpdate`): scene 11 at 22 s, 14 at 13 s, 15 at 11 s, 16 at 11 s, 19 at 21 s, 47 at 7 s, 49 at 8.4 s, 51 at 7 s (each `currentTime >=`).
- **When a waiting scene ends** (`audioPlayerDidFinishPlaying:`): scenes 1, 2, 5, 6, 26, 35, 39 and 43. Scenes 26 and 35 loop, so in practice they never end.
- The vibration cues for 15, 16 and 49 come a second or so after a swipe already counts (10, 10 and 7 s).
- The port has no vibration, so a buzz the game makes itself plays at these cues instead ([[audio_plan]]).

## The scenes

`-[MSSceneURLStore urlForScene:]` (0x100008b58, a jump table at 0x100009014) gives each scene its recording; `playNextScene` (0x100006a7c, a jump table at 0x100006e04) says what follows when it ends. "Saves" means the next scene's number is saved as it starts. "Waits" means nothing follows: the game waits for a swipe.

- 0 `Rewind` (misc): after a failure; then the retry, below.
- 1 `main_menu_list` (speech): waits.
- 2 `new_game_menu_choice`: waits.
- 3 `new_game_confirmation`: then 8.
- 4 `audio_manual_menu_choice`: then 1.
- 5 `credits_menu_choice`: waits.
- 6 `NoSavedGame`: waits.
- 7 `LoadedSuccessfully`: then loads the save and plays the saved scene from its start.
- 8 `introductory_scene` (sceen): then 9, saves.
- 9 `office_puzzle_lead_in`: then 11.
- 10 `Beeps` (misc): loops. Its case in `playNextScene` leads to 12, but a loop never ends, so that never happens.
- 11 `solve_office_puzzle`: then 10.
- 12 `street_puzzle_leadin`: then 13, saves.
- 13 `street_puzzle_leadin2`: then 14, saves.
- 14, 15, 16 `street_puzzle_iteration_1` to `_3`: unanswered, straight to the Rewind (failure 14, 15 or 16), with no fail scene.
- 17 `street_puzzle_pass`: then 19, saves.
- 18 `street_puzzle_fail`: then the Rewind.
- 19 `car_accident_scene`: unanswered, 21 (failure 19).
- 20 `car_accident_puzzle_pass`: then 22, saves.
- 21 `car_accident_puzzle_fail`: then the Rewind.
- 22 `flashback_scene`: then 23, saves.
- 23 `flashback_scene2`: then 24, saves.
- 24 `first_tower_scene`: then 25.
- 25 `solve_guard_puzzle`: then 26.
- 26 `solve_guard_puzzle2`: loops.
- 27 `guard_puzzle_pass`, 28 `guard_puzzle_fail`: either way, then 29, saves.
- 29 `tower_entry_scene`, then 30 to 33 `tower_entry_scene2` to `5`: each then the next, saves; 33 then 34, saves.
- 34 `second_floor_scene`: then 35.
- 35 `pirahnaloop` (misc): loops.
- 36 `pirahna_puzzle_pass`: then 38, saves.
- 37 `pirahna_puzzle_fail`: then the Rewind.
- 38 `third_floor_scene`: then 39, saves.
- 39 `third_floor_scene2`: heard to the end, then waits.
- 40 `tones_puzzle_pass`: then 42, saves.
- 41 `tones_puzzle_fail`: then the Rewind.
- 42 `fourth_floor_scene`: then 43, saves.
- 43 `fourth_floor_scene2`: heard to the end, then waits.
- 44 `safe_puzzle_pass`: then 46, saves.
- 45 `safe_puzzle_fail`: then the Rewind.
- 46 `roof_entry_scene`: then 47.
- 47, 49, 51 `roof_puzzle_iteration_1` to `_3`: unanswered, 53 (failure 47, 49 or 51).
- 48, 50 `roof_puzzle_iteration_1_pass`, `_2_pass`: then 49, then 51.
- 52 `roof_puzzle_iteration_3_pass`: then 54.
- 53 `roof_puzzle_fail`: then the Rewind.
- 54 `boss_death_scene`: then 55.
- 55 `end_game_congrats` (speech): then 5, the credits; but see the ending's quirk.

Looping (`setNumberOfLoops:` -1, in `playScene:fromInterval:`): scenes 10, 26 and 35 only.

Achievements are reported as a scene's recording is fetched: `ach1` scene 11, `ach2` 19, `ach3` 20, `ach4` 24, `ach5` 27, `ach6` 36, `ach7` 40, `ach8` 44, `ach9` 55, `ach11` 5, `ach12` 53.

## The menus

All spoken recordings, answered by swipes once each has finished:
- **Main menu, scene 1** (`handleMainMenu:`, 0x100005950): up New game (scene 2); down Continue (`loadData`: a save gives 7, `LoadedSuccessfully`, and no save gives 6, `NoSavedGame`); left the audio manual (scene 4, then back to 1); right the credits (scene 5).
- **New game, scene 2** (`handleNewGame:`, 0x100005b98): up confirms (scene 3, then the story at 8); down goes back to 1. Starting a new game clears nothing; the old save is overwritten at the next save.
- **No saved game, scene 6** (`handleNoSavedGameFound:`, 0x100005c74): up starts a new game (scene 3); down goes back to 1.
- **Credits, scene 5** (`handleCredits:`, 0x100005d50): right goes back to 1; left opens the dissertation PDF in another app (`sendPDFtoiBooks`, 0x100008018). Coming back from that app, or closing the "Open in" menu, plays the main menu.
- The game opens straight on scene 1 (`viewDidLoad`, 0x100004f1c). There are no opening screens.

## The puzzles

Every answer below was read from its handler. "Solved" means the Solved sound plays (`playSolvedSound`, 0x1000073a0: `Solved` on its own player at volume 0.2, over the start of the next scene).

- **Office keys** (`handleOfficeKeysPuzzle:`, 0x100005e14): **right**, during scene 10 at any time, or scene 11 after 22 s. Other swipes do nothing. Then scene 12, solved, saved.
- **Street, three rounds** (`handleStreetPuzzle1:` to `3:`, 0x100005eec, 0x100005fe4, 0x1000060d8): round 1 (scene 14) after 13 s, **right**; round 2 (15) after 10 s, **up**; round 3 (16) after 10 s, **left**. A right answer plays the next round with Solved (the third gives 17, the pass); a wrong one gives 18, the fail, with the failure set to that round.
- **Car accident** (`handleCarAccident:`, 0x1000061dc): scene 19 after 21 s, **right**: 20, saved, solved. Wrong: 21, failure 19. The recording is 23.7 s, so the window is under 3 s.
- **Guard** (`handleGuard:`, 0x1000062f4): scene 26, at any time: **right** passes (27), **left** fails (28); up and down do nothing. Both go on to 29, with no Rewind and no Solved.
- **Piranhas** (`handlePiranhaPuzzleSuccess:` and `Failure:`, `piranhaPuzzleTimeValid` at 0x100006f08): scene 35, **any swipe**. It passes when the loop's time is inside one of 13 windows, strictly between start and end (`currentTimeWithinRangeStart:end:`, 0x1000070bc): 15 to 19, 25 to 27, 31 to 34, 41 to 45, 50 to 52, 57 to 59, 67 to 71, 77 to 79, 83 to 86, 93 to 97, 103 to 105, 109 to 111, 119 to 122 seconds. The loop is 124 s, and the time starts again with each loop. Pass: 36, saved, solved. Outside a window: 37, failure 35.
- **Tones** (`handleTones:`, 0x10000657c): scene 39, once heard to the end, **left**: 40, saved, solved. Any other: 41, failure 39.
- **Safe** (`handleSafe:`, 0x10000666c): scene 43, once heard to the end, **down**: 44, saved, solved. Any other: 45, failure 43.
- **Roof, three rounds** (`handleRoofPuzzle1:` to `3:`, 0x10000675c, 0x100006860, 0x100006964): round 1 (scene 47) after 7 s, **right**; round 2 (49) after 7 s, **left**; round 3 (51) after 7 s, **down**. A right answer plays that round's pass (48, 50, or 52, saved) with Solved. A wrong one gives 53, the fail, with the failure set to that round. Each round's recording is 9.5 to 11.2 s, so about 2.5 to 4 s to answer.

## Failing and the Rewind

A fail scene, or a timed round that runs out, leads to scene 0, `Rewind`. When it ends, `playNextScene` (0x100006d2c) resumes by the failure (`whichFailure`):
- 14, 15 or 16 (street): scene 13, from 20.4 s.
- 19 (car accident): scene 19, from the start.
- 35 (piranhas): scene 34, from 70 s.
- 39 (tones): scene 39, from 42 s.
- 43 (safe): scene 43, from 68.5 s.
- 47, 49 or 51 (roof): scene 46, from 112 s.

## The ending's quirk

`whichFailure` is set on every failure and **never cleared**; it is not saved, so a relaunch starts it at 0. When scene 55 ends, `playNextScene` sets scene 5, the credits, and then falls into the Rewind's code above, which reads `whichFailure` (0x100006d24). So if the player failed any puzzle during this run, the ending resumes that puzzle's retry point instead of playing the credits; only a run with no failures reaches the credits. This looks like a bug in the original, and the port fixes it, at the dev's word: the credits always follow the ending ([[story_engine_plan]]).

## Saving

- The save is **one number, the current scene**, in `Documents/saved.plist` as an array of one number (`saveData`, 0x100007e10; `loadData`, 0x100007ef8).
- It is written when `playNextScene` moves to a scene marked "saves" above, and by the office keys, car accident, piranha, tones, safe and roof round 3 passes.
- Continue plays `LoadedSuccessfully`, then the saved scene from its start.

## Pause and interruptions

- **The double tap pauses**: the scene player pauses, and `pause_menu` plays on the pause player (5.1 s). **Another double tap resumes**: the scene plays on, and the pause clip stops.
- Pausing does not lock the swipes. A swipe while paused still acts, starting the next scene while the game still counts as paused. The port ignores swipes while paused, at the dev's word ([[story_engine_plan]]). `pause_menu` says only that the game is paused, and to double tap the screen to pick up where you left off (the dev, 2026-10-23: "It just says, you paused the game, to pick up where you left off, double tap the screen."); it offers no options, as the code shows. In the port, Enter, Escape or P stands for that double tap ([[foundation_plan]]).
- **An interruption, such as a phone call** (`interruptedPlayer:`, 0x100007b64, on `AVAudioSessionInterruptionNotification`, at its start and its end alike): the scene pauses, steps back 3 s, `WelcomeBack` plays, and the game counts as paused, so the double tap resumes it.
- Only the scene player's end moves the story on; the pause clips and the Solved sound ending do nothing.
