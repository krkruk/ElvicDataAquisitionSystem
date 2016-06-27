import sqlite3
import datetime
import time

CREATE_TABLE_DATARECORDS = """
CREATE TABLE DataRecords (
ID_DataRecords INTEGER PRIMARY KEY AUTOINCREMENT,
Date TEXT NOT NULL
);"""

CREATE_TABLE_GPS = """
CREATE TABLE GPS (
ID_GPS INTEGER PRIMARY KEY AUTOINCREMENT,
ID_DataRecords INTEGER NOT NULL,
Time REAL NOT NULL,
Data BLOB NOT NULL,
FOREIGN KEY(ID_DataRecords) REFERENCES DataRecords(ID_DataRecords)
);"""

CREATE_TABLE_POWERINVERTER = """
CREATE TABLE PowerInverter (
ID_PowerInverter INTEGER PRIMARY KEY AUTOINCREMENT,
ID_DataRecords INTEGER NOT NULL,
Time REAL NOT NULL,
Data BLOB NOT NULL,
FOREIGN KEY(ID_DataRecords) REFERENCES DataRecords(ID_DataRecords)
);"""

DATARECORDS_LAST_ELEMENT = """
SELECT * FROM DataRecords
ORDER BY ID_DataRecords DESC
LIMIT 1;
"""


def insert_into_datarecords(db, data):
    INSERT = """INSERT INTO DataRecords(Date)
    VALUES(?)"""
    db.execute(INSERT, data)


def insert_into_gps(db, data):
    INSERT = """INSERT INTO GPS (ID_DataRecords, Time, Data)
    VALUES(?,?,?)"""
    db.execute(INSERT, data)


def insert_into_power_inverter(db, data):
    INSERT = """INSERT INTO PowerInverter (ID_DataRecords, Time, Data)
    VALUES(?,?,?)"""
    db.execute(INSERT, data)


def create_table_safely(cursor):
    def create_table_with_try_statement(sql_cmd):
        try:
            cursor.execute(sql_cmd)
        except sqlite3.OperationalError as e:
            print(e)

    return create_table_with_try_statement


def populate_db(cur):
    for i in range(1, 31):
        time.sleep(1.2)
        insert_into_datarecords(cur, (time.ctime(),))
        for ii in range(100):
            insert_into_gps(cur, (i, time.time(), "hello world :) --- {}".format(ii).encode("ascii")))
        for iii in range(100):
            insert_into_power_inverter(cur, (i, time.time(), "power inverter here :) --- {}".format(iii).encode("ascii")))


def main():
    with sqlite3.connect("testDB.db") as db:
        cur = db.cursor()
        create_table = create_table_safely(cur)
        create_table(CREATE_TABLE_DATARECORDS)
        create_table(CREATE_TABLE_GPS)
        create_table(CREATE_TABLE_POWERINVERTER)

        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        print(cur.fetchall())

        populate_db(cur)
        db.commit()

if __name__ == "__main__":
    main()