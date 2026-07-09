import sqlite3

import sys


class SqliteDB:
    def __init__(self, table, db_uri='petra.db'):
        con = sqlite3.connect(db_uri)
        cur = con.cursor()

        if table == "transports":
            self.table = "transports"

            try:
                cur.execute('''CREATE TABLE transports
                            (id int, data text)''')
            except sqlite3.OperationalError:
                print("Table already exists", file=sys.stderr)

        elif table == "users":
            self.table = "users"

            try:
                cur.execute('''CREATE TABLE users
                            (id int, data text)''')
            except sqlite3.OperationalError:
                print("Table already exists", file=sys.stderr)

        else:
            print("Wrong table name", file=sys.stderr)

        con.commit()
        con.close()

    def select_one(self, id):
        con = sqlite3.connect('petra.db')
        cur = con.cursor()
        if self.table == "transports":
            cur.execute("SELECT * FROM transports WHERE id = (?)",
                        (id,))
        else:
            print("Wrong table name", file=sys.stderr)

        entry = cur.fetchall()

        return {"_id": entry[0][0], "data": entry[0][1]}

        # con.close()

    def insert(self, data):
        con = sqlite3.connect('petra.db')
        cur = con.cursor()
        cur.execute("INSERT INTO transports (id, data) VALUES (1, 'test')")
        # (self.table, data["_id"], data["data"]))
        print("test", file=sys.stderr)
        con.commit()
        con.close()

    # def __del__(self):
        # con.close()
