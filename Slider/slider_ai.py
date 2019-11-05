""" TODO
- valid moves takes most time (by far) --> make it faster
"""

import slider_model
import time, random

def random_play(game):
    first = random.choice(game.valid_moves())
    game.apply_move(first)
    moves = [first]
    valid = game.valid_moves()
    while valid:
        m = random.choice(valid)
        game.apply_move(m)
        moves.append(m)
        valid = game.valid_moves()
    return game.score, moves

random.seed(0)
NUM_GAMES = 10
game = slider_model.SliderGame()
k = 0
while game.valid_moves():
    k += 1
    start = time.time()
    scores = {m: 0 for m in game.valid_moves()}
    
    for i in range(NUM_GAMES):
        copy = slider_model.SliderGame()
        copy.field = list(map(list, game.field))
        score, moves = random_play(copy)
        scores[moves[0]] += score
            
    move = max(scores, key=scores.get)
    print(k, move, score, time.time() - start)
    game.apply_move(move)
    game.show()
    
    if k > 10:
        break

