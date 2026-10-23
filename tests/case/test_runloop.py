"""The timer loop: order, repeats, cancelling, errors, and hold and resume."""
import _quiet  # noqa: F401  (first, before any of the game)

from mindsight.platform import runloop
from mindsight.platform.runloop import RunLoop


class Clock:
    """A clock the test moves by hand."""
    def __init__(self):
        self.now = 100.0

    def __call__(self):
        return self.now


def fresh():
    clock = Clock()
    runloop.clock = clock
    return RunLoop(), clock


def test_calls_run_in_order_when_due():
    loop, clock = fresh()
    ran = []
    loop.after(2, ran.append, 'b')
    loop.after(1, ran.append, 'a')
    loop.after(1, ran.append, 'a2')
    clock.now += 0.5
    loop.pump()
    assert ran == []
    clock.now += 2
    loop.pump()
    assert ran == ['a', 'a2', 'b']


def test_repeats_skip_missed_beats():
    loop, clock = fresh()
    ran = []
    loop.every(1, ran.append, 'x')
    clock.now += 1
    loop.pump()
    clock.now += 5.5            # a slow frame: five beats missed
    loop.pump()
    assert ran == ['x', 'x']
    clock.now += 1
    loop.pump()
    assert ran == ['x', 'x', 'x']


def test_cancel_before_and_between_runs():
    loop, clock = fresh()
    ran = []
    once = loop.after(1, ran.append, 'once')
    once.cancel()
    tick = loop.every(1, ran.append, 'tick')
    clock.now += 1
    loop.pump()
    tick.cancel()
    clock.now += 3
    loop.pump()
    assert ran == ['tick']


def test_an_error_is_logged_and_the_loop_carries_on():
    loop, clock = fresh()
    ran = []

    def broken():
        raise ValueError('test')
    loop.after(1, broken)
    loop.after(1, ran.append, 'after')
    clock.now += 1
    loop.pump()
    clock.now += 1
    loop.pump()
    assert ran == ['after']


def test_hold_stops_and_resume_moves_calls_on():
    loop, clock = fresh()
    ran = []
    call = loop.after(5, ran.append, 'x')
    clock.now += 2
    loop.hold()
    assert loop.held
    clock.now += 100            # a long pause
    loop.pump()
    assert ran == [] and loop.remaining(call) == 3
    loop.resume()
    assert not loop.held
    clock.now += 2.9
    loop.pump()
    assert ran == []
    clock.now += 0.2
    loop.pump()
    assert ran == ['x']


def test_a_call_made_while_held_waits_its_full_delay():
    loop, clock = fresh()
    ran = []
    loop.hold()
    clock.now += 10
    loop.after(2, ran.append, 'x')
    clock.now += 10
    loop.resume()
    clock.now += 1.9
    loop.pump()
    assert ran == []
    clock.now += 0.2
    loop.pump()
    assert ran == ['x']


def test_a_repeat_needs_an_interval():
    loop, _ = fresh()
    try:
        loop.every(0, print)
    except ValueError:
        return
    raise AssertionError('every(0) was allowed')


_quiet.run_tests(globals())
