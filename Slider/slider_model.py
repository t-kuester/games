import random

"""
TODO
get valid moves
make application of moves more efficient (for AI random plays)
documentation
check game over (simply try-except?)
improve key-handling for testing in terminal
keep track of merged cells and calculate score
"""

WIDTH      = 4
CREATE_NUM = 1
CREATE_MAX = 1
ALLOW_NOOP = True

LEFT, RIGHT, UP, DOWN = "LEFT RIGHT UP DOWN".split()

class SliderGame:
    
    def __init__(self):
        self.score = 0
        self.field = [[0 for _ in range(WIDTH)] for _ in range(WIDTH)]
        self.spawn(CREATE_NUM)
    
    def spawn(self, n):
        new_cells = random.sample(self.empty_cells(), n)
        for x,y in new_cells:
            self.field[y][x] = random.randint(1, CREATE_MAX)
        return new_cells
    
    def empty_cells(self):
        return [(x,y) for x in range(WIDTH) for y in range(WIDTH)
                if self.field[y][x] == 0]
    
    def valid_moves(self):
        # test which moves alter the field
        pass
        
    def apply_move(self, move):
        if   move == UP:
            self.field = list(map(list, zip(*[self.compress(line) for line in zip(*self.field)])))
        elif move == DOWN:
            self.field = list(map(list, zip(*[self.compress(line) for line in zip(*self.field[::-1])])))[::-1]
        elif move == LEFT:
            self.field = [self.compress(line) for line in self.field]
        elif move == RIGHT:
            self.field = [self.compress(line[::-1])[::-1] for line in self.field]
        else:
            print("UNKNOWN MOVE:", move)
        
        self.spawn(CREATE_NUM)

    def compress(self, line):
        i, j, k = 0, 0, 1
        line=list(line)
        while True:
            while i < len(line) and line[i] == 0: i += 1
            while k < len(line) and (line[k] == 0 or k <= i): k += 1
            if i >= len(line):
                break
            if k < len(line) and line[i] == line[k]:
                line[j] = line[i] + 1
                i, k, j = k+1, k+2, j+1
            else:
                line[j] = line[i]
                i, k, j = k, k+1, j+1
        for i in range(j, len(line)):
            line[i] = 0
        return line    
    
    
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
                skip = True
            else:
                res.append(c)
        while len(res) < WIDTH:
            res.append(0)
        return res
    
    def calculate_score(self):
        pass
    
    def show(self):
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
