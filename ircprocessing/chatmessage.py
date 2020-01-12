from time import gmtime, strftime

class ChatMessage:
    def __init__(self, user=None, body=None, channel=None, raw_message=None, names_list=None, connected_as=None):
        self.time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        self.channel = channel
        self.names_list = names_list
        self.connected_as = connected_as

        if raw_message:
            self.raw_message = raw_message
            self.body = raw_message.split('PRIVMSG ' + self.channel + ' :')[-1].strip()
            self.user = raw_message[1:].split('!')[0]
        else:
            self.user = user
            self.body = body

        self.message = '{u}: {b}'.format(u=self.user, b=self.body)

    def __repr__(self):
        return self.raw_message
