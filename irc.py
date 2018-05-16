import asyncio
import logging
import secrets

import response_msgs
from commands import commands


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

        commands['update_viewers'](self, self.nick, '')

        self.send_msg('Connected')

    def data_received(self, data):
        print(data)
        if data == b'PING :tmi.twitch.tv':
            self.transport.write(b'PONG :tmi.twitch.tv\r\n')

        raw_msg = data.decode()

        try:
            user, msg = self.parse_raw_msg(raw_msg)
        except ValueError:
            return

        if msg[0] != '!':
            return

        if msg[1:] in response_msgs.canned_response:
            [self.send_msg(x) for x in response_msgs.canned_response[msg[1:]]]
            return

        if msg[1:] in response_msgs.random_response:
            self.send_msg(
                secrets.choice(
                    response_msgs.random_response[msg[1:]]).format(user=user))
            return

        command = msg[1:].split(' ', 1)[0]
        if command in commands:
            try:
                commands[command](self, user, msg)
            except TypeError:
                pass
            return

    def check_user(self, user):
        return user in self.mods

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
