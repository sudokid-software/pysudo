import os
import asyncio
import random

import asyncio_redis as redis
import aiohttp

import irc


class CustomSleep:
    def __init__(self, r):
        self.r = r

    async def print_msg(self, msg):
        timer = random.randrange(10)
        await asyncio.sleep(timer)
        print(msg, timer)

    async def print_multiple_msg(self, msg, number):
        print(f'starting print_msg {msg} {number}')
        for i in range(number):
            asyncio.ensure_future(self.print_msg(f'{msg} - {i}'))

    @staticmethod
    async def print_chatters():
        async with aiohttp.ClientSession() as session:
            async with session.get('http://tmi.twitch.tv/group/user/sudokid/chatters', timeout=25) as resp:
                print(resp.status)
                if resp.status != 200:
                    print(await resp.text())
                else:
                    print(await resp.json())


async def main():
    print('starting')
    reader, writer = await asyncio.open_connection(
        SERVER, PORT, loop=asyncio.get_event_loop())

    password = f'PASS {AUTH}\r\n'.encode()
    nick = f'NICK {NICK}\r\n'.encode()
    channel = f'JOIN #{NICK}\r\n'.encode()

    writer.write(password)
    writer.write(nick)
    writer.write(channel)

    while True:
        raw_msg = (await reader.readline()).decode().strip()
        print(raw_msg)

        if not raw_msg:
            continue

        if raw_msg == 'PING :tmi.twitch.tv':
            writer.write(b'PONG :tmi.twitch.tv\r\n')


if __name__ == '__main__':
    AUTH = os.environ.get('TWITCH_AUTH', None)
    SERVER = 'irc.chat.twitch.tv'
    PORT = 6667
    NICK = 'sudokid'

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()
