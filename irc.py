import asyncio
import logging
import random
import secrets

import response_msgs


logger = logging.getLogger(__name__)


class IRCClientProtocol(asyncio.Protocol):
    def __init__(self, loop, auth, nick):
        self.loop = loop
        self.transport = None
        self.auth = auth
        self.nick = nick

        self.mods = {
            'sudokid',
        }

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

    def data_received(self, data):
        if data == b'PING :tmi.twitch.tv':
            self.transport.write(b'PONG :tmi.twitch.tv\r\n')

        raw_msg = data.decode()

        try:
            user, msg = self.parse_raw_msg(raw_msg)
            print(user, msg)
        except ValueError:
            return

        if msg.startswith('!crashcode'):
            response = random.choice([
                'You can not crash me!',
                'You man not crash me!'
            ])
            self.send_msg(response)

        elif msg.startswith('!chickenwings'):
            self.send_msg(response_msgs.chicken_wings)

        elif msg.startswith('!project'):
            self.send_msg(response_msgs.project)

        elif msg.startswith('!discord'):
            self.send_msg(response_msgs.discord)

        elif msg.startswith('!github'):
            self.send_msg(response_msgs.github)

        elif msg.startswith('!babby'):
            self.send_msg(response_msgs.babby)

        elif msg.startswith('!senpai'):
            self.send_msg(random.choice(response_msgs.senpai))

        elif msg.startswith('!help') or msg.startswith('!man'):
            [self.send_msg(response) for response in response_msgs.help]

        elif msg.startswith('!Initiate_Self_Destruction_Protocol_803'):
            [self.send_msg(response) for response in response_msgs.protocol_803]

        elif msg.startswith('!addmod'):
            self.add_mod(user, msg)

        elif msg.startswith('!emotes'):
            self.send_msg(response_msgs.emotes)

        elif msg.startswith('!roll'):
            self.send_msg(
                'You rolled a ' +
                str(secrets.randbelow(101)))

    def check_user(self, user):
        return user in self.mods

    def add_mod(self, requester, msg):
        user = msg.split(' ')[1]
        if self.check_user(requester):
            self.mods.add(user.lower())
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
