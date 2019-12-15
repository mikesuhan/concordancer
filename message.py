class Message:
    def __init__(self, *message, conc_finished=False, tag=''):
        self.conc_finished = conc_finished
        self.message = ' '.join(message)
        self.tag = tag
    def __repr__(self):
        return self.message
