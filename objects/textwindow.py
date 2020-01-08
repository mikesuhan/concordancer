import tkinter as tk
from operator import attrgetter
from objects.fancytext import FancyText
import formatting as fm
from textprocessing.result import Result

class TextWindow(tk.Toplevel):

    def __init__(self, parent, view=None, title='', wrap=tk.WORD, *args, **kwargs):
        tk.Toplevel.__init__(self, parent.root, *args, **kwargs)
        self.parent = parent
        self.title(title)
        # self.results = None
        self.results = []
        self.complete = True
        self.order = [True, False, True, True, False]
        self.rows_n = 0

        if view is not None:
            inst = self.parent.instructions.get(view)



            instructions_frame = tk.Frame(self)
            self.instructions_lbl = tk.Label(instructions_frame,
                                         text=inst,
                                         justify=tk.LEFT)

            self.instructions_lbl.bind("<Configure>", self.set_label_wrap)
            self.instructions_lbl.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
            instructions_frame.pack(side=tk.TOP, expand=tk.YES, fill=tk.X)


        top_frame = tk.Frame(self)

        self.text = FancyText(top_frame, wrap=wrap, padx=10, pady=5)
        self.text.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)

        self.text.tag_config('text_bg', background=fm.text_bg)
        self.text.tag_config('white', background=fm.white)
        self.text.tag_config('heading', font=fm.bold_text_font)
        # give priority to formatting of selected text over that of tags
        self.text.tag_raise('sel')

        self.text.tag_bind('heading', '<Button-1>', self.heading_click)

        self.vsb = tk.Scrollbar(top_frame)
        self.vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.vsb.config(command=self.text.yview)
        self.text.config(yscrollcommand=self.vsb.set)

        top_frame.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)

    def set_label_wrap(self, event):
        wraplength = event.width - 12  # 12, to account for padding and borderwidth
        event.widget.configure(wraplength=wraplength)

    def add_result(self, result):

        self.text.insert(tk.END, result.row(), fm.list_bgs[self.rows_n % 2])
        self.results.append(result)
        self.rows_n += 1

    def heading_click(self, event, tag='heading'):
        if self.complete:
            # get the index of the mouse click
            index = self.text.index("@%s,%s" % (event.x, event.y))

            # get the indices of all "adj" tags
            tag_indices = list(self.text.tag_ranges('heading'))

            # iterate them pairwise (start and end index)
            for start, end in zip(tag_indices[0::2], tag_indices[1::2]):
                # check if the tag matches the mouse click index
                if self.text.compare(start, '<=', index) and self.text.compare(index, '<', end):
                    # return string between tag start and end
                    clicked_heading = self.text.get(start, end)
                    for i, h in enumerate(self.results[0].heading()):
                        if clicked_heading.startswith(h):
                            self.text.delete(2.0, tk.END)
                            self.text.insert(tk.END, '\n\n')
                            self.order[i] = not self.order[i]
                            for k, res in enumerate(sorted(self.results, key=attrgetter(Result.attrs[i]), reverse=self.order[i])):
                                self.text.insert(tk.END, res.row(), fm.list_bgs[k % 2])
                            break

