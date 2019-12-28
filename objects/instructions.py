import tkinter as tk

class Instructions:
    def __init__(self):
        self.instructions = [
            ['Main Window', 'Welcome to the concordancing program'],
            ['Concordance Window', ''],
            ['Word List Window', ''],
            ['Ngrams List Window', '']
        ]

    def label(self, key, parent, **kwargs):
        for k, v in self.instructions:
            if key == k:
                return tk.Label(parent, text=v, **kwargs)
        else:
            return None
    def keys(self):
        return [a for a,b in self.instructions]

    def get(self , key=None):
        if key is None:
            return self.instructions
        else:
            for i, (item, _) in enumerate(self.instructions):
                if i == key or item == key:
                    return self.instructions[i][1]
            else:
                return ''

    def set(self, key, value):
        for i, (item, _) in enumerate(self.instructions):
            if key == i or key == item:
                self.instructions[i][1] = value