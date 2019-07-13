# TODO
# determine losing moves (other player can win with next move)
# proper monte carlo tree search
# fast method for board copying (maybe try flat board again?)

import sys, functools, random, time, copy, itertools

random.seed(0)
debug = functools.partial(print, file=sys.stderr)
rows = range(3) # yes, this does makes a difference!

SYMBOL = [".", "X", "#", "O"]
NONE, OWN, OPP, DRAW = 0, 1, -1, 2
TIMEOUT = 0.5

def get_moves(board, last):
	""" get valid moves given board and last move
	"""
	R, C = last[0] % 3, last[1] % 3
	playable_fields = [(R,C)] if last != (-1, -1) and type(board[R][C]) == list else \
			((r,c) for r in rows for c in rows if type(board[r][c]) == list)
	return [(3*R+r, 3*C+c) for (R,C) in playable_fields
			for r in rows for c in rows if board[R][C][r][c] == NONE]

def winning_draw(board, player):
	""" In case of no line, player with more smaller boards wins
	"""
	own = sum(1 for line in board for c in line if c == +player)
	opp = sum(1 for line in board for c in line if c == -player)
	return player if (own > opp) else (-player if opp > own else 0)

def losing_move(board, move, player):
	# just for testing, copy board and apply the move (should not be necessary)
	# check if the move is a winning move
	# if not, get moves after that, check if any of those is a winning move
	pass

def winning(board, player):
	""" check whether player has won the board, works for sub- or for meta board
	"""
	return (any(all(board[r][c] == player for c in rows) for r in rows)
		 or any(all(board[r][c] == player for r in rows) for c in rows)
		 or all(board[i][   i]  == player for i in rows)
		 or all(board[i][-1-i]  == player for i in rows))

def apply_move(board, move, player):
	""" apply move; if player won smaller board, update meta board
	"""
	R, C = move[0] // 3, move[1] // 3
	r, c = move[0] % 3, move[1] % 3
	
	board = partial_copy(board, move)
	subgrid = board[R][C]
	
	subgrid[r][c] = player
	if winning(subgrid, player):
		board[R][C] = player
	elif not any(c == NONE for line in subgrid for c in line):
		board[R][C] = DRAW
		
	return board
	
def random_play(move, player):
	""" perform random moves until the game is over,
	return winning player and number of moves
	"""
	board = partial_copy(grid, move) # redundant, but keep in for now
	board = apply_move(board, move, player)
	for i in itertools.count():
		if winning(board, player):
			return player, i
		moves = get_moves(board, move)
		if not moves:
			return winning_draw(board, player), i
		player = - player
		board = apply_move(board, random.choice(moves), player)

def best_move(player):
	""" perform random plays for random moves until time is up,
	select move with best win/loss ratio
	"""
	moves = {move: 0 for move in valid_actions}
	start = time.time()
	
	total = 0
	for i in itertools.count():
		if time.time() - start > TIMEOUT:
			break
		move = random.choice(valid_actions)
		r, c = random_play(move, player)
		moves[move] += player * r
		total += c
	
	debug(i, total, moves)
	return max((moves[m], m) for m in moves)

def partial_copy(board, move):
	""" create partial copy of only the affected parts of the board
	about 10% slower... maybe with flat lists? should be ~5x faster
	"""
	R, C = move[0] // 3, move[1] // 3
	board = list(map(list, board))
	board[R][C] = list(map(list, board[R][C]))
	return board
	

def show_grid():
	""" draw a nice representation of the grid; mainly to check apply_move
	"""
	for r in range(9):
		if r in (3, 6):
			debug('-'.join("---+---+---"))
		line = ""
		for c in range(9):
			if c in (3, 6):
				line += "|"
			g = grid[r//3][c//3]
			x = g if type(g) == int else g[r%3][c%3]
			line += SYMBOL[x]
		debug(' '.join(line))


# INITIALIZATION
grid = [[[[NONE for _ in range(3)] for _ in range(3)]
				for _ in range(3)] for _ in range(3)]
valid_actions = []

def play_game():
	player, move = OPP, (-1, -1)
	while True:
		valid_actions[:] = get_moves(grid, move)
		if not valid_actions:
			return 0
		
		if 1 or player == OWN:
			score, move = best_move(player)
		else:
			score, move = 0, random.choice(valid_actions)
		
		debug("move: {}, score: {}".format(move, score))
		board = apply_move(grid, move, player)

		show_grid()
		print(*move)
		
		if winning(grid, player):
			return player
		player = -player

r = play_game()
print("Winner:", SYMBOL[r])
