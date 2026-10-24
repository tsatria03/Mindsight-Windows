---
name: project_dev_tasks
description: "The developer tasks (repository, tools, tests, build and docs), open and finished, kept out of docks/todo list.txt, which is for players only."
metadata:
  node_type: memory
  type: project
---

The developer tasks, which `docks/todo list.txt` leaves out because it ships to players ([[feedback_todo_list_format]]). Same style: newest at the top, one or two short sentences each. An item moves to Finished only when the dev confirms it.

## Unfinished

None.

## Finished

- `docks/readme.txt`, `changelog.txt` and `todo list.txt` are written, after plan 4 made the game playable (2026-10-23).
- `README.md` is a proper developer's guide, written after plan 1 at the dev's request (2026-10-23).
- The dev's move of the scene listing into `analysis/script/` is committed as a rename, and `tools/scenes.py` writes it there (2026-10-23).
- The dev's sound reorganization, from the original's one flat folder into `story/sceen/`, `story/speech/` and `system/misc/` under `game/data/audio/`, with the m4a files converted to MP3, went in with the initial commit (2026-10-22).
