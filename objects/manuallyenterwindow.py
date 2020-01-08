import tkinter as tk
from objects.fancytext import FancyText
from objects.fancybutton import FancyButton
from message import Message
import formatting as fm

class ManuallyEnterWindow(tk.Toplevel):

    def __init__(self, parent, wrap=tk.WORD, *args, **kwargs):
        tk.Toplevel.__init__(self, parent.root, *args, **kwargs)
        self.parent = parent
        self.title('Manually Enter a Text')

        top_frame = tk.Frame(self)

        self.text = FancyText(top_frame, wrap=wrap, padx=10, pady=5, background=fm.white, font=fm.status_font)
        self.text.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)


        self.vsb = tk.Scrollbar(top_frame)
        self.vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.vsb.config(command=self.text.yview)
        self.text.config(yscrollcommand=self.vsb.set)

        top_frame.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)


        save_btn = FancyButton(self, text='Save', command=self.save)
        save_btn.pack(side=tk.RIGHT)

    def save(self):
        print(self.text.get(1.0, tk.END))
        self.parent.corpus.load_string(self.text.get(1.0, tk.END))
        self.parent.msg('Text loaded')
        self.destroy()
