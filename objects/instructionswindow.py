import tkinter as tk
from objects.fancytext import FancyText
from objects.textwindow import TextWindow
import formatting as fm

class InstructionsWindow(tk.Toplevel):
    def __init__(self, parent, instructions, *args, **kwargs):
        tk.Toplevel.__init__(self, parent.root, *args, **kwargs)
        self.geometry(fm.geometry)
        self.parent = parent
        self.current_sel = 0

        text_frame = tk.Frame(self)

        self.listbox = tk.Listbox(text_frame, width=20)
        self.instructions = instructions

        for k in self.instructions.keys():
            self.listbox.insert(tk.END, k)

        self.listbox.pack(side=tk.LEFT, fill=tk.Y)
        self.listbox.bind('<<ListboxSelect>>', self.on_lb_select)
        self.listbox.selection_set(0, 0)


        self.text = FancyText(text_frame, height=150, wrap=tk.WORD)
        self.text.bind('<KeyRelease>', self.on_text_modify)

        vsb = tk.Scrollbar(self)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        vsb.config(command=self.text.yview)
        self.text.pack(expand=tk.YES, fill=tk.X, side=tk.LEFT, padx=vsb.winfo_width())
        self.text.insert(1.0, self.instructions.get(0))
        self.text.config(yscrollcommand=vsb.set)

        text_frame.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)

    def on_text_modify(self, event):
        self.instructions.set(self.current_sel, event.widget.get(1.0, tk.END))
        if self.current_sel == 0:
            self.parent.status_text.delete(1.0, tk.END)
            self.parent.status_text.insert(1.0, event.widget.get(1.0, tk.END))


    def on_lb_select(self, event):
        cs = self.listbox.curselection()[0]
        if cs != self.current_sel:
            self.current_sel = cs
            self.text.delete(1.0, tk.END)
            self.text.insert(tk.END, self.instructions.get(cs))

