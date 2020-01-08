import tkinter as tk
import formatting as fm

class FancyListbox(tk.Listbox):

    def __init__(self, parent,  remove=False, open_text=False, copy_path=False, *args, **kwargs):
        tk.Listbox.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.popup_menu = tk.Menu(self, tearoff=0)

        if remove:
            self.popup_menu.add_command(label="Remove", command=remove)
        if open_text:
            self.popup_menu.add_command(label="Open", command=open_text)



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