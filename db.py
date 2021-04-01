"""SQL shenanigans [DEPLOY]

At any given stop and time, there are two options for connectivity:
    - The next stop on the same line
    - The next bus at the same stop

Accordingly the stoptimes table is indexed in the following ways:
    - trip_id, stop_sequence
    - stop_id, departure_time

Note that times should be padded with zeroes to fit 8 characters.
i.e.
7:23:21 -> 07:23:21

Example usage:

Run init_db() once to create the transit database and add all stop times in a table 'stoptimes'.
Further development of this module, should that happen, will include other tables.

After, you can query the database using the QueryDB object.

q = QueryDB()
q.get('stoptimes', columns=('trip_id', 'departure_time', 'stop_id'), conditions="stop_id='1277' AND departure_time>'22:00:00'")
q.close()
"""

import os
import sqlite3


def init_db() -> bool:
    """If transit.db does not exist, create this database. Otherwise do nothing.
    Returns true if operation succeeds. Else false, and error message is printed to console.

    Hmm i realized whether or not the file exists is actually not a good check for if the
    database exists/is populated. Will revisit.
    TODO: make checking if db exists better
    """
    if not os.path.isfile('transit.db'):
        try:
            con = sqlite3.connect('transit.db')

            con.execute('''CREATE TABLE IF NOT EXISTS stoptimes 
                            (trip_id, arrival_time, departure_time, stop_id, stop_sequence, 
                            stop_headsign, pickup_type, drop_off_type, shape_dist_traveled)''')

        # create database
            _insert_st_file('data/stop_times_1.txt', 'stoptimes', con)
            _insert_st_file('data/stop_times_2.txt', 'stoptimes', con)
            _insert_st_file('data/stop_times_3.txt', 'stoptimes', con)
        except Exception as e:
            print(e)
            return False

        # index
        con.execute("CREATE INDEX idx_tiss ON stoptimes (trip_id, stop_sequence)")
        con.execute("CREATE INDEX idx_sidt ON stoptimes (stop_id, departure_time)")

        con.commit()
        con.close()
        return True

    return True


def _insert_st_file(file: str, table: str, con: sqlite3.Connection):
    with open(file, 'r') as f:
        f.readline()  # read header

        for line in f:
            entry = line.strip('\n').split(',')
            entry[1] = entry[1].rjust(8, '0')
            entry[2] = entry[2].rjust(8, '0')
            con.execute(f"INSERT INTO {table} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", tuple(entry))


class QueryDB:
    """Object for persisting database connections to speed up searches."""

    con: sqlite3.Connection
    tables: dict[str, set[str]]

    def __init__(self) -> None:
        self.con = sqlite3.connect('transit.db')
        tables_temp = self.con.execute("SELECT name FROM sqlite_master "
                                       "WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()

        self.tables = {}
        for table in tables_temp:
            table_info = self.con.execute(f"PRAGMA table_info({table[0]})").fetchall()
            self.tables[table[0]] = {t[1] for t in table_info}

    def get(self, table: str, columns: tuple[str] = None, condition: str = None)\
            -> list[tuple]:
        """Make a search on a table. The desired columns to be returned should be given as a tuple
        of strings. Search conditions are given as a string, in SQL syntax.
        TODO: make condition handling more robust

        If the table does not exist in the database:
            Return an empty list.

        If the table does exist:
            Return a list of rows returned by the search. Each element
            of the list is a tuple containing the columns requested for that returned row. If no
            columns are specified, all columns are returned.
            Only columns which exist in the table are provided. Columns that do not exist are
            ignored. If none of the columns provided exist in this table, then an empty list is
            returned.

        Note: all this checking is helpful when using this function. However, does it add
        unecessary overhead? I have no idea. In any case, once all code is up and running it can
        probably be deleted.
        """
        if table not in self.tables:
            return []
        else:
            if columns is not None:
                column_text = ''
                for c in columns:
                    if c in self.tables[table]:
                        column_text += (c + ', ')
                column_text = column_text[:len(column_text) - 2]
            else:
                column_text = '*'

            if column_text == '':
                return []

            if condition is None:
                return self.con.execute(f"SELECT {column_text} FROM {table}").fetchall()
            else:
                return self.con.execute(f"SELECT {column_text} "
                                        f"FROM {table} WHERE {condition}").fetchall()

    def close(self) -> None:
        """Close connection to database. Call when this session of queries is over."""
        self.con.close()
