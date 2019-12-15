import tkinter as tk
from objects.fancytext import FancyText
from objects.textwindow import TextWindow

class ConcWindow(tk.Toplevel):

    max_center_len= 0

    def __init__(self, parent, query, id, save,  *args, **kwargs):
        tk.Toplevel.__init__(self, parent, *args, **kwargs)
        self.query = query
        self.parent = parent
        self.id = id
        self.title('Results for ' + query)

        self.center_inds = {}
        self.bind('<Double-Button-1>', self.db_click)

        top_frame = tk.Frame(self)

        self.text = FancyText(top_frame, wrap='none')
        self.text.pack( side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)

        vsb = tk.Scrollbar(top_frame)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        vsb.config(command=self.text.yview)
        self.text.config(yscrollcommand=vsb.set)

        top_frame.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)

        hsb = tk.Scrollbar(self, orient='horizontal')
        hsb.pack(fill=tk.X, side=tk.BOTTOM)
        hsb.config(command=self.text.xview)
        self.text.config(xscrollcommand=hsb.set)

        menu_bar = tk.Menu(self)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Save", command=lambda: save(self.text.get(1.0, tk.END), self.max_center_len))
        menu_bar.add_cascade(label="File", menu=file_menu)
        self.config(menu=menu_bar)

    def db_click(self, event):
        print(self.text.index(tk.INSERT))
        ins_ind = self.text.index(tk.INSERT)
        row, col = str(ins_ind).split('.')
        row, col = int(row), int(col)

        w_left, w_right = self.center_inds.get(row, (0, 0))
        if w_right -1 > col >= w_left:
            print('MATCH', ins_ind, w_left, w_right)

        #text_window = TextWindow(self)

