from unittest import TestCase

from twitch_irc_parser import Parser


class TestParser(TestCase):
    def test_random_string(self):
        with open('test_data.txt', 'rb') as file:
            test_msgs = file.readlines()

        # [print(dir(Parser(msg[2:-1]))) for msg in test_msgs]
        [Parser(msg[2:-1]) for msg in test_msgs]
