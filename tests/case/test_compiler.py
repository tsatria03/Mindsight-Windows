"""compiler.py's own rules, without building anything: the changelog, what a build carries,
the pack it makes, the PyInstaller command line, the licences, how --test judges a run,
and the menu."""
import _quiet  # noqa: F401  (first, before any of the game)

import json
import os
import shutil
import types

import compiler

FLAGS = dict(embed=False, onefile=False, console=False, clean=False)


def args(**changed):
    return types.SimpleNamespace(**dict(FLAGS, **changed))


def test_an_empty_unrelease_is_taken_out_of_the_shipped_changelog():
    text = 'unrelease:\n\n26.10.22-1:\nThe game opens.\n'
    assert compiler.without_unrelease(text) == '26.10.22-1:\nThe game opens.\n'
    kept = 'unrelease:\nA new thing.\n\n26.10.22-1:\nThe game opens.\n'
    assert compiler.without_unrelease(kept) == kept                 # lines under it are kept
    assert compiler.unreleased_lines(kept) == ['A new thing.']


def test_a_sentence_ending_in_a_colon_is_never_a_heading():
    blocks = compiler.parse_changelog('unrelease:\nThe menu says: up for a new game.\nIt says:\n')
    assert blocks == [['unrelease:', ['The menu says: up for a new game.', 'It says:']]]


def test_the_build_carries_the_misc_sounds_and_the_dissertation_but_not_the_story():
    src = compiler.game_source()
    assert src is not None and compiler.missing_game_files(src) == []
    names = compiler.game_files(src)
    misc = os.path.join(src, 'data', 'audio', 'system', 'misc')
    assert sorted(n for n in names if n.endswith('.mp3')) == sorted(
        os.path.join('data', 'audio', 'system', 'misc', n) for n in os.listdir(misc))
    assert len([n for n in names if n.endswith('.mp3')]) == 5          # FanRadio included
    assert os.path.join('data', 'text', 'MiNDSIGHT.pdf') in names
    assert not any(n.startswith(os.path.join('data', 'audio', 'story')) for n in names)
    assert not any(n == 'MiNDSIGHT' or n.startswith('Base.lproj') for n in names)


def test_the_compiler_makes_a_pack_that_reads_back_and_its_fingerprint():
    from mindsight.platform import pack
    src = os.path.join(_quiet.FOLDER, 'compiler game')
    sceen = os.path.join(src, 'data', 'audio', 'story', 'sceen')
    os.makedirs(sceen, exist_ok=True)
    real = os.path.join(compiler.game_source(), 'data', 'audio', 'system', 'misc')
    for name in sorted(os.listdir(real))[:2]:
        shutil.copy2(os.path.join(real, name), os.path.join(sceen, name))
    dest = os.path.join(_quiet.FOLDER, 'compiler stage', compiler.PACK)
    info = compiler.make_pack(src, dest)
    assert info['files'] == 2 and len(pack.Pack(dest).files) == 2
    game = os.path.join(_quiet.FOLDER, 'compiler build', 'game')
    compiler.write_fingerprint(game, info)
    from mindsight import paths
    assert paths.PACK_FINGERPRINT == os.path.join('data', 'text', 'story_pack.json')
    assert not os.path.exists(os.path.join(game, 'data', compiler.FINGERPRINT))  # never outside the text folder
    with open(os.path.join(game, paths.PACK_FINGERPRINT), encoding='utf-8') as fh:
        assert json.load(fh) == {'size': info['size'], 'sha256': info['sha256']}


def test_the_command_carries_the_cipher_and_never_the_nvda_client():
    cmd = compiler.command(args())
    joined = ' '.join(cmd)
    assert '--hidden-import cryptography.hazmat.primitives.ciphers.aead' in joined
    assert 'nvda' not in joined.lower() and 'fmod' not in joined.lower() and 'prism' not in joined
    assert '--windowed' in cmd and '--onefile' not in cmd and cmd[-1] == 'Mindsight.py'
    embedded = compiler.command(args(embed=True), embed_game=True)
    assert '--onefile' in embedded and compiler.GAME_STAGE + os.pathsep + 'game' in embedded
    assert '--windowed' not in compiler.command(args(console=True))


def test_the_licences_include_pygames_and_cryptographys():
    rels = [rel for rel, _src in compiler.license_files()]
    assert os.path.join('pygame', 'LGPL.txt') in rels
    assert any(r.startswith('cryptography' + os.sep) for r in rels)
    assert not any('nvda' in r.lower() for r in rels)


def test_a_good_run_passes_and_each_bad_one_says_why():
    good = ('00:00:01 INFO mindsight game data: x\n00:00:01 INFO audio sound opened: (44100, -16, 2)\n'
            '00:00:01 INFO recordings story recordings: C:\\x\\data\\story.dat\nMindsight closed\n')
    assert compiler.judge_test(0, good, '') == []
    loose = good.replace('C:\\x\\data\\story.dat', 'C:\\x\\game\\data\\audio\\story')
    assert any('story.dat' in p for p in compiler.judge_test(0, loose, ''))
    assert any('crash report' in p for p in compiler.judge_test(1, good, 'Traceback'))
    assert any('no "game data:"' in p for p in compiler.judge_test(0, good.replace('game data', 'x'), ''))
    assert any('sound opened' in p for p in compiler.judge_test(0, good.replace('sound opened', 'x'), ''))
    assert any('did not close' in p for p in compiler.judge_test(0, good.replace('Mindsight closed', ''), ''))
    assert any('still running' in p for p in compiler.judge_test(None, good, ''))
    assert any('exit code 1' in p for p in compiler.judge_test(1, good, ''))
    assert 'no log at all' in compiler.judge_test(0, '', '')[0]


def test_the_test_runs_silent_and_without_message_boxes():
    assert compiler.TEST_QUIET['MINDSIGHT_NO_MESSAGEBOX'] == '1'
    assert compiler.TEST_QUIET['SDL_AUDIODRIVER'] == 'dummy'
    assert compiler.TEST_QUIET['SDL_VIDEODRIVER'] == 'dummy'


def test_the_game_logs_what_the_test_looks_for():
    import Mindsight
    import logging
    root = logging.getLogger()
    assert Mindsight.main(['--exit-after', '0.3']) == 0
    for h in list(root.handlers):
        if isinstance(h, logging.FileHandler):
            root.removeHandler(h)
            h.close()
    from mindsight import paths
    with open(paths.user_path('logs', 'log.txt'), encoding='utf-8') as f:
        text = f.read()
    problems = compiler.judge_test(0, text, '')
    assert problems == ['the log never says the story recordings came from story.dat'], problems


def test_every_menu_choice_is_a_command_line_the_parser_takes():
    for _text, flags in compiler.MENU:
        assert set(flags) <= {'--test', '--embed', '--clean', '--console', '--onefile',
                              '--no-game', '--dry-run'}


def test_enter_with_nothing_typed_says_the_menu_again():
    answers = iter(['', 'x', '2'])
    said = []
    saved_say = compiler.say
    compiler.input = lambda prompt='': next(answers)
    compiler.say = lambda text='': said.append(text)
    try:
        assert compiler.menu() == ['--test']
    finally:
        compiler.say = saved_say
        del compiler.input
    assert sum(1 for line in said if line.startswith('Mindsight compiler.')) == 2
    assert any(line.startswith('There is no choice "x"') for line in said)


_quiet.run_tests(globals())
