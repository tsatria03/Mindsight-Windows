---
name: build_release_plan
description: "Plan 6, the last: compiler.py builds Mindsight.exe with PyInstaller, carrying the recordings, the PDF and the docs; releaser.py versions, files the changelog, builds, zips and publishes a release from the dev's own machine with gh. Windows only, no workflow."
metadata:
  node_type: memory
  type: project
---

**Status: FINISHED** (2026-10-23). All three sections were built at once on the dev's word ("Yes, then do plan 6. All of the sections."); the dev passed every test of `compiler.py` and played the built game from `story.dat` ("That past as well."). It has no section review ([[feedback_all_plans_first]]).

**Built:**
- `mindsight/platform/pack.py`, the pack, magic `MINDSPK1`, with its own key; `paths.story_pack()`, `dist\data\story.dat` from source and `data\story.dat` beside the exe in a build; `recordings.open_pack()` checking the size in the build's `game\data\text\story_pack.json`, beside the dissertation (the dev, 2026-10-23: "Please put story_pack.json inside the text folder, not outside it."), a missing, damaged or foreign pack a message box through `paths.MissingData`; `Recording.source()` giving a packed recording as bytes in memory, which `audio.py` hands to `mixer.music.load` with the hint `mp3`, keeping them while it plays; the log line `story recordings:`; `tools/build_pack.py`.
- `compiler.py`: no FMOD, Prism or NVDA client; the build's `game\` holds `data\audio\system\misc`, all five, and `data\text\MiNDSIGHT.pdf`; the licences of cryptography, cffi when installed, and pygame; `--test` judging the log for `game data:`, `sound opened:`, `story recordings: ...story.dat` and `Mindsight closed`. `--dry-run` checked: 6 files, 9.4 MB, beside the exe, and 55 recordings, 73 MB, into `story.dat`.
- `releaser.py`, `Mindsight-Win-<version>.zip` holding one `Mindsight-Windows` folder.
- `test_pack` (9), `test_compiler` (11) and `test_releaser` (9), all passing.

Plan 6, the last ([[reading_original_plan]] lists the order). It packages what plans 2 to 5 build.

## Sections

1. **`compiler.py`**, the build, with its silent `--test`.
2. **`releaser.py`**, the release.
3. **The story pack:** `mindsight/platform/pack.py`, the pack and its reader, played from memory, made by `compiler.py` and `tools/build_pack.py`.

## Decided

- **No section review for this plan** (the dev, 2026-10-23: "Yes. Skip the section review for that plan only."), since it has nothing to hear beyond a finished build. It still starts only on the dev's word, and each section's tests are still listed ahead, each optional or mandatory; playing a little of a built game from `story.dat` is mandatory ([[feedback_say_ear_tests_ahead]]). Every other plan keeps its review.
- **Windows only,** with no GitHub Actions workflow and no Linux or macOS parts ([[project_windows_only]]).
- **Two scripts at the repo's root, adapted from the reference material in the gitignored `user/` folder,** never naming where they came from ([[feedback_no_other_games]]):
  - `compiler.py` builds the game with PyInstaller into `dist\Mindsight-Windows\`, around `Mindsight.exe`. It only builds: it never zips and never changes the repository. Run with no options, it shows a numbered menu, each choice one command line, and Enter with nothing typed says the menu again. `--dry-run` lists what it would do without building.
  - `releaser.py` makes a release on the dev's own machine, asking Y or N before each step: check the changelog and the repo, set `VERSION` to today's date and that day's number (such as `26.10.22-1`), file the changelog's `unrelease:` lines under it, build with the compiler, zip the build, commit "Release <version>", tag `V<version>`, and upload the zip with `gh`. A failed build puts `VERSION` and the changelog back. It never moves or replaces a tag, a release, or a file already on one. Its check holds the changelog rules: every entry ends in a period, 5 to 100 entries ([[feedback_changelog]]).
- **What a build carries:**
  - From `game/`, only what the game reads: the recordings in `game/data/audio/`, and `game/data/text/MiNDSIGHT.pdf`, which the credits open ([[menus_saves_plan]]). Not the binary, the images, the icons or the rest of the iOS bundle.
  - **Not the NVDA client:** the game never speaks; only the by-ear tools use it, and they are for the repository, never the build ([[audio_plan]]).
  - Beside the exe: `docks\` (the readme, changelog and todo list, the changelog without an empty `unrelease:`), `VERSION` and the port's licence as `license.txt`.
  - The third-party licences, as `licenses\`, for what the build carries, such as pygame's LGPL.
- **The story folder is packed; the misc folder ships as it is** (the dev, 2026-10-22: "Yes, pack the story folder in. Leave the misc folder as is in the system. Do not exclude any sounds from there."):
  - **`data\story.dat`** beside `Mindsight.exe` holds every file of `game/data/audio/story/`, both `sceen/` (45) and `speech/` (10), 55 recordings, about 70 MB.
  - **`game/data/audio/system/misc/` ships loose and whole**, all 5 files, about 4.4 MB: `Beeps`, `FanRadio`, `pirahnaloop`, `Rewind` and `Solved`. Nothing is left out, `FanRadio.mp3` included, though the game never plays it ([[project_original_findings]]); an earlier suggestion to leave it out was turned down.
  - **Encrypted with AES-256-GCM** through the `cryptography` package: an index naming each recording by its path inside `story/`, such as `sceen/roof_entry_scene.mp3`, and each recording encrypted on its own, with a fresh nonce and its own name as associated data. No compression, since MP3s barely shrink. The key ships inside the game, so this keeps out casual copying, not a determined person.
  - **Played from memory:** a recording is read and decrypted when it is needed and handed to pygame as bytes, `pygame.mixer.music.load` taking a file-like object for the scene; nothing decrypted is ever written to disk.
  - **Where the game looks:** from source, the loose `game/data/audio/story/` wins; without it, `dist\data\story.dat`; in a build, `data\story.dat` beside the exe. A missing or damaged pack shows a message box saying to extract the whole folder again ([[foundation_plan]]).
  - **`compiler.py` makes the pack** with every build, reads every recording back, leaves `story/` out of the build's `game\`, and puts the pack's size and SHA-256 inside the build, so a `story.dat` from another build is caught at once. **`tools/build_pack.py`** makes `dist\data\story.dat` on its own, for a source run without the loose folder.
  - `--test` also needs the log to say the story's recordings came from `story.dat`; the zip stores `.dat` files, as it stores MP3s.
- **Both kinds of build, chosen each time** (the dev, 2026-10-23, asked for both): the folder build, `Mindsight.exe` with its files beside it, the default; and the single exe, everything inside it. Each is one choice in `compiler.py`'s numbered menu and one command line, and `data\story.dat` sits beside the exe in both. `--test` checks either.
- **`compiler.py --test` starts a finished build silently** for a few seconds with `--exit-after`, on a throwaway save, with SDL's dummy drivers and the message boxes off, and reads its log: the data found, the sound opened, a clean close, no `crash.txt` and exit code 0 ([[foundation_plan]]).
- **The release zip** holds one `Mindsight-Windows` folder, stores the MP3s as they are, since they barely shrink, and compresses the rest; it is written as `.part` and renamed once whole.
- **Players download releases from this repo's GitHub releases page,** `tsatria03/Mindsight-Windows`.
- **Releases are never recorded** in notes or the README ([[feedback_no_release_records]]).
- **Claude never builds or releases**; the dev runs both ([[feedback_dont_run_or_build]]).

## Open questions

Asked one at a time; each answer moves into Decided.
1. Answered: the story folder packed into `data\story.dat`, the misc folder loose and whole.
2. Answered: both kinds of build, chosen each time.
3. Answered: no section review for this plan only.
