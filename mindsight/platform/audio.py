"""The sound: three players, like the original's three AVAudioPlayers
(aidocks/plans/audio_plan.md).

* The scene player streams one scene at a time through ``pygame.mixer.music``, the only
  pygame player that starts partway and loops. Starting a scene replaces the last.
* The Solved player plays ``Solved`` on a channel of its own, at 0.2, the original's
  volume, over the start of the next scene (playSolvedSound, 0x1000073a0).
* The pause player plays the pause clips, ``pause_menu`` and ``WelcomeBack``, on another.

The mixer opens at 44,100 Hz, 16-bit stereo, so the binaural recordings play untouched;
the 22,050 Hz sounds in system/misc are resampled by the mixer. There are no volumes of
the game's own: the player sets the level with Windows' (aidocks/plans/foundation_plan.md).

The scene's position is timed on the game's own clock (platform/runloop.py's ``clock``),
from the point it started at, held still while paused, and wrapped by the recording's
length when it loops, so a cue time and a pause can never drift apart. A scene counts as
ended only once the mixer has stopped and it has played a quarter of a second, so a
start that is slow to begin is never taken for an end.
"""
from __future__ import annotations

import logging

from . import runloop

log = logging.getLogger('audio')

FREQUENCY, SIZE, CHANNELS, BUFFER = 44100, -16, 2, 1024
#: Solved's volume, from the binary: setVolume: 0.2 at 0x1000074dc.
SOLVED_VOLUME = 0.2
SOLVED_CHANNEL, CLIP_CHANNEL = 0, 1
#: A scene playing less than this is never taken to have ended.
END_GRACE = 0.25


class NoSound(Exception):
    """No sound device could be opened; its text is the player's message."""


NO_SOUND_MESSAGE = ('Mindsight could not open a sound device, so the game cannot start.\n\n'
                    'Every part of Mindsight is a recording, so it needs one. Please connect '
                    'headphones or speakers, check that Windows can play sound, and start the '
                    'game again.')


class ScenePlayer:
    """The scene, streamed through ``pygame.mixer.music``."""

    def __init__(self, pygame):
        self.pygame = pygame
        self.recording = None
        self.loop = False
        self.start = 0.0
        self.started_at = None
        self.paused_at = None
        self.paused_for = 0.0
        self.ended = False
        self.on_end = None

    def play(self, recording, start=0.0, loop=False, on_end=None):
        """Play ``recording`` from ``start`` seconds, looping forever if ``loop``. A
        ``on_end`` callback is called once, when it ends of itself."""
        music = self.pygame.mixer.music
        music.stop()
        music.load(recording.source())
        start = max(0.0, float(start))
        music.play(loops=-1 if loop else 0, start=start)
        self.recording, self.loop, self.start = recording, loop, start
        self.started_at, self.paused_at, self.paused_for = runloop.clock(), None, 0.0
        self.ended, self.on_end = False, on_end
        log.info('scene: %s from %.1f s%s', recording.name, start, ', looping' if loop else '')

    def stop(self):
        """Stop the scene, without calling its ``on_end``."""
        self.pygame.mixer.music.stop()
        self.recording, self.on_end, self.paused_at = None, None, None

    @property
    def playing(self):
        return self.recording is not None and not self.ended

    @property
    def paused(self):
        return self.paused_at is not None

    def pause(self):
        if self.playing and not self.paused:
            self.pygame.mixer.music.pause()
            self.paused_at = runloop.clock()

    def resume(self):
        if self.paused:
            self.paused_for += runloop.clock() - self.paused_at
            self.paused_at = None
            self.pygame.mixer.music.unpause()

    def played_for(self, now=None):
        """Seconds the scene has played since it started, not counting pauses."""
        if self.started_at is None:
            return 0.0
        now = runloop.clock() if now is None else now
        upto = self.paused_at if self.paused_at is not None else now
        return max(0.0, upto - self.started_at - self.paused_for)

    def position(self, now=None):
        """Where in the recording it is, in seconds; within the recording when it loops."""
        if self.recording is None:
            return 0.0
        length = self.recording.length
        at = self.start + self.played_for(now)
        if self.loop and length > 0:
            return at % length
        return min(at, length)

    def update(self, now=None):
        """Called once a frame: notice the scene's end, and call its ``on_end``."""
        if not self.playing or self.paused or self.loop:
            return
        if self.played_for(now) < END_GRACE or self.pygame.mixer.music.get_busy():
            return
        self.ended = True
        log.info('scene ended: %s', self.recording.name)
        callback, self.on_end = self.on_end, None
        if callback is not None:
            callback()


class Audio:
    """The mixer and the three players."""

    _shared = None

    @classmethod
    def shared(cls):
        if cls._shared is None:
            cls._shared = cls()
        return cls._shared

    def __init__(self):
        self.pygame = None
        self.scene = None
        self._sounds = {}

    @property
    def ok(self):
        return self.scene is not None

    def open(self, pygame):
        """Open the sound device; :class:`NoSound` when it cannot be."""
        if self.ok:
            return
        try:
            pygame.mixer.pre_init(FREQUENCY, SIZE, CHANNELS, BUFFER)
            pygame.mixer.init()
        except Exception as error:
            log.error('no sound device could be opened: %s', error)
            raise NoSound(NO_SOUND_MESSAGE) from error
        pygame.mixer.set_reserved(2)
        self.pygame = pygame
        self.scene = ScenePlayer(pygame)
        log.info('sound opened: %s', pygame.mixer.get_init())

    def close(self):
        if not self.ok:
            return
        self.pygame.mixer.music.stop()
        self.pygame.mixer.quit()
        self.scene, self._sounds = None, {}

    def _sound(self, recording):
        sound = self._sounds.get(recording.name)
        if sound is None:
            sound = self.pygame.mixer.Sound(recording.source())
            self._sounds[recording.name] = sound
        return sound

    def play_solved(self, recording):
        """Solved, at 0.2, over whatever the scene player is playing."""
        sound = self._sound(recording)
        sound.set_volume(SOLVED_VOLUME)
        self.pygame.mixer.Channel(SOLVED_CHANNEL).play(sound)

    def play_clip(self, recording):
        """A pause clip, pause_menu or WelcomeBack, replacing any clip playing."""
        self.pygame.mixer.Channel(CLIP_CHANNEL).play(self._sound(recording))

    def stop_clip(self):
        self.pygame.mixer.Channel(CLIP_CHANNEL).stop()

    def update(self, now=None):
        """Called once a frame."""
        if self.ok:
            self.scene.update(now)
