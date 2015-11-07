#!/usr/bin/env python3

"""Nonogram
by Tobias Kuester, <tobias.kuester@gmx.net>, 2010

This is a very simple, but very addictive puzzle game inspired by 'Picross' for
Nintendo Game Boy and other Nonogram games. The goal of the game is to entirely
reveal a more or less large field of empty and filled cells only with the hints
of how long the sequences of consecutive filled cells are in each row and
column. For example, the line .##...###.# would yield the hint 2-3-1.

Currently, this only provides randomly generated puzzles (which, of course, 
makes it all the more interesting, as one can not just guess the picture).
The size of the grid is determined with a command-line parameter, as well as 
whether or not to show a 'crosshair'.

Mouse-Controls: left-click: mark as filled; right-click: mark as empty.
Keyboard-Controls (only w/ cross-hair ): Arrow keys: move, f/e: mark full/empty
"""

import tkinter, random, itertools

class Nonogram(object):
	"""Nonogram Data Class.

	Essentially, this is a random matrix of ones and zeros plus some methods for
	retrieving the hints for the columns and rows.
	"""

	def __init__(self, size):
		"""Create Nonogram game and initialize with random values of 0 and 1.
		@param size: both width and height of field (int)
		"""
		self.size = size
		self.field = [[random.randint(0, 1) for _ in range(size)] for _ in range(size)]

	def line_code(self, line_no):
		"""Return hint for line.
		@param line_no: number of line (int)
		"""
		line = self.field[line_no]
		return self.sequence_code(line)

	def column_code(self, column_no):
		"""Return hint for column.
		@param column_no: number of column (int)
		"""
		column = [line[column_no] for line in self.field]
		return self.sequence_code(column)

	def sequence_code(self, sequence):
		"""Create hint for given sequence."""
		return [sum(g) for k, g in itertools.groupby(sequence) if k == 1]


class NonogramFrame(tkinter.Frame):
	"""Application Frame for Nonogram Game.

	The Nonogram Frame shows the field and the line- and column hints. Also, the
	frame can show a crosshair, helping to identify the current line and column.
	"""

	# build frame
	def __init__(self, master=None, size=10, space=20, cross=False):
		"""Create Frame for a game of Nonogram.
		@param size:      size of Nonogram game (int)
		@param space:     size of one cell in pixels (int)
		@param cross:     draw crosshair? (bool)
		"""
		tkinter.Frame.__init__(self, master)
		self.master.title("Nonogram")
		self.grid()
		self.size, self.space = size, space
		self.game = None
		self.bind_all("q", lambda e: self.quit())
		
		# create button
		button = tkinter.Button(self, text="NEW", relief="groove", command=self.new_game)
		button.grid(row=0, column=0)
		
		# create labels
		self.columns, self.rows = [], []
		for n in range(size):
			self.rows += [tkinter.Label(self)]
			self.rows[n].grid(row=n+1, column=0, sticky="E")
			self.columns += [tkinter.Label(self)]
			self.columns[n].grid(row=0, column=n+1, sticky="S")
		
		# create central field
		self.canvas = tkinter.Canvas(self, width=space*size, height=space*size, bg="#a0a0a0")
		self.canvas.grid(row=1, column=1, rowspan=size, columnspan=size)
		self.canvas.bind("<Button>", self.reveal_cell_event)
		for n in range(size):
			self.canvas.create_line(0, space*n, space*size, space*n)
			self.canvas.create_line(space*n, 0, space*n, space*size)
		
		# create crosshair?
		if cross:
			self.last_highlighted = (self.rows[0], self.columns[0])
			self.line_x = self.canvas.create_line(0, 0, 0, space*size, fill="blue", tags="cross")
			self.line_y = self.canvas.create_line(0, 0, space*size, 0, fill="blue", tags="cross")
			self.canvas.bind("<Motion>", lambda e: self.draw_cross(e.x, e.y))
			self.bind_all("<KeyRelease>", self.keyboard_control)
			self.x = self.y = 0
		self.new_game()

	def new_game(self):
		"""Start new game."""
		self.game = Nonogram(self.size)
		for n in range(self.size):
			line_code = map(str, self.game.line_code(n))
			self.rows[n]["text"] = " ".join(line_code)
			column_code = map(str, self.game.column_code(n))
			self.columns[n]["text"] = "\n".join(column_code)
		self.canvas.delete("cell")

	def reveal_cell_event(self, event):
		"""Reveal cell where the mouse has been clicked."""
		if self.game and (event.num == 1 or event.num == 3):
			col, line = event.x // self.space, event.y // self.space
			self.reveal_cell(col, line, event.num == 1)
			
	def reveal_cell(self, col, line, black=True):
		"""Reveal cell at the given position."""
		try:			
			value = self.game.field[line][col]
			if value != -1:
				if black:
					color = "black" if value else "#faa"
				else:
					color = "white" if not value else "#800"
				offset = 2
				x, y = self.space*col+offset, self.space*line+offset
				s = self.space-2*offset
				last = self.canvas.create_rectangle(x, y, x+s, y+s, 
													tags="cell", fill=color)
				self.canvas.tag_raise("cross", last)
				self.game.field[line][col] = -1
		except IndexError:
			pass

	def draw_cross(self, x, y):
		"""Relocate cross hair to current mouse position and highlight hint
		codes for respective line and column.
		"""
		s = self.size * self.space
		# draw cross hair
		self.canvas.coords(self.line_x, x, 0, x, s)
		self.canvas.coords(self.line_y, 0, y, s, y)
		# highlight respective line codes
		try:
			column, row = self.columns[x/self.space], self.rows[y/self.space]
			if self.last_highlighted != (row, column):
				(last_row, last_column) = self.last_highlighted
				last_column.config(fg="black")
				last_row.config(fg="black")
				column.config(fg="blue")
				row.config(fg="blue")
				self.last_highlighted = (row, column)
		except IndexError:
			pass	
		
	def keyboard_control(self, event):
		"""Listen to key events and move the crosshair and reveal cells."""
		if event.keysym == "q":
			exit()
		if event.keysym == "n":
			self.new_game()
		directions = {"Right": (+1, 0), "Left": (-1, 0), 
		              "Up": (0,-1), "Down": (0, +1)}
		if event.keysym in directions:
			dx, dy = directions[event.keysym]
			minmax = lambda n: min(self.size-1, max(n, 0))
			self.x, self.y = minmax(self.x+dx), minmax(self.y+dy)
			# TODO paint cross hair or box
			pos = lambda n: int(self.space * (n + 0.5))
			self.draw_cross(pos(self.x), pos(self.y))
		elif event.keysym in ("f", "e"):
			self.reveal_cell(self.x, self.y, event.keysym == "f")


# start application
if __name__ == "__main__":
	import optparse
	parser = optparse.OptionParser("nonogram.py [Options] [Size=10]")
	parser.add_option("-c", "--cross", dest="cross", help="show cross hair?", action="store_true")
	(options, args) = parser.parse_args()

	try:
		size = int(args[0]) if args else 10
		if not 5 < size < 50:
			raise ValueError
	except ValueError:
		parser.error("Size must be a number between 5 and 50")
	else:
		app = NonogramFrame(None, size, 20, options.cross)
		app.mainloop()
