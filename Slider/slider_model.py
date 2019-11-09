"""
TODO
make application of moves more efficient (for AI random plays)
documentation
wrap configuration into separate class or namedtuple
problem when creating more than one but not enough space
code cleanup, remove old, slower methods
"""

import random
import itertools
import collections

WIDTH        = 4
CREATE_START = 2
CREATE_TURN  = 1
CREATE_MAX   = 2
PROB_MORE    = 0.1
ALLOW_NOOP   =  False

LEFT, RIGHT, UP, DOWN, SKIP = "LEFT RIGHT UP DOWN SKIP".split()

Move = collections.namedtuple("Move", "mdir start delta")
P    = collections.namedtuple("P",    "x y")

MOVES = {UP:    Move(P( 0,+1), P(0,+0), P(1,+0)),
         DOWN:  Move(P( 0,-1), P(0,+1), P(1,+0)),
         LEFT:  Move(P(+1,+0), P(0,+0), P(0,+1)),
         RIGHT: Move(P(-1,+0), P(1,+0), P(0,+1)),
         SKIP:  None}

MOVES2 = {UP:    (( 0,+1), (0,+0), (1,+0)),
         DOWN:  (( 0,-1), (0,+1), (1,+0)),
         LEFT:  ((+1,+0), (0,+0), (0,+1)),
         RIGHT: ((-1,+0), (1,+0), (0,+1)),
         SKIP:  None}


class SliderGame:
    
    def __init__(self):
        self.turn = 0
        self.score = 0
        self.field = [[0 for _ in range(WIDTH)] for _ in range(WIDTH)]
        self.new = self.spawn(CREATE_START)
        self.merged = []
        
        self.compress = self.compress4
        self.update_field = self.update_field2
        self.valid_moves = self.valid_moves
    
    def new_random(self):
        n = 1
        while n < CREATE_MAX and random.random() < PROB_MORE:
            n += 1
        return n
    
    def spawn(self, n):
        self.new = random.sample(self.empty_cells(), n)
        for x,y in self.new:
            self.field[y][x] = self.new_random()
        return self.new
    
    def empty_cells(self):
        return [(x,y) for x in range(WIDTH) for y in range(WIDTH)
                if self.field[y][x] == 0]

    def is_game_over(self):
        return not self.valid_moves()

    def valid_moves(self):
        v1 = self.valid_moves1()
        v2 = self.valid_moves2()
        if v1 != v2:
            print(v1, v2)
        return v2
    
    def valid_moves2(self):
        moves = set()
        if ALLOW_NOOP and sum(line.count(0) for line in self.field) >= CREATE_TURN:
            moves.add(SKIP)

        # TODO generalize to one parameterized function
        for line in self.field:
            if any(line[i-1] == line[i] != 0 for i in range(1, len(line))):
                moves.add(RIGHT)
                moves.add(LEFT)
            else:
                zeros = [i for i, e in enumerate(line) if e == 0]
                if zeros:
                    if any(e != 0 for i, e in enumerate(line) if i < zeros[-1]):
                        moves.add(RIGHT)
                    if any(e != 0 for i, e in enumerate(line) if i > zeros[0]):
                        moves.add(LEFT)
                
        for line in zip(*self.field):
            if any(line[i-1] == line[i] != 0 for i in range(1, len(line))):
                moves.add(DOWN)
                moves.add(UP)
            else:
                zeros = [i for i, e in enumerate(line) if e == 0]
                if zeros:
                    if any(e != 0 for i, e in enumerate(line) if i < zeros[-1]):
                        moves.add(DOWN)
                    if any(e != 0 for i, e in enumerate(line) if i > zeros[0]):
                        moves.add(UP)

        return sorted(moves)
    
    def valid_moves1(self):
        moves = set()
        for move in MOVES:
            if ALLOW_NOOP or move != SKIP:
                new_field = self.update_field(move)
                if new_field != self.field:
                    moves.add(move)
        return sorted(moves)
        
    def apply_move(self, move):
        if move in self.valid_moves():
            self.turn += 1
            
            #~ref = self.update_field1(move)
            #~res = self.update_field2(move)
            #~if ref != res:
                #~print(move, self.field)
                
            self.merged = []
            self.field = self.update_field(move)
            
            self.spawn(CREATE_TURN)
            score = self.calculate_score()
            self.score += score
            return score
        else:
            print("INVALID MOVE")

    def update_field1(self, move):
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

    def update_field2(self, move):
        res = self.field
        # XXX FOR NOW, NOT IN-PLACE
        res = list(map(list, self.field))
        
        if move == SKIP: return res
        m = MOVES[move]
        
        for i in range(WIDTH):
            px = (WIDTH-1) * m.start.x + i * m.delta.x
            py = (WIDTH-1) * m.start.y + i * m.delta.y
            
            last = None
            w = 0
            for r in range(WIDTH):
                cur = res[py + m.mdir.y * r][px + m.mdir.x * r]
                if cur != 0:
                    wx, wy = px + m.mdir.x * w, py + m.mdir.y * w
                    if cur == last:
                        res[wy][wx] = last + 1
                        self.merged.append((wx, wy))
                        cur = None
                        w += 1
                    elif last is not None:
                        res[wy][wx] = last
                        w += 1
                    last = cur
            for w in range(w, WIDTH):
                res[py + m.mdir.y * w][px + m.mdir.x * w] = last or 0
                last = 0
                    
        return res
        
        
    def update_field3(self, move):
        res = self.field
        # XXX FOR NOW, NOT IN-PLACE
        #~res = list(map(list, self.field))
        
        if move == SKIP: return res
        (mx,my),(sx,sy),(dx,dy) = MOVES2[move]
        
        for i in range(WIDTH):
            px = (WIDTH-1) * sx + i * dx
            py = (WIDTH-1) * sy + i * dy
            
            last = None
            w = 0
            for r in range(WIDTH):
                cur = res[py + my * r][px + mx * r]
                if cur != 0:
                    wx, wy = px + mx * w, py + my * w
                    if cur == last:
                        res[wy][wx] = last + 1
                        self.merged.append((wx, wy))
                        cur = None
                        w += 1
                    elif last is not None:
                        res[wy][wx] = last
                        w += 1
                    last = cur
            for w in range(w, WIDTH):
                res[py + my * w][px + mx * w] = last or 0
                last = 0
                    
        return res

    def compress4(self, line):
        res = []
        last = None
        for c in line:
            if c == 0: continue
            if c == last:
                res.append(c+1)
                self.merged.append(c+1)
                last = None
            else:
                if last is not None:
                    res.append(last)
                last = c
        if last is not None:
            res.append(last)
        while len(res) < WIDTH:
            res.append(0)
        return res

    def compress2(self, line):
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
    
    def compress3(self, line):
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
    
    def compress1(self, line):
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
        #~return sum(2**m for m in self.merged)
        return sum(2**self.field[y][x] for (x,y) in self.merged)
    
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
