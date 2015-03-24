#!/usr/bin/python

"""Minesweeper
by Tobias Kuester, 2010

Yet another 'Mine Sweeper' clone. Minimalistic, clean, easy to modify.
- minimal UI, configuration is done via command line arguments
- any grid size and mine density possible
- 'auto reveal' mode automatically opens neighbors when cell has enough mines
"""

import Tkinter
import random

BOOM, FLAG, CLOSED, CLEAR = -3, -2, -1, 0


class MineField:
	"""Minesweeper Game Class.
	
	This class provides all the game logic for the minesweeper game and can even
	be played without a GUI in the Python interpreter.
	"""

	def __init__(self, width=10, height=10, density=0.25):
		"""Create MineField. There is no fixed number of mines, instead they are
		randomly created according to the density, between 0.0 and 1.0.
		"""
		self.width = width
		self.height = height
		# create marks and mine field
		self.marks = [[CLOSED for _ in range(height)] for _ in range(width)]
		self.mines = [[random.random() < density for _ in range(height)] 
		                                         for _ in range(width)]
				
	def print_mines(self):
		"""Print a matrix to the console, showing the positions of the mines."""
		for y in range(self.height):
			for x in range(self.width):
				print "#" if self.mines[x][y] else ".",
			print ""
			
	def print_marks(self):
		"""Print a matrix to the console, showing the various marks."""
		SYMBOLS = {CLOSED: ".", FLAG: "x", BOOM: "#", CLEAR: " "}
		for y in range(self.height):
			for x in range(self.width):
				m = self.marks[x][y]
				print SYMBOLS.get(m, m),
			print ""

	def reveal(self, x, y, autoreveal=True):
		"""Reveal the cell at the given coordinate. Return True, if it did not
		hit a mine. If autoreveal is set, the autoreveal method is called.
		"""
		if self.marks[x][y] == CLOSED:
			if self.mines[x][y] == True:
				self.marks[x][y] = BOOM
				return False
			else:
				n = self.count_neighbor_mines(x, y)
				self.marks[x][y] = n
				if autoreveal or n == 0:
					self.auto_reveal(x, y)
		return True
		
	def auto_reveal(self, x, y):
		"""If the cell has sufficient flag markers, all neighboring cells are
		revealed (recursively).
		"""
		n = self.count_neighbor_flags(x, y)
		if self.marks[x][y] == n:
			for (x2, y2) in self.get_valid_neighbors(x, y):
				self.reveal(x2, y2, True)
		
	def mark(self, x, y, autoreveal=True):
		"""Mark / unmark the given cell; call autoreveal to neighboring cells.
		"""
		if self.marks[x][y] == CLOSED:
			self.marks[x][y] = FLAG
			if autoreveal:
				for (x2, y2) in self.get_valid_neighbors(x, y):
					self.auto_reveal(x2, y2)
		elif self.marks[x][y] == FLAG:
			self.marks[x][y] = CLOSED
		
	def count_neighbor_mines(self, x, y):
		"""Count neighbor cells with a mine in it."""
		return sum(self.mines[n][m] for (n, m) in self.get_valid_neighbors(x, y))

	def count_neighbor_flags(self, x, y):
		"""Count neighbor cells with a flag on it."""
		return sum(self.marks[n][m] == FLAG for (n, m) in self.get_valid_neighbors(x, y))

	def get_valid_neighbors(self, x, y):
		"""Get valid neighbor cells for given cell."""
		x_1, x_2 = max(x-1, 0), min(x+1, self.width-1)
		y_1, y_2 = max(y-1, 0), min(y+1, self.height-1)
		return [ (n, m) for n in range(x_1, x_2+1) 
		                for m in range(y_1, y_2+1) if x != n or y != m]
		                
	def get_mines(self):
		"""Return positions of all the mines."""
		return ( (x, y) for x in range(self.width)
		                for y in range(self.height) if self.mines[x][y])
		


class MineFrame(Tkinter.Frame):
	"""Application Frame for Minesweeper game.
	
	The Frame is on purpose absolutely minimalistic. It features only the mine
	field and a 'New Game' button. No options (other than the start parameters),
	no mine counter, no timer, no highscores. Just you and the mines...
	"""

	def __init__(self, density=0.25, width=10, height=10, side= 20, autoreveal=False):
		"""Create Application Frame. The parameters are passed right through to
		the Mine game object.
		"""
		Tkinter.Frame.__init__(self, None)
		self.master.title("Minesweeper")
		self.grid()
		self.width, self.height, self.side = width, height, side
		self.density = density
		self.auto = autoreveal
		self.game = None
		# create button
		button = Tkinter.Button(self, text="NEW", relief="groove", command=self.new_game)
		button.grid(row=0, column=0)
		# create mine field
		self.canvas = Tkinter.Canvas(self, width=width*side, height=height*side, bg="white")
		self.canvas.grid(row=1, column=0)
		self.canvas.bind("<Button>", self.reveal_cell)
		self.new_game()
		
	def new_game(self):
		"""Start new game."""
		self.game = MineField(self.width, self.height, self.density)
		self.draw_field()

	def reveal_cell(self, event):
		"""Reveal cell where the mouse has been clicked."""
		if self.game and (event.num == 1 or event.num == 3):
			try:			
				x, y = event.x / self.side, event.y / self.side
				if event.num == 1:
					self.game.reveal(x, y, self.auto)
				elif event.num == 3:
					self.game.mark(x, y, self.auto)
				self.draw_field()
			except IndexError:
				pass
	
	def draw_field(self):
		"""Draw the entire mine field. First, the canvas is cleared, then one by
		one the marks for the individual cells are drawn. If there is a BOOM
		marker, the game is set to gameover and the remaining mines are drawn.
		"""
		coords = lambda col, line: (self.side * col, self.side * line)
		s, s2, s4 = (self.side / x for x in (1, 2, 4))
		if self.game:
			self.canvas.delete("all")
			gameover = False
			for line in range(self.game.height):
				for col in range(self.game.width):
					x, y = coords(col, line)
					mark = self.game.marks[col][line]
					if mark == CLEAR:
						continue
					elif mark == CLOSED:
						self.canvas.create_rectangle(x, y, x+s, y+s, fill="gray")
					elif mark == FLAG:
						self.canvas.create_oval(x+s4, y+s4, x+s2+s4, y+s2+s4, fill="blue")
					elif mark == BOOM:
						self.canvas.create_rectangle(x, y, x+s, y+s, fill="red")
						gameover = True
					else:
						self.canvas.create_text(x+s2, y+s2, text=str(mark))
			if gameover:
				# draw all mines
				for (col, line) in self.game.get_mines():
					x, y = coords(col, line)
					self.canvas.create_oval(x+s4, y+s4, x+s2+s4, y+s2+s4, fill="black")
				self.game = None


# start application
if __name__ == "__main__":
	density = .25
	s_def = 15
	s_min = 5
	s_max = 50
	import optparse
	parser = optparse.OptionParser(("minesweeper.py [Options] [Density=%3f] "
			+ "[Width=%d [Height=%d]]") % (density, s_def, s_def))
	parser.add_option("-a", "--auto", dest="auto", help="auto reveal", action="store_true")
	(options, args) = parser.parse_args()

	try:
		density = float(args[0]) if args else density
		width = int(args[1]) if args and len(args) > 1 else s_def
		height = int(args[2]) if args and len(args) > 2 else width
		if not (s_min <= width <= s_max and s_min <= height <= s_max):
			raise ValueError
	except ValueError:
		parser.error("Size must be a number between %d and %d" % (s_min, s_max))
	else:
		app = MineFrame(density, width, height, 20, options.auto)
		app.mainloop()

