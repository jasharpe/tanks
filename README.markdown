Tanks! is a game implemented with pygame in which the player must use a tank to destroy other tanks and assorted other dangerous foes.

## How to Use

### Dependencies, version and OS info

Requires pygame to be installed. Developed on python 2.7 and Windows 7, other versions or OSes are supported, but I may not know if they work or not. Please let me know if they don't and I'll try to fix.

### How to run

Run the game by typing

    python main.py
  
at the command line while in the top level directory.

## Controls

The tank's driving is controlled by either the arrow keys or WASD:

* Up/W: Forward (or brake if in reverse)
* Down/S: Backward (or brake if going forwards)
* Left/A: Turn tank to the left
* Right/D: Turn tank to the right

The tank's turret is controlled by the position of the mouse. The turret will turn towards the mouse.

To fire a bullet, hit the left mouse button. It will fire in the direction that the turret is currently facing (which may not be in the direction of the mouse since the turret does not turn instantly).

Other controls:

* P: pauses/unpauses the game
* R: restarts the current level
* ESC: go to the menu

## Settings

_[Accessed from the "settings" option of the main menu]_

* Music: toggles playing the game music
* Sound: toggles playing game sounds, such as explosions 
* Debug: toggles some debug features (see below)

## Debug mode

_[Active when the debug option is enabled from the settings menu]_

* Prints the milliseconds taken to render long frames

## Credits

All code, art and sound effects were produced by Jeremy Sharpe, with the exception of the following acknowledgements:

* Thanks to JewelBeat.com for the music, "Move, Move, Move"
* The menu font, "Army", the original source of which is unknown
