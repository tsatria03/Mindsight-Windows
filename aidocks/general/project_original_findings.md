---
name: project_original_findings
description: "What the original iOS bundle in game/ is and holds: MiNDSiGHT 1.0.2 by Luke Charman, a tiny unencrypted arm64 binary with the whole story hard-coded, 60 MP3 recordings in the dev's own layout, the name mapping from the binary's names to the files, what is never played, and what to drop."
metadata:
  node_type: memory
  type: project
---

**The original is MiNDSiGHT 1.0.2** (`com.lukecharman.mindsight`, display name "MiNDSiGHT", iOS 7 or later), by Luke Charman. It is an interactive audio adventure told through binaural recordings, played by swiping up, down, left or right. How it plays is in [[project_original_behaviour]].

**Why:** read from the bundle on 2026-10-22, with the dev's corrections the same day. Every later plan builds on it.

## The binary

- `game/MiNDSIGHT`: a thin arm64 Mach-O, 91,344 bytes, **not encrypted** (`cryptid` 0).
- Only **three Objective-C classes**: `MSAppDelegate`, `MSSceneURLStore` (the scene table and Game Center achievements) and `MSViewController` (everything else).
- **No audio engine.** Three `AVAudioPlayer`s play everything: the scene player, the pause player (pause and welcome-back clips) and the Solved player.
- **There is no story data file.** The 56 scenes, their order, the puzzles, their answers and every timing are hard-coded in `MSViewController`. The port's scene table is written from the binary, citing its addresses.
- It links Game Center (achievements `ach1` to `ach12`, with no `ach10`), `UIDocumentInteractionController` (to open the PDF in another app) and `AudioServicesPlaySystemSound` (vibration).
- Plans and notes cite the binary's own virtual addresses, such as `-[MSViewController pushDirection:]` at 0x1000055c8.

## The recordings

- **60 MP3 files** (the dev, 2026-10-22): 45 in `game/data/audio/story/sceen/`, 10 in `game/data/audio/story/speech/` and 5 in `game/data/audio/system/misc/`. The folder name `sceen` is the dev's spelling and stays as it is.
- **Every one was `.m4a` in the original and was converted to MP3 by the dev** so pygame can play it with no conversion at run time ([[project_python_only]]). The binary still asks for each one as `m4a`.
- **The layout is the dev's own.** The original kept every sound in one flat folder in the app; the dev sorted them into these folders before making the repo (2026-10-22). The binary asks for each sound by bare name, never by path, so the port finds a recording by its file name anywhere under `game/data/audio/`.
- **The names on disk drop the binary's number prefixes**: the binary's `08_introductory_scene` is `introductory_scene.mp3`. Five letter-suffixed names need a mapping:
  - `26b_tower_entry_scene` to `26e_tower_entry_scene`: `tower_entry_scene2.mp3` to `tower_entry_scene5.mp3`
  - `30b_third_floor_scene`: `third_floor_scene2.mp3`
  - `33b_fourth_floor_scene`: `fourth_floor_scene2.mp3`
  - (`21b_flashback_scene2` is already `flashback_scene2.mp3`, and `11_street_puzzle_leadin2` and `23_solve_guard_puzzle2` keep their `2`.)
- **The binary names 59 recordings, and all 59 are on disk** (checked 2026-10-22): the 56 scenes, plus `Solved`, `pause_menu` and `WelcomeBack`.
- **`FanRadio.mp3` is never played by itself.** The binary never names it. The dev remembered hearing a fan and radio while following the beeps, and then found by ear that `solve_office_puzzle.mp3` is `Beeps.mp3` and `FanRadio.mp3` mixed together (the dev: "The solv office sound is a combenation of the other 2 files left in the system folder."). `FanRadio.mp3` is a production leftover. It stays on disk untouched, and the port never plays it.
- **The recordings are binaural**, made with a Neumann KU 100 dummy head, so they must be played in stereo, untouched; headphones matter.
- Sample rates: the story scenes are 44,100 Hz stereo; the five misc sounds are 22,050 Hz stereo.
- Lengths that matter for the puzzles (read from the MP3 frames, 2026-10-22): `pirahnaloop` 124.0 s, `Beeps` 39.6 s, `solve_office_puzzle` 55.8 s, the street rounds 37.4, 35.2 and 35.7 s, `car_accident_scene` 23.7 s, the roof rounds 9.5, 11.2 and 9.7 s, `roof_entry_scene` 141.8 s, `Rewind` 6.4 s, `Solved` 1.1 s, `pause_menu` 5.1 s.

## Other files

- `game/data/text/MiNDSIGHT.pdf`: **not a manual.** It is the creator's 2009 SAE Institute research dissertation, "MiNDSiGHT: An Interactive Aural Adventure" (165 pages, written in Word 2007), about the game's making and binaural audio. The original offered it from the credits, by swiping left, through "Open in".
- `game/images/` (`bg-6.png`, `speaker.png`), the app icons, launch images, `Assets.car`, `en.lproj/` with the storyboard, `Info.plist`, `PkgInfo`, `_CodeSignature/` and `archived-expanded-entitlements.xcent`: the iOS app around the game. Nothing here holds story or timing.
- `game/` is the original bundle, reorganized by the dev, and is never written to by Claude.

## What the port drops

- Game Center and its achievements; the port keeps no achievements at all, at the dev's word ([[menus_saves_plan]]).
- The on-screen remaining-time label (`updateCurrentTimeLabel`, 0x100007590), the background image and the now-playing icon.
- The idle-timer switching in `MSAppDelegate`, which only kept the phone's screen awake.
