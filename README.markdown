Tanks! is a game implemented with pygame in which the player must use a tank to destroy other tanks and assorted other dangerous foes.

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
* [Left Shift] + N: In a menu, this will cause the font to change if in sysfont mode, and print the name of the font used (forward a font with just N, or backwards with Left Shift + N)

## Credits

All code, art and sound effects were produced by Jeremy Sharpe, with the exception of the following acknowledgements:

* Thanks to JewelBeat.com for the music, "Move, Move, Move"
