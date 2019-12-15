import tkinter as tk
from objects.fancytext import FancyText

class TextWindow(tk.Toplevel):

    def __init__(self, parent, *args, **kwargs):
        tk.Toplevel.__init__(self, parent, *args, **kwargs)
        self.parent = parent


        top_frame = tk.Frame(self)

        self.text = FancyText(top_frame, wrap=tk.WORD)
        self.text.pack( side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)

        vsb = tk.Scrollbar(top_frame)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        vsb.config(command=self.text.yview)
        self.text.config(yscrollcommand=vsb.set)

        top_frame.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
