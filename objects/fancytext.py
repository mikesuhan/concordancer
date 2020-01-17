import tkinter as tk
import formatting as fm

class FancyText(tk.Text):

    def __init__(self, parent, placeholder=None, width=90, background=fm.text_bg, font=fm.text_font, foreground=fm.text_fg, *args, **kwargs):
        tk.Text.__init__(self, parent, *args, **kwargs,
                         background=background,
                         font=font,
                         foreground=foreground,
                         insertbackground=fm.text_fg,
                         width=width)
        self.parent = parent
        self.popup_menu = tk.Menu(self, tearoff=0)
        self.popup_menu.add_command(label="Copy", command=self.copy_selected)
        self.popup_menu.add_command(label="Select All", command=self.select_all)

        self.bind("<Button-3>", self.popup) # Button-2 on Aqua

        if placeholder:
            self.insert(tk.END, placeholder)
            self.bind('<Button-1>', self.clear_placeholder)

    def clear_placeholder(self, event):
        self.delete(1.0, tk.END)
        self.unbind('<Button-1>')

    def popup(self, event):
        try:
            self.popup_menu.tk_popup(event.x_root + 50, event.y_root, 0)
        finally:
            self.popup_menu.grab_release()

    def copy_selected(self):
        self.parent.clipboard_clear()
        self.parent.clipboard_append(self.selection_get())

    def select_all(self):
        self.tag_add(tk.SEL, "1.0", tk.END)
        self.mark_set(tk.INSERT, "1.0")
        self.see(tk.INSERT)
        return 'break'