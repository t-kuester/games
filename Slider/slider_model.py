"""
Slider Game, inspired by '2048', but with more options. Tobias Küster, 2019
Game model, incl. rules for applying moves, updating the field, scoring, etc.

TODO
- make application of moves more efficient (for AI random plays)
- wrap configuration into separate class or namedtuple
- problem when creating more than one but not enough space
"""

import random

WIDTH        = 4  # width and height of the playing field
CREATE_START = 2  # how many number to create when game starts
CREATE_TURN  = 1  # how many number to create in each turn
CREATE_MAX   = 2  # maximum number to create (as power of two)
PROB_MORE    = .1 # probability for increasing the new number
ALLOW_NOOP   = 1  # allow no-op / skip move?

# available moves; numbers mean MoveDir, Start, Delta
LEFT, RIGHT, UP, DOWN, SKIP = "LEFT RIGHT UP DOWN SKIP".split()
MOVES = {UP:    (( 0,+1), (0,0), (1,0)),
         DOWN:  (( 0,-1), (0,1), (1,0)),
         LEFT:  ((+1,+0), (0,0), (0,1)),
         RIGHT: ((-1,+0), (1,0), (0,1)),
         SKIP:  None}

class SliderGame:
    """ Class representing the current state of the slider game
    """
    
    def __init__(self):
        """ Create new instance and initialize fields. """
        self.turn = 0
        self.score = 0
        self.field = [[0 for _ in range(WIDTH)] for _ in range(WIDTH)]
        self.new = self.spawn(CREATE_START)
        self.merged = []
        
        self.valid_moves = self.valid_moves2
        self.update_field = self.update_field2
    
    def new_random(self):
        """ Create new random number; increase number with certain probability
        or until maximum value for new number is reached. """
        n = 1
        while n < CREATE_MAX and random.random() < PROB_MORE:
            n += 1
        return n
    
    def spawn(self, n):
        """ Randomly spawn certain amount of new numbers on empty cells. """
        self.new = random.sample(self.empty_cells(), n)
        for x,y in self.new:
            self.field[y][x] = self.new_random()
        return self.new
    
    def empty_cells(self):
        """ Get empty cells. """
        return [(x,y) for x in range(WIDTH) for y in range(WIDTH)
                if self.field[y][x] == 0]

    def is_game_over(self):
        """ Check whether game is over, i.e. no more valid moves. """
        return not self.valid_moves()

    def valid_moves(self):
        """ Helper method for testing/comparing different methods of getting
        valid moves. """
        v1 = self.valid_moves1()
        v2 = self.valid_moves2()
        if v1 != v2:
            print(v1, v2)
        return v2
    
    def valid_moves2(self):
        """ Get valid moves by checking in which direction cells can be shifted,
        but without actually applying those movements. """
        def _get_moves(lines, back, forth):
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
        moves |= _get_moves(     self.field,  LEFT, RIGHT)
        moves |= _get_moves(zip(*self.field), UP,   DOWN)
        if ALLOW_NOOP and sum(line.count(0) for line in self.field) >= CREATE_TURN:
            moves.add(SKIP)
        return sorted(moves)
    
    def valid_moves1(self):
        """ Get valid moves by trying to apply the different moves and seeing if
        anything changes; this is somewhat "safer", but much slower. """
        moves = set()
        for move in MOVES:
            if ALLOW_NOOP or move != SKIP:
                new_field = self.update_field(move)
                if new_field != self.field:
                    moves.add(move)
        return sorted(moves)
        
    def apply_move(self, move, check_valid=True):
        """ Apply the given move, update score, and spawn new cells. Optionally
        check whether the move is valid first. """
        if not check_valid or move in self.valid_moves():
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
        """ Helper method for testing/comparing different methods of updating
        the playing field. """
        ref = self.update_field1(move)
        res = self.update_field2(move)
        if ref != res:
            print(move, self.field)
        return res

    def update_field1(self, move):
        """ Update the field by "compressing" the different rows or columns of
        the field. This is somewhat simpler, but is not in-place, is a bit slower,
        and more difficult (and currently not implemented) to get the positions
        of merged cells. """
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
        """ Update the field in-place by iterating all the different rows and
        columns using the tuples from the MOVES dict. This is a (small) bit faster,
        and it is easier to keep track of positions of merged cells. """
        # XXX IN-PLACE OR NOT?
        res = self.field
        #~res = list(map(list, self.field))
        
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
                        self.merged.append((wx, wy))
                        #~self.merged.append(last + 1)
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
        """ Compress a single row of column; this is not in-place but creates
        and returns a new list. """
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
        """ Calculate score from list of merged cells. Score is sum of powers of
        two of the values in those cells. """
        #~return sum(2**m for m in self.merged)
        return sum(2**self.field[y][x] for (x,y) in self.merged)
    
    def show(self):
        """ Show the current state of the field in a somewhat readable way. """
        print("SCORE", self.score)
        for line in self.field:
            print(*("%2d" % c for c in line))


def main():
    """ Very simple way of playing the game on console; for testing, but now
    entirely obsolete. """
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
