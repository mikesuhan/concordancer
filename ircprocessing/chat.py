import socket
from random import randint

from .chatmessage import ChatMessage

class IRC:

    def __init__(self,
                 queue=None,
                 server="chat.freenode.net",
                 port=6667,
                 channel="#mikecool",
                 nickname="mikebot5000",
                 adminname="mikecool",
                 exitcode="bye"):

        print('IRC started')

        self.queue = queue
        self.server = server
        self.port = port
        self.channel = channel
        self.nickname = nickname
        self.adminname = adminname
        self.exitcode = exitcode
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
        self.join_chan(self.channel)

        self.stream()

    def set_nick(self):
        ircmsg = ''
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
                    self.nickname += str(randint(0, 9))
                    nickset = False
                elif '001 ' + self.nickname in ircmsg:
                    cm = ChatMessage(connected_as=self.nickname)
                    self.queue.put(cm)
                    break
            except socket.error:
                pass

    def join_chan(self, chan):  # join channel(s).
        self.ircsock.send(bytes("JOIN " + chan + "\n", "UTF-8"))
        name_list_string = '{u} @ {ch} :{u}'.format(u=self.nickname, ch=self.channel)
        joining = True
        while joining:
            try:
                ircmsgs = self.ircsock.recv(2048).decode("UTF-8")
                ircmsgs = ircmsgs.split('\n')
                for ircmsg in ircmsgs:
                    if name_list_string in ircmsg:
                        # example names list when other users are in channel
                        # :weber.freenode.net 353 hardvark @ #mikecool :hardvark mikecool
                        names = ircmsg.strip().split(':' + self.nickname)
                        if names [-1] == '':
                            self.names = []
                        else:
                           self.names = names[-1].split(' ')

                        msg = ChatMessage(names_list=self.names)
                        self.queue.put(msg)
                        joining = False
                    else:
                        print(ircmsg)

            except socket.error:
                pass

        print('JOINED', self.channel)



    def ping(self):
        """respond to server Pings."""
        self.ircsock.send(bytes("PONG :pingis\n", "UTF-8"))

    def sendmsg(self, target, msg):  # sends messages to the target.
        self.ircsock.send(bytes("PRIVMSG " + target + " :" + msg + "\n", "UTF-8"))

    def stream(self):
        while 1:
            try:
                ircmsgs = self.ircsock.recv(2048).decode("UTF-8")

                for ircmsg in ircmsgs.split('\n'):
                    if 'PRIVMSG' in ircmsg:

                        if 'PRIVMSG ' + self.channel in ircmsg:
                            if self.queue:
                                m = ChatMessage(raw_message=ircmsg, channel=self.channel)
                                self.queue.put(m)
                                print(ircmsg)

                    elif ' JOIN ' + self.channel in ircmsg:
                        # example join message
                        # :mikecool54!5565c0a2@gateway/web/cgi-irc/kiwiirc.com/ip.85.101.192.162 JOIN #mikecool
                        username = ircmsg.split('!')[0][1:].strip()
                        self.names.append(username)
                        self.names = list(sorted(self.names))
                        self.queue.put(ChatMessage(names_list=self.names))

                    elif ' QUIT :' in ircmsg:
                        # example quit message
                        # :mikecool100!5565c0a2@gateway/web/cgi-irc/kiwiirc.com/ip.85.101.192.162 QUIT :Remote host closed the connection
                        username = ircmsg.split('!')[0][1:].strip()
                        self.names = [n for n in self.names if n != username]
                        print(username, self.names)
                        self.queue.put(ChatMessage(names_list=self.names))

                    elif ircmsg.startswith("PING :") != -1:
                        self.ping()
                        print(ircmsg)

                    elif ircmsg.strip():
                        print(ircmsg)

            except socket.error:
                pass