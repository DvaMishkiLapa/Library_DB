import sqlite3

class DBManager():
    def __init__(self, path):
        try:
            self.connect = sqlite3.connect(path)
        except sqlite3.Error as e:
            print(e)
        self.cursor = self.connect.cursor()

    def query(self, arg):
        self.cursor.execute(arg)
        self.connect.commit()
        return self.cursor

    def get_tables_names(self):
        return self.query("SELECT name FROM sqlite_master WHERE type = 'table'")

    def get_columns_names(self, table):
        self.query("select * from {}".format(table))
        columns = list(map(lambda x: x[0], self.cursor.description))
        return columns

    def get_rows(self, table):
        return self.query("select * from {}".format(table))

    def __del__(self):
        self.connect.close()
