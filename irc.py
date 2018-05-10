import logging
import socket
import asyncio


logger = logging.getLogger(__name__)


async def run(reader, writer):
    while True:
        data = await reader.read(100)
        print(data.decode())
        if data == 'PING :tmi.twitch.tv':
            await writer.write(b'PONG :tmi.twitch.tv\r\n')


async def irc_connect(server, port, nick, auth):
    reader, writer = await asyncio.open_connection(
        server, port, loop=asyncio.get_event_loop())

    password = f'PASS {auth}\r\n'.encode()
    nick = f'NICK {nick}\r\n'.encode()
    channel = f'JOIN #{nick}\r\n'.encode()

    writer.write(password)
    writer.write(nick)
    writer.write(channel)
    asyncio.get_event_loop().create_task(run(reader, writer))
