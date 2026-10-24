"""The original's rules, as plain state with no sound (aidocks/plans/story_engine_plan.md).

The story screen hands this the recording's position, the swipes and the ends, and does
what it says: each call returns a list of effects, such as ``Play(15, 0.0)`` and
``SOLVED``. The rules follow the binary exactly (aidocks/general/project_original_behaviour.md),
with the port's changes:

* the failure is cleared as scene 55 begins, so the credits always follow the ending;
* the screen sends no swipes while paused, so a swipe while paused does nothing;
* the buzz resets whenever a scene starts, so street rounds 2 and 3 buzz at their cue.
  In the original, ``justVibrated`` was cleared only as a recording ended of itself, so
  those two rounds, reached by answering, never vibrated;
* after a recording ends, the buzz plays for a waiting scene whose own recording just
  ended, and for the two looping puzzles, 26 and 35, as they begin, since they never end;
  never as another waiting scene begins. The original, testing the scene current once
  the next had started, also vibrated as the credits, the main menu, the tones and the
  safe began.

The input lock, ``userInputAvailable``, starts closed, so the main menu must be heard to
the end. It opens as a recording ends of itself, and stays open into the next scene;
starting scene 39 or 43 closes it, and starting 35 opens it. Nearly every answer closes
it again. A timed scene ignores a swipe until it is past its gate.

The buzz, ``justVibrated`` in the original, comes once per recording: at a timed scene's
cue, or after a recording ends of itself when the scene then current is one of
CUE_AT_END.
"""
from __future__ import annotations

from collections import namedtuple

from . import scenes as S

#: Play scene ``scene`` from ``start`` seconds; it loops if the scene loops.
Play = namedtuple('Play', 'scene start')
#: Save ``scene`` as the place to continue from.
Save = namedtuple('Save', 'scene')
SOLVED = 'solved'       # the Solved sound, over the start of the next scene
BUZZ = 'buzz'           # the buzz, where the original vibrated
PDF = 'pdf'             # open the dissertation
LOAD = 'load'           # play the saved scene, from its start


class Story:
    def __init__(self, has_save=lambda: False):
        #: Whether there is a save to continue from (progress.has_save in the game).
        self.has_save = has_save
        self.scene = None
        self.failure = None
        self.input_open = False
        self.buzzed = False

    # ---- starting a scene ------------------------------------------------------
    def start(self, scene, at=0.0):
        """The effects of starting ``scene`` at ``at`` seconds: it plays, and the input
        lock opens or closes as the original's playScene:fromInterval: does."""
        self.scene = scene
        self.buzzed = False             # the port's fix: every scene can buzz at its cue
        if scene in S.LOCKED_WHILE_PLAYING:
            self.input_open = False
        elif scene in S.OPEN_AT_START:
            self.input_open = True
        if scene == S.ENDING:
            self.failure = None         # the port's fix: the credits always follow
        return [Play(scene, at)]

    def jump(self, scene, at=0.0):
        """Start ``scene`` as if the recording before it had just ended: the input lock
        open and the buzz reset, for debug's --scene and the by-ear tools."""
        self.input_open, self.buzzed, self.failure = True, False, None
        return self.start(scene, at)

    # ---- swipes -------------------------------------------------------------------
    def counts(self, position):
        """Whether a swipe would count now: the lock open, any gate passed, and the scene
        one that answers swipes."""
        if not self.input_open or not S.answers_swipes(self.scene):
            return False
        gate = S.GATES.get(self.scene)
        return gate is None or position > gate

    def answer(self, direction, position):
        """The Answer a swipe gives in this scene, or None when it does nothing."""
        if self.scene == S.PIRANHA:
            inside = any(a < position < b for a, b in S.PIRANHA_WINDOWS)
            return S.PIRANHA_PASS if inside else S.PIRANHA_FAIL
        table = S.ANSWERS.get(self.scene, {})
        return table.get(direction) or table.get(S.ANY)

    def swipe(self, direction, position):
        """The effects of a swipe, ``up``, ``down``, ``left`` or ``right``, at ``position``
        seconds into the scene; an empty list when it is ignored, which makes no sound."""
        if not self.counts(position):
            return []
        answer = self.answer(direction, position)
        if answer is None:
            return []
        if answer.locks:
            self.input_open = False
        if answer.failure is not None:
            self.failure = answer.failure
        if answer.to == S.PDF:
            return [PDF]
        to = answer.to
        if to == S.CONTINUE:
            to = S.LOADED if self.has_save() else S.NO_SAVE
        effects = []
        if answer.solved:
            effects.append(SOLVED)
        if answer.saves:
            effects.append(Save(to))
        return effects + self.start(to)

    # ---- time and ends ------------------------------------------------------------
    def tick(self, position):
        """Called as the scene plays: the buzz, once, as it reaches its cue time."""
        cue = S.CUES.get(self.scene)
        if cue is not None and not self.buzzed and position >= cue:
            self.buzzed = True
            return [BUZZ]
        return []

    def ended(self):
        """The effects of the scene's recording ending of itself.

        As audioPlayerDidFinishPlaying:successfully: (0x100008518) does: the lock opens and
        the buzz resets, and what follows starts. Then the buzz plays if the scene now
        current is one of CUE_AT_END, and either it is the scene that just ended, waiting
        for a swipe, or it is one of the two looping puzzles beginning, whose only cue this
        is (the port's change: the original also vibrated as the other waiting scenes began).
        """
        ended = self.scene
        self.input_open = True
        self.buzzed = False
        effects = self._what_follows()
        now = self.scene
        if now in S.CUE_AT_END and (now == ended or now in S.LOOPING):
            self.buzzed = True
            effects.append(BUZZ)
        return effects

    def _what_follows(self):
        then = S.THEN[self.scene]
        if then.how == S.WAITS:
            return []
        if then.how == S.LOADS:
            return [LOAD]
        if then.how == S.RETRY:
            retry = S.RETRIES.get(self.failure)
            if retry is None:
                return []               # as the original: nothing to retry, nothing plays
            return self.start(*retry)
        if then.failure is not None:
            self.failure = then.failure
        effects = [Save(then.next)] if then.saves else []
        return effects + self.start(then.next)

    def loaded(self, scene):
        """The effects of Continue's saved scene, after LoadedSuccessfully: it plays from
        its start. With ``None``, the save gone while LoadedSuccessfully played, No saved
        game plays instead, heard to the end like every menu."""
        if scene is None:
            self.input_open = False
            return self.start(S.NO_SAVE)
        return self.start(scene)
