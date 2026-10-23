"""Disassemble arm64 methods of game/MiNDSIGHT, naming the selectors, imported
functions, classes, strings, instance variables and number constants each
instruction refers to, and decoding the jump tables behind switch statements.
Needs capstone (pip install capstone); the game itself never does.

    python tools/dis64.py MSViewController pushDirection:   one method
    python tools/dis64.py --list MSViewController           the class's methods
    python tools/dis64.py --at 0x100006d2c                  code at an address
    python tools/dis64.py --find puzzle                     methods whose selector holds a word
    python tools/dis64.py --refs 0x10000e9f8                the code that uses an address
    python tools/dis64.py --refs playSolvedSound            ... or calls a selector
    python tools/dis64.py --writes _whichFailure            every store to an instance variable
    python tools/dis64.py --brief MSViewController handleSafe:   only calls, strings, numbers and tests
    python tools/dis64.py --full MSViewController playNextScene  on past an early return

A class method is named with a + in front. Output stops at the first ret, so
a method that continues past one shows only its first part; --full reads on to
where the next method begins. --refs and --writes always read in full.

This binary loads nearly every string and selector with adr or a literal ldr,
and an instance variable by first loading its offset, as in
`ldrsw x8, #0x10000ec68`; each is named. A store or load through such an
offset is marked with the variable, as `-> _currentScene`. A switch's jump
table sits inline after the code; it is shown as its cases, each with its
target, and the listing carries on after it.
"""
import sys

from capstone import Cs, CS_ARCH_ARM64, CS_MODE_ARM
import macho64 as M

SEL = M.selrefs()
STUB = M.stubs()
CFSTR = M.cfstrings()
IVAR = M.ivar_offsets()
IMPS = {}
for name, inst, cls in M.classes():
    for s, i in inst:
        IMPS[(name, s)] = i
    for s, i in cls:
        IMPS[(name, "+" + s)] = i
BY_ADDR = {v: "%s %s" % k for k, v in IMPS.items()}
STARTS = sorted(BY_ADDR)
TEXT_END = M.sections["__TEXT,__text"][0] + M.sections["__TEXT,__text"][1]

classrefs = {}
if "__DATA,__objc_classrefs" in M.sections:
    a, size, _ = M.sections["__DATA,__objc_classrefs"]
    for k in range(size // 8):
        target = M.u64(a + k * 8)
        name = None
        if target:
            try:
                name = M.read_class(target, False)[0]
            except Exception:
                name = None
        # A system class is bound only when the app loads, so it reads as 0 here.
        classrefs[a + k * 8] = name or STUB.get(a + k * 8) or "class@%x" % target

md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)


def method_end(start):
    """Where the method after this one begins, which is as far as this one can reach."""
    for a in STARTS:
        if a > start:
            return a
    return TEXT_END


def name_of(addr):
    if addr in SEL:
        return "sel:" + str(SEL[addr])
    if addr in CFSTR:
        return '@"%s"' % CFSTR[addr]
    if addr in IVAR:
        return "ivar " + IVAR[addr]
    for table in (classrefs, STUB):
        if addr in table:
            return str(table[addr])
    if addr in BY_ADDR:
        return BY_ADDR[addr]
    if M.in_section(addr, "__TEXT,__cstring"):
        return '"%s"' % M.cstr(addr)
    return None


def number_at(addr, reg):
    """The constant a floating-point load reads, by the register's width."""
    if reg.startswith("d"):
        v = M.f64(addr)
    elif reg.startswith("s"):
        v = M.f32(addr)
    else:
        return None
    return None if v is None else "= %g" % v


def jump_table(table, count):
    """The targets of a switch's jump table: signed 32-bit offsets from the table's start."""
    return [table + M.s32(table + 4 * k) for k in range(count)]


BRIEF = False
FULL = False
# In --brief, the lines kept besides those with a note: tests, branches and constants.
KEEP = ("cmp", "fcmp", "cbz", "cbnz", "tbz", "tbnz", "b.", "csel", "cset", "ccmp", "ret", "br")


class Line:
    """One listed line: an instruction, or a jump table's case."""
    def __init__(self, address, mnemonic, op_str, note="", addr=None, ivar=None, store=False):
        self.address, self.mnemonic, self.op_str = address, mnemonic, op_str
        self.note, self.addr, self.ivar, self.store = note, addr, ivar, store


def _imm(text):
    return int(text.strip().lstrip("#"), 0)


def walk(start, full=None):
    """Yield a Line for each instruction, and for each case of a jump table, up to the method's end.

    By default it stops at the first ret or tail call. With full, it reads on
    to where the next method begins, which takes in the code after an early
    return. --full sets it for the listings, and --refs and --writes always use it.
    """
    full = FULL if full is None else full
    end = method_end(start)
    regs = {}        # register -> address it holds, from adrp, add or adr
    ivreg = {}       # register -> instance variable whose offset it holds
    last_cmp = None  # the immediate of the last cmp, which bounds a switch
    tables = {}      # table address -> number of cases, skipped when the walk reaches it
    pending = None   # (register, table address) from an adr that may start a switch
    switch = None    # (table address, number of cases), listed after the switch's br
    pos = start
    while pos < end:
        if pos in tables:
            pos += 4 * tables.pop(pos)
            continue
        o = M.va2off(pos)
        ins = next(md.disasm(M.m[o:o + 4], pos, 1), None)
        if ins is None:
            pos += 4
            continue
        mn, ops = ins.mnemonic, ins.op_str
        parts = [p.strip() for p in ops.replace("[", "").replace("]", "").replace("!", "").split(",")]
        line = Line(pos, mn, ops)
        if mn == "adrp":
            regs[parts[0]] = _imm(parts[1])
        elif mn == "adr":
            a = _imm(parts[1])
            regs[parts[0]] = a
            line.addr = a
            line.note = name_of(a) or ""
            pending = (parts[0], a)
        elif mn == "cmp" and parts[-1].startswith("#"):
            last_cmp = _imm(parts[-1])
        elif mn == "ldrsw" and pending and len(parts) >= 3 and parts[1] == pending[0] and "lsl #2" in ops:
            # adr xT, table; ldrsw xI, [xT, xR, lsl #2]: a switch over cmp's bound.
            if last_cmp is not None:
                tables[pending[1]] = last_cmp + 1
                switch = (pending[1], last_cmp + 1)
            pending = None
        elif mn in ("ldr", "ldrsw") and len(parts) == 2 and parts[1].startswith("#"):
            # A literal load, from a constant next to the code.
            a = _imm(parts[1])
            line.addr = a
            if a in IVAR:
                ivreg[parts[0]] = IVAR[a]
                line.note = "ivar " + IVAR[a]
            else:
                line.note = number_at(a, parts[0]) or name_of(a) or ""
        elif mn in ("ldr", "ldrsw", "ldrb", "add") and len(parts) >= 3 and parts[1] in regs and parts[-1].startswith("#"):
            a = regs[parts[1]] + _imm(parts[-1])
            line.addr = a
            if mn == "ldrsw" and a in IVAR:
                ivreg[parts[0]] = IVAR[a]
                line.note = "ivar " + IVAR[a]
            else:
                line.note = (number_at(a, parts[0]) if mn == "ldr" else None) or name_of(a) or ""
            if mn == "add":
                regs[parts[0]] = a
        elif mn == "fmov" and "#" in ops:
            line.note = "= " + ops.split("#")[-1]
        elif mn in ("bl", "b"):
            a = _imm(parts[0])
            line.addr = a
            line.note = name_of(a) or ""
        # A load or store through a register holding an instance variable's offset.
        if mn in ("str", "strb", "ldr", "ldrb") and len(parts) == 3 and parts[2] in ivreg:
            line.ivar = ivreg[parts[2]]
            line.store = mn.startswith("str")
            arrow = "-> " if line.store else "<- "
            line.note = (line.note + " " if line.note else "") + arrow + ivreg[parts[2]].split(".")[-1]
        yield line
        if mn == "br" and switch:
            table, count = switch
            for k, target in enumerate(jump_table(table, count)):
                yield Line(table + 4 * k, ".case", "%d -> %x" % (k, target), addr=target)
            switch = None
        pos += 4
        if full:
            continue
        if mn == "ret":
            break
        if mn == "b":
            # A tail branch out of the method, into a library function or
            # another method, ends it; one that stays inside does not.
            target = _imm(parts[0])
            if target in STUB or target < start or target >= end:
                break


def dis(start):
    for ln in walk(start):
        if BRIEF and not ln.note and not ln.mnemonic.startswith(KEEP) and ln.mnemonic not in ("b", ".case") \
                and not (ln.mnemonic == "mov" and "#" in ln.op_str):
            continue
        if BRIEF and ln.mnemonic == "bl" and ln.note in ("_objc_retainAutoreleasedReturnValue", "_objc_release",
                                                          "_objc_retain", "_objc_msgSend"):
            continue
        print("  %x: %-6s %-34s %s" % (ln.address, ln.mnemonic, ln.op_str, ("; " + ln.note) if ln.note else ""))


def refs(target):
    """Yield (method, line) for each use of an address or selector name."""
    for (cls, sel), imp in sorted(IMPS.items(), key=lambda kv: kv[1]):
        for ln in walk(imp, full=True):
            if ln.addr == target or (isinstance(target, str) and ln.note.startswith("sel:" + target)
                                     and ln.note[len("sel:" + target):len("sel:" + target) + 1] in ("", " ")):
                yield "%s %s" % (cls, sel), ln


def writes(ivar):
    """Yield (method, line) for each store to an instance variable, by its name with or without the _."""
    want = ivar if ivar.startswith("_") else "_" + ivar
    for (cls, sel), imp in sorted(IMPS.items(), key=lambda kv: kv[1]):
        for ln in walk(imp, full=True):
            if ln.store and ln.ivar.split(".")[-1] == want:
                yield "%s %s" % (cls, sel), ln


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--brief" in args:
        args.remove("--brief")
        BRIEF = True
    if "--full" in args:
        args.remove("--full")
        FULL = True
    if args[:1] == ["--list"]:
        for (cls, sel), imp in sorted(IMPS.items(), key=lambda kv: kv[1]):
            if cls == args[1]:
                print("%x %s" % (imp, sel))
        sys.exit()
    if args[:1] == ["--find"]:
        word = args[1].lower()
        for (cls, sel), imp in sorted(IMPS.items(), key=lambda kv: kv[1]):
            if word in sel.lower():
                print("%x %s %s" % (imp, cls, sel))
        sys.exit()
    if args[:1] == ["--at"]:
        dis(int(args[1], 16))
        sys.exit()
    if args[:1] == ["--refs"]:
        t = args[1]
        target = int(t, 16) if t.lower().startswith("0x") else t
        for meth, ln in refs(target):
            print("%x in %s %s" % (ln.address, meth, ("; " + ln.note) if ln.note else ""))
        sys.exit()
    if args[:1] == ["--writes"]:
        for meth, ln in writes(args[1]):
            print("%x in %s, %s %s" % (ln.address, meth, ln.mnemonic, ln.op_str))
        sys.exit()
    if len(args) < 2 or len(args) % 2:
        sys.exit(__doc__)
    for k in range(0, len(args), 2):
        key = (args[k], args[k + 1])
        if key not in IMPS:
            sys.exit("No method %s %s. Try --list %s, or --find %s." % (key[0], key[1], key[0], key[1].strip("+:")))
        print("=== -[%s %s] at %x" % (key[0], key[1], IMPS[key]))
        dis(IMPS[key])
