import tkinter as tk
from objects.fancyentry import FancyEntry
from objects.fancybutton import FancyButton
from textprocessing.dictgetter import dictgetter

import formatting as fm
from tkinter import ttk

class NgramsOptionsWindow(tk.Toplevel):
    def __init__(self, parent, presets=None, *args, **kwargs):
        tk.Toplevel.__init__(self, parent.root, *args, **kwargs)
        self.geometry('360x320')
        self.title('Ngrams Options')

        self.options = {}

        padx = 10
        pady = 5

        r = 0

        start_button = FancyButton(self, text='Generate List', command=parent.ngram_freq_list)
        start_button.grid(row=r, column=0, columnspan=2, pady=pady * 3)

        r += 1

        ttk.Separator(self, orient=tk.HORIZONTAL).grid(row=r, column=0, sticky=tk.EW, columnspan=2, pady=pady, padx=padx)

        r += 1

        filter_frame = tk.Frame(self)

        self.options['filter'] = tk.StringVar()

        tk.Label(filter_frame, text='Filter').grid(row=0, column=0, sticky=tk.E, padx=padx)
        self.filter = FancyEntry(filter_frame,
                                 background=fm.white,
                                 font=fm.settings_font,
                                 textvariable=self.options['filter'])
        self.filter.grid(row=0, column=1, sticky=tk.W)
        self.filter.config(width=25)

        filter_frame.grid(row=r, column=0, columnspan=2, pady=pady*2)

        r += 1

        self.options['no_punct'] = {
            'checked': tk.IntVar(value=1),
            'label': tk.StringVar(value='Exclude ngrams with punctuation')
        }
        self.no_punct_cb = tk.Checkbutton(self,
                                          text='Exclude ngrams with punctuation',
                                          variable=self.options['no_punct']['checked'],
                                          textvariable=self.options['no_punct']['label'])
        self.no_punct_cb.grid(row=r, column=0, columnspan=2)

        # r += 1

        # tk.Label(self, text='List Settings').grid(row=r, column=0, columnspan=2, pady=pady)

        r += 1

        self.options['ngrams'] = {}

        self.options['ngrams']['max_len'] = tk.StringVar(value=4)
        self.options['ngrams']['min_len'] = tk.StringVar(value=4)


        nr = 0

        ngram_frame = tk.Frame(self)
        tk.Label(ngram_frame, text='Number of Tokens').grid(row=nr, column=0, columnspan=2)

        nr += 1

        tk.Label(ngram_frame, text='Min').grid(row=nr, column=0, sticky=tk.W, pady=pady)
        self.min_len_sb = tk.Spinbox(ngram_frame, from_=1, to=10, width=3, textvariable=self.options['ngrams']['min_len'])
        self.min_len_sb.grid(row=nr, column=1, sticky=tk.W, pady=pady, padx=padx)

        nr += 1

        tk.Label(ngram_frame, text='Max').grid(row=nr, column=0, sticky=tk.W)
        self.max_len_sb = tk.Spinbox(ngram_frame, from_=1, to=10, width=3, textvariable=self.options['ngrams']['max_len'])
        self.max_len_sb.grid(row=nr, column=1, sticky=tk.W, padx=padx)

        nr += 1

        tk.Label(ngram_frame, text='Norm Rate').grid(row=nr, column=0, columnspan=2, sticky=tk.W)
        nr += 1
        self.norm_rate_entry = tk.Entry(ngram_frame, width=9)
        self.norm_rate_entry.grid(row=nr, column=0, columnspan=2, sticky=tk.W)
        self.options['norm_rate'] = self.norm_rate_entry


        sr = 0
        sc = 3

        tk.Label(ngram_frame, text='Statistic').grid(row=sr, column=sc)
        tk.Label(ngram_frame, text='Minimum').grid(row=sr, column=sc + 1)
        tk.Label(ngram_frame, text='Maximum').grid(row=sr, column=sc + 2)
        tk.Label(ngram_frame, text='Show').grid(row=sr, column=sc + 3)

        sr += 1

        self.options['stats'] = {}

        for key in ['Rank', 'Frequency', 'Rate', 'Dispersion']:
            self.options[key.lower()] = {
                'min': tk.StringVar(value=0),
                'max': tk.StringVar(value=0),
                'checked': tk.IntVar(value=1)
            }

            tk.Label(ngram_frame, text=key).grid(row=sr, column=sc, sticky=tk.W)
            key = key.lower()
            tk.Spinbox(ngram_frame, from_=0, to=99999999999, width=6, textvariable=self.options[key]['min']).grid(row=sr, column=sc + 1)
            tk.Spinbox(ngram_frame, from_=0, to=99999999999, width=6, textvariable=self.options[key]['max']).grid(row=sr, column=sc + 2)
            tk.Checkbutton(ngram_frame, variable=self.options[key]['checked']).grid(row=sr, column=sc + 3, sticky=tk.W, padx=padx)

            sr += 1

        ngram_frame.grid(row=r, column=0, sticky=tk.NW, padx=padx, pady=pady)

        r += 1

        ngram_frame.grid_columnconfigure(1, minsize=60)

        for key in presets:
            if (presets[key]) is int:
                self.options[key].set(presets[key])
            elif type(presets[key]) is dict:
                for k in presets[key]:
                    self.options[key][k].set(presets[key][k])


    def get_options(self):
        return dictgetter(self.options)
