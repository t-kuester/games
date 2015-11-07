#!/usr/bin/env python3

"""Sudoku Game
by Tobias Kuester, <tobias.kuester@gmx.net>, 2011

Sudoku-Frame and Cell-Canvas for the Sudoku model (sudoku_model.py). Apart from 
being just another Sudoku game, this one has a rather nice control mode: To add
a number, just click in the corresponding corner of the cell, i.e. upper-left
for 1, upper-right for 3, centre for 5, etc.

What this does:
- load random game from text file
- check current state
- automatically set 'marker' numbers
- set/unset markers and actual numbers by clicking in any corner of the cell

What this does not:
- generate new random games
"""

import tkinter
import tkinter.font
import sudoku_model

SIDE = 36
FONT_FAMILY = "Arial"
FONT_VALUE  = None
FONT_MARKER = None

class Field(tkinter.Canvas):
	"""Canvas element for displaying and controlling a single Cell in the Sudoku.
	"""

	def __init__(self, master, cell):
		tkinter.Canvas.__init__(self, master, width=SIDE, height=SIDE, bg="white")
		self.cell = cell
		self.update()
		if not self.cell.fixed:
			self.bind("<Button>", self.mouse_clicked)

	def mouse_clicked(self, event):
		"""The values for the Cell are controlled by clicking in a specific region
		of the Canvas (top-left for 1 to bottom-right for 9).  LMB sets the value,
		RMB toggles a marker, CMB unsets the value.
		"""
		# get number
		col  = min(3 * event.x // SIDE, 2)
		line = min(3 * event.y // SIDE, 2)
		value = line * 3 + col + 1
		if event.num == 1:
			# set value
			self.cell.value = value
		elif event.num == 2:
			# un-set value
			self.cell.value = 0
		elif event.num == 3:
			# (un-)set marker
			self.cell.markers[value] = not self.cell.markers[value]
		self.update()
		
	def update(self):
		"""Update this Cell's visualisation. Initial Values are srawn black,
		others blue.  Markers are drawn in their respective places, with 1 at
		the top-left and 9 at the bottom-right.
		"""
		self.delete("all")
		if self.cell.value:
			# draw value
			color = "black" if self.cell.fixed else "blue"
			self.create_text(SIDE/2, SIDE/2, text=str(self.cell.value),
			                       font=FONT_VALUE, fill=color)
		else:
			# draw markers
			for n in filter(lambda n: self.cell.markers[n], range(1, 9 + 1)):
				x = SIDE//6 + ((n-1) %  3) * SIDE//3
				y = SIDE//6 + ((n-1) // 3) * SIDE//3
				self.create_text(x, y, text=str(n), font=FONT_MARKER, fill="blue")


class SudokuFrame(tkinter.Frame):
	"""Tkinter-Frame for displaying and playing a game of Sudoku.
	"""

	def __init__(self, master=None, grid_no=None):
		tkinter.Frame.__init__(self, master)
		self.master.title("Sudoku")
		self.grid()
		self.game = sudoku_model.load_game(grid_no)
		
		# create fonts
		global FONT_VALUE, FONT_MARKER
		FONT_VALUE  = tkinter.font.Font(family=FONT_FAMILY, size=3*SIDE//4)
		FONT_MARKER = tkinter.font.Font(family=FONT_FAMILY, size=  SIDE//4)
				
		# create buttons panel
		buttons = tkinter.Canvas(self)
		buttons.grid(row=0, column=0, columnspan=3)
		tkinter.Button(buttons, text="Markers", command=self.markers).grid(row=0, column=0)
		tkinter.Button(buttons, text="Check", command=self.check).grid(row=0, column=1)
		tkinter.Button(buttons, text="Solve", command=self.solve).grid(row=0, column=2)
		
		# create cells
		self.fields = []
		for gx, gy in ((x, y) for x in range(3) for y in range(3)):
			group = tkinter.Canvas(self, bg="black")
			group.grid(row=gy+1, column=gx, ipadx=2, ipady=2)
			for c, r in ((x, y) for x in range(3) for y in range(3)):
				cell = self.game.cells[gy*3 + r][gx*3 + c]
				field = Field(group, cell)
				field.grid(row=r, column=c, padx=1, pady=1)
				self.fields += [field]
				
	def markers(self):
		"""Create all markers and update Fields.
		"""
		self.game.markers()
		for field in self.fields:
			field.update()
		
	def check(self):
		"""Check for errors and update Fields.
		"""
		for field in self.fields:
			ok = field.cell.check()
			field["bg"] = "white" if ok else "red"
			field.update()
		
	def solve(self):
		"""Solve Sudoku (if still possible) and update Fields.
		"""
		self.game.solve()
		for field in self.fields:
			field.update()
		
	
# start application
if __name__ == "__main__":
	import optparse
	parser = optparse.OptionParser("sudoku.py [GridNo=random]")
	(options, args) = parser.parse_args()

	try:
		grid_no = int(args[0]) if args else None
		if grid_no and (grid_no < 0 or grid_no > 50):
			raise ValueError
	except ValueError:
		parser.error("Grid number must be a number between 0 and 50")
	else:
		app = SudokuFrame(None, grid_no)
		app.mainloop()
