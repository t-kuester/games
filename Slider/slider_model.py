"""
TODO
make application of moves more efficient (for AI random plays)
documentation
check game over (simply try-except?)
10% for 4, 1% for 8, etc.
"""

import random
import itertools

WIDTH        = 4
CREATE_START = 2
CREATE_TURN  = 1
CREATE_MAX   = 2
PROB_MORE    = 0.1
ALLOW_NOOP   =  False

MOVES = LEFT, RIGHT, UP, DOWN, SKIP = "LEFT RIGHT UP DOWN SKIP".split()


class SliderGame:
    
    def __init__(self):
        self.turn = 0
        self.score = 0
        self.field = [[0 for _ in range(WIDTH)] for _ in range(WIDTH)]
        self.new = self.spawn(CREATE_START)
        self.merged = []
    
    def new_random(self):
        n = 1
        while n < CREATE_MAX and random.random() < PROB_MORE:
            n += 1
        return n
    
    def spawn(self, n):
        new_cells = random.sample(self.empty_cells(), n)
        for x,y in new_cells:
            self.field[y][x] = self.new_random()
        return new_cells
    
    def empty_cells(self):
        return [(x,y) for x in range(WIDTH) for y in range(WIDTH)
                if self.field[y][x] == 0]
    
    def valid_moves(self):
        moves = set()
        if ALLOW_NOOP:
            moves.add(SKIP)

        #~for line in self.field:
            #~for i in range(1, len(line)):
                #~if line[i-1] == line[i]:
                    #~moves.add(LEFT)
                    #~moves.add(RIGHT)
            #~if any(line[i] == 0 for i in range(1, len(line))):
                #~moves.add(RIGHT)
            #~if any(line[i] == 0 for i in range(len(line)-1)):
                #~moves.add(LEFT)
                #~
        #~for line in zip(*self.field):
            #~for i in range(1, len(line)):
                #~if line[i-1] == line[i]:
                    #~moves.add(UP)
                    #~moves.add(DOWN)
            #~if any(line[i] == 0 for i in range(1, len(line))):
                #~moves.add(DOWN)
            #~if any(line[i] == 0 for i in range(len(line)-1)):
                #~moves.add(UP)

        for move in MOVES:
            new_field = self.update_field(move)
            if new_field != self.field:
                moves.add(move)
                
        return list(moves)
        
    def apply_move(self, move):
        if move in self.valid_moves():
            self.turn += 1
            self.merged = []
            self.field = self.update_field(move)
            self.spawn(CREATE_TURN)
            score = self.calculate_score()
            self.score += score
            return score
        else:
            print("INVALID MOVE")

    def update_field(self, move):
        if   move == UP:
            return list(map(list, zip(*[self.compress(line) for line in zip(*self.field)])))
        elif move == DOWN:
            return list(map(list, zip(*[self.compress(line) for line in zip(*self.field[::-1])])))[::-1]
        elif move == LEFT:
            return [self.compress(line) for line in self.field]
        elif move == RIGHT:
            return [self.compress(line[::-1])[::-1] for line in self.field]
        elif move == SKIP:
            return list(map(list, self.field))
        else:
            print("unknown move", move)

    def compress_new(self, line):
        i, j, k = 0, 0, 1
        line = list(line)
        n = len(line)
        while True:
            while i < n and  line[i] == 0:            i += 1
            while k < n and (line[k] == 0 or k <= i): k += 1
            if i >= n:
                break
            if k < n and line[i] == line[k]:
                line[j] = line[i] + 1
                self.merged.append(line[j])
                i, k, j = k+1, k+2, j+1
            else:
                line[j] = line[i]
                i, k, j = k, k+1, j+1
        for i in range(j, n):
            line[i] = 0
        return line    
    
    def compress(self, line):
        res = []
        for k, grp in itertools.groupby(filter(None, line)):
            for x in grp:
                try:
                    next(grp)
                    res.append(k+1)
                    self.merged.append(k+1)
                except:
                    res.append(x)
        while len(res) < WIDTH:
            res.append(0)
        return res
    
    def compress_old(self, line):
        res = []
        skip = False
        line = [c for c in line if c != 0]
        for i, c in enumerate(line):
            if skip:
                skip = False
                continue
            if i < len(line) - 1 and line[i+1] == c:
                res.append(c+1)
                self.merged.append(c+1)
                skip = True
            else:
                res.append(c)
        while len(res) < WIDTH:
            res.append(0)
        return res
    
    def calculate_score(self):
        return sum(2**m for m in self.merged)
    
    def show(self):
        print("SCORE", self.score)
        for line in self.field:
            print(*("%2d" % c for c in line))


def main():
    game = SliderGame()
    game.show()
    while True:
        print()
        moves = {"u": UP, "d": DOWN, "l": LEFT, "r": RIGHT}
        m = input().lower()[:1]
        game.apply_move(moves.get(m))
        game.show()

if __name__ == "__main__":
    main()
