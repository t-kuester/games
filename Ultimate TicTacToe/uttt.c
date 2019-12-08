#include <stdio.h>
#include <stdlib.h>
#include <time.h>


const int NONE = 0, OWN = 1, OPP = -1, DRAW = 2;
const char SYMBOLS[] = {'.', 'X', '#', 'O'};

/*
 * BOARD REPRESENTATION AND MANIPULATION
 */

struct board {
    int meta[9];
    int field[9][9];
};

int idx_meta(int move) {
    return ((move / 9) / 3) * 3 + ((move % 9) / 3);
}

int idx_inner(int move) {
    return ((move / 9) % 3) * 3 + ((move % 9) % 3);
}

int contains(int field[], int size, int symbol) {
    int i;
    for (i = 0; i < size; i++) {
        if (field[i] == symbol) return 1;
    }
    return 0;
}

struct board* init_board() {
    struct board *b = malloc(sizeof (struct board));
    int i, k;
    for (i = 0; i < 9; i++) {
        b->meta[i] = 0;
        for (k = 0; k < 9; k++) {
            b->field[i][k] = 0; // i*9+k;
        }
    }
    return b;
}

void copy(struct board *from, struct board *to) {
    // TODO use proper stringcopy function
    int i, k;
    for (i = 0; i < 9; i++) {
        to->meta[i] = from->meta[i];
        for (k = 0; k < 9; k++) {
            to->field[i][k] = from->field[i][k];
        }
    }
}

void get_moves(struct board *b, int last, int moves[]) {
    int active_field = ((last / 9) % 3) * 3 + ((last % 9) % 3);
    int any_field = last == -1 || b->meta[active_field] != NONE;
    
    int i;
    for (i = 0; i < 81; i++) {
        int index_meta = idx_meta(i);
        int index_inner = idx_inner(i);
        int is_free = b->field[index_meta][index_inner] == NONE;
        int can_play = (index_meta == active_field) || any_field;
        moves[i] = is_free && can_play;
    }
}

int winning_draw(int field[], int player) {
    return 0;
	//~""" In case of no line, player with more smaller boards wins
	//~"""
	//~own = sum(1 for c in board if c == +player)
	//~opp = sum(1 for c in board if c == -player)
	//~return player if (own > opp) else (-player if opp > own else 0)    
}

int winning(int field[], int player) {
    return 0;
	//~""" check whether player has won the board, works for sub- or for meta board
	//~"""
    //~return (any(all(board[r*3+c] == player for c in rows) for r in rows)
     //~or any(all(board[r*3+c] == player for r in rows) for c in rows)
     //~or all(board[i*3+   i]  == player for i in rows)
     //~or all(board[i*3+2-i]  == player for i in rows))
}

void apply_move(struct board *b, int move, int player) {
    int index_meta = idx_meta(move);
    int index_inner = idx_inner(move);
    
    b->field[index_meta][index_inner] = player;
    
    if (winning(b->field[index_meta], player)) {
        b->meta[index_meta] = player;
    } else if (! contains(b->field[index_meta], 9, NONE)) {
        b->meta[index_meta] = DRAW;
    }
}

void show_grid(struct board *b) {
    int i;
    for (i = 0; i < 81; i++) {
        int row = i / 9, col = i % 9;
        if ((row == 3 || row == 6) && col == 0) {
            printf("- - - + - - - + - - -\n");
        }
        if ( col == 3 || col == 6) {
            printf("| ");
        }
        
        int index_meta = idx_meta(i);
        int index_inner = idx_inner(i);
        int v_meta = b->meta[index_meta];
        int v_field = b->field[index_meta][index_inner];
        int v = v_meta != NONE ? v_meta : v_field;
        char sym = SYMBOLS[(v + 4) % 4];
        printf("%c ", sym);
        //~printf("%d ", v_field);
            
        if ((col+1) % 9 == 0) {
            printf("\n");
        }
    }
    printf("\n");
}

void show_moves(int moves[]) {
    int i;
    for (i = 0; i < 81; i++) {
        if (moves[i]) {
            printf("%d ", i);
        }
    }
    printf("\n");
}

/*
 * STRATEGY
 * stuff related to which moves to take, independent of board data structure
 */

int is_winning_move(struct board *b, int move, int player) {
    return 0;
	//~""" get move that leads to immediate victory, if any, or None
	//~"""
	//~return next((m for m in moves if winning(apply_move(board, m, player), player)), None)
}

int is_non_losing_move(struct board *b, int move, int player) {
    return 0;
	//~""" get moves that do not lead to victory of other player in next turn
	//~"""
	//~return [m for m, nb in ((m, apply_move(board, m, player)) for m in moves)
	        //~if not winning_move(nb, get_moves(nb, m), -player)]
}

int random_play(struct board *b, int move, int player) {
    return 0;
	//~""" perform random moves until the game is over,
	//~return winning player and number of moves
	//~"""
	//~board = apply_move(board, move, player)
	//~for i in itertools.count():
		//~if winning(board, player):
			//~return player, i
		//~moves = get_moves(board, move)
		//~if not moves:
			//~return winning_draw(board, player), i
		//~player = -player
		//~move = random.choice(moves)
		//~board = apply_move(board, move, player)
}

void evaluate_moves(struct board *b, int moves[], int player, int scores[], int timeout) {
	//~""" perform random plays for random moves until time is up,
	//~"""
	//~scores = {move: 0 for move in moves}
	//~start = time.time()
	//~total = 0
	//~for i in itertools.count():
		//~if time.time() - start > timeout:
			//~break
		//~move = random.choice(moves)
		//~r, c = random_play(board, move, player)
		//~scores[move] += player * r
		//~total += c
	//~debug(i, total, scores)
	//~return scores
}

int best_move_random_plays(struct board *b, int moves[], int player) {
    return 0;
	//~""" select move with best win/loss ratio
	//~"""
	//~scores = evaluate_moves(board, moves, player, TIMEOUT)
	//~return max((scores[m], m) for m in moves)
}

int best_move(struct board *b, int moves[], int player) {
    return best_move_random_plays(b, moves, player);
	//~""" return winning move, or best non-losing move, if any
	//~"""
	//~win_move = winning_move(board, moves, player)
	//~non_lose = non_losing_moves(board, moves, player)
	//~if win_move:
		//~return 999, win_move
	//~elif non_lose:
		//~return best_move_random_plays(board, non_lose, player)
	//~else:
		//~return best_move_random_plays(board, moves, player)
}


/*
 * TESTING AND PERFORMANCE
 */

int play_game() {
    return 0;
	//~board = init_board()
	//~player, move = random.choice([OWN, OPP]), (-1, -1)
	//~for i in itertools.count():
		//~moves = get_moves(board, move)
		//~if not moves:
			//~return winning_draw(board, player)

		//~score, move = best_move(board, moves, player)
		//~
		//~debug("{} move: {}, score: {}".format(i, move, score))
		//~board = apply_move(board, move, player)

		//~show_grid(board)
		//~
		//~if winning(board, player):
			//~return player
		//~player = -player
}

int random_move(int moves[]) {
    int n = 0;
    int i;
    for (i = 0; i < 81; i++) {
        n += moves[i];
    }
    n = rand() % n;
    for (i = 0; i < 81; i++) {
        if (moves[i] && n-- == 0) return i;
    }
    return -1;
}

void test_board() {
    // init board, show empty grid
    struct board *b = init_board();
    show_grid(b);
    
    // apply random moves, print move, show grid
    int moves[81];
    int i;
    int last = -1;
    for (i = 0; i < 100; i++) {
        printf("ROUND %d\n", i);
        int player = i % 2 ? OWN : OPP;
        
        get_moves(b, last, moves);
        printf("valid moves:\n");
        show_moves(moves);
        
        if (contains(moves, 81,1) == 0) {
            printf("No valid move\n");
            break;
        }
        
        int move = random_move(moves);
        printf("playing move %d\n", move);
        apply_move(b, move, player);
        show_grid(b);
        last = move;
    }
}

int main() {
    
    test_board();
    
	//~seed = random.randrange(1000000)
	//~random.seed(seed)
	//~TIMEOUT = 0.5
	//~results = {+1: 0, 0: 0, -1: 0}
	//~for i in range(100):
		//~r = play_game()
		//~results[r] += 1
		//~print(i, r, results)
		//~break
	//~print(results)
	//~print(seed)
    
    return 0;
}
