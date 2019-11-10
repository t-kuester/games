"""
Slider Game, inspired by '2048', but with more options. Tobias Küster, 2019
Simple AI for playing the slider game.

TODO
- valid moves takes most time (by far) --> make it faster
- try some heuristic, e.g. minimum difference between adjacent cells
"""

import slider_model
import time, random

def random_play(game):
    """ Perform one random playout, chosing valid moves until game over; return
    final score and first move. """
    first = random.choice(game.valid_moves())
    game.apply_move(first, False)
    moves = [first]
    valid = game.valid_moves()
    while valid:
        m = random.choice(valid)
        game.apply_move(m, False)
        moves.append(m)
        valid = game.valid_moves()
    return game.score, moves

def best_move_random_plays(game, num_plays):
    """ Perform a certain number of random plays and then return the move that
    yielded the highest score over all those plays. """
    scores = {m: 0 for m in game.valid_moves()}
    for i in range(num_plays):
        copy = slider_model.SliderGame()
        copy.field = list(map(list, game.field))
        score, moves = random_play(copy)
        scores[moves[0]] += score
    return max(scores, key=scores.get)

def adjacent_diff(game):
    """ Heuristic function, returning sum of differences (squared) of adjacent
    cells in the field. """
    def h(line):
        return sum(2**abs(a-b) for a,b in zip(line, line[1::]) if a and b)
    return sum(map(h, game.field)) + sum(map(h, zip(*game.field)))

def best_move_heuristic(game, h):
    """ Deterministically select best move using given heuristic function. """
    heur = {}
    for move in game.valid_moves():
        copy = slider_model.SliderGame()
        copy.field = list(map(list, game.field))
        copy.apply_move(move, False)
        heur[move] = h(copy)
    return max(heur, key=heur.get)


random.seed(0)
NUM_GAMES = 20
MAX_TURNS = 1000
game = slider_model.SliderGame()
k = 0
START = time.time()
while k < MAX_TURNS and game.valid_moves():
    k += 1
    start = time.time()
    move = best_move_random_plays(game, NUM_GAMES)
    #~move = best_move_heuristic(game, adjacent_diff)
    print(k, move, time.time() - start)
    game.apply_move(move)
    game.show()
    
print(game.score, time.time() - START)
