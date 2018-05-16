import sqlite3


class SQL:
    def __init__(self, db: str):
        self.conn = sqlite3.connect(db)
        self.db = self.conn.cursor()

    def close(self):
        self.conn.close()
