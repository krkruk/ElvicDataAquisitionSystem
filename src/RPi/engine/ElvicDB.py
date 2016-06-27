import time
import sqlite3

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

DATARECORDS_INSERT_INTO = """INSERT INTO DataRecords(Date)
VALUES(?)"""

GPS_INSERT_INTO = """INSERT INTO GPS (ID_DataRecords, Time, Data)
VALUES(?,?,?)"""

POWER_INVERTER_INSERT_INTO = """INSERT INTO PowerInverter (ID_DataRecords, Time, Data)
VALUES(?,?,?)"""

DATARECORDS_ALL_ELEMENTS = """
SELECT * FROM DataRecords"""

GPS_ALL_ELEMENTS = """
SELECT * FROM GPS"""

POWER_INVERTER_ALL_ELEMENTS = """
SELECT * FROM PowerInverter"""

JOIN_DATARECORDS_GPS = """
SELECT DataRecords.Date, GPS.Time, GPS.Data
FROM DataRecords
INNER JOIN GPS
ON DataRecords.ID_DataRecords == GPS.ID_DataRecords
WHERE DataRecords.ID_DataRecords==?"""

JOIN_DATARECORDS_POWER_INVERTER = """
SELECT DataRecords.Date, PowerInverter.Time, PowerInverter.Data
FROM DataRecords
INNER JOIN PowerInverter
ON DataRecords.ID_DataRecords == PowerInverter.ID_DataRecords
WHERE DataRecords.ID_DataRecords==?"""


class ElvicDatabase:
    def __init__(self, name):
        """Initialize a database. Name - file name and/or directory"""
        self.data_records_current_id = -1
        try:
            self.db = sqlite3.connect(name)
        except sqlite3.OperationalError:
            with open("log.txt", 'a') as f:
                f.write("Could not open a database at time {}".format(time.time()))
            exit()
        self.cur = self.db.cursor()
        self._create_tables((CREATE_TABLE_POWERINVERTER,
                            CREATE_TABLE_GPS,
                            CREATE_TABLE_DATARECORDS))

    def __del__(self):
        self.db.commit()
        self.cur.close()
        self.db.close()

    def _create_tables(self, tables):
        """Creates tables based on iterable passed into the method. Any SQLite error
        is omited."""
        for table in tables:
            try:
                self.cur.execute(table)
            except sqlite3.OperationalError:
                pass

    def _execute(self, sql, vars=()):
        try:
            return self.cur.execute(sql, vars)
        except sqlite3.OperationalError:
            print("Execute error")

    def commit(self):
        self.db.commit()

    def insert_into_DataRecords(self, date=None):
        """Inserts a time value into DataRecords. Any new data inserted into
        the remaining tables will be associated with the time value just saved."""
        try:
            self.cur.execute(DATARECORDS_INSERT_INTO, ((date,) if date else (time.ctime(),)))
        except sqlite3.OperationalError as e:
            raise sqlite3.OperationalError(e)
        self.data_records_current_id = self.last_element_DataRecords()[0]

    def insert_into_gps(self, data):
        """Inserts binary 'data' into GPS table. Time in seconds is added automatically.
         The reference to DataRecords table is passed automatically. If it fails an IndexError
        exception is raised"""
        if self.data_records_current_id:
            data_into = (self.data_records_current_id, time.time(), data)
        else:
            raise IndexError("ID_DataRecords invalid: {}", self.data_records_current_id)
        self._execute(GPS_INSERT_INTO, data_into)

    def insert_into_power_inverter(self, data):
        """Inserts binary 'data' into PowerInverter table. Time in seconds is added automatically.
        The reference to DataRecords table is passed automatically. If it fails an IndexError
         exception is raised"""
        if self.data_records_current_id:
            data_into = (self.data_records_current_id, time.time(), data)
        else:
            raise IndexError("ID_DataRecords invalid: {}", self.data_records_current_id)
        self._execute(POWER_INVERTER_INSERT_INTO, data_into)

    def last_element_DataRecords(self):
        """Gets last element from DataRecords table."""
        self._execute(DATARECORDS_LAST_ELEMENT)
        return self.cur.fetchone()

    def list_DataRecords(self):
        """Lists all the values that are present in DataRecords table."""
        self._execute(DATARECORDS_ALL_ELEMENTS)
        return self.cur.fetchall()

    def list_GPS(self):
        """Lists all the values that are present in GPS table."""
        self._execute(GPS_ALL_ELEMENTS)
        return self.cur.fetchall()

    def list_PowerInverter(self):
        """Lists all the values that are present in PowerInverter table."""
        self._execute(POWER_INVERTER_ALL_ELEMENTS)
        return self.cur.fetchall()

    def join_DataRecords_with_GPS(self, id_datarecords):
        """Join DataRecords table with GPS table. See SQL for more details"""
        self._execute(JOIN_DATARECORDS_GPS, (id_datarecords,))
        return self.cur.fetchall()

    def join_DataRecords_with_PowerInverter(self, id_datarecords):
        """Join DataRecords table with PowerInverter table. See SQL for more details"""
        self._execute(JOIN_DATARECORDS_POWER_INVERTER, (id_datarecords,))
        return self.cur.fetchall()

if __name__ == "__main__":
    db = ElvicDatabase("elvicdb_test.db")
    for row in db.join_DataRecords_with_PowerInverter(4):
        print(row)
