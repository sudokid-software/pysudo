class Parser:
    def __init__(self, msg: bytes):
        decoded_msg = msg.decode()
        if not decoded_msg.startswith('@'):
            self.valid = False
            return

        self.valid = True
        split_msg = msg.decode().lstrip('@').split(';')

        for record in split_msg:
            key, value = self.get_value(record)

            if key == 'user_type':
                try:
                    self.msg = value.split(':', 2)[2]
                except IndexError:
                    self.msg = ''
            else:
                setattr(self, key, value)

    @staticmethod
    def get_value(msg):
        key, value = msg.split('=', 1)
        return key.replace('-', '_'), value
