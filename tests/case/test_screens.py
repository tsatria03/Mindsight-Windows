"""The screen stack, the App's keys and focus, a silent run, and the stand-in screen."""
import _quiet  # noqa: F401  (first, before any of the game)

import types

import pygame

from mindsight.app import App
from mindsight.game.standin import StandInScreen
from mindsight.platform.runloop import RunLoop
from mindsight.ui.screens import Screen, ScreenStack


class Recorder(Screen):
    name = 'recorder'

    def __init__(self, app=None, tag=''):
        super().__init__(app)
        self.tag = tag
        self.heard = []

    def opened(self):
        self.heard.append('opened')

    def closed(self):
        self.heard.append('closed')

    def covered(self):
        self.heard.append('covered')

    def gesture(self, gesture):
        self.heard.append(('gesture', gesture))

    def ignored_key(self, key, mods):
        self.heard.append(('ignored', key, tuple(mods)))

    def other_key(self, key, mods):
        self.heard.append(('other', key, tuple(mods)))

    def focus_lost(self):
        self.heard.append('lost')

    def focus_gained(self):
        self.heard.append('gained')


def test_the_stack():
    stack = ScreenStack()
    a, b, c = Recorder(tag='a'), Recorder(tag='b'), Recorder(tag='c')
    stack.push(a)
    stack.push(b)
    assert stack.top is b and a.heard == ['opened', 'covered']
    stack.pop()
    assert stack.top is a and b.heard == ['opened', 'closed'] and a.heard[-1] == 'opened'
    stack.replace(c)
    assert stack.top is c and a.heard[-1] == 'closed'
    stack.reset(Recorder(tag='d'))
    assert c.heard[-1] == 'closed' and stack.top.tag == 'd'
    stack.clear()
    assert stack.empty and stack.top is None


def test_keys_reach_the_top_screen_three_ways():
    app = App(loop=RunLoop())
    r = Recorder(app)
    app.stack.push(r)
    app.key_down('up', [])
    app.key_down('p', [])
    app.key_down('up', ['shift'])
    app.key_down('x', [])
    app.key_down('left shift', ['shift'])
    assert r.heard[1:] == [('gesture', 'up'), ('gesture', 'pause'), ('ignored', 'up', ('shift',)),
                           ('other', 'x', ())]


def test_focus_and_quit_events():
    app = App(loop=RunLoop())
    r = Recorder(app)
    app.stack.push(r)
    app.handle_event(types.SimpleNamespace(type=pygame.WINDOWFOCUSLOST), pygame)
    app.handle_event(types.SimpleNamespace(type=pygame.WINDOWFOCUSGAINED), pygame)
    app.handle_event(types.SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_s, mod=0), pygame)
    app.handle_event(types.SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_s, mod=pygame.KMOD_LCTRL), pygame)
    assert r.heard[1:] == ['lost', 'gained', ('gesture', 'down'), ('ignored', 's', ('control',))]
    app.handle_event(types.SimpleNamespace(type=pygame.QUIT), pygame)
    assert not app.running


def test_window_title():
    assert App(loop=RunLoop()).window_title() == 'Mindsight'
    assert App(loop=RunLoop(), debug=True).window_title() == 'Mindsight (debug)'


def test_a_silent_run_quits_by_itself():
    options = types.SimpleNamespace(exit_after=0.2)
    app = App(options, loop=RunLoop())
    r = Recorder(app)
    app.run(r, pygame)
    assert r.heard == ['opened', 'closed'] and not app.running


def test_the_stand_in_screen():
    app = App(loop=RunLoop())
    s = StandInScreen(app)
    app.stack.push(s)
    assert 'Last key: No key yet.' in s.lines()
    app.key_down('d', [])
    assert 'Last key: Swipe right.' in s.lines()
    app.key_down('return', [])
    assert 'Last key: Pause or resume.' in s.lines()
    app.key_down('a', ['alt'])
    assert 'Last key: Alt plus A: ignored, with a modifier held.' in s.lines()
    s.focus_lost()
    assert 'The window lost the keyboard.' in s.lines()
    s.focus_gained()
    assert 'The window has the keyboard.' in s.lines()


_quiet.run_tests(globals())
