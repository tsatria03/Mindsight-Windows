"""The story as a screen: story.py's rules played on the audio
(aidocks/plans/story_engine_plan.md).

The game opens here, on scene 1, the main menu, as the original did, or on the scene
``--scene`` names in debug mode. Every frame, the scene's position goes to the rules for
the buzz at a cue; a swipe goes to them with the position; and a recording ending of
itself goes to them too. Whatever they say is done: a scene plays, looping if it loops;
Solved plays over it; the buzz plays; the place is saved.

The double tap, Escape, Enter or P, pauses: the scene and every timer stop, and
``pause_menu`` plays; the double tap again stops the clip and plays on. While paused, a
swipe does nothing (the port's change). In the menus, Escape quits instead
(aidocks/plans/menus_saves_plan.md). Losing the window's focus pauses the same way, with
no clip; coming back steps the scene back 3 seconds and plays ``WelcomeBack``, and it
stays paused until the double tap, as after the original's interruption
(interruptedPlayer:, 0x100007b64). Pausing while a scene waits, its recording over, only
plays the clip; resuming stops it, and the scene goes on waiting.

The place is saved in progress.py at the original's checkpoints, and Continue plays the
saved scene from its start (aidocks/plans/menus_saves_plan.md); a save that cannot be
written is logged, and the story goes on. A run started with ``--scene`` never saves.
Until section 2, the credits' left swipe only logs.
"""
from __future__ import annotations

import logging

from . import progress as saved_progress
from . import scenes as S
from .recordings import Recordings, disk_name
from .story import BUZZ, LOAD, PDF, SOLVED, Play, Save, Story
from ..platform.audio import Audio
from ..ui.screens import Screen

log = logging.getLogger('story')


def plain_name(scene):
    """A scene's recording as words, such as "roof puzzle iteration 1"."""
    return disk_name(S.name(scene)).replace('_', ' ')


class StoryScreen(Screen):
    name = 'story'

    def __init__(self, app, audio=None, recordings=None, story=None, start_scene=None,
                 progress=saved_progress):
        super().__init__(app)
        self.audio = audio or Audio.shared()
        self.recordings = recordings or Recordings.shared()
        #: The save, progress.py; the tests and the by-ear tools may hand another.
        self.progress = progress
        self.story = story or Story(has_save=progress.has_save)
        #: The scene --scene named; a run that starts there never saves.
        self.start_scene = start_scene
        self.saving = start_scene is None
        self.paused = False

    @property
    def escape_quits(self):
        """Escape quits in the menus, before the story starts, and pauses after
        (aidocks/plans/menus_saves_plan.md)."""
        return self.story.scene in S.MENUS

    # ---- starting --------------------------------------------------------------
    def opened(self):
        if self.story.scene is not None:
            return                      # back on top after another screen
        if self.start_scene is not None:
            log.info('starting at scene %d, as --scene asked; this run never saves', self.start_scene)
            self.perform(self.story.jump(self.start_scene))
        else:
            self.perform(self.story.start(S.MAIN_MENU))

    def position(self):
        return self.audio.scene.position() if self.audio.ok and self.audio.scene.playing else 0.0

    # ---- doing what the rules say ----------------------------------------------------
    def perform(self, effects):
        for effect in effects:
            if isinstance(effect, Play):
                self.play(effect.scene, effect.start)
            elif isinstance(effect, Save):
                self.save(effect.scene)
            elif effect == SOLVED:
                self.audio.play_solved(self.recordings.get(S.SOLVED))
            elif effect == BUZZ:
                self.audio.play_buzz()
            elif effect == PDF:
                log.info('the credits would open the dissertation; plan 5 adds it')
            elif effect == LOAD:
                self.load()

    def play(self, scene, start=0.0):
        log.info('scene %d, %s, from %.1f s', scene, plain_name(scene), start)
        self.audio.scene.play(self.recordings.get(S.name(scene)), start, loop=scene in S.LOOPING,
                              on_end=self.ended)

    def save(self, scene):
        if not self.saving:
            log.info('not saving scene %d: this run started with --scene', scene)
            return
        try:
            self.progress.save(scene)
            log.info('saved scene %d', scene)
        except OSError:
            log.exception('scene %d could not be saved', scene)

    def load(self):
        """Continue, after LoadedSuccessfully: the saved scene from its start."""
        scene = self.progress.load()
        if scene is None:
            log.warning('the save was gone by the end of LoadedSuccessfully')
        else:
            log.info('continuing from the saved scene %d', scene)
        self.perform(self.story.loaded(scene))

    def ended(self):
        self.perform(self.story.ended())

    # ---- keys and time ----------------------------------------------------------------
    def gesture(self, gesture):
        if gesture == 'pause':
            self.resume() if self.paused else self.pause()
            return
        if self.paused:
            return                      # the port's change: a swipe while paused does nothing
        self.perform(self.story.swipe(gesture, self.position()))

    # ---- pause and losing focus ------------------------------------------------------
    def hold(self):
        """Stop the scene and every timer."""
        self.paused = True
        self.app.loop.hold()
        if self.audio.ok:
            self.audio.scene.pause()

    def pause(self):
        log.info('paused')
        self.hold()
        self.audio.play_clip(self.recordings.get(S.PAUSE_MENU))

    def resume(self):
        log.info('resumed')
        self.paused = False
        self.audio.stop_clip()
        self.audio.scene.resume()
        self.app.loop.resume()

    def focus_lost(self):
        log.info('the window lost focus: paused')
        self.hold()

    def focus_gained(self):
        if not self.paused:
            return
        log.info('the window has focus again: stepped back, waiting for the double tap')
        self.audio.focus_gained(self.recordings.get(S.WELCOME_BACK))

    def update(self):
        self.audio.update()
        if self.audio.ok and self.audio.scene.playing and not self.audio.scene.paused:
            self.perform(self.story.tick(self.position()))

    def closed(self):
        if self.audio.ok:
            self.audio.scene.stop()

    # ---- the window --------------------------------------------------------------------
    def lines(self):
        scene = self.story.scene
        if scene is None:
            return [self.app.window_title()]
        turn = 'Your turn' if self.story.counts(self.position()) else 'Listening'
        out = [self.app.window_title(), '', 'Scene %d: %s' % (scene, plain_name(scene)), turn]
        if self.paused:
            out.append('Paused')
        return out
