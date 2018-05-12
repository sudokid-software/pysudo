import asyncio
import logging
import ssl

from config import AUTH, SERVER, PORT, NICK
from irc import IRCClientProtocol


logger = logging.getLogger(__name__)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    client_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    client_context.get_ciphers()

    coro = loop.create_connection(
        lambda AUTH=AUTH: IRCClientProtocol(loop=loop, auth=AUTH, nick=NICK),
        SERVER, PORT, ssl=client_context)

    del AUTH

    loop.run_until_complete(coro)
    loop.run_forever()
    loop.close()
