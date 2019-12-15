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
    int i, p = player;
    // rows and columns
    for (i = 0; i < 3; i++) {
        if (field[  i] == p && field[  i+3] == p && field[  i+6] == p) return 1;
        if (field[3*i] == p && field[3*i+1] == p && field[3*i+2] == p) return 1;
    }
    // diagonals
    if (field[0] == p && field[4] == p && field[8] == p) return 1;
    if (field[2] == p && field[4] == p && field[6] == p) return 1;
    return 0;
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

/*
 * perform random moves until the game is over,
 * return winning player and number of moves
 */
int random_play(struct board *b, int move, int player) {
    int moves[81];
	apply_move(b, move, player);
    while (1) {
        if (winning(b->meta, player)) {
            return player;
        }
        get_moves(b, move, moves);
        if (! contains(moves, 81, 1)) {
            return winning_draw(b->meta, player);
        }
        
        player = -player;
        move = random_move(moves);
        apply_move(b, move, player);
    }
}

void evaluate_moves(struct board *b, int moves[], int player, int scores[]) {
    int i;
    struct board b2;
    for (i = 0; i < 1000; i++) {
        copy(b, &b2);
        int move = random_move(moves);
        int win = random_play(&b2, move, player);
        scores[move] += player * win;
    }
    show_moves(scores);
}

int best_move_random_plays(struct board *b, int moves[], int player) {
    int scores[81], i;
    for (i = 0; i < 81; i++) scores[i] = 0;
	evaluate_moves(b, moves, player, scores);
    int best = 0;
    for (i = 1; i < 81; i++) {
        if (scores[i] > scores[best]) best = i;
    }
    printf("move %d; score %d\n", best, scores[best]);
    return best;
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
	struct board *b = init_board();
    int player = rand() % 2 ? 1 : -1;
    int move = -1;
    int moves[81];
    int turn = 0;
    while (1) {
        get_moves(b, move, moves);
        if (! contains(moves, 81, 1)) {
            return winning_draw(b->meta, player);
        }
        move = best_move(b, moves, player);
		apply_move(b, move, player);
		show_grid(b);
        
		if (winning(b->meta, player)) {
			return player;
        }
		player = -player;
        turn++;
    }
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
    
    //~test_board();
    
    play_game();
    
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
