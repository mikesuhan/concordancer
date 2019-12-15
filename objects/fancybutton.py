import tkinter as tk
import formatting as fm

class FancyButton(tk.Button):

    def __init__(self, parent, *args, **kwargs):
        tk.Button.__init__(self, parent, *args, **kwargs, background=fm.button_bg, foreground=fm.button_fg, font=fm.button_font)
        self.parent = parent