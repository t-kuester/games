# TODO
# proper monte carlo tree search

import sys, functools, random, time, copy, itertools


debug = functools.partial(print, file=sys.stderr)
rows = range(3) # yes, this does makes a difference!

SYMBOL = [".", "X", "#", "O"]
NONE, OWN, OPP, DRAW = 0, 1, -1, 2


# BASIC BOARD HANDLING
# how to represent and manipulate the board, to be used by all stragegies

def get_moves(board, last):
	""" get valid moves given board and last move
	"""
	R, C = last[0] % 3, last[1] % 3
	playable_fields = [(R,C)] if last != (-1, -1) and type(board[R*3+C]) == list else \
			((r,c) for r in rows for c in rows if type(board[r*3+c]) == list)
	return [(3*R+r, 3*C+c) for (R,C) in playable_fields
			for r in rows for c in rows if board[R*3+C][r*3+c] == NONE]

def winning_draw(board, player):
	""" In case of no line, player with more smaller boards wins
	"""
	own = sum(1 for c in board if c == +player)
	opp = sum(1 for c in board if c == -player)
	return player if (own > opp) else (-player if opp > own else 0)

def winning(board, player):
	""" check whether player has won the board, works for sub- or for meta board
	"""
	return (any(all(board[r*3+c] == player for c in rows) for r in rows)
		 or any(all(board[r*3+c] == player for r in rows) for c in rows)
		 or all(board[i*3+   i]  == player for i in rows)
		 or all(board[i*3+2-i]  == player for i in rows))

def apply_move(board, move, player):
	""" apply move; if player won smaller board, update meta board
	"""
	R, C = move[0] // 3, move[1] // 3
	r, c = move[0] % 3, move[1] % 3
	board = list(board)
	board[R*3+C] = list(board[R*3+C])
	subgrid = board[R*3+C]
	
	subgrid[r*3+c] = player
	if winning(subgrid, player):
		board[R*3+C] = player
	elif not NONE in subgrid:
		board[R*3+C] = DRAW
	return board
	
def show_grid(board):
	""" draw a nice representation of the grid; mainly to check apply_move
	"""
	for r in range(9):
		if r in (3, 6):
			debug('-'.join("---+---+---"))
		line = ""
		for c in range(9):
			if c in (3, 6):
				line += "|"
			g = board[(r//3)*3+(c//3)]
			x = g if type(g) == int else g[(r%3)*3+(c%3)]
			line += SYMBOL[x]
		debug(' '.join(line))


# STRATEGY
# stuff related to which moves to take, independent of board data structure

def winning_move(board, moves, player):
	""" get move that leads to immediate victory, if any, or None
	"""
	return next((m for m in moves if winning(apply_move(board, m, player), player)), None)

def non_losing_moves(board, moves, player):
	""" get moves that do not lead to victory of other player in next turn
	"""
	return [m for m, nb in ((m, apply_move(board, m, player)) for m in moves)
	        if not winning_move(nb, get_moves(nb, m), -player)]

def random_play(board, move, player):
	""" perform random moves until the game is over,
	return winning player and number of moves
	"""
	board = apply_move(board, move, player)
	seq = [move]
	for i in itertools.count():
		if winning(board, player):
			return player, i, seq
		moves = get_moves(board, move)
		if not moves:
			return winning_draw(board, player), i, seq
		player = -player
		move = random.choice(moves)
		board = apply_move(board, move, player)
		seq.append(move)

def best_move_random_plays(board, moves, player):
	""" perform random plays for random moves until time is up,
	select move with best win/loss ratio
	"""
	scores = {move: 0 for move in moves}
	start = time.time()
	total = 0
	for i in itertools.count():
		if time.time() - start > TIMEOUT:
			break
		move = random.choice(moves)
		r, c, seq = random_play(board, move, player)
		scores[move] += r
		total += c
	
	debug(i, total)#, scores)
	return max((player * scores[m], m) for m in moves)


def best_move_random_plays_game_tree(board, moves, player):
	# idea: keep score about all later states in random plays for later rounds
	# slowdown of about 10% in terms of played turns
	# number of games actually kept for next turn is almost nonexisting...
	# no measurable effect (if anything, it might be worse)
	
	start = time.time()
	total = 0

	for i in itertools.count():
		if time.time() - start > TIMEOUT:
			break
		
		move = random.choice(moves)
		r, c, seq = random_play(board, move, player)

		# random play gibt ID des gewinners zurück, also -1 für OPP
		# game tree enthält dann auch jeweils den gewinner dieses zuges
		# wie bei normalem best-move-random-play bei max mit player multiplizieren

		t = game_tree
		for m in seq:
			if m not in t:
				t[m] = [0, 0, {}]
			t[m][0] += r # victory ratio
			t[m][1] += 1 # number of games played
			t = t[m][2] # descend into child tree
		
		total += c
	
	diff = sum(v[1] for v in game_tree.values()) - i
	debug(i, total, diff)
	return max((player * game_tree[m][0] if m in game_tree else 0, m) for m in moves)



def best_move(board, moves, player):
	""" return winning move, or best non-losing move, if any
	"""
	bmf = best_move_random_plays if player == OWN else best_move_random_plays_game_tree
	
	win_move = winning_move(board, moves, player)
	non_lose = non_losing_moves(board, moves, player)
	if win_move:
		return 999, win_move
	elif non_lose:
		return bmf(board, non_lose, player)
	else:
		return bmf(board, moves, player)


# INITIALIZATION

def play_game():
	
	global game_tree
	game_tree = {}
	
	board = [[NONE for _ in range(9)] for _ in range(9)]
	player, move = random.choice([OWN, OPP]), (-1, -1)
	for i in itertools.count():
		moves = get_moves(board, move)
		if not moves:
			return winning_draw(board, player)

		score, move = best_move(board, moves, player)
		
		game_tree = game_tree[move][2] if move in game_tree else {}
		
		#~debug("{} move: {}, score: {}".format(i, move, score))
		board = apply_move(board, move, player)

		#~show_grid(board)
		#~input()
		
		if winning(board, player):
			return player
		player = -player

seed = random.randrange(1000000)
random.seed(seed)
TIMEOUT = 0.1
results = {+1: 0, 0: 0, -1: 0}
for i in range(100):
	r = play_game()
	results[r] += 1
	print(i, r, results)
	#~break
print(results)
print(seed)
