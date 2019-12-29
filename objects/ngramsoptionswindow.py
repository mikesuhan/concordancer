import tkinter as tk
from objects.fancyentry import FancyEntry
from objects.fancybutton import FancyButton

import formatting as fm
from tkinter import ttk

class NgramsOptionsWindow(tk.Toplevel):
    def __init__(self, parent, *args, **kwargs):
        tk.Toplevel.__init__(self, parent.root, *args, **kwargs)
        self.geometry('300x250')
        self.title('Ngrams Options')

        padx = 10
        pady = 5

        r = 0

        start_button = FancyButton(self, text='Generate Ngrams List')
        start_button.grid(row=r, column=0, columnspan=2, pady=pady * 3)

        r += 1

        ttk.Separator(self, orient=tk.HORIZONTAL).grid(row=r, column=0, sticky=tk.EW, columnspan=2, pady=pady, padx=padx)

        r += 1

        tk.Label(self, text='Ngram List Settings').grid(row=r, column=0, columnspan=2, pady=pady)



        r += 1



        self.max_tv = tk.IntVar()
        self.max_tv.set(4)

        self.min_tv = tk.IntVar()
        self.min_tv.set(4)

        ngram_frame = tk.Frame(self)
        tk.Label(ngram_frame, text='Ngram Length').grid(row=0, column=0, columnspan=2)
        tk.Label(ngram_frame, text='Min').grid(row=1, column=0, sticky=tk.W, pady=pady)
        self.min_len_sb = tk.Spinbox(ngram_frame, from_=1, to=10, width=3, textvariable=self.min_tv)
        self.min_len_sb.grid(row=1, column=1, sticky=tk.W, pady=pady)

        tk.Label(ngram_frame, text='Max').grid(row=2, column=0, sticky=tk.W)
        self.max_len_sb = tk.Spinbox(ngram_frame, from_=1, to=10, width=3, textvariable=self.max_tv)
        self.max_len_sb.grid(row=2, column=1, sticky=tk.W)

        tk.Label(ngram_frame, text='Norm Rate').grid(row=3, columnspan=2, pady=pady)

        ngram_frame.grid(row=r, column=0, sticky=tk.NW, padx=padx, pady=pady)


        # Statistics

        stats_frame = tk.Frame(self)

        # Heading
        sr = 0
        tk.Label(stats_frame, text='Statistic').grid(row=sr, column=0)
        tk.Label(stats_frame, text='Minimum').grid(row=sr, column=1)
        tk.Label(stats_frame, text='Show').grid(row=sr, column=2)

        sr += 1

        self.stats = {}

        for key in ['Rank', 'Frequency', 'Rate', 'Dispersion']:
            self.stats[key] = {
                'min': tk.IntVar(value=0),
                'checked': tk.IntVar(value=1)
            }

            tk.Label(stats_frame, text=key).grid(row=sr, column=0, sticky=tk.W)
            tk.Spinbox(stats_frame, from_=0, width=6, textvariable=self.stats[key]['min']).grid(row=sr, column=1)
            tk.Checkbutton(stats_frame, variable=self.stats[key]['checked']).grid(row=sr, column=2, sticky=tk.W, padx=padx)

            sr += 1

        stats_frame.grid(row=r, column=1, sticky=tk.NE, padx=padx, pady=pady)

        r += 1

        filter_frame = tk.Frame(self)

        tk.Label(filter_frame, text='Filter').grid(row=0, column=0, sticky=tk.E, padx=padx)
        self.filter = FancyEntry(filter_frame, background=fm.white, font=fm.settings_font)
        self.filter.grid(row=0, column=1, sticky=tk.W)
        self.filter.config(width=25)

        filter_frame.grid(row=r, column=0, columnspan=2, pady=pady*2)