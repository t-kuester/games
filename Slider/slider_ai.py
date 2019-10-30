import slider_model

import time, random

TIMEOUT = 0.1


def random_play(game):
    first = random.choice(list(game.valid_moves()))
    game.apply_move(first)
    moves = [first]
    valid = list(game.valid_moves())
    while valid:
        m = random.choice(valid)
        game.apply_move(m)
        moves.append(m)
        valid = list(game.valid_moves())
    return game.score, moves


game = slider_model.SliderGame()
while list(game.valid_moves()):
    
    start = time.time()
    
    scores = {m: 0 for m in game.valid_moves()}
    
    while time.time() < start + TIMEOUT:
        
        copy = slider_model.SliderGame()
        copy.field = list(map(list, game.field))
        score, moves = random_play(copy)
        scores[moves[0]] += score
    
    move = max(scores, key=scores.get)
    
    print(score, move)
    
    game.apply_move(move)
    
    game.show()
        
    
    






