import logging


logger = logging.getLogger(__name__)


def parse_raw_msg(raw_msg: str):
    info, msg = raw_msg.split(':', 2)[1:]
    user = info.split("!", 1)[0]
    return user, msg


def send_msg(msg: str, writer, channel):
    print('sending message')
    formatted_msg = f'PRIVMSG #{channel} :{msg}\r\n'

    writer.write(formatted_msg.encode())
