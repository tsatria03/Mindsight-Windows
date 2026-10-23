---
name: project_later_topics
description: "Ideas, open questions and requirements for plans not yet written, kept here until that plan is written; each moves into its plan's Decided or Open questions and is struck from here."
metadata:
  node_type: memory
  type: project
---

Topics that belong to a plan not yet written. When that plan is written, each goes into it, and its line here is removed.

**Why:** questions come up long before the plan that answers them. Kept here, they are not lost when the context is compacted.

**How to apply:** before writing a plan, read this note and bring in every item that belongs to it. Ask the dev one at a time ([[feedback_one_question_at_a_time]]).

## Open, for the dev

- **The vibration cues.** The original vibrates to say "answer now" at each timed puzzle's cue and when a menu or waiting puzzle ends ([[project_original_behaviour]]). The port has no speech and no settings ([[foundation_plan]]), so this means a sound in their place, which one, and how loud against the recordings. For the audio or story engine plan.
- **The input lock.** The original ignores swipes until a recording ends, and before a timed puzzle's cue. Whether the port keeps that strictly, and whether an early key press makes any sound. For the story engine plan.
- **The ending's quirk.** After a run with any failure, the ending resumes that failure's retry point instead of the credits. Keep it as the original, or fix it so the credits always follow. For the story engine plan.
- **Swipes while paused.** The original still acts on a swipe while paused. Keep it, or ignore swipes while paused. What `pause_menu` says may settle it. For the story engine plan.
- **Interruptions.** The original steps back 3 s and plays `WelcomeBack` after a phone call. Whether the port does that when its window loses focus, or not at all. For the audio or menus plan.
- **The dissertation PDF.** The credits' left swipe opened it in another app. Whether the port opens it with Windows' default viewer, and whether the build ships it. For the menus plan.
- **Achievements.** Game Center is dropped. With no speech, local achievements could not be announced, so most likely none. For a later plan, if at all.
- **A headphones notice** at the start, since the recordings are binaural. With no speech it could only be in the window or the readme, or left out. For the menus plan.
- **`vendor/nvda/`.** With no speech, the NVDA client is unused. Whether to remove it from the repo; nothing is deleted without the dev's word. For the foundation's build, asked before then.
- **`cryptography` in `requirements.txt`.** It suggests the recordings packed and encrypted for a build. Whether the build does that, or ships the MP3s loose. For the build and release plan.
- **The plan order and the progress weights** ([[feedback_progress_summary]]), agreed once plan 1 is finished.
