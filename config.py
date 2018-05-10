from os import environ


AUTH = environ.get('TWITCH_AUTH', None)
SERVER = 'irc.chat.twitch.tv'
PORT = 6667
NICK = 'sudokid'

PROJECT = 'We are building a custom Twitch chat bot using the Python STD and aiohttp!'
