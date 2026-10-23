"""The original's rules, with no sound: the menus, the input lock, the cues and the buzz,
every puzzle, failing and the Rewind's retries, the piranha windows, and the ending."""
import _quiet  # noqa: F401  (first, before any of the game)

from mindsight.game import scenes as S
from mindsight.game.recordings import Recordings
from mindsight.game.story import BUZZ, LOAD, PDF, SOLVED, Play, Save, Story


def at(scene, has_save=False):
    """A story whose scene ``scene`` has just started after the one before it ended."""
    story = Story(has_save=lambda: has_save)
    story.jump(scene)
    return story


def test_the_table_is_whole():
    assert S.COUNT == 56 and set(S.THEN) == set(range(56))
    for k, then in S.THEN.items():
        assert then.next is None or 0 <= then.next < 56, k
        assert Recordings.shared().find(S.name(k)) is not None, k
    for k, answers in S.ANSWERS.items():
        for a in answers.values():
            assert a.to in (S.CONTINUE, S.PDF) or 0 <= a.to < 56, (k, a)


def test_the_game_opens_locked_on_the_main_menu():
    story = Story()
    assert story.start(S.MAIN_MENU) == [Play(1, 0.0)]
    assert story.swipe('up', 5.0) == [] and not story.counts(5.0)
    assert story.ended() == [BUZZ]
    assert story.counts(0.0)
    assert story.swipe('up', 18.0) == [Play(2, 0.0)]
    assert story.swipe('down', 1.0) == []           # locked again until it ends
    assert story.ended() == [BUZZ]
    assert story.swipe('down', 1.0) == [Play(1, 0.0)]


def test_the_menus():
    story = at(S.MAIN_MENU)
    assert story.swipe('left', 0) == [Play(4, 0.0)]
    assert story.ended() == [Play(1, 0.0), BUZZ]    # the main menu, buzzing as it begins
    assert story.swipe('right', 0) == [Play(5, 0.0)]
    assert story.ended() == [BUZZ]
    assert story.swipe('left', 0) == [PDF]
    assert at(S.CREDITS).swipe('right', 0) == [Play(1, 0.0)]
    assert at(S.NEW_GAME).swipe('up', 0) == [Play(3, 0.0)]
    story = at(S.CONFIRM)
    assert story.ended() == [Play(8, 0.0)]
    assert story.ended() == [Save(9), Play(9, 0.0)]
    assert story.ended() == [Play(11, 0.0)]


def test_continue_with_and_without_a_save():
    assert at(S.MAIN_MENU).swipe('down', 0) == [Play(6, 0.0)]
    story = at(S.NO_SAVE)
    assert story.swipe('up', 0) == [Play(3, 0.0)]
    story = at(S.MAIN_MENU, has_save=True)
    assert story.swipe('down', 0) == [Play(7, 0.0)]
    assert story.ended() == [LOAD]
    assert story.loaded(24) == [Play(24, 0.0)]


def test_the_office_keys():
    story = at(11)
    assert story.swipe('right', 21.9) == [] and story.swipe('right', 22.0) == []
    assert story.tick(21.9) == [] and story.tick(22.0) == [BUZZ] and story.tick(23) == []
    assert story.swipe('left', 30) == []
    assert story.swipe('right', 22.1) == [SOLVED, Save(12), Play(12, 0.0)]
    story = at(11)
    assert story.ended() == [Play(10, 0.0)]
    assert story.swipe('right', 0.5) == [SOLVED, Save(12), Play(12, 0.0)]


def test_the_street_rounds():
    story = at(14)
    assert story.swipe('right', 12.9) == []
    assert story.tick(13.0) == [BUZZ]
    assert story.swipe('right', 13.1) == [SOLVED, Play(15, 0.0)]
    assert story.input_open                          # rounds 1 and 2 leave the lock open
    assert story.tick(10.9) == [] and story.tick(11.0) == [BUZZ]     # the port's fix: round 2 buzzes
    assert story.swipe('up', 10.1) == [SOLVED, Play(16, 0.0)]
    assert story.tick(11.0) == [BUZZ]                                 # and round 3
    assert story.swipe('left', 10.1) == [SOLVED, Play(17, 0.0)]
    assert story.ended() == [Save(19), Play(19, 0.0)]


def test_failing_a_street_round():
    story = at(15)
    assert story.swipe('down', 10.5) == [Play(18, 0.0)] and story.failure == 15
    assert story.ended() == [Play(0, 0.0)]
    assert story.ended() == [Play(13, 20.4)]


def test_a_street_round_running_out():
    story = at(14)
    assert story.ended() == [Play(0, 0.0)] and story.failure == 14
    assert story.ended() == [Play(13, 20.4)]


def test_the_car_accident():
    story = at(19)
    assert story.swipe('right', 21.0) == []
    assert story.swipe('right', 21.5) == [SOLVED, Save(20), Play(20, 0.0)]
    story = at(19)
    assert story.swipe('left', 21.5) == [Play(21, 0.0)]
    assert story.ended() == [Play(0, 0.0)]
    assert story.ended() == [Play(19, 0.0)]
    story = at(19)
    assert story.ended() == [Play(21, 0.0)] and story.failure == 19


def test_the_guard_goes_on_either_way():
    story = at(25)
    assert story.ended() == [Play(26, 0.0), BUZZ]
    assert story.swipe('up', 3) == [] and story.swipe('down', 3) == []
    assert story.swipe('left', 3) == [Play(28, 0.0)]
    assert story.ended() == [Save(29), Play(29, 0.0)]
    assert at(26).swipe('right', 0) == [Play(27, 0.0)]


def test_the_piranha_windows():
    story = at(34)
    assert story.ended() == [Play(35, 0.0), BUZZ] and story.input_open
    assert at(35).swipe('up', 16.0) == [SOLVED, Save(36), Play(36, 0.0)]
    for edge in (15.0, 19.0, 20.0, 0.5, 123.0):
        story = at(35)
        assert story.swipe('left', edge) == [Play(37, 0.0)], edge
        assert story.failure == 35
        assert story.ended() == [Play(0, 0.0)]
        assert story.ended() == [Play(34, 70.0)]
    for inside in (17, 26, 33.5, 44, 51, 58, 70, 78, 85, 95, 104, 110, 121.9):
        assert at(35).swipe('right', inside)[0] == SOLVED, inside


def test_the_tones_and_the_safe_must_be_heard_to_the_end():
    story = at(38)
    assert story.ended() == [Save(39), Play(39, 0.0), BUZZ]
    assert not story.input_open and story.swipe('left', 100) == []
    assert story.ended() == [BUZZ]
    assert story.swipe('right', 0) == [Play(41, 0.0)]
    assert story.ended() == [Play(0, 0.0)]
    assert story.ended() == [Play(39, 42.0), BUZZ]
    assert story.ended() == [BUZZ]
    assert story.swipe('left', 0) == [SOLVED, Save(40), Play(40, 0.0)]
    story = Story()
    story.input_open = True
    story.start(43)
    assert story.swipe('down', 120) == []
    assert story.ended() == [BUZZ]
    assert story.swipe('down', 0) == [SOLVED, Save(44), Play(44, 0.0)]
    story = at(43)
    story.ended()
    assert story.swipe('up', 0) == [Play(45, 0.0)]
    story.ended()
    assert story.ended() == [Play(43, 68.5), BUZZ]


def test_the_roof():
    story = at(46)
    assert story.ended() == [Play(47, 0.0)]
    assert story.tick(7.0) == [BUZZ]
    assert story.swipe('right', 7.0) == [] and story.swipe('right', 7.1) == [SOLVED, Play(48, 0.0)]
    assert story.ended() == [Play(49, 0.0)]
    assert story.tick(8.3) == [] and story.tick(8.4) == [BUZZ]
    assert story.swipe('left', 7.5) == [SOLVED, Play(50, 0.0)]
    assert story.ended() == [Play(51, 0.0)]
    assert story.swipe('down', 7.5) == [SOLVED, Save(52), Play(52, 0.0)]
    assert story.ended() == [Play(54, 0.0)]


def test_failing_the_roof_and_running_out():
    story = at(49)
    assert story.swipe('right', 7.5) == [Play(53, 0.0)] and story.failure == 49
    assert story.ended() == [Play(0, 0.0)]
    assert story.ended() == [Play(46, 112.0)]
    story = at(51)
    assert story.ended() == [Play(53, 0.0)] and story.failure == 51


def test_the_credits_always_follow_the_ending():
    story = at(14)
    story.ended()                                    # a failure, this run
    assert story.failure == 14
    story.start(54)
    assert story.ended() == [Play(55, 0.0)] and story.failure is None
    assert story.ended() == [Play(5, 0.0), BUZZ]


def test_your_turn():
    story = at(47)
    assert not story.counts(6.9) and story.counts(7.1)
    story = at(8)
    assert not story.counts(100)                     # a scene with no answers
    assert at(35).counts(0)


def test_the_menus_are_where_escape_quits():
    assert S.MENUS == {1, 2, 3, 4, 5, 6, 7}


_quiet.run_tests(globals())
