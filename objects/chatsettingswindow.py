import tkinter as tk
from random import choice
import string

from objects.fancyentry import FancyEntry
from objects.fancybutton import FancyButton

import formatting as fm

class ChatSettingsWindow(tk.Toplevel):
    def __init__(self, parent, settings, *args, **kwargs):
        tk.Toplevel.__init__(self, parent, *args, **kwargs)
        self.geometry('340x110')
        self.title('Chat Settings')
        self.settings = settings

        r = 0

        tk.Label(self, text='IRC Connection Information').grid(row=r, column=0, columnspan=4, sticky=tk.EW, pady=fm.pady*2)

        r += 1

        self.channel_var = tk.StringVar(value=settings['channel'])
        tk.Label(self, text='Channel').grid(row=r, column=0, sticky=tk.W, padx=fm.padx, pady=fm.pady)
        self.channel_entry = FancyEntry(self, width=33, background=fm.white, font=fm.settings_font, textvariable=self.channel_var)
        self.channel_entry.grid(row=r, column=1, columnspan=3, sticky=tk.W, padx=fm.padx, pady=fm.pady)

        r += 1

        tk.Label(self, text='Server').grid(row=r, column=0, sticky=tk.W, padx=fm.padx, pady=fm.pady)
        self.server_var = tk.StringVar(value=settings['server'])
        self.server_entry = FancyEntry(self, width=20, background=fm.white, textvariable=self.server_var, font=fm.settings_font)
        self.server_entry.grid(row=r, column=1, sticky=tk.W, padx=fm.padx, pady=fm.pady)


        tk.Label(self, text='Port').grid(row=r, column=2, sticky=tk.W, padx=fm.padx, pady=fm.pady)
        self.port_var = tk.StringVar(value=str(settings['port']))
        self.port_entry = FancyEntry(self, width=5, background=fm.white, textvariable=self.port_var, font=fm.settings_font)
        self.port_entry.grid(row=r, column=3, sticky=tk.E, padx=fm.padx, pady=fm.pady)

        r += 1

        button_frame = tk.Frame(self)
        cancel_button = FancyButton(button_frame, text='Cancel', command=self.destroy)
        cancel_button.pack(side=tk.LEFT)
        save_button = FancyButton(button_frame, text='Save', command=self.save)
        save_button.pack(side=tk.LEFT)
        button_frame.grid(row=r, column=0, columnspan=4, sticky=tk.E, padx=fm.padx, pady=fm.pady*2)

    def save(self):
        self.settings['channel'] = self.channel_var.get()
        self.settings['server'] = self.server_var.get()
        self.settings['port'] = self.port_var.get()

        try:
            self.settings['port'] = int(self.settings['port'])
        except ValueError:
            print('Port must be number')

        self.destroy()