import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from os import path
import sys
import formatting as fm
from objects.fancybutton import FancyButton
from objects.fancyentry import FancyEntry
from textprocessing.msexcel import write_xlsx
from xlsxwriter.exceptions import FileCreateError


class SaveOptions(tk.Toplevel):

    def __init__(self, parent, filepath, text, tokens_left, msg,  *args, **kwargs):
        tk.Toplevel.__init__(self, parent, *args, **kwargs)

        self.filepath = filepath
        self.text = text
        self.tokens_left = tokens_left
        self.msg = msg

        self.title('Excel Format Options')
        self.geometry('325x175')

        self.radio_value = tk.IntVar()
        self.entry_value = tk.StringVar()

        top_frame = tk.Frame(self, width=300)

        fp_entry = FancyEntry(top_frame,
                              width=30,
                              font=fm.text_font,
                              background=fm.text_bg,
                              foreground=fm.text_fg,
                              textvariable=self.entry_value)
        fp_entry.pack(side=tk.LEFT)
        self.entry_value.set(filepath)

        file_select_btn = tk.Button(top_frame, text='...', command=self.select_path)
        file_select_btn.pack(side=tk.RIGHT, padx=5)
        file_select_btn.config(height=1, width=10)

        top_frame.pack(side=tk.TOP, padx=10, pady=20)

        heading = tk.Label(self,
                    text="Excel Format Options",
                    justify=tk.LEFT,
                    padx=20)
        heading.pack(side=tk.TOP)

        opt1 = tk.Radiobutton(self,
                    text="3 cells per row",
                    padx=20,
                    variable=self.radio_value,
                    value=1)
        opt1.select()
        opt1.pack(side=tk.TOP)

        opt2 = tk.Radiobutton(self,
                   text="1 word per cell",
                   padx=20,
                   variable=self.radio_value,
                   value=2)
        opt2.pack(side=tk.TOP)

        btn_frame = tk.Frame(self)

        cancel_button = FancyButton(btn_frame, text='Cancel', command=self.destroy)
        cancel_button.pack(side=tk.LEFT)

        save_button = FancyButton(btn_frame, text='Save'.center(len('Cancel')), command=self.save)
        save_button.pack(side=tk.RIGHT)

        btn_frame.pack(side=tk.BOTTOM, pady=10)


    def save(self):
        try:
            fp = self.entry_value.get()

            folder = path.split(fp)[0]

            if folder is '' or path.exists(folder):

                if fp:
                    if self.radio_value.get() == 1:
                        write_xlsx(fp, self.text)
                    else:
                        write_xlsx(self.filepath, self.text, self.tokens_left)

                    self.msg('Concordance lines saved as ' + fp)
                    self.destroy()

                else:
                    messagebox.showerror('Error', 'Please enter a filename.')
            else:
                messagebox.showerror('Error', folder + ' is not a directory.')
        except FileCreateError as e:
            messagebox.showerror('Error', e)

    def select_path(self):
        self.entry_value.set(filedialog.asksaveasfilename(filetypes=(('Excel', '.xlsx'),)) + '.xlsx')
        self.lift()


