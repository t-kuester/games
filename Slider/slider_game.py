"""
TODO
- animation
- colors
- highlight new and merged tiles
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
        
        self.canvas = tk.Canvas(self)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        
        self.bind_all("<KeyPress>", self.handle_keys)
        self.bind("<Configure>", self.draw_state)
        self.draw_state()
        
    def handle_keys(self, event, shift=False):
        if event.keysym == "q":
            self.quit()
        DIRECTIONS = {"Right": slider_model.RIGHT,
                      "Left":  slider_model.LEFT,
                      "Up":    slider_model.UP,
                      "Down":  slider_model.DOWN,
                      "space": slider_model.SKIP}
        if event.keysym in DIRECTIONS:
            move = DIRECTIONS[event.keysym]
            self.game.apply_move(move)
            self.draw_state()
        
    def draw_state(self, event=None):
        self.update()
        self.canvas.delete("all")
        w = self.get_cellwidth()
        font = tkf.Font(family="Arial", size=int(w)//4)
        for r, row in enumerate(self.game.field):
            for c, col in enumerate(row):
                value = self.game.field[r][c]
                x, y = c*w, r*w
                self.canvas.create_rectangle(x, y, x+w, y+w)
                if value != 0:
                    self.canvas.create_text(x+w/2, y+w/2, text=str(2**value),
                                            anchor="center", font=font)
        print(self.game.turn, self.game.score)

    def get_cellwidth(self):
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        return min(height, width) / slider_model.WIDTH


def main():
    root = tk.Tk()
    frame = SliderFrame(root)
    frame.mainloop()

if __name__ == "__main__":
    main()
