# TODO
# proper monte carlo tree search
# fast method for board copying (maybe try flat board again?)
# MCTS "lite"? create game tree, descent and update game tree in each turn

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
	for i in itertools.count():
		if winning(board, player):
			return player, i
		moves = get_moves(board, move)
		if not moves:
			return winning_draw(board, player), i
		player = -player
		board = apply_move(board, random.choice(moves), player)

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
		r, c = random_play(board, move, player)
		scores[move] += player * r
		total += c
	
	debug(i, total, scores)
	return max((scores[m], m) for m in moves)

def best_move(board, moves, player):
	""" return winning move, or best non-losing move, if any
	"""
	win_move = winning_move(board, moves, player)
	non_lose = non_losing_moves(board, moves, player)
	if win_move:
		return 999, win_move
	elif non_lose:
		return best_move_random_plays(board, non_lose, player)
	else:
		return best_move_random_plays(board, moves, player)


# INITIALIZATION

def play_game():
	board = [[NONE for _ in range(9)] for _ in range(9)]
	player, move = random.choice([OWN, OPP]), (-1, -1)
	for i in itertools.count():
		moves = get_moves(board, move)
		if not moves:
			return winning_draw(board, player)

		score, move = best_move(board, moves, player)
		
		debug("{} move: {}, score: {}".format(i, move, score))
		board = apply_move(board, move, player)

		show_grid(board)
		
		if winning(board, player):
			return player
		player = -player

seed = random.randrange(1000000)
random.seed(seed)
TIMEOUT = 0.5
results = {+1: 0, 0: 0, -1: 0}
for i in range(100):
	r = play_game()
	results[r] += 1
	print(i, r, results)
	break
print(results)
print(seed)

# WHY ARE RESULTS STILL BIASED TOWARDS PLAYER +1 ?
# {0: 17, 1: 52, -1: 31} best move random play vs. best move random play
# {0: 6, 1: 54, -1: 40} BMRP vs BMRP + winning-draw
# {0: 3, 1: 42, -1: 55} BMRP vs. BM + winning move
# {0: 14, 1: 55, -1: 31} BM + winning move vs BMRP
# {0: 8, 1: 66, -1: 26} BM + winning + non-losing vs BMRP
# {0: 5, 1: 30, -1: 65} BMRP vs BM + winning + non-losing
