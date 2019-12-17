import tkinter as tk
import formatting as fm

class FancyEntry(tk.Entry):

    def __init__(self, parent, *args, **kwargs):
        tk.Entry.__init__(self, parent, *args, **kwargs, background=fm.entry_bg, foreground=fm.entry_fg, insertbackground=fm.entry_fg,
                          font=fm.entry_font, borderwidth=1)
        self.parent = parent
        self.popup_menu = tk.Menu(self, tearoff=0)
        self.popup_menu.add_command(label="Cut", command=self.cut_selected)
        self.popup_menu.add_command(label="Copy", command=self.copy_selected)
        self.popup_menu.add_command(label="Paste", command=self.paste)


        self.bind("<Button-3>", self.popup) # Button-2 on Aqua

    def popup(self, event):
        try:
            self.popup_menu.tk_popup(event.x_root + 50, event.y_root, 0)
        finally:
            self.popup_menu.grab_release()

    def cut_selected(self):
        self.copy_selected()
        self.delete(0, tk.END)

    def copy_selected(self):
        self.parent.clipboard_clear()
        self.parent.clipboard_append(self.selection_get())


    def paste(self):
        self.insert(self.index(tk.INSERT), self.parent.clipboard_get())