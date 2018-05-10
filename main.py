import asyncio
import logging
import random

from chatters import get_chatters
from config import AUTH, SERVER, PORT, NICK, PROJECT
from irc import send_msg, parse_raw_msg


logger = logging.getLogger(__name__)


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

    counter = 0

    while True:
        raw_msg = (await reader.readline()).decode().strip()

        counter += 1
        if counter == 10:
            asyncio.get_event_loop().create_task(
                get_chatters())
            counter = 0

        if not raw_msg:
            continue

        if raw_msg == 'PING :tmi.twitch.tv':
            writer.write(b'PONG :tmi.twitch.tv\r\n')
            continue

        try:
            user, msg = parse_raw_msg(raw_msg)
            print(user, msg)
        except ValueError:
            continue

        if msg.startswith('!crashcode'):
            response = random.choice([
                'You can not crash me!',
                'You man not crash me!'
            ])
            send_msg(response, writer, NICK)
        elif msg.startswith('!project'):
            send_msg(PROJECT, writer, NICK)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print('exiting')
    loop.close()
