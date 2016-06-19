import sqlite3


class Database:
    def __init__(self, name, tables):
        self.conn = sqlite3.connect(name)
        self.cursor = self.conn.cursor()

        for table in tables:
            self._create_table(table)

    def __del__(self):
        self.commit()
        self.conn.close()

    def _create_table(self, table):
        try:
            self.cursor.execute(table)
        except sqlite3.OperationalError:
            pass

    def execute(self, insert, values):
        try:
            self.cursor.execute(insert, values)
            return True
        except sqlite3.OperationalError:
            return False

    def fetchall(self):
        return self.cursor.fetchall()

    def into(self, insert, values=None):
        execute = [insert]
        if values: execute.append(values)
        try:
            self.cursor.execute(*execute)
            return True
        except sqlite3.OperationalError:
            return False

    def commit(self, *args, **kwargs):
        self.conn.commit(*args, **kwargs)

    def select_from(self, cmd):
        try:
            self.cursor.execute(cmd)
        except sqlite3.OperationalError:
            raise StopIteration("Could not read a cmd {}".format(cmd))
        rows = self.cursor.fetchall()
        yield from rows

    def get_single_record(self, cmd):
        try:
            self.cursor.execute(cmd)
        except sqlite3.OperationalError:
            raise ValueError("Could not fetch the last record")
        return self.cursor.fetchone()

    def get_all_records(self, cmd):
        try:
            self.cursor.execute(cmd)
        except sqlite3.OperationalError:
            raise ValueError("Could not fetch the last record")
        return self.cursor.fetchall()


if __name__ == "__main__":
    import time
    db = Database("/home/krzysztof/Programming/Python/Elvic/testDB_(copy).db", [])

    # insert = """INSERT INTO DataRecords(Date)
    # VALUES(?)"""
    # db.exec(insert, (time.ctime(),))
    # db.commit()
    for row in db.select_from("SELECT * FROM DataRecords;"):
        print(row)
    print("Last record")
    print(db.get_last_record("DataRecords", "ID_DataRecords"))

