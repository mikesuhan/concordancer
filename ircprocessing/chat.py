import socket
from random import randint
from re import findall

from .chatmessage import ChatMessage

class IRC:

    def __init__(self, queue, server, channel, port, nickname):

        print('IRC started')

        self.queue = queue
        self.server = server
        self.port = port
        self.channel = channel
        self.nickname = nickname
        self.nick_registered = False
        self.names = []

        try:
            self.ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.ircsock.connect((server, port))
            self.ircsock.setblocking(0)
            self.error = False
        except socket.gaierror:
            self.error = True

    def start(self):
        print(self.server, self.port)
        self.ircsock.send(bytes("USER " + self.nickname + " " + self.nickname + " " + self.nickname + " " + self.nickname + "\n",
                   "UTF-8"))
        self.set_nick()
        self.join_chan()

        self.stream()

    def set_nick(self):
        nickset = False
        while True:
            if not nickset:
                self.ircsock.send(bytes("NICK " + self.nickname + "\n", "UTF-8"))
                nickset = True

            try:
                ircmsg = self.ircsock.recv(2048).decode("UTF-8")
                if self.nickname + ' :Nickname is already in use.' in ircmsg:
                    # example nickname already in use message
                    # :weber.freenode.net 433 * mikecool :Nickname is already in use.
                    self.nickname += str(randint(10, 1000))
                    nickset = False
                elif '001 ' + self.nickname in ircmsg:
                    break
            except socket.error:
                pass

    def join_chan(self):  # join channel(s).
        self.ircsock.send(bytes("JOIN " + self.channel + "\n", "UTF-8"))

        joining = True

        while joining:
            try:
                ircmsgs = self.ircsock.recv(2048).decode("UTF-8")
                ircmsgs = ircmsgs.split('\n')
                for ircmsg in ircmsgs:

                    if findall('\s@\s#[^\s]+\s:', ircmsg):
                        # example names list when other users are in channel
                        # :weber.freenode.net 353 hardvark @ #mikecool :hardvark mikecool
                        names = ircmsg.strip().replace('@', '').split(':' + self.nickname)
                        if names [-1] == '':
                            self.names = []
                        else:
                           self.names = names[-1].split(' ')

                        if self.names:
                            msg = ChatMessage(names_list=self.names)
                            self.queue.put(msg)

                        joining = False

                    elif ':This nickname is registered.' in ircmsg:
                        # example
                        # :NickServ!NickServ@services. NOTICE bob7 :This nickname is registered. Please choose a different nickname, or identify via /msg NickServ identify <password>.
                        self.nick_registered = True


                    else:
                        print(self.nickname, self.channel, 'join_chan:', ircmsg)

            except socket.error:
                pass

        print('YOU HAVE JOINED', self.channel)



    def ping(self):
        """respond to server Pings."""
        self.ircsock.send(bytes("PONG :pingis\n", "UTF-8"))

    def sendmsg(self, target, msg):  # sends messages to the target.
        self.ircsock.send(bytes("PRIVMSG " + target + " :" + msg + "\n", "UTF-8"))

    def stream(self):
        if self.nick_registered:
            self.nickname += str(randint(100, 1000))
            self.ircsock.send(bytes("NICK " + self.nickname + "\n", "UTF-8"))
            self.nick_registered = False

        cm = ChatMessage(connected_as=self.nickname)
        self.queue.put(cm)
        while 1:
            try:
                ircmsgs = self.ircsock.recv(2048).decode("UTF-8")

                for ircmsg in ircmsgs.split('\n'):
                    if 'PRIVMSG #' in ircmsg:
                        m = ChatMessage(raw_message=ircmsg, channel=self.channel)
                        self.queue.put(m)
                        print(ircmsg)

                    elif ' JOIN #' in ircmsg:
                        # example join message
                        # :mikecool54!5565c0a2@gateway/web/cgi-irc/kiwiirc.com/ip.85.101.192.162 JOIN #mikecool
                        username = ircmsg.split('!')[0][1:].strip()
                        print(username, 'HAS JOINED')
                        self.names.append(username)
                        self.names = list(sorted(self.names))
                        self.queue.put(ChatMessage(names_list=self.names))

                    elif ' QUIT :' in ircmsg:
                        # example quit message
                        # :mikecool100!5565c0a2@gateway/web/cgi-irc/kiwiirc.com/ip.85.101.192.162 QUIT :Remote host closed the connection
                        username = ircmsg.split('!')[0][1:].strip()
                        self.names = [n for n in self.names if n != username]
                        self.queue.put(ChatMessage(names_list=self.names))

                    elif ':This nickname is registered.' in ircmsg:
                        # This is already handled when joining the channel. It's unlikely that the original
                        # nickname with a random number from 100 to 1000 will be registered. But just in case...
                        self.nickname += str(randint(100, 1000))
                        self.ircsock.send(bytes("NICK " + self.nickname + "\n", "UTF-8"))
                        self.nick_registered = False


                    elif ircmsg.startswith("PING :") != -1:
                        self.ping()
                        print(ircmsg)

                    elif ircmsg.strip():
                        print('stream():', ircmsg)

            except socket.error:
                pass