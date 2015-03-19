"""Sudoku Model
by Tobias Kuester, <tobias.kuester@gmx.net>, 2011

Originally created for Project Euler Challenge No. 96, using the sudoku grids
from the same challenge (file 'grids.txt').
"""

class Cell:
	"""One Cell in the Sudoku grid. Each Cell belongs to three Groups: a row,
	a column, and a block.
	"""

	def __init__(self, value):
		self.value = value
		self.fixed = False if value == 0 else True
		self.groups = []
		self.markers = [False] * 10

	def __str__(self):
		return str(self.value)
	
	def add_to_group(self, group):
		"""Add this Cell to the given Group.
		"""
		self.groups += [group]
	
	def get_possible_values(self):
		"""Return all the possible values for this Cell, given the other Cells
		in this Cell's Groups.
		"""
		return [n for n in range(1, 10)
		                if not any(group.has_value(n) for group in self.groups)]

	def check(self):
		"""Check whether this Cell's value is already assigned to another Cell
		in this Cell's Groups.
		"""
		if self.value == 0:
			return True
		else:
			all_others = reduce(lambda l1, l2: l1 + l2, [g.cells for g in self.groups])
			return not any(other.value == self.value
			                           for other in all_others if other != self)


class Group:
	"""A Group of Cells, like a row, a column, or a block in the Sudoku grid.
	"""

	def __init__(self, cells):
		self.cells = cells
		for cell in cells:
			cell.add_to_group(self)

	def __str__(self):
		return str([str(cell) for cell in self.cells])
		
	def has_value(self, value):
		"""Check whether the given value is already assigned to any of the Cells
		in this Group.
		"""
		return any(cell.value == value for cell in self.cells)
	

class Sudoku:
	"""A Sudoku grid.
	"""
	
	def __init__(self, lines):
		self.cells = [ [Cell(value) for value in line] for line in lines]
		self.groups = []
		for i in range(9):
			row = Group(self.cells[i])
			col = Group([self.cells[k][i] for k in range(9)])
			self.groups.append(row)
			self.groups.append(col)
		for i, k in [ (3*i, 3*k) for i in range(3) for k in range(3)]:
			sqr = Group([self.cells[i+n][k+m] for n in range(3) for m in range(3)])
			self.groups.append(sqr)

	def __str__(self):
		return "\n".join(" ".join(str(c) for c in line) for line in self.cells) + "\n"

	def solve(self, depth=0):
		"""Solve the Sudoku using backtracking.
		"""
		# find cell with least possible values
		next_cell, least, possible = None, 10, []
		for cells in self.cells:
			for cell in cells:
				if cell.value == 0:
					p = cell.get_possible_values()
					if len(p) < least:
						next_cell, least, possible = cell, len(p), p
		if next_cell:
			# try next possible value
			for new_value in possible:
				next_cell.value = new_value
				if self.solve(depth+1):
					return True
			# reset value, backtrack
			next_cell.value = 0
			return False
		else:
			# no more cells with value 0 -> solution found
			return True

	def markers(self):
		"""Set the markers for all the cells.
		"""
		for cells in self.cells:
			for cell in cells:
				possible = cell.get_possible_values()
				cell.markers = [n in possible for n in range(10)]
		

import random

MAX_NUMBER = 50
GRIDS_FILE = "grids.txt"

def load_game(number=None):
	"""Load the game with the given number from the GRIDS_FILE and return it.
	If no number if given, a game is selected at random.
	"""
	if number == None:
		number = random.randint(1, MAX_NUMBER)

	# open file, define some helper fields
	with open(GRIDS_FILE) as f:
		header = "Grid %s%d" % ("" if number > 9 else "0", number)
		def get_line():
			line = f.readline()
			return line[:-2] if line[-2:] == "\r\n" else line

		# search file for grid, create game
		sudoku = None
		line = get_line()
		while line:
		
			if line == header:
				# grid found!
				print "Loading Grid No.%d" % number
				lines = [ [int(c) for c in get_line()] for i in range(9)]
				sudoku = Sudoku(lines)
				break
		
			line = get_line()
	return sudoku


# Test
if __name__ == "__main__":
	sudoku = load_game(1)
	print sudoku
	if sudoku:
		sudoku.solve()
		print sudoku
