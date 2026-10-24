"""releaser.py's own rules, without git, GitHub or a build: the version, filing the
changelog, the changelog's checks, the zip, and the menu."""
import _quiet  # noqa: F401  (first, before any of the game)

import os
import zipfile

import releaser


def test_the_version_counts_the_days_releases_from_the_tags():
    assert releaser.next_version([], '26.10.22') == '26.10.22-1'
    tags = ['V26.10.22-1', 'V26.10.22-2', 'V26.10.21-5', 'other']
    assert releaser.next_version(tags, '26.10.22') == '26.10.22-3'
    assert releaser.tag_for('26.10.22-3') == 'V26.10.22-3'
    assert releaser.title_for('26.10.22-3') == 'Mindsight V26.10.22-3'


def test_the_unreleased_lines_are_filed_under_the_version_and_unrelease_stays_empty():
    text = 'unrelease:\nContinue plays the saved scene.\nThe game opens.\n\n26.10.21-1:\nOld.\n'
    new, changed, _notes = releaser.plan_changelog(text, '26.10.22-1')
    assert changed
    assert new == ('unrelease:\n\n26.10.22-1:\nContinue plays the saved scene.\nThe game opens.\n\n'
                   '26.10.21-1:\nOld.\n')
    assert releaser.release_notes(new, '26.10.22-1') == 'Continue plays the saved scene.\nThe game opens.'


def test_a_missing_unrelease_is_put_back():
    new, changed, notes = releaser.plan_changelog('26.10.21-1:\nOld.\n', '26.10.22-1')
    assert changed and new.startswith('unrelease:\n') and 'put back' in notes[0]


def test_every_entry_must_end_in_a_full_stop():
    lines = ['Ends well.', 'Says "Continue: the office."', 'No stop', "It's 'quoted.'"]
    assert releaser.without_full_stop(lines) == ['No stop']


def test_the_changelog_as_it_is_now_has_every_full_stop():
    """Every entry in the file, released or waiting; unrelease: may be empty, as just after a
    release."""
    entries = [line for _heading, lines in releaser.parse_changelog(releaser.read_changelog())
               for line in lines]
    assert entries and releaser.without_full_stop(entries) == []


def test_the_changelogs_problems_are_named():
    assert 'nothing is under' in releaser.changelog_problems([], [], False)[0]
    many = ['Line %d.' % n for n in range(releaser.MAX_ENTRIES + 1)]
    assert any('no more than' in p for p in releaser.changelog_problems(many, [], False))
    few = releaser.changelog_problems(['One.', 'Two'], [], False)
    assert any('full stop' in p for p in few) and any('at least' in p for p in few)
    fine = ['Line %d.' % n for n in range(releaser.MIN_ENTRIES)]
    assert releaser.changelog_problems(fine, [], False) == []


def test_the_zip_holds_one_mindsight_windows_folder_and_stores_the_recordings():
    build = os.path.join(_quiet.FOLDER, 'build')
    os.makedirs(os.path.join(build, 'game'), exist_ok=True)
    os.makedirs(os.path.join(build, 'docks'), exist_ok=True)
    for name, data in (('Mindsight.exe', b'MZ'), ('VERSION', b'26.10.22-1\n'),
                       (os.path.join('docks', 'readme.txt'), b'Read me.'),
                       (os.path.join('game', 'a.mp3'), b'ID3' * 100),
                       ('story.dat', b'MINDSPK1' + b'\x00' * 100)):
        with open(os.path.join(build, name), 'wb') as fh:
            fh.write(data)
    assert releaser.built_version(build) == '26.10.22-1'
    archive = os.path.join(_quiet.FOLDER, releaser.zip_name('26.10.22-1'))
    assert os.path.basename(archive) == 'Mindsight-Win-26.10.22-1.zip'
    releaser.package(build, '26.10.22-1', archive)
    assert not os.path.exists(archive + '.part')
    with zipfile.ZipFile(archive) as box:
        names = box.namelist()
        assert all(n.startswith('Mindsight-Windows/') for n in names)
        assert 'Mindsight-Windows/docks/readme.txt' in names
        assert box.getinfo('Mindsight-Windows/game/a.mp3').compress_type == zipfile.ZIP_STORED
        assert box.getinfo('Mindsight-Windows/story.dat').compress_type == zipfile.ZIP_STORED
        assert box.getinfo('Mindsight-Windows/VERSION').compress_type == zipfile.ZIP_DEFLATED


def test_enter_with_nothing_typed_says_the_menu_again():
    answers = iter(['', '0'])
    said = []
    saved_say = releaser.say
    releaser.input = lambda prompt='': next(answers)
    releaser.say = lambda text='': said.append(text)
    try:
        releaser.menu()
    finally:
        releaser.say = saved_say
        del releaser.input
    assert sum(1 for line in said if line.startswith('Mindsight releaser.')) == 2


def test_the_build_choice_says_its_choices_again_on_enter():
    answers = iter(['', '2'])
    said = []
    saved_say = releaser.say
    releaser.input = lambda prompt='': next(answers)
    releaser.say = lambda text='': said.append(text)
    try:
        assert releaser.choose_build() == ['--embed']
    finally:
        releaser.say = saved_say
        del releaser.input
    assert sum(1 for line in said if line.strip().startswith('2. the single exe')) == 2


_quiet.run_tests(globals())
