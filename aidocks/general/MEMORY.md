# Memory index

The `[[name]]` links in `CLAUDE.md` and across these notes resolve to `aidocks/general/<name>.md`, beside this index, or, for a plan, planned or complete, to `aidocks/plans/<name>.md`. Add a one-line pointer here for every new note.

## Project
- [Original findings](project_original_findings.md): MiNDSiGHT 1.0.2 by Luke Charman; the tiny unencrypted arm64 binary with the story hard-coded; the 60 MP3s in the dev's layout; the name mapping; FanRadio never played alone; the PDF is a dissertation; what to drop.
- [Original behaviour](project_original_behaviour.md): the four swipes and the double tap, the input lock, the 56 scenes and what follows each, every puzzle's answer and timing, the vibration cues, failing and the Rewind, saving, pause, and the ending's quirk, with addresses.
- [Python only](project_python_only.md): pygame for the window, keys and all sound; no FMOD, no OpenAL and no speech, since the original is self-voiced; the MP3s converted by the dev.
- [Windows only](project_windows_only.md): no Linux, macOS or GitHub Actions workflow.
- [Solo project](project_solo.md): tsatria03 alone; credits name Luke Charman for the original.
- [Later topics](project_later_topics.md): open questions for plans not yet written, such as the plan order and the progress weights.
- [Developer tasks](project_dev_tasks.md): repository, tools, tests, build and docs tasks, kept out of the player todo list.

## Plans
- [Foundation](../plans/foundation_plan.md): plan 2, written, every question answered; debug mode on the command line only. Mindsight.py, paths, logs, error message boxes, the timer loop, the fixed keys (arrows and WASD; Escape, Enter and P), the window's text and the silent tests; no speech, Settings, key binder or volumes.
- [Audio](../plans/audio_plan.md): plan 3, written, every question answered. The recordings found by name, the scene player through pygame.mixer.music, Solved and the pause clips, MP3 lengths, the generated buzz in place of vibration with buzz_check.py, pausing on losing focus, and the NVDA client for every by-ear tool.
- [Story engine](../plans/story_engine_plan.md): plan 4, written, every question answered. The 56 scenes and their rules, the input lock kept with silent ignored keys, the buzz cues, the puzzles, failing and the Rewind, the ending fixed so the credits always follow, swipes ignored while paused, the window's three lines, --scene, and story_check.py.
- [Menus and saves](../plans/menus_saves_plan.md): plan 5, written, every question answered. The original's recorded menus answered by the swipe keys, the PDF in the default viewer, the one saved scene in saves/progress.json, --scene runs never saving, headphones in the readme only, and no achievements.
- [Build and release](../plans/build_release_plan.md): plan 6, the last, written, every question answered; no section review. compiler.py with both kinds of build and releaser.py, the story folder packed in data\story.dat with misc loose, --test, the zip and gh.

## Completed projects
- [Reading the original](../plans/reading_original_plan.md): plan 1, FINISHED 2026-10-23. tools/macho64.py, dis64.py and scenes.py, and analysis/script/scenes.txt; every puzzle value checked against the binary, no problems; the notes corrected to six renamed recordings.

## Feedback
- [Memory in aidocks](feedback_memory_in_aidocks.md): all memory lives in aidocks/, general/ for notes and plans/ for plans.
- [Plans first](feedback_record_plans_first.md): an agreed plan gets its own note, committed first; finished only on the dev's word.
- [Completed projects](feedback_completed_projects.md): a finished plan stays in plans/; only its index line moves.
- [All plans first](feedback_all_plans_first.md): write every plan, one at a time with the dev's answers, before any section review or building.
- [Review plan sections](feedback_review_plan_sections.md): before building any plan, review all its sections with the dev in one message; never start the next plan alone.
- [Next section on a pass](feedback_next_section_on_pass.md): when the dev says a section's tests passed, mark and commit it, then build the next; not across plans.
- [Say ear tests ahead](feedback_say_ear_tests_ahead.md): before each section, list the by-ear tests, sound and speech, each optional or mandatory; remind the dev of a mandatory one not reported on.
- [Grow check tools](feedback_grow_check_tools.md): a plan's by-ear tool starts in its first audible section and grows with each section.
- [Test tools in interact](feedback_test_tools_in_interact.md): by-ear tools go in tests/interact/, never in the game's menus.
- [Don't run or build](feedback_dont_run_or_build.md): never build unless told; ask before running anything that plays sound or speaks.
- [Git commits](feedback_git_commits.md): one commit per change, commit without asking, push only when a plan is finished and its docs updated; git commit -F from Git Bash.
- [GitHub usernames](feedback_use_github_usernames.md): tsatria03 and the noreply address, never real names.
- [No other games](feedback_no_other_games.md): never name the games in user/ anywhere in this repo.
- [Questions are checks](feedback_questions_are_checks.md): a question or correction from the dev is answered in chat, with no edits.
- [One question at a time](feedback_one_question_at_a_time.md): one question per reply, with a recommendation.
- [No question pickers](feedback_no_question_pickers.md): ask in plain text, never through the picker tool.
- [No release records](feedback_no_release_records.md): never record individual releases in notes or the README.
- [Changelog](feedback_changelog.md): the unrelease: block, newest first, one plain sentence per line ending in a period.
- [Todo list format](feedback_todo_list_format.md): ##Unfinished. and ##Finished., players only, bugs stated as what happens.
- [Back first](feedback_back_first.md): Back is the first row of every menu with a way back, and it opens on it.
- [Docs after each plan](feedback_docs_after_each_plan.md): when a plan is finished, bring every developer and player doc up to date, then ask to push.
- [Progress summary](feedback_progress_summary.md): after each plan, a brief overall percentage, by weights to be agreed.

## User
- [Screen reader](user_screen_reader.md): the dev uses NVDA; headings, lists and short lines, no wide tables, no noise from tools.
