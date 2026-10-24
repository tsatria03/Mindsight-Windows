Mindsight for Windows

MiNDSiGHT is an interactive audio adventure for the iPhone, made by Luke Charman, told entirely through recordings.
You listen to the story and solve the puzzles inside it by swiping up, down, left or right at the right moment.
Every word in it is a recording: it never uses text to speech, and it was made to be played entirely by ear.
This is a port of it for Windows, played with the keyboard.

Headphones

Headphones are needed.
The recordings were made with a dummy head microphone, so their sound moves around you in three dimensions, and that only works in headphones.

Starting the game

Extract the whole Mindsight-Windows folder from the zip, and start Mindsight.exe in it.
Keep the folder together: the story's recordings are in story.dat, in the data folder beside Mindsight.exe, and the rest of the game is beside it too.

What it has

The whole game can be played, from its main menu, through the story and its puzzles, to its ending and its credits, with the original's recordings.
Your place is saved as you play, and Continue on the main menu carries on from it.

The keys

The arrow keys, or W, A, S and D, are the four swipes: up, down, left and right.
Escape, Enter or P is the double tap, which pauses the game and resumes it.
Before the story starts, in the menus, Escape quits the game instead, while Enter and P still pause.
A key held with Shift, Control, Alt or the Windows key does nothing, so your screen reader's own commands never reach the game.
Alt F4, or closing the window, quits at any time.

The menus

The game opens on its main menu, a recording that tells you which swipe does what: up for a new game, down to continue, left for the audio manual, and right for the credits.
Every menu is a recording like this.
Listen to it to the end: a swipe does nothing until it has finished.
On the credits, swiping left opens the creator's dissertation on the game, a PDF, in your PDF viewer; when you come back to the game, it plays the main menu.

Saving

The game saves your place by itself at the story's checkpoints, as the original did; nothing is saved when you quit.
Continue on the main menu plays your last checkpoint from its start. With no save, it tells you so: swipe up for a new game, or down for the main menu.
Starting a new game does not wipe your save; it is replaced at the new game's first checkpoint.
The save is in the saves folder of the game's save folder, Mindsight, in your AppData Roaming folder.

The buzz

Where the original made the phone vibrate, the game plays a short, low buzz.
It tells you that a swipe counts now: when a menu has finished and is waiting for you, and at the moment a timed puzzle starts to listen for your answer.
A swipe before the buzz does nothing, and makes no sound, so it never counts against you.

The puzzles

Each puzzle is a recording that asks you for a swipe.
Some must be heard to the end before a swipe counts, and some give you only a few seconds after the buzz.
A right answer plays a short sound and the story goes on.
A wrong answer, or letting a timed puzzle run out, plays what went wrong, then a rewind, and takes you back to try again.

Pausing

Escape, Enter or P pauses the game and plays a short message; press one again to carry on from the same moment.
While paused, the swipes do nothing.
If you switch to another window, the game pauses by itself.
When you come back, it steps back 3 seconds, welcomes you back, and waits for Escape, Enter or P to carry on.

Changes from the original

The game buzzes where the original vibrated.
It ignores the swipes while paused.
It always plays the credits after the ending; the original sometimes sent you back to a puzzle instead.
The second and third rounds of the street puzzle buzz when they start to listen, as every other timed round does; in the original they did not.
A scene buzzes as it begins only for the two puzzles that loop, the guard and the piranhas.

If something goes wrong

If the game cannot find its recordings, or cannot open a sound device, or stops because of an error, it says so in a message box, which your screen reader reads.
The details of an error are in crash.txt, in the logs folder of the game's save folder, Mindsight, in your AppData Roaming folder.

Credits

The port is by tsatria03.
MiNDSiGHT is by Luke Charman, made as a research project at SAE Institute London in 2009. Its cast and crew are named in its own credits.
