"""Netwalk-Clone (Model)
by Tobias Kuester, <tobias.kuester@gmx.net>, 2011

Clone of the Netwalk-Game (KDE-Suite), in which a number of 'network'-segments
have to be rotated so that the entire network ends up being connected.

The game can be configured via command line arguments to have any size that fits
the screen. It also features a "toroid" mode, in which the game worlds wraps
around at the edges, making the entire game much harder and more interesting.
"""

import random

# sides as complex numbers: east, south, west, north
SIDES = [1+0j, 0+1j, -1+0j, 0-1j]

class Node:
	"""Class representing one Node in the Network. The node has a coordinate and
	a quadruple of connections (north, east, south, west) to other nodes, and
	a fixed/unfixed and connectedness states.
	"""

	def __init__(self, x: int, y: int):
		"""Create Node instance at position (x, y).
		"""
		self.x = x
		self.y = y
		self.connections = set([])
		self.fixed = False
		self.connected = False
		self.dangling = False
		self.circle = False
	
	def rotate(self, counterclockwise=False):
		"""Rotate the node, changing its connections accordingly.
		"""
		if not self.fixed:
			mult = 1j if counterclockwise else -1j
			self.connections = set([x * mult for x in self.connections])
	

class Network:
	"""A Network of connected Nodes. The Network constitutes a spanning tree of
	all the nodes, with no loops, which can also be toroid (e.g. connected at the
	edged). The class provides methods for creating, scrambling and checking such
	a network.
	"""

	def __init__(self, width=10, height=10, toroid=False):
		"""Initialize Network with width x height nodes, creating random
		connections spanning the entire network without loops.
		"""
		self.width = width
		self.height = height
		self.toroid = toroid
		
		# create initial field
		self.nodes = [[None for x in range(width)] for y in range(height)]
		remaining = [(x, y) for x in range(width) for y in range(height)]
		for (x, y) in remaining:
			self.nodes[y][x] = Node(x, y)

		# expand the network starting from the hub
		x0, y0 = random.randint(0, width-1), random.randint(0, height-1)
		self.hub = self.nodes[y0][x0]
		fringe = [self.hub]
		remaining.remove((x0, y0))
		while fringe:
			# select random from fringe
			node = random.choice(fringe)
			x, y = node.x, node.y
			
			# get sides leading to node from remaining
			sides = [s for s in SIDES if self.xymod(x, y, s) in remaining]
			if sides:
				# select side at random
				side = random.choice(sides)
				sides.remove(side)
				x2, y2 = self.xymod(x, y, side)
			
				# add connection, move to fringe
				other = self.nodes[y2][x2]
				node.connections.add(side)
				other.connections.add(side * -1)
				remaining.remove((x2, y2))
				fringe.append(other)

			if not sides:
				fringe.remove(node)
	
	def scramble(self):
		"""Scramble the Network by rotating each node zero to three times.
		"""
		for line in self.nodes:
			for node in line:
				for _ in range(random.randint(0, 3)):
					node.rotate()

	def check(self):
		"""Check to what extend the tree is connected.
		"""
		# un-connect all nodes
		for line in self.nodes:
			for node in line:
				node.connected = False
				node.circle = False
				node.dangling = False

		# starting from hub, reconnect connected nodes
		fringe = [self.hub]
		while fringe:
			# get node from fringe
			node = fringe.pop()
			node.connected = True
			
			# get sides leading to node from remaining
			x, y = node.x, node.y
			sides = [s for s in node.connections if self.toroid or
			           (0 <= x+s.real < self.width and 0 <= y+s.imag < self.height)]

			# move connected neighbors to fringe
			adj_connected = 0
			for s in sides:
				x2, y2 = self.xymod(x, y, s)
				other = self.nodes[y2][x2]
				if s * -1 in other.connections:
					if other.connected:
						adj_connected += 1
					else:
						fringe.append(other)
				else:
					node.dangling = True
			if adj_connected >= 2:
				node.circle = True

	def xymod(self, x: int, y: int, c: complex) -> tuple[int, int]:
		"""Return (x, y) plus other side (complex), module width/height if toroid.
		"""
		x2, y2 = x + int(c.real), y + int(c.imag)
		if self.toroid:
			x2, y2 = x2 % self.width, y2 % self.height
		return x2, y2

