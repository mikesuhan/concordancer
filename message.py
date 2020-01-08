class Message:
    def __init__(self, *message, conc_finished=False, tag='', added_texts=None):
        self.conc_finished = conc_finished
        self.message = ' '.join(message)
        self.tag = tag
        self.added_texts = added_texts
    def __repr__(self):
        return self.message
