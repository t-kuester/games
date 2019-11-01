"""
TODO
- highlight new and merged tiles
- animation
- documentation
- maybe allow undo once?
"""

import slider_model
import tkinter as tk
import tkinter.font as tkf

class SliderFrame(tk.Frame):
    
    def __init__(self, master):
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
            self.game.apply_move(move)
            self.draw_state()
        
    def draw_state(self, event=None):
        self.update()
        self.canvas.delete("all")
        w = self.get_cellwidth()
        font = tkf.Font(family="Arial", size=int(w)//3)
        for r, row in enumerate(self.game.field):
            for c, col in enumerate(row):
                value = self.game.field[r][c]
                bg = int(255 * 0.95**(value)) if value else 255
                x, y = c*w, r*w
                self.canvas.create_rectangle(x, y, x+w, y+w, fill='#%02X%02X%02X' % (bg, bg, bg))
                if value != 0:
                    self.canvas.create_text(x+w/2, y+w/2, text=to_str(value), anchor="center", font=font)
        self.update_status()

    def update_status(self):
        self.var.set("Turn %d, Score %d" % (self.game.turn, self.game.score))
        if self.game.is_game_over():
            self.var.set(self.var.get() + "\n GAME OVER")

    def get_cellwidth(self):
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        return min(height, width) / slider_model.WIDTH

def to_str(value):
    #~return str(value)
    return str(2**value)


def main():
    root = tk.Tk()
    frame = SliderFrame(root)
    frame.mainloop()

if __name__ == "__main__":
    main()
