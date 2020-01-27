from json import loads
import tkinter as tk

class Instructions:
    def __init__(self, json_instructions=None, instructions=None):
        # Load from file or string
        if json_instructions:
            if json_instructions.endswith('.json'):
                with open(json_instructions) as f:
                    json_instructions = f.read()
            self.instructions = loads(json_instructions)

        # Set to default
        elif instructions:
            self.instructions = instructions
        else:
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