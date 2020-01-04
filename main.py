import tkinter as tk
from tkinter import filedialog
from multiprocessing import Queue, Process
import queue
from time import gmtime, strftime

import formatting as fm

from textprocessing.corpus import Corpus
from textprocessing.concordance import Concordance
from textprocessing.result import Result
from textprocessing.msword import write_docx
from textprocessing.html import write_html
from textprocessing.dictgetter import dictgetter

from objects.fancytext import FancyText
from objects.fancybutton import FancyButton
from objects.fancyentry import FancyEntry
from objects.concwindow import ConcWindow
from objects.textwindow import TextWindow
from objects.saveoptions import SaveOptions
from objects.instructions import Instructions
from objects.instructionswindow import InstructionsWindow
from objects.ngramsoptionswindow import NgramsOptionsWindow

from message import Message


class GUI:

    corpus = None
    default_conc_length = '5'
    conc_processes = []
    save_process = None
    freq_list_processes = []
    search_val = None
    conc_windows = {}
    conc_id = 0
    freq_list_windows = {}
    freq_list_id = 0
    prev_results = None

    def __init__(self):
        self.q = Queue()
        self.root = tk.Tk()
        self.root.minsize(300, 200)
        self.root.geometry(fm.geometry)
        self.instructions = Instructions()

        status_frame = tk.Frame()
        self.status_text = FancyText(status_frame, wrap=tk.WORD, background=fm.white, font=fm.instructions_font)
        self.status_text.tag_config('red', foreground='red')
        self.status_var = tk.StringVar()

        # Menu bar
        menu_bar = tk.Menu(self.root)

        # File menu on menu bar
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Load files", command=self.load_files)
        file_menu.add_command(label="Load from URL", command=self.load_from_url)
        file_menu.add_command(label="Remove Files") #todo add this

        file_menu.add_separator()

        file_menu.add_command(label="Reset", command=self.reset)

        file_menu.add_separator()

        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        # Tools menu
        tools_menu = tk.Menu(menu_bar, tearoff=0)
        tools_menu.add_command(label='List', command=self.word_list_options)
        tools_menu.add_command(label='Edit Instructions', command=self.open_instructios_window)
        menu_bar.add_cascade(label='Tools', menu=tools_menu)

        """
        settings_menu = tk.Menu(menu_bar, tearoff=0)
        settings_menu.add_command(label='Edit Instructions', command=self.open_instructios_window)
        menu_bar.add_cascade(label='Settings', menu=settings_menu)
        """

        self.root.config(menu=menu_bar, background=fm.dark_bg)

        # search bar
        search_frame = tk.Frame(self.root)

        self.conc_left_entry = FancyEntry(search_frame, width=2, justify=tk.CENTER)
        self.conc_left_entry.insert(0, self.default_conc_length)
        self.conc_left_entry.pack(side=tk.LEFT)
        self.conc_right_entry = FancyEntry(search_frame,  width=2, justify=tk.CENTER)
        self.conc_right_entry.insert(0, self.default_conc_length)
        self.conc_right_entry.pack(side=tk.LEFT)

        self.search_var = tk.StringVar()
        self.search_entry = FancyEntry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(expand=tk.YES, side=tk.LEFT, fill=tk.X)

        search_button = FancyButton(search_frame, text='Search', padx=15, command=self.search)
        search_button.pack(side=tk.RIGHT, fill=tk.Y)
        search_button.pack()

        self.root.bind('<Return>', self.search_kp)

        search_frame.pack(expand=tk.NO, side=tk.TOP, fill=tk.X)

        # status area
        self.status_text.pack(expand=tk.YES, side=tk.LEFT, fill=tk.BOTH)
        status_frame.pack(expand=tk.YES, side=tk.TOP, fill=tk.BOTH)

        # vertical scroll bar
        vsb = tk.Scrollbar(status_frame)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        vsb.config(command=self.status_text.yview)
        self.status_text.config(yscrollcommand=vsb.set)


        self.status_entry = FancyEntry(self.root, background=fm.text_bg, font=fm.status_font)
        self.status_entry.pack(side=tk.BOTTOM, expand=tk.NO, fill=tk.BOTH)


        tk.mainloop()

    def word_list_options(self):
        presets = {
            'ngrams':
                {'min_len': 1,
                 'max_len': 1},
            'no_punct': {
                'label': 'Exclude punctuation.'
            }
        }

        self.ngrams_options_window = NgramsOptionsWindow(self, presets=presets)

    def ngrams_options(self):
        presets = {
            'frequency': {'min': 2},
            'no_punct': {
                'label': 'Exclude punctuation.'
            }
        }
        self.ngrams_options_window = NgramsOptionsWindow(self, presets=presets)


    def ngram_freq_list(self):
        if self.corpus is None or len(self.corpus.texts) == 0:
            m = Message('You must load texts before making a frequency list. Select "File > Load files" to load texts.',
                        tag='red')
            self.msg(m)
        else:

            options = self.ngrams_options_window.get_options()
            self.ngrams_options_window.destroy()
            self.ngrams_options_window.update()

            p = Process(target=self.corpus.ngram_dist,
                        args=(self.ngrams_options_window.options,
                              self.freq_list_id)
                        )
            p.start()
            self.freq_list_processes.append(p)
            self.freq_list_id += 1
            self.root.after(100, self.process_queue)

    def freq_list(self):
        if self.corpus is None or len(self.corpus.texts) == 0:
            m = Message('You must load texts before making a frequency list. Select "File > Load files" to load texts.',
                        tag='red')
            self.msg(m)

        else:

            p = Process(target=self.corpus.ngram_dist, args=(None, self.freq_list_id,))
            p.start()
            self.freq_list_processes.append(p)
            self.freq_list_id += 1
            self.root.after(100, self.process_queue)



    def save(self, text, max_center_len, tokens_left):
        file_types = (('Word', '.docx'),
                      ('Excel', '.xlsx'),
                      ('plaintext', '.txt'),
                      ('tab-separated values', '.tsv'),
                      ('html', '.html'))

        fp = filedialog.asksaveasfilename(filetypes=file_types, defaultextension='.docx')
        if fp.endswith(('.tsv', '.txt',)):
            with open(fp, 'w') as f:
                f.write(text)

        elif fp.endswith('.docx'):
            self.save_process = Process(target=write_docx,
                                args=(self.q, fp, text, max_center_len))
            self.save_process.start()
            self.root.after(100, self.process_queue)

        elif fp.endswith('.html'):
            write_html(fp, text)

        elif fp.endswith('.xlsx'):
            save_options = SaveOptions(self.root, fp, text, tokens_left, msg=self.msg)

    def search_kp(self, event):
        self.search()

    def search(self):
        # determines concordance settings
        conc_left, conc_right = self.conc_left_entry.get(), self.conc_right_entry.get()

        if conc_left.isdigit():
            conc_left = int(conc_left)
        else:
            conc_left = self.default_conc_length
            self.conc_left_entry.delete(0, tk.END)
            self.conc_left_entry.insert(0, self.default_conc_length)
        if conc_right.isdigit():
            conc_right = int(conc_right)
        else:
            conc_right = self.default_conc_length
            self.conc_right_entry.delete(0, tk.END)
            self.conc_right_entry.insert(0, self.default_conc_length)

        p = Process(target=self.corpus.concordance, args=(self.search_var.get(), conc_left, conc_right, self.conc_id))
        self.conc_processes.append(p)
        self.conc_id += 1
        p.start()
        self.root.after(100, self.process_queue)

    def reset(self):
        """Removes any data and clears the queue."""
        self.clear_queue()
        self.search_entry.delete(0, tk.END)
        self.status_text.delete(1.0, tk.END)
        self.corpus = None

    def open_instructios_window(self):
        InstructionsWindow(self.root, self.instructions)


    def load_from_url(self):
        pass

    def load_files(self):
        """Loads texts from local files."""
        filenames = filedialog.askopenfilenames()

        if self.corpus is None:
            self.corpus = Corpus(self.q)

        m = self.corpus.load_texts(*filenames)
        self.msg(m)

    def msg(self, m):
        tag = ''
        if type(m) == Message:
            if m.tag:
                tag = m.tag
            m = m.message

        m = '[{d}] {m}'.format(d=strftime("%Y-%m-%d %H:%M:%S", gmtime()), m=m)
        self.status_entry.delete(0, tk.END)
        self.status_entry.insert(0, m)


    def process_queue(self):
        for p in self.conc_processes + self.freq_list_processes:
            if p.is_alive():
                self.root.after(100, self.process_queue)
                break

        if self.save_process and self.save_process.is_alive():
            self.root.after(100, self.process_queue)

        try:
            q_item = self.q.get(0)
            if type(q_item) is Concordance:
                # creates record of what window the results get added to
                if not self.conc_windows.get(q_item.id, False):
                    self.conc_windows[q_item.id] = ConcWindow(self,
                                                              q_item.query,
                                                              self.corpus,
                                                              id=q_item.id,
                                                              save=self.save,
                                                              tokens_left=q_item.tokens_left)

                # Stops process if the window has been closed
                elif not tk.Toplevel.winfo_exists(self.conc_windows[q_item.id]):
                    self.conc_processes[q_item.id].terminate()



                # determines which search result has the most characters
                if '*' not in q_item.query and not self.conc_windows[q_item.id].max_center_len:
                    self.conc_windows[q_item.id].max_center_len = len(q_item.query)
                else:
                    self.conc_windows[q_item.id].max_center_len = max(q_item.max(), self.conc_windows[q_item.id].max_center_len)

                # Updates window with concordance data
                self.conc_windows[q_item.id].max_center_len = int(self.conc_windows[q_item.id].max_center_len * .8)
                self.conc_windows[q_item.id].text.insert(tk.END, q_item.to_string())


                for i, indices in enumerate(q_item.center_inds):

                    self.conc_windows[q_item.id].center_inds.append(indices)
                    self.conc_windows[q_item.id].text_locs.append(q_item.text_locs[i])

            elif type(q_item) is Message:
                self.msg(q_item)


            elif type(q_item) is list and type(q_item[0]) is Result:
                if q_item[0].r_id not in self.freq_list_windows.keys():
                    if q_item[0].rtype == 'Tokens':
                        view = 'Word List Window'
                    elif q_item[0].rtype == 'Ngrams':
                        view = 'Ngrams List Window'
                    else:
                        view = ''

                    self.freq_list_windows[q_item[0].r_id] = TextWindow(self, view=view, wrap='none')

                    for i, heading in enumerate(q_item[0].heading()):
                        self.freq_list_windows[q_item[0].r_id].text.insert(tk.END, heading, 'heading')
                        if len(heading) - 1 > i:
                            self.freq_list_windows[q_item[0].r_id].text.insert(tk.END, q_item[0].delimiter)

                    self.freq_list_windows[q_item[0].r_id].text.insert(tk.END, '\n\n')

                for result in q_item:
                    self.freq_list_windows[q_item[0].r_id].add_result(result)


            self.root.after(100, self.process_queue)

        except queue.Empty:
            pass

    def clear_queue(self):
        try:
            while True:
                self.q.get_nowait()
        except queue.Empty:
            pass

if __name__ == '__main__':
    GUI()