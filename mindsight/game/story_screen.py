"""The story as a screen: story.py's rules played on the audio
(aidocks/plans/story_engine_plan.md).

The game opens here, on scene 1, the main menu, as the original did, or on the scene
``--scene`` names in debug mode. Every frame, the scene's position goes to the rules for
the buzz at a cue; a swipe goes to them with the position; and a recording ending of
itself goes to them too. Whatever they say is done: a scene plays, looping if it loops;
Solved plays over it; the buzz plays; the place is saved.

Until plan 5 (aidocks/plans/menus_saves_plan.md), saving only logs where it would save,
Continue always finds no save, and the credits' left swipe does nothing. Pause and losing
focus come with this plan's section 4. A run started with ``--scene`` never saves.
"""
from __future__ import annotations

import logging

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

    def __init__(self, app, audio=None, recordings=None, story=None, start_scene=None):
        super().__init__(app)
        self.audio = audio or Audio.shared()
        self.recordings = recordings or Recordings.shared()
        self.story = story or Story()
        #: The scene --scene named; a run that starts there never saves.
        self.start_scene = start_scene
        self.saving = start_scene is None

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
                log.info('Continue would load the save; plan 5 adds it')

    def play(self, scene, start=0.0):
        log.info('scene %d, %s, from %.1f s', scene, plain_name(scene), start)
        self.audio.scene.play(self.recordings.get(S.name(scene)), start, loop=scene in S.LOOPING,
                              on_end=self.ended)

    def save(self, scene):
        if not self.saving:
            log.info('not saving scene %d: this run started with --scene', scene)
            return
        log.info('the game would save scene %d here; plan 5 adds the save', scene)

    def ended(self):
        self.perform(self.story.ended())

    # ---- keys and time ----------------------------------------------------------------
    def gesture(self, gesture):
        if gesture == 'pause':
            log.info('the pause comes with section 4')
            return
        self.perform(self.story.swipe(gesture, self.position()))

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
        if self.audio.ok and self.audio.scene.paused:
            out.append('Paused')
        return out
