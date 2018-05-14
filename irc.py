import asyncio
import logging
import secrets
from time import sleep

import response_msgs
from http_lib import get


logger = logging.getLogger(__name__)


class IRCClientProtocol(asyncio.Protocol):
    def __init__(self, loop, auth, nick):
        self.loop = loop
        self.transport = None
        self.auth = auth
        self.nick = nick

        self.votes = {}
        self.viewers_voted = set()

        self.suggestions = []

        self.random_viewer_ban_list = {
            'sudokid',
            'electricalskateboard'
        }

        self.admin = {
            'sudokid',
            'ceaser_gaming',
        }
        self.mods = {
            'sudokid',
        }
        self.viewers = set()

    def connection_made(self, transport):
        self.transport = transport

        password = f'PASS {self.auth}\r\n'.encode()
        del self.auth

        nick = f'NICK {self.nick}\r\n'.encode()
        channel = f'JOIN #{self.nick}\r\n'.encode()

        transport.write(password)
        del password

        transport.write(nick)
        transport.write(channel)

        self.update_viewers('self.nick')

        self.send_msg('Connected')

    def data_received(self, data):
        if data == b'PING :tmi.twitch.tv':
            print(data)
            self.transport.write(b'PONG :tmi.twitch.tv\r\n')

        raw_msg = data.decode()

        try:
            user, msg = self.parse_raw_msg(raw_msg)
            print(user, msg)
        except ValueError:
            return

        if msg == '!crashcode':
            response = secrets.choice([
                'You can not crash me!',
                'You man not crash me!'
            ])
            self.send_msg(response)

        elif msg == '!chickenwings':
            self.send_msg(response_msgs.chicken_wings)

        elif msg == '!project':
            self.send_msg(response_msgs.project)

        elif msg == '!discord':
            self.send_msg(response_msgs.discord)

        elif msg == '!github':
            self.send_msg(response_msgs.github)

        elif msg == '!babby':
            self.send_msg(response_msgs.babby)

        elif msg.startswith('!senpai'):
            self.send_msg(secrets.choice(response_msgs.senpai))

        elif msg.startswith('!help') or msg.startswith('!man'):
            [self.send_msg(response) for response in response_msgs.help]

        elif msg == '!Initiate_Self_Destruction_Protocol_803' or msg == '!InitiateSelfDestructProtocol803':
            [self.send_msg(response) for response in response_msgs.protocol_803]

        elif msg.startswith('!addmod'):
            self.add_mod(user, msg)

        elif msg == '!emotes':
            self.send_msg(response_msgs.emotes)

        elif msg == '!roll':
            self.send_msg(
                'You rolled a ' +
                str(secrets.randbelow(101)))

        elif msg == '!update_viewers':
            self.update_viewers(user)

        elif msg == '!random_viewer':
            self.random_viewer(user)

        elif msg == '!sr hawks and eagles':
            number = secrets.randbelow(31)
            self.send_msg(
                response_msgs.hawks_and_eagles * number)
            self.send_msg(f'{number} Hawks and Eagles are attacking {user}')

        elif msg == '!atom':
            self.send_msg(response_msgs.atom)

        elif msg == '!vote':
            self.vote(user, msg)

        elif msg == '!vote_reset':
            self.vote_reset(user)

        elif msg.startswith('!start_vote'):
            self.start_vote(user, msg)

        elif msg.startswith('!vote'):
            self.vote(user, msg)

        elif msg == '!end_vote':
            self.end_vote(user)

        elif msg.startswith('!suggest'):
            self.suggest(msg)

        elif msg == '!reset_suggestions':
            self.reset_suggestions(user)

    def suggest(self, msg):
        suggestion = msg[9:]

        self.suggestions.append(suggestion)
        self.send_msg(f'The suggestion: {suggestion}')

    def reset_suggestions(self, user):
        if not self.check_user(user):
            return

        self.suggestions = []
        self.send_msg('Suggestions have been reset!')

    def vote_reset(self, user):
        if not self.check_user(user):
            return

        self.viewers_voted = set()
        self.votes = {}
        self.transport.write('The vote has been reset!')

    def start_vote(self, user, msg):
        if user != self.nick:
            return

        choices = msg.split(' ')[1:]

        self.votes = {choice: 0 for choice in choices}

        self.send_msg('Your vote is ready!')
        self.send_msg('Please type in !vote "CHOICE" to vote')
        self.send_msg('The choices are as follows')
        for choice in choices:
            self.send_msg(f'!vote {choice}')

    def vote(self, user, msg):
        if user in self.viewers_voted:
            self.send_msg(f'{user} you have already voted!')
            return

        vote = msg[6:]
        if vote not in self.votes:
            self.send_msg(f'{user} you didn\'t provide a valid vote!')
            return

        self.viewers_voted.add(user)
        self.votes[vote] += 1
        self.send_msg(f'{user} you have voted for {vote}!')

    def end_vote(self, user):
        if not self.check_user(user):
            return

        vote = None
        value = 0
        for k, v in self.votes.items():
            if v > value:
                value = v
                vote = k

        self.send_msg(f'{vote} has won with a total of {value} votes!')

    def random_viewer(self, user):
        if not self.check_user(user):
            print(f'{user} are not a valid mod')
            return

        if len(self.viewers) <= 0:
            self.update_viewers(user)

        viewers = list(self.viewers - {'sudokid'})

        r_user = secrets.choice(viewers)

        self.send_msg(f'{r_user} was selected!')

    def update_viewers(self, user):
        print(user)
        if not self.check_user(user):
            return

        response = None
        chatters = None
        counter = 0
        while chatters is None or counter == 100:
            response = get(
                'http://tmi.twitch.tv/group/user/sudokid/chatters')
            chatters = response.get('chatters', None)
            print(response)
            counter += 1
            sleep(10)

        mods = set(response.get('chatters', {}).get('moderators', []))
        viewers = set(response.get(
            'chatters', {}).get('viewers', []))

        self.mods |= mods
        self.viewers |= mods
        self.viewers |= viewers

        print('Mods:', self.mods)
        print('Viewers:', self.viewers)
        print('Viewers and mods have been updated')

    def check_user(self, user):
        return user in self.mods

    def add_mod(self, requester, msg):
        try:
            user = msg.split(' ')[1]
        except IndexError:
            return self.send_msg('You must provide a username!')

        if self.check_user(requester):
            self.mods.add(user.lower())
            self.send_msg(response_msgs.addmod.format(user=user))
        else:
            self.send_msg(response_msgs.youre_not_a_mod.format(
                user=requester))

    def remove_mod(self, requester, msg):
        try:
            user = msg.split(' ')[1]
        except IndexError:
            return self.send_msg('You must provide a username!')

        if requester in self.admin:
            self.mods.remove(user.lower())
            self.send_msg(response_msgs.addmod.format(user=user))
        else:
            self.send_msg(response_msgs.youre_not_a_mod.format(
                user=requester))

    def connection_list(self, _exc):
        print('The server closed the connection')
        print('Stop the event loop')
        self.loop.stop()

    @staticmethod
    def parse_raw_msg(raw_msg: str):
        info, msg = raw_msg.split(':', 2)[1:]
        user = info.split("!", 1)[0]
        return user, msg.strip()

    def send_msg(self, msg: str):
        print('sending message: %s' % msg)
        formatted_msg = f'PRIVMSG #{self.nick} :{msg}\r\n'

        self.transport.write(formatted_msg.encode())
