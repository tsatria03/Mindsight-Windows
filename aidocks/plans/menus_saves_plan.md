---
name: menus_saves_plan
description: "Plan 5: the original's recorded menus around the story (the main menu, New game, Continue, No saved game, the audio manual and the credits) answered by the swipe keys, the dissertation PDF, and the save: one scene number in saves/progress.json, written at the original's checkpoints."
metadata:
  node_type: memory
  type: project
---

**Status: written,** every question answered on 2026-10-22. Its section review waits until every plan is written ([[feedback_all_plans_first]]).

Plan 5 ([[reading_original_plan]] lists the order). The menus and the saves were first proposed as two plans and were combined at the dev's word (2026-10-22: "yes, combine them."), since the original's menus are scenes the story engine already plays, and its save is one number. It stands on [[story_engine_plan]].

## What the original does

Read from the binary ([[project_original_behaviour]]):
- **The game opens straight on scene 1**, the main menu recording. Every menu is a recording, answered by a swipe once it has finished, with a vibration (the port's buzz) to say so.
- **Main menu, scene 1:** up New game; down Continue; left the audio manual; right the credits.
- **New game, scene 2:** up confirms (scene 3, then the story at 8); down goes back to 1.
- **Continue:** with a save, scene 7, `LoadedSuccessfully`, then the saved scene from its start; with none, scene 6, `NoSavedGame`: up starts a new game, down goes back to 1.
- **The audio manual, scene 4**, plays, then goes back to 1.
- **The credits, scene 5:** right goes back to 1; left opens the dissertation PDF in another app, and coming back plays the main menu. The ending leads here too ([[story_engine_plan]]).
- **The save** is one number, the current scene, written at the original's checkpoints: when the story moves to a scene marked "saves", and on the office keys, car accident, piranha, tones, safe and roof round 3 passes. Nothing is saved on quitting. Starting a new game clears nothing; the old save is overwritten at the first checkpoint.

## Sections

1. **The save.** `mindsight/game/progress.py`: `saves/progress.json` in the save folder, holding the scene number, written through the safe JSON files ([[foundation_plan]]) at the original's checkpoints, and read by Continue. A damaged or missing file counts as no save. Silent tests.
2. **The menus around the story.** The story engine already plays the menu scenes and their swipes ([[story_engine_plan]]); this section adds what needs the save or the PDF: Continue with and without a save, the credits' left swipe opening the dissertation, and coming back from it to the main menu, checked end to end. `tests/interact/menu_check.py`, with its own save, runs the game from its start, with keys to make or clear a save.

## Decided

- **The menus are the original's recordings**, answered by the swipe keys; the port adds no list menus of its own ([[foundation_plan]]).
- **The save is the original's:** one scene number, at the original's checkpoints, nothing on quitting, and New game clearing nothing.
- **The save file is `saves/progress.json`** under `%APPDATA%\Mindsight`, as `{"scene": N}`. A number outside 0 to 55 counts as no save.
- **The dissertation PDF keeps the credits' left swipe** (the dev, 2026-10-22: "I agree.", to the proposal):
  - Left on the credits, scene 5, opens `MiNDSIGHT.pdf` in Windows' default PDF viewer (`os.startfile`), as the original's "Open in" did (`sendPDFtoiBooks`, 0x100008018).
  - The build ships the PDF beside the game ([[build_release_plan]], when written); a run from source opens `game/data/text/MiNDSIGHT.pdf`.
  - The game pauses as the viewer takes focus, as losing focus does ([[audio_plan]]).
  - Coming back plays the main menu, scene 1, as the original did (`returnedFromBackground`, 0x100008278), in place of the usual step back and `WelcomeBack`.
  - If Windows has no PDF viewer, nothing opens, the log says why, and the credits carry on waiting for a swipe.
- **Headphones are named in the player docs only** (the dev, 2026-10-22: "Keep that in the player facing docks."). `docks/readme.txt` says near its top that the recordings are binaural and need headphones; the game itself shows no notice, so the original's opening is unchanged. It is written when the readme is brought up to date ([[feedback_docs_after_each_plan]]).
- **A run started with `--scene` never writes the save** (the dev, 2026-10-22: "Agreed", to the proposal), at any checkpoint it reaches, so a test jump can never overwrite real progress. A plain `--debug` run, without `--scene`, saves as normal, since it plays from the start like any other run ([[foundation_plan]]).
- **No achievements** (the dev, 2026-10-22: "We do not need achievements at all"). The original's eleven Game Center achievements, `ach1` to `ach9`, `ach11` and `ach12`, are dropped with Game Center, and the port reports or keeps none ([[project_original_findings]]).
- **Escape quits the game before the story has started** (the dev, 2026-10-23: "in Mindsight.py, escape should quit the game if you did not start the story yet."):
  - In the menu scenes, 1 to 7 (the main menu, New game, Continue's two answers, the audio manual and the credits), Escape quits at once, with nothing saved, as quitting never saves. Enter and P still stand for the double tap there.
  - Once the story begins, at scene 8 or at a scene Continue loads, Escape is the double tap again, pausing and resuming ([[foundation_plan]]).
  - After the ending, the credits are a menu again, so Escape quits there.
  - Each screen says whether Escape quits on it (`Screen.escape_quits`); the App asks before Escape becomes the pause. Built into plan 2's stand-in screen on 2026-10-23, since it comes before any story.
- **Quitting** is also closing the window or Alt+F4 ([[foundation_plan]]); the original had no Quit.

## Open questions

Asked one at a time; each answer moves into Decided.
1. Answered: the dissertation PDF.
2. Answered: headphones, in the player docs only.
3. Answered: a `--scene` run never saves.
4. Answered: no achievements.
