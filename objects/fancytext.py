import tkinter as tk
import formatting as fm

class FancyText(tk.Text):

    def __init__(self, parent, gui_obj=None, placeholder=None, width=90, background=fm.text_bg, font=fm.text_font, foreground=fm.text_fg, *args, **kwargs):
        """
        parent: parent object
        gui_obj: GUI from main.py -- enables searching using the mouse click context menu if this is not None
        """
        tk.Text.__init__(self, parent, *args, **kwargs,
                         background=background,
                         font=font,
                         foreground=foreground,
                         insertbackground=fm.text_fg,
                         width=width)
        self.parent = parent
        self.gui_obj = gui_obj
        self.popup_menu = tk.Menu(self, tearoff=0)
        self.popup_menu_search = tk.Menu(self, tearoff=0)

        self.popup_menu.add_command(label="Copy", command=self.copy_selected)
        self.popup_menu_search.add_command(label="Copy", command=self.copy_selected)

        self.popup_menu.add_command(label="Select All", command=self.select_all)
        self.popup_menu_search.add_command(label="Select All", command=self.select_all)

        self.popup_menu_search.add_command(label='Search')

        self.bind("<Button-3>", self.popup) # Button-2 on Aqua

        if placeholder:
            self.insert(tk.END, placeholder)
            self.bind('<Button-1>', self.clear_placeholder)

    def clear_placeholder(self, event):
        self.delete(1.0, tk.END)
        self.unbind('<Button-1>')

    def popup(self, event):
        if self.gui_obj is not None:
            try:
                sel = self.selection_get().strip()
                if sel:
                    self.popup_menu_search.entryconfigure(2, label='Search for: ' + sel, command=lambda: self.gui_obj.search(sel))
                    menu = self.popup_menu_search
                else:
                    menu = self.popup_menu
            except tk.TclError:
                menu = self.popup_menu
        else:
            menu = self.popup_menu

        try:
            menu.tk_popup(event.x_root + 50, event.y_root, 0)
        finally:
            menu.grab_release()

    def cut_selected(self):
        self.copy_selected()
        self.delete(0, tk.END) #todo make this not delete everything

    def paste(self):
        self.insert(self.index(tk.INSERT), self.parent.clipboard_get())

    def copy_selected(self):
        self.parent.clipboard_clear()
        self.parent.clipboard_append(self.selection_get())

    def select_all(self):
        self.tag_add(tk.SEL, "1.0", tk.END)
        self.mark_set(tk.INSERT, "1.0")
        self.see(tk.INSERT)
        return 'break'