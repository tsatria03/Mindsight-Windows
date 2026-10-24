"""Read the original's 56 scenes from game/MiNDSIGHT, check them and the
puzzles against the binary and the recordings on disk, and write the whole
story as analysis/script/scenes.txt. Needs capstone, through tools/dis64.py.

    python tools/scenes.py            check, then write analysis/script/scenes.txt
    python tools/scenes.py --check    check only, printing only problems

Read straight from the binary:
- each scene's recording, from -[MSSceneURLStore urlForScene:]'s jump table
- what follows each scene and whether it saves, from -[MSViewController
  playNextScene]'s jump table, by following each case to the shared tail
- the looping scenes and the input lock's scenes, from playScene:fromInterval:
- the scenes that vibrate as they end, from audioPlayerDidFinishPlaying:

The puzzles' answers, cue times, piranha windows and retry points sit in
less regular code, so they are a table here, PUZZLES and RETRIES, each value
with the address it comes from; every one is checked against the binary.
A recording is found on disk by the game's own lookup and timed by the game's
own MP3 reader (mindsight/game/recordings.py, mindsight/platform/mp3.py): the
binary's name without its number prefix, six letter-suffixed names mapped, as
.mp3 anywhere under game/data/audio/. Nothing here plays or writes under game/.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import dis64 as D  # noqa: E402
import macho64 as M  # noqa: E402
from mindsight.game.recordings import RENAMED, disk_name  # noqa: E402,F401  (the game's own lookup)
from mindsight.platform.mp3 import length as mp3_length  # noqa: E402  (the game's own reader)
from mindsight.game import scenes as game_scenes  # noqa: E402  (the game's own table, checked here)

ROOT = M.ROOT
AUDIO = os.path.join(ROOT, "game", "data", "audio")
OUT = os.path.join(ROOT, "analysis", "script", "scenes.txt")

UP, DOWN, LEFT, RIGHT = 0, 1, 2, 3
DIRECTIONS = {UP: "up", DOWN: "down", LEFT: "left", RIGHT: "right"}
SCENES = 56

# The recordings played outside the scene table: pause, interruption and Solved.
EXTRA = ("pause_menu", "WelcomeBack", "Solved")

# Each puzzle, as the behaviour note gives it, with the address each value is read from.
# answer: (direction, address of the cmp or cbz that tests it); gate and cue: (address, seconds).
PUZZLES = [
    dict(name="Office keys", scenes=(10, 11), handler="handleOfficeKeysPuzzle:",
         answer=(RIGHT, 0x100005e24), gate={11: (0x100005668, 22)}, cue={11: (0x100007778, 22)},
         passes=12, fails=None, failure=None, saves=True, solved=True),
    dict(name="Street, round 1", scenes=(14,), handler="handleStreetPuzzle1:",
         answer=(RIGHT, 0x100005f28), gate={14: (0x1000056ac, 13)}, cue={14: (0x1000077b0, 13)},
         passes=15, fails=18, failure=14, saves=False, solved=True),
    dict(name="Street, round 2", scenes=(15,), handler="handleStreetPuzzle2:",
         answer=(UP, 0x100006020), gate={15: (0x1000056f0, 10)}, cue={15: (0x1000077e8, 11)},
         passes=16, fails=18, failure=15, saves=False, solved=True),
    dict(name="Street, round 3", scenes=(16,), handler="handleStreetPuzzle3:",
         answer=(LEFT, 0x100006108), gate={16: (0x100005734, 10)}, cue={16: (0x100007820, 11)},
         passes=17, fails=18, failure=16, saves=False, solved=True),
    dict(name="Car accident", scenes=(19,), handler="handleCarAccident:",
         answer=(RIGHT, 0x10000620c), gate={19: (0x100005778, 21)}, cue={19: (0x100007858, 21)},
         passes=20, fails=21, failure=19, saves=True, solved=True),
    dict(name="Guard", scenes=(26,), handler="handleGuard:",
         answer=(RIGHT, 0x100006304), wrong=(LEFT, 0x10000636c), gate={}, cue={},
         passes=27, fails=28, failure=None, saves=False, solved=False),
    dict(name="Piranhas", scenes=(35,), handler="handlePiranhaPuzzleSuccess:", fail_handler="handlePiranhaPuzzleFailure:",
         answer=None, gate={}, cue={}, passes=36, fails=37, failure=35, saves=True, solved=True),
    dict(name="Tones", scenes=(39,), handler="handleTones:",
         answer=(LEFT, 0x1000065a0), gate={}, cue={}, passes=40, fails=41, failure=39, saves=True, solved=True),
    dict(name="Safe", scenes=(43,), handler="handleSafe:",
         answer=(DOWN, 0x100006690), gate={}, cue={}, passes=44, fails=45, failure=43, saves=True, solved=True),
    dict(name="Roof, round 1", scenes=(47,), handler="handleRoofPuzzle1:",
         answer=(RIGHT, 0x1000067a4), gate={47: (0x10000583c, 7)}, cue={47: (0x100007890, 7)},
         passes=48, fails=53, failure=47, saves=False, solved=True),
    dict(name="Roof, round 2", scenes=(49,), handler="handleRoofPuzzle2:",
         answer=(LEFT, 0x1000068a8), gate={49: (0x100005894, 7)}, cue={49: (0x1000078cc, 8.4)},
         passes=50, fails=53, failure=49, saves=False, solved=True),
    dict(name="Roof, round 3", scenes=(51,), handler="handleRoofPuzzle3:",
         answer=(DOWN, 0x1000069ac), gate={51: (0x1000058e4, 7)}, cue={51: (0x100007904, 7)},
         passes=52, fails=53, failure=51, saves=True, solved=True),
]

# The piranha loop's windows, strictly between start and end, from piranhaPuzzleTimeValid.
PIRANHA_WINDOWS = [(15, 19), (25, 27), (31, 34), (41, 45), (50, 52), (57, 59), (67, 71),
                   (77, 79), (83, 86), (93, 97), (103, 105), (109, 111), (119, 122)]

# After the Rewind, by the failure: (failures, scene, address of its mov, seconds, address of the time or None).
RETRIES = [
    ((14, 15, 16), 13, 0x100006d50, 20.4, 0x100006d5c),
    ((19,), 19, 0x100006db4, 0, None),
    ((35,), 34, 0x100006d74, 70, 0x100006d80),
    ((39,), 39, 0x100006d98, 42, 0x100006da4),
    ((43,), 43, 0x100006df0, 68.5, 0x100006dfc),
    ((47, 49, 51), 46, 0x100006ddc, 112, 0x100006de8),
]
# The tests that send each failure to its retry: (address, the immediate it compares or subtracts).
RETRY_TESTS = [(0x100006d44, 0xe), (0x100006d48, 3), (0x100006dac, 0x13),
               (0x100006d6c, 0x23), (0x100006d90, 0x27), (0x100006dbc, 0x2b)]
RETRY_TABLE = (0x100006ee4, 9)          # failure - 43: 0 the safe, 4, 6 and 8 the roof
ENDING_SETS_CREDITS = (0x100006d24, 5)  # scene 55's case sets scene 5, then reads the failure

problems = []


def problem(text):
    problems.append(text)


# Every line of every method, by address, with the walk's notes.
LINES = {}
for _key, _imp in D.IMPS.items():
    for _ln in D.walk(_imp, full=True):
        LINES.setdefault(_ln.address, (_key, _ln))


def line_at(addr):
    entry = LINES.get(addr)
    return entry[1] if entry else None


def value_at(addr):
    """The number an instruction holds: a loaded time, a moved or compared immediate, or 0 for cbz."""
    ln = line_at(addr)
    if ln is None:
        return None
    if ln.note.startswith("= "):
        return float(ln.note[2:])
    if ln.mnemonic in ("cbz", "cbnz"):
        return 0
    found = re.findall(r"#(-?0x[0-9a-f]+|-?\d+(?:\.\d+)?)", ln.op_str)
    if not found:
        return None
    v = found[-1] if ln.mnemonic not in ("mov", "cmp", "sub", "fmov") else found[0]
    return float(v) if "." in v and not v.startswith(("0x", "-0x")) else int(v, 0)


def method_lines(cls, sel):
    return list(D.walk(D.IMPS[(cls, sel)], full=True))


# ---- read from the binary ----

def read_recordings():
    """Scene -> the binary's recording name."""
    lines = method_lines("MSSceneURLStore", "urlForScene:")
    cases = [ln for ln in lines if ln.mnemonic == ".case"]
    if len(cases) != SCENES:
        problem("urlForScene: has %d cases, not %d" % (len(cases), SCENES))
    names = {}
    for k, case in enumerate(cases):
        for ln in D.walk(case.addr, full=True):
            if ln.mnemonic == "adr" and ln.note.startswith('@"'):
                names[k] = ln.note[2:-1]
                break
            if ln.address - case.addr > 16:
                break
    return names


def read_masks(cls, sel):
    """The 64-bit masks a method builds in x10 before testing a scene's bit, in order."""
    masks, x10 = [], 0
    for ln in method_lines(cls, sel):
        ops = ln.op_str
        if ln.mnemonic in ("mov", "movz") and ops.startswith("x10, #"):
            x10 = int(ops.split("#")[1], 0)
        elif ln.mnemonic == "movk" and ops.startswith("x10, #"):
            parts = ops.split(", ")
            imm = int(parts[1].lstrip("#"), 0)
            shift = int(parts[2].split("#")[1]) if len(parts) > 2 else 0
            x10 = (x10 & ~(0xFFFF << shift)) | (imm << shift)
        elif ln.mnemonic == "and" and ops.endswith("x10"):
            masks.append(x10)
    return masks


def bits(mask):
    return {b for b in range(64) if mask >> b & 1}


def read_flow():
    """Scene -> dict(next, saves, failure, kind) for what playNextScene does as it ends.

    Each case is followed through its moves and stores, and its unconditional
    branches, to the shared tail that plays the new scene. A case that tests
    anything is the Rewind's retry or the ending, read from RETRIES instead.
    """
    lines = method_lines("MSViewController", "playNextScene")
    cases = [ln for ln in lines if ln.mnemonic == ".case"][:SCENES]
    tail = next(ln.address for ln in lines if ln.mnemonic == "str" and ln.op_str.startswith("q0"))
    flow = {}
    for k, case in enumerate(cases):
        pos, regs, out = case.addr, {}, dict(next=k, saves=False, failure=None, kind="plays")
        if pos == tail:
            flow[k] = dict(out, kind="waits")
            continue
        for _ in range(40):
            if pos == tail:
                break
            ln = line_at(pos)
            if ln is None:
                out["kind"] = "unread"
                break
            mn, ops = ln.mnemonic, ln.op_str
            if mn in ("cmp", "cbz", "cbnz", "tbz", "tbnz", "ccmp") or mn.startswith("b."):
                out["kind"] = "tests"
                break
            if mn == "mov" and "#" in ops:
                regs[ops.split(",")[0]] = int(ops.split("#")[1], 0)
            if ln.store and ln.ivar.endswith("._currentScene"):
                src = ops.split(",")[0]
                out["next"] = 0 if src in ("xzr", "wzr") else regs.get(src)
            if ln.store and ln.ivar.endswith("._whichFailure"):
                out["failure"] = regs.get(ops.split(",")[0])
            if ln.note == "sel:saveData":
                out["saves"] = True
            if ln.note == "sel:loadData":
                out["kind"] = "loads"
                break
            pos = ln.addr if mn == "b" else pos + 4
        flow[k] = out
    return flow


# ---- the recordings on disk ----

def files_on_disk():
    found = {}
    for d, _, fs in os.walk(AUDIO):
        for f in fs:
            stem, ext = os.path.splitext(f)
            if ext.lower() == ".mp3":
                found[stem.lower()] = os.path.relpath(os.path.join(d, f), AUDIO).replace(os.sep, "/")
    return found


# ---- the checks ----

def check_puzzles(flow, loops, locked_off, locked_on):
    for p in PUZZLES:
        handler = D.IMPS.get(("MSViewController", p["handler"]))
        if handler is None:
            problem("%s: no handler %s" % (p["name"], p["handler"]))
            continue
        if p["answer"]:
            want, at = p["answer"]
            if value_at(at) != want:
                problem("%s: the answer tested at %x is %r, not %s" % (p["name"], at, value_at(at), DIRECTIONS[want]))
        if p.get("wrong"):
            want, at = p["wrong"]
            if value_at(at) != want:
                problem("%s: the wrong answer tested at %x is %r, not %s" % (p["name"], at, value_at(at), DIRECTIONS[want]))
        for scene, (at, secs) in p["gate"].items():
            if value_at(at) != secs:
                problem("%s: scene %d's cue time at %x is %r, not %r" % (p["name"], scene, at, value_at(at), secs))
        for scene, (at, secs) in p["cue"].items():
            if value_at(at) != secs:
                problem("%s: scene %d's vibration at %x is %r, not %r" % (p["name"], scene, at, value_at(at), secs))
        stored, failures, saves, solved = set(), set(), False, False
        for sel in (p["handler"], p.get("fail_handler")):
            if not sel:
                continue
            regs = {}
            for ln in method_lines("MSViewController", sel):
                if ln.mnemonic == "mov" and "#" in ln.op_str:
                    regs[ln.op_str.split(",")[0]] = int(ln.op_str.split("#")[1], 0)
                if ln.store and ln.ivar.endswith("._currentScene"):
                    stored.add(regs.get(ln.op_str.split(",")[0]))
                if ln.store and ln.ivar.endswith("._whichFailure"):
                    failures.add(regs.get(ln.op_str.split(",")[0]))
                saves |= ln.note == "sel:saveData"
                solved |= ln.note == "sel:playSolvedSound"
        want_scenes = {p["passes"]} | ({p["fails"]} if p["fails"] is not None else set())
        if stored != want_scenes:
            problem("%s: the handler sets scenes %s, not %s" % (p["name"], sorted(stored), sorted(want_scenes)))
        want_failures = {p["failure"]} if p["failure"] is not None else set()
        if failures != want_failures:
            problem("%s: the handler sets failure %s, not %s" % (p["name"], sorted(failures), p["failure"]))
        if saves != p["saves"]:
            problem("%s: saves is %s, not %s" % (p["name"], saves, p["saves"]))
        if solved != p["solved"]:
            problem("%s: Solved is %s, not %s" % (p["name"], solved, p["solved"]))
        # A timed round that runs out goes to its fail scene, or straight to the Rewind.
        for scene in p["scenes"]:
            if p["gate"] and p["failure"] and flow[scene]["failure"] != p["failure"]:
                problem("%s: scene %d running out sets failure %s, not %s"
                        % (p["name"], scene, flow[scene]["failure"], p["failure"]))
    # The piranha windows.
    # Each window is a call with its start in d0 and its end in d1, loaded in either order.
    windows, d = [], {}
    for ln in method_lines("MSViewController", "piranhaPuzzleTimeValid"):
        if ln.note.startswith("= ") and ln.op_str[:2] in ("d0", "d1"):
            d[ln.op_str[:2]] = float(ln.note[2:])
        if ln.mnemonic == "bl" and ln.note == "_objc_msgSend" and "d0" in d and "d1" in d:
            windows.append((d["d0"], d["d1"]))
            d = {}
    if windows != [(float(a), float(b)) for a, b in PIRANHA_WINDOWS]:
        problem("the piranha windows are %s, not %s" % (windows, PIRANHA_WINDOWS))
    if loops != {10, 26, 35}:
        problem("the looping scenes are %s, not 10, 26 and 35" % sorted(loops))
    if locked_off != {39, 43} or locked_on != {35}:
        problem("the input lock's scenes are off %s and on %s, not 39 and 43, and 35" % (sorted(locked_off), sorted(locked_on)))


def check_retries():
    for failures, scene, mov_at, secs, time_at in RETRIES:
        if value_at(mov_at) != scene:
            problem("retry for %s: scene at %x is %r, not %d" % (failures, mov_at, value_at(mov_at), scene))
        if time_at is not None and value_at(time_at) != secs:
            problem("retry for %s: time at %x is %r, not %r" % (failures, time_at, value_at(time_at), secs))
    for at, imm in RETRY_TESTS:
        if value_at(at) != imm:
            problem("the retry test at %x compares %r, not %r" % (at, value_at(at), imm))
    targets = D.jump_table(*RETRY_TABLE)
    if not (targets[4] == targets[6] == targets[8] == 0x100006ddc and targets[0] == 0x100006df0):
        problem("the retry table at %x does not send 43 to the safe and 47, 49, 51 to the roof" % RETRY_TABLE[0])
    at, scene = ENDING_SETS_CREDITS
    if value_at(at) != scene:
        problem("the ending at %x sets scene %r, not %d" % (at, value_at(at), scene))


def read_input_lock():
    """The scenes playScene:fromInterval: turns the input lock off and on for, by its compares."""
    off, on, pending = set(), set(), []
    lines = method_lines("MSViewController", "playScene:fromInterval:")
    for ln in lines:
        if ln.mnemonic == "cmp" and "#" in ln.op_str and ln.address > 0x10000727b:
            pending.append(int(ln.op_str.split("#")[1], 0))
        if ln.store and ln.ivar.endswith("._userInputAvailable"):
            src = ln.op_str.split(",")[0]
            (off if src in ("wzr", "xzr") else on).update(pending)
            pending = []
    return off, on


# ---- the listing ----

PUZZLE_OF = {s: p for p in PUZZLES for s in p["scenes"]}
RETRY_OF = {f: (scene, secs) for fs, scene, _, secs, _ in RETRIES for f in fs}


def seconds(v):
    return ("%g" % v) + " second" + ("" if v == 1 else "s")


def write_listing(names, flow, found, lengths, loops, vibrate_end, locked_off):
    order = [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 10] + list(range(12, SCENES)) + [0]
    out = [
        "MiNDSIGHT, every scene",
        "",
        "Written by tools/scenes.py from the original's binary, game/MiNDSIGHT; do not edit it by hand.",
        "Scenes are numbered as the binary numbers them, and listed in story order: the menus, then the story, with scene 11 before 10, and the Rewind last.",
        "Find \"Scene <number>:\" to jump to a scene.",
        "Swipes are up, down, left and right; the port answers them with the arrow keys or W, S, A and D.",
        "A double tap pauses and resumes; the port uses Escape, Enter or P.",
        "A looping scene never ends, so nothing follows it until it is answered, and it never vibrates.",
        "",
        "Where the port departs from the original:",
        "The port plays a short buzz wherever the original vibrated.",
        "The port ignores swipes while paused; the original still acted on them.",
        "The port always plays the credits after the ending; the original went back to a retry point if the player had failed any puzzle that run.",
        "The port buzzes at street rounds 2 and 3's cue; the original never vibrated there, since it reset its vibration only as a recording ended.",
        "The port buzzes as a scene begins only for the two loops, scenes 26 and 35; the original also vibrated as the main menu, the credits, the tones and the safe began.",
        "",
    ]
    for k in order:
        name = names.get(k, "?")
        rel = found.get(disk_name(name).lower())
        out.append("Scene %d: %s" % (k, disk_name(name)))
        out.append("Recording: %s, %s." % (rel or "missing", seconds(round(lengths.get(k, 0), 1))))
        f = flow[k]
        p = PUZZLE_OF.get(k)
        if k in loops:
            out.append("It loops until answered.")
        if k in locked_off:
            out.append("It must be heard to the end before a swipe counts.")
        if k == 0:
            out.append("It plays after a failure, then the retry, by the puzzle failed:")
            for fs, scene, _, secs, _ in RETRIES:
                which = "scene %d" % fs[0] if len(fs) == 1 else                     "scenes " + ", ".join(map(str, fs[:-1])) + " or %d" % fs[-1]
                out.append("After %s: scene %d, from %s." % (which, scene, seconds(secs) if secs else "its start"))
        elif f["kind"] == "loads":
            out.append("Then: the saved scene, from its start.")
        elif f["kind"] == "waits" and not p and k not in loops:
            out.append("Then: it waits for a swipe.")
        elif f["kind"] == "tests" and k == 55:
            out.append("Then: scene 5, the credits.")
            out.append("Port: the credits always follow; the original went back to a retry point after any failure that run.")
        elif f["kind"] == "plays" and f["next"] != k and k not in loops:
            if f["next"] == 0:
                out.append("Then%s: the Rewind, scene 0." % (", if unanswered" if p else ""))
            elif p and f["failure"]:
                out.append("Then, if unanswered: scene %d, the fail." % f["next"])
            else:
                out.append("Then: scene %d%s." % (f["next"], ", and the game saves" if f["saves"] else ""))
        if k in vibrate_end:
            if k in loops:
                out.append("As it begins after the scene before it ends: a buzz in the port, a vibration in the original.")
            else:
                out.append("As it ends, or begins after the scene before it ends: a buzz in the port, a vibration in the original.")
        if k in MENUS:
            for d, text in MENUS[k]:
                out.append("Swipe %s: %s." % (DIRECTIONS[d], text))
        if p:
            if p["answer"]:
                out.append("Puzzle: %s. Answer: %s." % (p["name"], DIRECTIONS[p["answer"][0]]))
            else:
                out.append("Puzzle: %s. Answer: any swipe, inside a window." % p["name"])
                out.append("Windows, in seconds into each loop: " + ", ".join("%d to %d" % w for w in PIRANHA_WINDOWS) + ".")
            if k in p["gate"]:
                out.append("A swipe counts after %s." % seconds(p["gate"][k][1]))
            if k in p["cue"]:
                out.append("Buzz at %s, where the original vibrated." % seconds(p["cue"][k][1]))
            out.append("Right answer: scene %d%s%s." % (p["passes"], ", with Solved" if p["solved"] else "",
                                                       ", and the game saves" if p["saves"] else ""))
            if p.get("wrong"):
                out.append("Swipe %s: scene %d; either way the story goes on." % (DIRECTIONS[p["wrong"][0]], p["fails"]))
            elif p["fails"] is not None:
                retry = RETRY_OF.get(p["failure"])
                out.append("Wrong answer: scene %d, the fail; then the Rewind; then scene %d, from %s." % (
                    p["fails"], retry[0], seconds(retry[1]) if retry[1] else "its start"))
            else:
                out.append("Any other swipe does nothing.")
        out.append("")
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out))


# The menus' swipes, from handleMainMenu:, handleNewGame:, handleNoSavedGameFound: and handleCredits:.
MENUS = {
    1: [(UP, "New game, scene 2"), (DOWN, "Continue: scene 7 with a save, scene 6 without one"),
        (LEFT, "the audio manual, scene 4"), (RIGHT, "the credits, scene 5")],
    2: [(UP, "start the new game, scene 3"), (DOWN, "back to the main menu, scene 1")],
    6: [(UP, "start a new game, scene 3"), (DOWN, "back to the main menu, scene 1")],
    5: [(RIGHT, "back to the main menu, scene 1"), (LEFT, "open the dissertation PDF")],
}
# The scene each menu swipe sets, checked against its handler: (handler, direction, scene, address of the cmp or None).
MENU_CHECKS = [("handleMainMenu:", (2, 7, 4, 5, 6)), ("handleNewGame:", (1, 3)),
               ("handleNoSavedGameFound:", (1, 3)), ("handleCredits:", (1,))]


def check_menus():
    for sel, want in MENU_CHECKS:
        regs, stored = {}, set()
        for ln in method_lines("MSViewController", sel):
            if ln.mnemonic == "mov" and "#" in ln.op_str:
                regs[ln.op_str.split(",")[0]] = int(ln.op_str.split("#")[1], 0)
            if ln.store and ln.ivar.endswith("._currentScene"):
                stored.add(regs.get(ln.op_str.split(",")[0]))
        if stored != set(want):
            problem("%s sets scenes %s, not %s" % (sel, sorted(stored), sorted(want)))


def check_game_table(flow, vibrate_end, locked_off, locked_on):
    """mindsight/game/scenes.py's table, value by value, against the binary and the
    tables above, which are themselves checked against the binary."""
    G = game_scenes
    for k in range(SCENES):
        then, f = G.THEN[k], flow[k]
        if f["kind"] == "waits" or k in G.LOOPING:
            ok = then.how == G.WAITS
        elif f["kind"] == "loads":
            ok = then.how == G.LOADS
        elif f["kind"] == "tests":
            ok = (k == 0 and then.how == G.RETRY) or (k == 55 and then.next == 5)
        else:
            ok = (then.how == G.PLAYS and then.next == f["next"] and then.saves == f["saves"]
                  and then.failure == f["failure"])
        if not ok:
            problem("scenes.py's THEN[%d] is %s, but the binary says %s" % (k, then, f))
    if set(G.CUE_AT_END) != vibrate_end:
        problem("scenes.py's CUE_AT_END differs from the binary's %s" % sorted(vibrate_end))
    if set(G.LOCKED_WHILE_PLAYING) != locked_off or set(G.OPEN_AT_START) != locked_on:
        problem("scenes.py's input lock scenes differ from the binary's")
    retries = {f: (scene, float(secs)) for fs, scene, _, secs, _ in RETRIES for f in fs}
    if G.RETRIES != retries:
        problem("scenes.py's RETRIES differ: %s, not %s" % (G.RETRIES, retries))
    if [tuple(map(int, w)) for w in G.PIRANHA_WINDOWS] != PIRANHA_WINDOWS:
        problem("scenes.py's PIRANHA_WINDOWS differ from the binary's")
    directions = {UP: G.UP, DOWN: G.DOWN, LEFT: G.LEFT, RIGHT: G.RIGHT}
    for p in PUZZLES:
        for k in p["scenes"]:
            if k in p["gate"] and G.GATES.get(k) != p["gate"][k][1]:
                problem("scenes.py's gate for scene %d is %s, not %s" % (k, G.GATES.get(k), p["gate"][k][1]))
            if k in p["cue"] and G.CUES.get(k) != p["cue"][k][1]:
                problem("scenes.py's cue for scene %d is %s, not %s" % (k, G.CUES.get(k), p["cue"][k][1]))
            if k == G.PIRANHA:
                answers = {G.ANY: G.PIRANHA_PASS}
                wrong = G.PIRANHA_FAIL
            else:
                answers = G.ANSWERS.get(k, {})
                wrong = answers.get(G.ANY) or (answers.get(directions[p["wrong"][0]]) if p.get("wrong") else None)
            right = answers.get(directions[p["answer"][0]]) if p["answer"] else answers.get(G.ANY)
            if right is None or right.to != p["passes"] or right.saves != p["saves"] or right.solved != p["solved"]:
                problem("scenes.py's right answer for scene %d is %s" % (k, right))
            if p["fails"] is not None and (wrong is None or wrong.to != p["fails"] or wrong.failure != p["failure"]):
                problem("scenes.py's wrong answer for scene %d is %s" % (k, wrong))
    if set(G.GATES) | set(G.CUES) != {k for p in PUZZLES for k in p["gate"]} | {k for p in PUZZLES for k in p["cue"]}:
        problem("scenes.py has gates or cues for scenes the binary does not")
    want_menus = {1: {G.UP: 2, G.DOWN: G.CONTINUE, G.LEFT: 4, G.RIGHT: 5}, 2: {G.UP: 3, G.DOWN: 1},
                  6: {G.UP: 3, G.DOWN: 1}, 5: {G.RIGHT: 1, G.LEFT: G.PDF}}
    for k, want in want_menus.items():
        if {d: a.to for d, a in G.ANSWERS[k].items()} != want:
            problem("scenes.py's menu answers for scene %d differ" % k)


def main():
    check_only = "--check" in sys.argv[1:]
    names = read_recordings()
    flow = read_flow()
    loop_masks = read_masks("MSViewController", "playScene:fromInterval:")
    end_masks = read_masks("MSViewController", "audioPlayerDidFinishPlaying:successfully:")
    loops = bits(loop_masks[0]) if loop_masks else set()
    vibrate_end = bits(end_masks[1]) if len(end_masks) > 1 else set()
    locked_off, locked_on = read_input_lock()
    if vibrate_end != {1, 2, 5, 6, 26, 35, 39, 43}:
        problem("the scenes that vibrate as they end are %s" % sorted(vibrate_end))

    found = files_on_disk()
    named = set()
    lengths = {}
    for k in range(SCENES):
        if k not in names:
            problem("scene %d has no recording in the binary" % k)
            continue
        key = disk_name(names[k]).lower()
        named.add(key)
        if key not in found:
            problem("scene %d's recording %s is not on disk as %s.mp3" % (k, names[k], disk_name(names[k])))
        else:
            lengths[k] = mp3_length(os.path.join(AUDIO, found[key]))
    strings = set(M.cfstrings().values())
    for n in EXTRA:
        if n not in strings:
            problem("the binary does not name %s" % n)
        named.add(n.lower())
        if n.lower() not in found:
            problem("%s is not on disk" % n)
    unnamed = sorted(found[k] for k in found if k not in named)

    check_game_table(flow, vibrate_end, locked_off, locked_on)
    if tuple(names.get(k) for k in range(SCENES)) != game_scenes.NAMES:
        problem("mindsight/game/scenes.py's NAMES differ from the binary's")
    if set(game_scenes.LOOPING) != loops:
        problem("mindsight/game/scenes.py's LOOPING differs from the binary's %s" % sorted(loops))
    for k in range(SCENES):
        if flow[k]["kind"] == "unread":
            problem("scene %d: what follows could not be read" % k)
    check_puzzles(flow, loops, locked_off, locked_on)
    check_retries()
    check_menus()

    if not check_only:
        write_listing(names, flow, found, lengths, loops, vibrate_end, locked_off)
        print("%d scenes, %d recordings named by the binary, all checked against it." % (SCENES, len(named)))
        print("Never named by the binary: %s." % (", ".join(unnamed) or "none"))
        print("Wrote %s." % os.path.relpath(OUT, ROOT))
    for p in problems:
        print("Problem:", p)
    if not problems and not check_only:
        print("No problems.")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
