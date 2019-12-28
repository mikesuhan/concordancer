import tkinter as tk
from objects.fancytext import FancyText
from objects.textwindow import TextWindow

class ConcWindow(tk.Toplevel):

    max_center_len= 0

    def __init__(self, parent, query, corpus, id, save, tokens_left, instructions=None, *args, **kwargs):
        tk.Toplevel.__init__(self, parent.root, *args, **kwargs)
        self.query = query
        self.parent = parent
        self.corpus = corpus
        self.id = id
        self.title('Results for ' + query)
        self.tokens_left = tokens_left
        self.geometry('1200x550')
        self.center_inds = []
        self.text_locs = []

        self.bind('<Double-Button-1>', self.db_click)

        inst = self.parent.instructions.get('Concordance Window')

        if inst:

            instructions_frame = tk.Frame(self)
            self.instructions_lbl = tk.Label(instructions_frame,
                                         text=inst,
                                         justify=tk.LEFT)

            self.instructions_lbl.bind("<Configure>", self.set_label_wrap)
            self.instructions_lbl.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
            instructions_frame.pack(side=tk.TOP, expand=tk.YES, fill=tk.X)


        conc_frame = tk.Frame(self)

        self.text = FancyText(conc_frame, wrap='none')
        self.text.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)

        vsb = tk.Scrollbar(conc_frame)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        vsb.config(command=self.text.yview)
        self.text.config(yscrollcommand=vsb.set)

        conc_frame.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)

        hsb = tk.Scrollbar(self, orient='horizontal')
        hsb.pack(fill=tk.X, side=tk.BOTTOM)
        hsb.config(command=self.text.xview)
        self.text.config(xscrollcommand=hsb.set)

        menu_bar = tk.Menu(self)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Save", command=lambda: save(self.text.get(1.0, tk.END), self.max_center_len, self.tokens_left))
        menu_bar.add_cascade(label="File", menu=file_menu)
        self.config(menu=menu_bar)

    def set_label_wrap(self, event):
        wraplength = event.width - 12  # 12, to account for padding and borderwidth
        event.widget.configure(wraplength=wraplength)

    def db_click(self, event):

        ins_ind = self.text.index(tk.INSERT)
        row, col = str(ins_ind).split('.')
        row, col = int(row), int(col)

        w_left, w_right = self.center_inds[row - 1]
        if w_right  > col > w_left:
            left_i, right_i, text_i = self.text_locs[row-1]
            self.show_context(left_i, right_i, text_i)


    def show_context(self, left_i, right_i, text_i):
        t = self.corpus.texts[text_i].text
        text_window = TextWindow(self.parent.root, title=self.corpus.texts[text_i].filepath)
        text_window.text.tag_config('highlight', foreground='red')
        text_window.text.tag_config('context', background='yellow')

        # gets indices from text that has been clicked on
        single_text_locs = [item for item in self.text_locs if item[-1] == text_i]

        # adds text coming before first match
        if single_text_locs[0][0] > 0:
            text_window.text.insert(tk.END, t[:single_text_locs[0][0]])

        # highlights matches and adds text between match i and the following match
        for i, (ltl, rtl, _) in enumerate(single_text_locs):

            if ltl == left_i:
                text_window.text.insert(tk.END, t[ltl:rtl], 'context')
                text_window.text.see(tk.END)
            else:
                text_window.text.insert(tk.END, t[ltl:rtl], 'highlight')
            if len(t) > rtl + 1:
                if len(single_text_locs) > i + 1:
                    text_window.text.insert(tk.END, t[rtl:single_text_locs[i+1][0]])
                else:
                    text_window.text.insert(tk.END, t[rtl:])
