#!/usr/bin/python

"""Netwalk-Clone (Frontend)
by Tobias Kuester, <tobias.kuester@gmx.net>, 2011

Clone of the Netwalk-Game (KDE-Suite), in which a number of 'network'-segments
have to be rotated so that the entire network ends up being connected.

Controls:
- left/right mouse button rotates left/right
- center mouse button fixes/unfixes the tile
- arrow keys to wrap the grid around the edges (in toroid mode)
"""

from netwalk import Network
import tkinter

# some helper functions
col_fg = lambda node: "blue" if node.connected else "black"
col_bg = lambda node: "gray" if node.fixed else "white"
tag_fg = lambda node: "f%dx%d" % (node.x, node.y)
tag_bg = lambda node: "b%dx%d" % (node.x, node.y)


class NetwalkFrame(tkinter.Frame):
	"""Application Frame for Netwalk game.
	
	This frame consists of just two buttons for creating and re-scrambling the
	network, and a large playing area. Settings (size, toroid-mode) have to be
	done by parameters.
	"""

	def __init__(self, width=10, height=10, side=20, toroid=False):
		"""Create Application Frame.
		"""
		tkinter.Frame.__init__(self, None)
		self.master.title("Netwalk")
		self.grid()
		self.width, self.height, self.side = width, height, side
		self.toroid = toroid
		self.shift_h, self.shift_v = 0, 0
		self.game = None
		
		# create button
		button = tkinter.Button(self, text="NEW", relief="groove", command=self.new_game)
		button.grid(row=0, column=0)
		
		# create network field
		self.canvas = tkinter.Canvas(self, width=width*side, height=height*side, bg="white")
		self.canvas.grid(row=1, column=0)
		self.canvas.bind("<Button>", self.interact)
		self.bind_all("<KeyPress>", self.shift)
		self.new_game()
		
	def new_game(self):
		"""Start new game.
		"""
		self.game = Network(self.width, self.height, self.toroid)
		self.game.scramble()
		self.game.check()
		self.draw_field()
		
	def interact(self, event):
		"""Interact with the clicked Node, either rotating or (un)fixing the node.
		"""
		if 1 <= event.num <= 3:
			col = (event.x // self.side - self.shift_h) % self.width
			row = (event.y // self.side - self.shift_v) % self.height
			node = self.game.nodes[row][col]
			if event.num == 2:
				node.fixed = not node.fixed
			else:
				if event.num == 1:
					node.rotate(False)
				if event.num == 3:
					node.rotate(True)
				self.game.check()
				self.update_colors()
			self.draw_node(node)
	
	def shift(self, event):
		"""When in 'toroid' mode, shift the viewport by one Node to N/E/S/W.
		"""
		if self.toroid:
			if event.keysym == "Right":
				self.move_nodes(-1, 0)
			if event.keysym == "Left":
				self.move_nodes(1, 0)
			if event.keysym == "Up":
				self.move_nodes(0, 1)
			if event.keysym == "Down":
				self.move_nodes(0, -1)
	
	def draw_field(self):
		"""Re-draw the entire network field.
		"""
		for node in self.iterate_nodes():
			self.draw_node(node)

	def draw_node(self, node):
		"""Re-draw a single Node.
		"""
		self.canvas.delete(tag_fg(node))
		self.canvas.delete(tag_bg(node))

		# lengths		
		col = (node.x + self.shift_h) % self.width
		row = (node.y + self.shift_v) % self.height
		s, s2, s3, s4 = (self.side / x for x in (1, 2, 3, 4))
		x, y = col * s, row * s
		x2, x3, x4 = (x + s for s in (s2, s3, s4))
		y2, y3, y4 = (y + s for s in (s2, s3, s4))
		
		# draw background
		options = {"fill": col_bg(node), "tag": tag_bg(node)}
		self.canvas.create_rectangle(x, y, x+s, y+s, **options)
		
		# draw foreground
		options = {"fill": col_fg(node), "tag": tag_fg(node)}
		for side in node.connections:
			dx, dy = side.real*s2, side.imag*s2
			self.canvas.create_line(x2, y2, x2+dx, y2+dy, width=4, **options)
		if self.game.hub == node:
			self.canvas.create_oval(x4, y4, x4+s2, y4+s2, **options)
		if len(node.connections) == 1:
			self.canvas.create_oval(x3, y3, x3+s3, y3+s3, **options)

	def move_nodes(self, dx, dy):
		"""More efficient method for moving the nodes by the given dx and dy,
		swapping nodes leaving the network at one side to the other side.
		"""
		for node in self.iterate_nodes():
			col_old = (node.x + self.shift_h) % self.width
			row_old = (node.y + self.shift_v) % self.height
			col_new = (node.x + self.shift_h + dx) % self.width
			row_new = (node.y + self.shift_v + dy) % self.height
			move_x = (col_new - col_old) * self.side
			move_y = (row_new - row_old) * self.side
			self.canvas.move(tag_bg(node), move_x, move_y)
			self.canvas.move(tag_fg(node), move_x, move_y)
		self.shift_h += dx
		self.shift_v += dy

	def update_colors(self):
		"""More efficient method for updating the foreground colors (connected
		state) for all nodes.
		"""
		for node in self.iterate_nodes():
			self.canvas.itemconfigure(tag_fg(node), fill=col_fg(node))
				
	def iterate_nodes(self):
		"""Node iterator."""
		for row in range(self.height):
			for col in range(self.width):
				yield self.game.nodes[row][col]
				

# start application
if __name__ == "__main__":
	s_def = 15
	s_min = 5
	s_max = 35
	import optparse
	parser = optparse.OptionParser(("netwalk_game.py [Options] "
			+ "[Width=%d [Height=%d]]") % (s_def, s_def))
	parser.add_option("-t", "--toroid", dest="toroid",
	                  help="use toroid network?", action="store_true")
	(options, args) = parser.parse_args()

	try:
		width = int(args[0]) if args and len(args) > 0 else s_def
		height = int(args[1]) if args and len(args) > 1 else width
		if not (s_min <= width <= s_max and s_min <= height <= s_max):
			raise ValueError
	except ValueError:
		parser.error("Size must be a number between %d and %d" % (s_min, s_max))
	else:
		app = NetwalkFrame(width, height, 30, options.toroid)
		app.mainloop()
