import tkinter as tk
from objects.fancytext import FancyText
import formatting as fm

class TextWindow(tk.Toplevel):

    def __init__(self, parent, title='', wrap=tk.WORD, *args, **kwargs):
        tk.Toplevel.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.title(title)
        self.results = None
        self.order = [True, False, True, True, False]

        top_frame = tk.Frame(self)

        self.text = FancyText(top_frame, wrap=wrap, padx=10, pady=5)
        self.text.pack( side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)

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

    def heading_click(self, event, tag='heading'):
        if self.results['complete']:
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
                    for i, h in enumerate(self.results['heading']):
                        if clicked_heading.startswith(h):
                            self.text.delete(2.0, tk.END)
                            self.text.insert(tk.END, '\n\n')
                            self.order[i] = not self.order[i]
                            for k, item in enumerate(sorted(self.results['results'], key=lambda x: x[i], reverse=self.order[i])):
                                self.text.insert(tk.END, item[-1], fm.list_bgs[k % 2])
                            break

