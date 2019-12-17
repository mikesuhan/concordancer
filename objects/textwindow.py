import tkinter as tk
from objects.fancytext import FancyText

class TextWindow(tk.Toplevel):

    def __init__(self, parent, title='', *args, **kwargs):
        tk.Toplevel.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.title(title)
        top_frame = tk.Frame(self)

        self.text = FancyText(top_frame, wrap=tk.WORD)
        self.text.pack( side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)

        self.vsb = tk.Scrollbar(top_frame)
        self.vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.vsb.config(command=self.text.yview)
        self.text.config(yscrollcommand=self.vsb.set)

        top_frame.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
