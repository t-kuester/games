"""
TODO
make application of moves more efficient (for AI random plays)
documentation
wrap configuration into separate class or namedtuple
problem when creating more than one but not enough space
for some reason, the non-in-place update_field method is still a bit faster...
"""

import random
import itertools

WIDTH        = 4
CREATE_START = 2
CREATE_TURN  = 1
CREATE_MAX   = 2
PROB_MORE    = 0.1
ALLOW_NOOP   =  False

LEFT, RIGHT, UP, DOWN, SKIP = "LEFT RIGHT UP DOWN SKIP".split()

#        Name    MoveDir  Start  Delta
MOVES = {UP:    (( 0,+1), (0,0), (1,0)),
         DOWN:  (( 0,-1), (0,1), (1,0)),
         LEFT:  ((+1,+0), (0,0), (0,1)),
         RIGHT: ((-1,+0), (1,0), (0,1)),
         SKIP:  None}


class SliderGame:
    
    def __init__(self):
        self.turn = 0
        self.score = 0
        self.field = [[0 for _ in range(WIDTH)] for _ in range(WIDTH)]
        self.new = self.spawn(CREATE_START)
        self.merged = []
        
        self.valid_moves = self.valid_moves
        self.update_field = self.update_field
    
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
        def get_moves(lines, back, forth):
            moves = set()
            for line in lines:
                if any(a == b != 0 for a, b in zip(line, line[1::])):
                    return {back, forth}
                zeros     = [i for i, e in enumerate(line) if e == 0]
                non_zeros = [i for i, e in enumerate(line) if e != 0]
                if zeros and non_zeros:
                    if zeros[ 0] < non_zeros[-1]:
                        moves.add(back)
                    if zeros[-1] > non_zeros[ 0]:
                        moves.add(forth)
                if len(moves) == 2:
                    break
            return moves

        moves = set()
        moves |= get_moves(     self.field,  LEFT, RIGHT)
        moves |= get_moves(zip(*self.field), UP,   DOWN)
        if ALLOW_NOOP and sum(line.count(0) for line in self.field) >= CREATE_TURN:
            moves.add(SKIP)
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
            self.merged = []
            self.field = self.update_field(move)
            self.spawn(CREATE_TURN)
            score = self.calculate_score()
            self.score += score
            return score
        else:
            print("INVALID MOVE")

    def update_field(self, move):
        ref = self.update_field1(move)
        res = self.update_field2(move)
        if ref != res:
            print(move, self.field)
        return res

    def update_field1(self, move):
        if   move == UP:
            return list(map(list, zip(*[self._compress(line) for line in zip(*self.field)])))
        elif move == DOWN:
            return list(map(list, zip(*[self._compress(line) for line in zip(*self.field[::-1])])))[::-1]
        elif move == LEFT:
            return [self._compress(line) for line in self.field]
        elif move == RIGHT:
            return [self._compress(line[::-1])[::-1] for line in self.field]
        elif move == SKIP:
            return list(map(list, self.field))
        else:
            print("unknown move", move)

    def update_field2(self, move):
        # XXX IN-PLACE OR NOT?
        res = self.field
        res = list(map(list, self.field))
        
        if move == SKIP: return res
        (mx,my),(sx,sy),(dx,dy) = MOVES[move]
        
        for i in range(WIDTH):
            px = (WIDTH-1) * sx + i * dx
            py = (WIDTH-1) * sy + i * dy
            
            last = w = 0
            for r in range(WIDTH):
                cur = res[py + my * r][px + mx * r]
                if cur != 0:
                    wx, wy = px + mx * w, py + my * w
                    if cur == last:
                        res[wy][wx] = last + 1
                        #~self.merged.append((wx, wy))
                        self.merged.append(last + 1)
                        cur = None
                        w += 1
                    elif last:
                        res[wy][wx] = last
                        w += 1
                    last = cur
            for w in range(w, WIDTH):
                res[py + my * w][px + mx * w] = last or 0
                last = 0
        return res

    def _compress(self, line):
        res = []
        last = None
        for c in filter(None, line):
            if c == last:
                res.append(c+1)
                self.merged.append(c+1)
                last = None
            else:
                if last is not None:
                    res.append(last)
                last = c
        while len(res) < WIDTH:
            res.append(last or 0)
            last = 0
        return res

    def calculate_score(self):
        return sum(2**m for m in self.merged)
        #~return sum(2**self.field[y][x] for (x,y) in self.merged)
    
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
