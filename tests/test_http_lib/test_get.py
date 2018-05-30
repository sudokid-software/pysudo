from unittest import TestCase
import asyncio

from http_lib import get


# class TestGet(TestCase):
#     def setUp(self):
#         # self.loop = asyncio.get_event_loop()
#         pass
#
#     def test_get_with_data(self):
#         # response = self.loop.run_until_complete(get('http://example.com/'))
#         self.assertIn(
#             b'<!doctype html>\n<html>\n<head>\n    <title>Example Domain</title>\n\n'.decode(),
#             get('http://example.com').decode()
#         )
