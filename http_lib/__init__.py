import logging
import urllib.request
from json import loads
from json.decoder import JSONDecodeError
# from http import HTTPStatus


logger = logging.getLogger(__name__)


def get(url, expected_status: int=200):
    with urllib.request.urlopen(url) as r:
        if expected_status == r.status:
            data = r.read()
            try:
                return loads(data)
            except JSONDecodeError:
                logging.exception('Unable to do JSONDecoding')
                return {'error': data}

        raise Exception('Invalid data in response. Status: %r, Data: %r' % (
            r.status, r.read()
        ))  # TODO create exception class
