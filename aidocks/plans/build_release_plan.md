---
name: build_release_plan
description: "Plan 6, the last: compiler.py builds Mindsight.exe with PyInstaller, carrying the recordings, the PDF and the docs; releaser.py versions, files the changelog, builds, zips and publishes a release from the dev's own machine with gh. Windows only, no workflow."
metadata:
  node_type: memory
  type: project
---

**Status: being written.** Its open questions are being asked one at a time; no review or building until every plan is written ([[feedback_all_plans_first]]).

Plan 6, the last ([[reading_original_plan]] lists the order). It packages what plans 2 to 5 build.

## Sections

1. **`compiler.py`**, the build, with its silent `--test`.
2. **`releaser.py`**, the release.
3. Whatever the open questions add, such as packing the recordings.

## Decided

- **Windows only,** with no GitHub Actions workflow and no Linux or macOS parts ([[project_windows_only]]).
- **Two scripts at the repo's root, adapted from the reference material in the gitignored `user/` folder,** never naming where they came from ([[feedback_no_other_games]]):
  - `compiler.py` builds the game with PyInstaller into `dist\Mindsight-Windows\`, around `Mindsight.exe`. It only builds: it never zips and never changes the repository. Run with no options, it shows a numbered menu, each choice one command line, and Enter with nothing typed says the menu again. `--dry-run` lists what it would do without building.
  - `releaser.py` makes a release on the dev's own machine, asking Y or N before each step: check the changelog and the repo, set `VERSION` to today's date and that day's number (such as `26.10.22-1`), file the changelog's `unrelease:` lines under it, build with the compiler, zip the build, commit "Release <version>", tag `V<version>`, and upload the zip with `gh`. A failed build puts `VERSION` and the changelog back. It never moves or replaces a tag, a release, or a file already on one. Its check holds the changelog rules: every entry ends in a period, 5 to 100 entries ([[feedback_changelog]]).
- **What a build carries:**
  - From `game/`, only what the game reads: the recordings in `game/data/audio/`, and `game/data/text/MiNDSIGHT.pdf`, which the credits open ([[menus_saves_plan]]). Not the binary, the images, the icons or the rest of the iOS bundle.
  - **Not the NVDA client:** the game never speaks; only the by-ear tools use it, and they are for the repository, never the build ([[audio_plan]]).
  - Beside the exe: `docks\` (the readme, changelog and todo list, the changelog without an empty `unrelease:`), `VERSION` and the port's licence as `license.txt`.
  - The third-party licences, as `licenses\`, for what the build carries, such as pygame's LGPL.
- **`compiler.py --test` starts a finished build silently** for a few seconds with `--exit-after`, on a throwaway save, with SDL's dummy drivers and the message boxes off, and reads its log: the data found, the sound opened, a clean close, no `crash.txt` and exit code 0 ([[foundation_plan]]).
- **The release zip** holds one `Mindsight-Windows` folder, stores the MP3s as they are, since they barely shrink, and compresses the rest; it is written as `.part` and renamed once whole.
- **Players download releases from this repo's GitHub releases page,** `tsatria03/Mindsight-Windows`.
- **Releases are never recorded** in notes or the README ([[feedback_no_release_records]]).
- **Claude never builds or releases**; the dev runs both ([[feedback_dont_run_or_build]]).

## Open questions

Asked one at a time; each answer moves into Decided.
1. **Packing the recordings:** `requirements.txt` lists `cryptography`. Whether a build packs the recordings, encrypted, into one file beside the exe, or ships the MP3s loose.
2. **The kinds of build:** the folder build, a single exe, or a choice of both each time.
3. **Section reviews:** whether this plan, with nothing to hear beyond a build, needs a section review before it is built.
