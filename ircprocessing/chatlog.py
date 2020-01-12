from .chatmessage import ChatMessage

class ChatLog:
    def __init__(self):
        self.log = []

    def add(self, *args):
        if [a for a in args if a is not type(ChatMessage)]:
            assert 'Arguments must be ChatMessage objects.'

        for arg in args:
            self.log.append(arg)

    def prev_user(self):
        if len(self.log) > 0:
            return self.log[-1].user
        else:
            return ''

    def to_string(self, users=True, times=False):
        messages = []
        for chat_message in self.log:
            m = chat_message.body
            if users:
                m = '{u}: {m}'.format(u=chat_message.user, m=m)
            if times:
                m = '[{t}] {m}'.format(t=chat_message.time, m=m)

            messages.append(m)

        return '\n'.join(messages)

    def save(self, filepath, **kwargs):
        content = self.to_string(**kwargs)
        with open(filepath, 'w', encoding='UTF-8') as f:
            f.write(content)
