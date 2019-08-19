#!/usr/bin/env python3

"""Ultimate Tic Tac Toe Game
by Tobias Kuester, <tobias.kuester@gmx.net>, 2019

Idea and basic algorithm from my CodinGame bot. UI loosely based on Sudoku game.
There is no clear distinction between one-player (vs. AI) and two-player game.
Instead, there are buttons for evaluating different valid moves that can be used
for manually executing the AI's move in a single player game, or for getting hints
on improving one's own play, or for evaluating and improving the AI itself.

TODO
- show current player
- highlight playable cells
- button evaluate valid moves
- button play best move
- button auto-play?
- check whether game already won

What this does not:
- generate new random games
"""

import tkinter
import tkinter.font
import uttt

SIDE = 36
FONT_FAMILY = "Arial"
FONT_VALUE  = None
FONT_MARKER = None


class UTTTFrame(tkinter.Frame):
	"""Tkinter-Frame for displaying and playing a game of Ultimate Tic Tac Toe.
	"""

	def __init__(self, master=None):
		tkinter.Frame.__init__(self, master)
		self.master.title("Ultimate Tic Tac Toe")
		self.grid()
		self.board = uttt.init_board()
		self.player = +1
		self.last_move = (-1, -1)
				
		# create buttons panel
		tkinter.Label(self, text="Now Playing...").grid(row=0, column=0)
		tkinter.Button(self, text="Evaluate", command=self.eval_moves).grid(row=0, column=1)
		tkinter.Button(self, text="Play Best", command=self.play_best).grid(row=0, column=2)
		
		# create canvas
		self.canvas = tkinter.Canvas(self, bg="white", width=9*SIDE, height=9*SIDE)
		self.canvas.grid(row=1, column=0, columnspan=3)
		self.canvas.bind("<Button>", self.mouse_clicked)
		self.update()
	
	def eval_moves(self):
		pass
		
	def play_best(self):
		pass
	
	def mouse_clicked(self, event):
		col  = min(event.x // SIDE, 8)
		line = min(event.y // SIDE, 8)
		move = (line, col)
		if move in uttt.get_moves(self.board, self.last_move):
			self.board = uttt.apply_move(self.board, move, self.player)
			self.last_move = move
			self.player = -self.player
			self.update()
		
	def update(self):
		self.canvas.delete("all")
		# TODO draw lines
		
		uttt.show_grid(self.board)

		for i, board in enumerate(self.board):
			row, col = i // 3, i % 3
			if isinstance(board, list):
				for k, cell in enumerate(board):
					r, c = k // 3, k % 3
					if cell is not None:
						x = SIDE/2 + SIDE * (3 * col + c)
						y = SIDE/2 + SIDE * (3 * row + r)
						self.canvas.create_text(x, y, text=uttt.SYMBOL[cell],
			                                    font=FONT_LARGE)
			else:
				pass

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
	FONT_LARGE = tkinter.font.Font(family=FONT_FAMILY, size=3*SIDE//4)
	FONT_SMALL = tkinter.font.Font(family=FONT_FAMILY, size=  SIDE//4)
		
	app = UTTTFrame(root)
	app.mainloop()
