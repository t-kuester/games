"""
Slider Game, inspired by '2048', but with more options. Tobias Küster, 2019
Simple graphical user interface for playing the game. No animation, yet, though.

TODO
- animation (still needed after highlighting?)
- maybe allow undo once? or save/restore?
"""

import slider_model
import tkinter as tk
import tkinter.font as tkf

class SliderFrame(tk.Frame):
    """ Class representing a simple UI for the Slider game.
    """
    
    def __init__(self, master):
        """ Create new instance of the frame. """
        tk.Frame.__init__(self, master)
        self.master.title("Slider")
        self.game = slider_model.SliderGame()
        
        self.pack(fill=tk.BOTH, expand=tk.YES)
        self.canvas = tk.Canvas(self, width=400, height=400)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        self.var = tk.StringVar()
        label = tk.Label(self, textvariable=self.var)
        label.pack(side=tk.BOTTOM)
        
        self.bind_all("<KeyPress>", self.handle_keys)
        self.bind("<Configure>", self.draw_state)
        self.draw_state()
        
    def handle_keys(self, event, shift=False):
        """ Handle keys for movements and other actions (new game, guit). """
        DIRECTIONS = {"Right": slider_model.RIGHT,
                      "Left":  slider_model.LEFT,
                      "Up":    slider_model.UP,
                      "Down":  slider_model.DOWN,
                      "space": slider_model.SKIP}
        if event.keysym == "q":
            self.quit()
        if event.keysym == "n":
            self.game = slider_model.SliderGame()
            self.draw_state()
        if event.keysym in DIRECTIONS:
            move = DIRECTIONS[event.keysym]
            if move in self.game.valid_moves():
                self.game.apply_move(move)
                self.draw_state()
        
    def draw_state(self, event=None):
        """ Re-draw the current state of the game. """
        self.update()
        self.canvas.delete("all")
        w = self.get_cellwidth()
        font        = tkf.Font(family="Arial", size=int(w)//3)
        font_merged = tkf.Font(family="Arial", size=int(w)//3, weight="bold")
        for r, row in enumerate(self.game.field):
            for c, col in enumerate(row):
                value = self.game.field[r][c]
                bg = int(255 * 0.95**(value)) if value else 255
                the_font = font_merged if (c, r) in self.game.merged else font
                x, y = c*w, r*w
                self.canvas.create_rectangle(x, y, x+w, y+w, fill='#%02X%02X%02X' % (bg, bg, bg),
                                             width=2 if (c, r) in self.game.new else 1)
                if value != 0:
                    self.canvas.create_text(x+w/2, y+w/2, text=to_str(value), anchor="center",
                                            font=the_font)
        self.update_status()

    def update_status(self):
        """ Update status line with turn number, score and game over or not. """
        self.var.set("Turn %d, Score %d" % (self.game.turn, self.game.score))
        if self.game.is_game_over():
            self.var.set(self.var.get() + "\n GAME OVER")

    def get_cellwidth(self):
        """ Get width of cells, depending on current window size. """
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        return min(height, width) / slider_model.WIDTH

def to_str(value):
    #~return str(value)
    return str(2**value)


def main():
    """ Start Slider game. """
    root = tk.Tk()
    frame = SliderFrame(root)
    frame.mainloop()

if __name__ == "__main__":
    main()
