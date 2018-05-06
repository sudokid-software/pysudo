import os
import asyncio
import random

import asyncio_redis as redis
import aiohttp

from irc import IRC


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
    r = await redis.Connection.create(host='localhost', port=6379)
    class_call = CustomSleep(r)

    asyncio.ensure_future(class_call.print_multiple_msg('Testing', 10))
    asyncio.ensure_future(class_call.print_chatters())

    counter = await class_call.r.get('counter')
    print('Counter:', counter)


if __name__ == '__main__':
    AUTH = os.environ.get('TWITCH_AUTH', None)
    SERVER = 'irc.chat.twitch.tv'
    PORT = 6667
    CHANNEL = 'sudokid'
    NICK = 'sudokid'

    irc = IRC(SERVER, PORT, NICK, CHANNEL, AUTH)


    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
