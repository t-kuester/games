# games

Some small games, usually very minimalistic, but quite fun nonetheless.
All of those are written in Python and Tkinter, usually in just one or two
files. All configuration is done via command line parameters.

Minesweeper
-----------
Not much to say about this, everyone knows Minesweeper. What's special about 
this version is that the field can have any size and any density of mines, both 
set with command line options. Also, there's an option to "auto-reveal" adjacent
cells once a cell has enough surrounding mine markers, which makes playing the
game much less tedious.

Netwalk
-------
A clone of the KDE game "Netwalk", where each cell in a grid has to be rotated
so that they connect to a single network, reaching each endpoint in the net.
Besides allowing any grid size (e.g. 30x20 instead of the puny 8x8 or 16x16 or 
whatever in the original), it also features a "toroid" mode, where the grid
"wraps around" the edges, making the whole game much more difficult and interesting.

Nonogram
--------
An implementation of the nonogram, or "Picross" game, where the player has to
find which cell in the grid is colored black and which is white by using hints
added to each row and column of the grid. Levels are randomly generated, so no
pretty pictures to uncover but just random noise. Again, grid size can be set
to any size using command line parameters.

Sudoku
------
While this one only comes with 50 pre-generated puzzles (taken from a Project 
Euler problem concerned with Sudoku), it has some (as far as I know) rather 
unique controls, as the number that is entered in a cell is determined by the
position where the mouse is pointed to in that cell: upper-left corresponds to
one, upper-right to three, centre to five, and so on. Also allows the user to 
set marker-numbers (either manually or automatically), to check and to solve
the current puzzle.
