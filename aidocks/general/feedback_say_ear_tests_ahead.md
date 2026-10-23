---
name: feedback_say_ear_tests_ahead
description: "Before starting each section, tell the dev what they will test by ear (sound or speech), marking each test optional or mandatory, in one numbered list; remind them of any mandatory test they have not reported on before moving on."
metadata:
  node_type: memory
  type: feedback
---

**Before each section starts, say whether the dev will need to test anything by ear, and what. Mark every test optional or mandatory.**

**Why:** the dev's standing rule, taken from the reference material in `user/` on 2026-10-22. Knowing beforehand, and knowing which tests matter, lets them plan their checking and confirm a section without a round of questions.

**How to apply:**
- When a section is proposed, or the dev asks to start one, give a short "To test by ear" list before building it:
  - what to run, such as `python Mindsight.py` or a tool in `tests/interact/`
  - what to listen for
- **By ear means both sound and speech.** A screen reader line to check counts as much as a sound.
- **Label each test.**
  - **Mandatory:** only a person can judge it, such as how something sounds, whether speech interrupts properly, or timing by feel. The silent tests cannot cover it.
  - **Optional:** a reassurance check that the silent tests already cover.
  - When a test becomes mandatory, say so plainly and name the script to open.
- Or say plainly "Nothing to test by ear", and why.
- Name what cannot be heard yet, so the dev doesn't look for it.
- When the section is finished, repeat the same list, still labelled, as the steps to try, and say if anything changed from what was promised.
- **Every test goes in the one numbered list,** including one added mid-section. When the dev reports a pass, take it as covering every test listed for that section; never ask again about one of them.
- **Hold the dev to the mandatory ones.** If the dev confirms a section or asks to move on without reporting on a mandatory test, remind them which one before going on. Don't remind them about optional ones.
- This goes with [[feedback_dont_run_or_build]]: the dev runs anything that makes sound or speaks, never Claude.
