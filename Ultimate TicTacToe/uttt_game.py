#!/usr/bin/env python3

"""Ultimate Tic Tac Toe Game
by Tobias Kuester, <tobias.kuester@gmx.net>, 2019

Idea and basic algorithm from my CodinGame bot. UI loosely based on Sudoku game.
There is no clear distinction between one-player (vs. AI) and two-player game.
Instead, there are buttons for evaluating different valid moves that can be used
for manually executing the AI's move in a single player game, or for getting hints
on improving one's own play, or for evaluating and improving the AI itself.

TODO
- code-cleanup, documentation
- handle draw and winning-draw
- key-bindings (q,n,e,p?)
- start parameters?
"""

import tkinter
import tkinter.font
import uttt

SIDE = 36
FONT_FAMILY = "Arial"
FONT_VALUE  = None
FONT_MARKER = None
TIMEOUT = 0.1

class UTTTFrame(tkinter.Frame):
	"""Tkinter-Frame for displaying and playing a game of Ultimate Tic Tac Toe.
	"""

	def __init__(self, master=None):
		tkinter.Frame.__init__(self, master)
		self.master.title("Ultimate Tic Tac Toe")
		self.grid()
				
		# create buttons panel
		tkinter.Button(self, text="New Game", command=self.new_game).grid(row=0, column=0)
		tkinter.Button(self, text="Evaluate", command=self.eval_moves).grid(row=0, column=1)
		tkinter.Button(self, text="Play Best", command=self.play_best).grid(row=0, column=2)
		self.status_var = tkinter.StringVar()
		tkinter.Label(self, textvariable=self.status_var).grid(row=1, column=0, columnspan=3)
		
		# create canvas
		self.canvas = tkinter.Canvas(self, bg="white", width=9*SIDE, height=9*SIDE)
		self.canvas.grid(row=2, column=0, columnspan=3)
		self.canvas.bind("<Button>", self.mouse_clicked)
		self.new_game()
	
	def new_game(self):
		self.board = uttt.init_board()
		self.player = +1
		self.last_move = (-1, -1)
		self.scores = {}
		self.game_over = False
		self.update()
	
	def eval_moves(self):
		if not self.game_over:
			moves = uttt.get_moves(self.board, self.last_move)
			scores = uttt.evaluate_moves(self.board, moves, self.player, TIMEOUT)
			for k in scores:
				self.scores[k] = self.scores.get(k, 0) + scores[k]
			self.update()
		
	def play_best(self):
		if not self.game_over:
			if not self.scores:
				self.eval_moves()
			moves = uttt.get_moves(self.board, self.last_move)
			win_move = uttt.winning_move(self.board, moves, self.player)
			non_lose = uttt.non_losing_moves(self.board, moves, self.player)
			best = win_move or max(non_lose or moves, key=self.scores.get)
			self.apply_move(best)
	
	def mouse_clicked(self, event):
		if not self.game_over:
			col  = min(event.x // SIDE, 8)
			line = min(event.y // SIDE, 8)
			move = (col, line)
			if move in uttt.get_moves(self.board, self.last_move):
				self.apply_move(move)
	
	def apply_move(self, move):
		self.board = uttt.apply_move(self.board, move, self.player)
		self.last_move = move
		self.player = -self.player
		self.scores = {}
		self.update()
	
	def get_color(self, move):
		r, g, b = 255, 255, 127
		applied = uttt.apply_move(self.board, move, self.player)
		if self.scores:
			if uttt.winning(applied, self.player):
				r, g, b = 0, 255, 0
			elif uttt.winning_move(applied, uttt.get_moves(applied, move), -self.player):
				r, g, b = 255, 0, 0
			elif move in self.scores:
				mx = max(self.scores.values())
				mn = min(self.scores.values())
				s = self.scores[move]
				if s < 0: g *= 1 - 0.5 * (s / mn)
				if s > 0: r *= 1 - 0.5 * (s / mx)
		return "#%02x%02x%02x" % (r, g, b)
	
	def update(self):
		if uttt.winning(self.board, -self.player):
			self.status_var.set("%s has won!" % uttt.SYMBOL[-self.player])
			self.game_over = True
		else:
			self.status_var.set("Next: %s's turn" % uttt.SYMBOL[self.player])
		self.canvas.delete("all")
		valid = uttt.get_moves(self.board, self.last_move)
		for i, board in enumerate(self.board):
			row, col = i // 3, i % 3
			if isinstance(board, list):
				for k, cell in enumerate(board):
					x, y = (3 * row + k // 3), (3 * col + k % 3)
					# highlight valid cells
					if (x, y) in valid and not self.game_over:
						self.canvas.create_rectangle(SIDE*x, SIDE*y, SIDE*(x+1), SIDE*(y+1),
								width=2, outline="white", fill=self.get_color((x, y)))
					# small marker
					if cell in (+1, -1):
						self.canvas.create_text(SIDE * (x+0.5), SIDE * (y+0.5),
								text=uttt.SYMBOL[cell], font=FONT_SMALL)
			else:
				# large marker
				self.canvas.create_text(SIDE * (row*3+1.5), SIDE * (col*3+1.5),
						text=uttt.SYMBOL[board], font=FONT_LARGE)
		# draw lines last
		for i in range(1, 9):
			w = 1 + (i % 3 == 0)
			self.canvas.create_line(SIDE * i, 0, SIDE * i, SIDE*9, width=w)
			self.canvas.create_line(0, SIDE * i, SIDE*9, SIDE * i, width=w)
		

# start application
if __name__ == "__main__":
	import optparse
	parser = optparse.OptionParser("uttt_game.py")
	(options, args) = parser.parse_args()

	#~try:
		#~grid_no = int(args[0]) if args else None
		#~if grid_no and (grid_no < 0 or grid_no > 50):
			#~raise ValueError
	#~except ValueError:
		#~parser.error("Grid number must be a number between 0 and 50")
		
	root = tkinter.Tk()
	FONT_LARGE = tkinter.font.Font(family=FONT_FAMILY, size=9*SIDE//4)
	FONT_SMALL = tkinter.font.Font(family=FONT_FAMILY, size=3*SIDE//4)
		
	app = UTTTFrame(root)
	app.mainloop()
