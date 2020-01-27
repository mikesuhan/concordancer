import tkinter as tk
from tkinter import filedialog
from multiprocessing import Queue, Process
import queue
import os
from time import gmtime, strftime
from math import ceil
from random import choice
import string
from json import dumps
from zipfile import ZipFile
from re import sub

import formatting as fm

from textprocessing.corpus import Corpus
from textprocessing.concordance import Concordance
from textprocessing.result import Result
from textprocessing.msword import write_docx
from textprocessing.html import write_html

from objects.chatsettingswindow import ChatSettingsWindow
from objects.fancytext import FancyText
from objects.fancybutton import FancyButton
from objects.fancyentry import FancyEntry
from objects.fancylistbox import FancyListbox
from objects.concwindow import ConcWindow
from objects.manuallyenterwindow import ManuallyEnterWindow
from objects.textwindow import TextWindow
from objects.saveoptions import SaveOptions
from objects.instructions import Instructions
from objects.instructionswindow import InstructionsWindow
from objects.ngramsoptionswindow import NgramsOptionsWindow

from ircprocessing.chat import IRC
from ircprocessing.chatmessage import ChatMessage
from ircprocessing.chatlog import ChatLog

from message import Message


class GUI:

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
        self.queue = Queue()
        self.root = tk.Tk()
        self.corpus = Corpus(self.queue)
        self.instructions = Instructions()

        self.chat_settings = {
            'server': 'chat.freenode.net',
            'channel': '#' + ''.join(
                choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16)),
            'port': 6667,
        }
        self.chat_scroll_lock = True
        self.chat = None
        self.chat_log = None


        # Menu bar
        menu_bar = tk.Menu(self.root)

        # File menu on menu bar
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label='Save Package', command=self.save_package)
        file_menu.add_command(label='Load package', command=self.load_package)

        file_menu.add_separator()

        file_menu.add_command(label="Load text file(s)", command=self.load_files)
        file_menu.add_command(label="Manually enter text", command=self.open_manually_enter_window)

        file_menu.add_separator()

        file_menu.add_command(label="Reset", command=self.reset)

        file_menu.add_separator()

        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        # Tools menu
        tools_menu = tk.Menu(menu_bar, tearoff=0)
        tools_menu.add_command(label='List', command=self.word_list_options)
        menu_bar.add_cascade(label='Tools', menu=tools_menu)

        options_menu = tk.Menu(menu_bar, tearoff=0)
        options_menu.add_command(label='Add/Edit Instructions', command=self.open_instructions_window)
        options_menu.add_command(label='Chat Settings', command=self.open_chat_settings)
        menu_bar.add_cascade(label='Options', menu=options_menu)

        self.root.config(menu=menu_bar)

        top_frame = tk.Frame(self.root)

        # File list

        file_list_frame = tk.Frame(top_frame)
        tk.Label(file_list_frame, text='File Manager').pack(side=tk.TOP, pady=4)


        fl_btn_frame = tk.Frame(file_list_frame)
        remove_text_btn = FancyButton(fl_btn_frame, text='Remove', command=self.remove)
        remove_text_btn.pack(expand=tk.YES, side=tk.LEFT, fill=tk.X)
        load_text_btn = FancyButton(fl_btn_frame, text='Load', command=self.load_files)
        load_text_btn.pack(expand=tk.YES, side=tk.LEFT, fill=tk.X)
        fl_btn_frame.pack(expand=tk.NO, fill=tk.X)

        lb_frame = tk.Frame(file_list_frame)

        self.file_list = FancyListbox(lb_frame,
                                      width=35,
                                      selectmode=tk.EXTENDED,
                                      remove=self.remove,
                                      open_text=self.open_text)
        self.file_list.pack(expand=tk.YES, fill=tk.Y, side=tk.LEFT)

        fl_vsb = tk.Scrollbar(lb_frame, orient=tk.VERTICAL)
        fl_vsb.config(command=self.file_list.yview)
        fl_vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_list.config(yscrollcommand=fl_vsb.set)

        lb_frame.pack(expand=tk.YES, fill=tk.Y)

        fl_hsb = tk.Scrollbar(file_list_frame, orient=tk.HORIZONTAL)
        fl_hsb.config(command=self.file_list.xview)
        fl_hsb.pack(side=tk.TOP, fill=tk.X, expand=tk.NO)
        self.file_list.config(xscrollcommand=fl_hsb.set)

        file_list_frame.pack(side=tk.LEFT, expand=tk.NO, fill=tk.Y)

        middle_frame = tk.Frame(top_frame)

        # search bar
        search_frame = tk.Frame(middle_frame)

        self.conc_left_entry = FancyEntry(search_frame, width=2, justify=tk.CENTER)
        self.conc_left_entry.insert(0, self.default_conc_length)
        self.conc_left_entry.pack(side=tk.LEFT)
        self.conc_right_entry = FancyEntry(search_frame,  width=2, justify=tk.CENTER)
        self.conc_right_entry.insert(0, self.default_conc_length)
        self.conc_right_entry.pack(side=tk.LEFT)

        self.search_var = tk.StringVar()
        self.search_entry = FancyEntry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(expand=tk.YES, side=tk.LEFT, fill=tk.X)
        self.search_entry.bind('<Return>', self.search_kp)

        search_button = FancyButton(search_frame, text='Search', padx=15, command=self.search)
        search_button.pack(side=tk.RIGHT, fill=tk.Y)
        search_button.pack()

        search_frame.pack(expand=tk.NO, side=tk.TOP, fill=tk.X)

        # Big text box in the middle
        status_frame = tk.Frame(middle_frame)

        self.status_text = FancyText(status_frame,
                                     gui_obj=self,
                                     width=55,
                                     wrap=tk.WORD,
                                     background=fm.white,
                                     font=fm.instructions_font,
                                     state=tk.DISABLED)
        self.status_text.d_insert(1.0, self.instructions.get('Main Window'))
        self.status_text.pack(expand=tk.YES, side=tk.LEFT, fill=tk.Y)
        status_frame.pack(expand=tk.YES, fill=tk.Y)

        # vertical scroll bar
        vsb = tk.Scrollbar(status_frame)
        vsb.pack(side=tk.LEFT, fill=tk.Y)
        vsb.config(command=self.status_text.yview)
        self.status_text.config(yscrollcommand=vsb.set)

        middle_frame.pack(side=tk.LEFT, fill=tk.Y)

        right_frame = tk.Frame(top_frame)

        chat_box_frame = tk.Frame(right_frame)

        self.names_text = FancyText(chat_box_frame,
                                    width=30,
                                    height=3,
                                    wrap=tk.WORD,
                                    background='SystemButtonFace',
                                    font=fm.chat_font,
                                    state=tk.DISABLED)
        self.names_text.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
        self.names_text.tag_config('other', font=fm.chat_user_font, foreground=fm.chat_other_fg)

        self.chat_text = FancyText(chat_box_frame,
                                   gui_obj=self,
                                   width=30,
                                   wrap=tk.WORD,
                                   background=fm.white,
                                   font=fm.chat_font,
                                   state=tk.DISABLED)
        self.chat_text.pack(expand=tk.YES, side=tk.LEFT, fill=tk.BOTH)


        self.chat_vsb = tk.Scrollbar(chat_box_frame)
        self.chat_vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_vsb.config(command=self.chat_scroll)
        self.chat_text.config(yscrollcommand=self.chat_vsb.set)

        self.chat_text.tag_config('user', font=fm.chat_user_font, foreground=fm.chat_me_fg)
        self.chat_text.tag_config('other', font=fm.chat_user_font, foreground=fm.chat_other_fg)

        self.chat_text.d_insert(1.0, 'Enter your name below and press Return to connect to the chat.\n')

        chat_box_frame.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)

        self.chat_input = FancyText(right_frame,
                                    gui_obj=self,
                                   width=30,
                                   height=3,
                                   wrap=tk.WORD,
                                   background=fm.white,
                                   font=fm.chat_font,
                                    placeholder='Enter Name',
                                    edit=True)
        self.chat_input.pack(expand=tk.YES, fill=tk.BOTH, side=tk.LEFT)
        self.chat_input.bind('<KeyRelease-Return>', self.chat_send_kp)

        right_frame.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.BOTH)

        top_frame.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)

        self.status_entry = FancyEntry(self.root, background='SystemButtonFace', font=fm.status_font)
        self.status_entry.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)


        tk.mainloop()

    def load_package(self):
        zip_fp = filedialog.askopenfilename(filetypes=(('Corpus Packages', '*.crps'), ))
        if zip_fp:
            m, self.chat_settings, instructions = self.corpus.load_package(zip_fp)
            self.instructions = Instructions(instructions=instructions)
            self.status_text.d_delete(1.0, tk.END)
            self.status_text.d_insert(1.0, self.instructions.get('Main Window'))
            self.msg(m)

    def save_package(self):
        zip_fp = filedialog.asksaveasfilename(filetypes=(('Corpus', '.crps'),), defaultextension='.crps')
        with ZipFile(zip_fp, 'w') as zip:
            text_data = {}
            for i, text in enumerate(self.corpus.texts):
                if text.filepath:
                    fn = os.path.split(text.filepath)[-1]
                    fn = fn.split('.')
                    fn[-1] = 'txt'
                    fn = '.'.join(fn)
                elif text.title:
                    fn = sub('[^a-zA-Z0-1 \-_()]', '', text.title)
                    fn += '.txt'
                else:
                    fn = 'text ' + str(i) + '.txt'

                zip.writestr(fn, text.text)

                text_data[fn] = {
                    'filename': fn,
                    'title': text.title,
                }
            # saves as json with cprsi extension
            zip.writestr('text_data.crpsi', dumps(text_data))
            zip.writestr('chat_settings.crpsi', dumps(self.chat_settings))
            zip.writestr('instructions.crpsi', dumps(self.instructions.instructions))

    def open_chat_settings(self):
        ChatSettingsWindow(self.root, self.chat_settings)

    def chat_send_kp(self, event):
        self.chat_send()
        self.chat_input.delete(1.0, tk.END)
        self.chat_input.mark_set(tk.SEL, 1.0)
        if self.chat_scroll_lock:
            self.chat_text.see(tk.END)

    def chat_scroll(self, *args):
        self.chat_text.yview(*args)
        sb_y_pos = args[1]
        sb_top, sb_bottom = self.chat_text.yview()
        sb_height = sb_bottom - sb_top
        sb_end_pos = 1.0 - sb_height
        sb_end_pos = ceil(sb_end_pos * 10000) / 10000
        self.chat_scroll_lock = str(sb_y_pos) == str(sb_end_pos)


    def chat_send(self):
        if self.chat is None:
            self.chat_text.d_insert(tk.END, 'Connecting...\n')
            nickname = self.chat_input.get(1.0, tk.END).strip().replace(' ', '')
            if nickname:
                self.chat = IRC(queue=self.queue,
                                server=self.chat_settings['server'],
                                port=self.chat_settings['port'],
                                channel=self.chat_settings['channel'],
                                nickname=nickname)

                if self.chat.error:
                    self.chat_text.d_insert(tk.END, 'Failed to connect. Trying again.\n')
                    self.chat = None
                    self.root.after(2000, self.chat_send)
                else:
                    self.chat_log = ChatLog()
                    chat_process = Process(target=self.chat.start)
                    chat_process.start()
                    self.root.after(100, self.process_queue)


        else:
            if self.chat_log.prev_user() != self.chat.nickname:
                self.chat_text.d_insert(tk.END, '\n' + self.chat.nickname + '\n', 'user')

            msg = self.chat_input.get(1.0, tk.END).strip()
            self.chat.sendmsg(self.chat_settings['channel'], msg)
            self.chat_text.d_insert(tk.END, msg + '\n')
            chat_msg = ChatMessage(user=self.chat.nickname, body=msg)
            self.chat_log.add(chat_msg)

    def open_manually_enter_window(self):
        ManuallyEnterWindow(self)

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

    def open_text(self):
        sel = self.file_list.curselection()
        if len(sel) > 1:
            self.msg('Too many texts selected. (Limit: 1)')
        elif len(sel) == 0:
            self.msg('No texts selected.')
        else:
            tw = TextWindow(self, title=self.corpus.texts[sel[0]].title)
            tw.text.insert(1.0, self.corpus.texts[sel[0]])

    def remove(self):
        texts = self.file_list.curselection()
        for i in reversed(texts):
            del self.corpus.texts[i]
            self.file_list.delete(i)
        self.msg('{} texts removed.'.format(len(texts)))

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
                                args=(self.queue, fp, text, max_center_len))
            self.save_process.start()
            self.root.after(100, self.process_queue)

        elif fp.endswith('.html'):
            write_html(fp, text)

        elif fp.endswith('.xlsx'):
            save_options = SaveOptions(self.root, fp, text, tokens_left, msg=self.msg)

    def search_kp(self, event):
        self.search()

    def search(self, search_str=None):
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

        if search_str is None:
            search_str = self.search_var.get()

        p = Process(target=self.corpus.concordance, args=(search_str, conc_left, conc_right, self.conc_id))
        self.conc_processes.append(p)
        self.conc_id += 1
        p.start()
        self.root.after(100, self.process_queue)

    def reset(self):
        """Removes any data and clears the queue."""
        self.clear_queue()
        self.search_entry.delete(0, tk.END)
        del self.corpus
        self.corpus = Corpus(self.queue)
        self.file_list.delete(0, tk.END)

    def open_instructions_window(self):
        InstructionsWindow(self, self.instructions)


    def load_from_url(self):
        pass

    def load_files(self):
        """Loads texts from local files."""
        filenames = filedialog.askopenfilenames()


        m = self.corpus.load_texts(*filenames)
        self.msg(m)

    def msg(self, m):
        tag = ''
        if type(m) == Message:
            if m.added_texts:
                for uf in m.added_texts:
                    self.file_list.insert(tk.END, uf)

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
        else:
            if self.chat is not None:
                self.root.after(100, self.process_queue)

        if self.save_process and self.save_process.is_alive():
            self.root.after(100, self.process_queue)

        try:
            q_item = self.queue.get(0)
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

            elif type(q_item) is ChatMessage:
                if q_item.names_list:
                    self.names_text.d_delete(1.0, tk.END)
                    for nm in q_item.names_list:
                        self.names_text.d_insert(tk.END, nm, 'other')
                        self.names_text.d_insert(tk.END, ' ')
                elif q_item.connected_as:
                    self.chat_text.d_insert(tk.END, 'Connected as ' + q_item.connected_as + '\n')
                    self.chat.nickname = q_item.connected_as
                else:
                    if not self.chat_log or q_item.user and q_item.user != self.chat_log.prev_user():
                        self.chat_text.d_insert(tk.END, '\n' + q_item.user + '\n', 'other')
                    self.chat_text.d_insert(tk.END, q_item.body + '\n')
                    self.chat_log.add(q_item)
                    if self.chat_scroll_lock:
                        self.chat_text.see(tk.END)


            elif type(q_item) is list and type(q_item[0]) is Result:
                if q_item[0].r_id not in self.freq_list_windows.keys():
                    if q_item[0].rtype == 'Tokens':
                        view = 'Word List Window'
                    elif q_item[0].rtype == 'Ngrams':
                        view = 'Ngrams List Window'
                    else:
                        view = ''

                    self.freq_list_windows[q_item[0].r_id] = TextWindow(self, view=view, wrap='none', font=fm.ms_font)

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
                self.queue.get_nowait()
        except queue.Empty:
            pass

if __name__ == '__main__':
    GUI()