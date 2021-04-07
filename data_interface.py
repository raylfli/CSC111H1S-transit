"""Data Interface

TODO ADD DOCSTRING

This file is Copyright (c) 2021 Anna Cho, Charles Wong, Grace Tian, Raymond Li
"""

import csv
import os
import sqlite3


# ---------- DATABASE CREATION ---------- #

def init_db(data_dir: str, force: bool = False) -> None:
    """Initialize a new database in a file called ``transit.db`` containing the GTFS static tables
    from the given data_directory. If one already exists, this function does nothing, but
    if ``force is True``, this function will overwrite tables in the ``transit.db`` file.

    Preconditions: TODO ADD MORE IF NEEDED
        - os.isfile(data_dir + 'routes.txt')
        - os.isfile(data_dir + 'shapes.txt')
        - os.isfile(data_dir + 'stop_times.txt')
        - os.isfile(data_dir + 'stops.txt')
        - os.isfile(data_dir + 'trips.txt')
        - files in the data_dir directory are formatted according to the GTFS static format.
    """
    if not os.path.isfile('transit.db') or force:
        con = sqlite3.connect('transit.db')

        if force:  # remove existing files in database
            con.executescript("""
            DROP TABLE IF EXISTS routes;
            DROP TABLE IF EXISTS shapes;
            DROP TABLE IF EXISTS stop_times;
            DROP TABLE IF EXISTS stops;
            DROP TABLE IF EXISTS trips;
            """)

        # create tables corresponding to GTFS files
        con.executescript("""
        CREATE TABLE routes 
            (route_id INTEGER PRIMARY KEY ASC UNIQUE, 
            agency_id INTEGER, 
            route_short_name INTEGER, 
            route_long_name TEXT, 
            route_desc TEXT, 
            route_type INTEGER, 
            route_url TEXT, 
            route_color TEXT, 
            route_text_color TEXT)
        WITHOUT ROWID;
        
        CREATE TABLE shapes
            (shape_id INTEGER,
            shape_pt_lat REAL,
            shape_pt_lon REAL,
            shape_pt_sequence INTEGER,
            shape_dist_traveled REAL);
        
        CREATE TABLE stop_times
            (trip_id INTEGER,
            arrival_time INTEGER, -- stored in num of seconds
            departure_time INTEGER, -- stored in num of seconds
            stop_id INTEGER, 
            stop_sequence INTEGER,
            stop_headsign TEXT,
            pickup_type INTEGER,
            drop_off_type INTEGER,
            shape_dist_traveled REAL DEFAULT 0);
            
        CREATE TABLE stops
            (stop_id INTEGER PRIMARY KEY ASC UNIQUE,
            stop_code INTEGER UNIQUE,
            stop_name TEXT,
            stop_desc TEXT,
            stop_lat REAL,
            stop_lon REAL, 
            zone_id INTEGER,
            stop_url TEXT,
            location_type INTEGER,
            parent_station INTEGER,
            stop_timezone INTEGER,
            wheelchair_boarding INTEGER)
        WITHOUT ROWID;
        
        CREATE TABLE trips
            (route_id INTEGER,
            service_id INTEGER,
            trip_id INTEGER PRIMARY KEY,
            trip_headsign TEXT,
            trip_short_name TEXT,
            direction_id INTEGER,
            block_id INTEGER,
            shape_id INTEGER,
            wheelchair_accessible INTEGER,
            bikes_allowed INTEGER);
        """)

        data_dir_formatted = data_dir + ('/' if not data_dir.endswith('/') else '')

        # insert data
        _insert_file(data_dir_formatted + 'routes.txt', 'routes', con)
        _insert_file(data_dir_formatted + 'shapes.txt', 'shapes', con)
        _insert_stop_times_file(data_dir_formatted + 'stop_times.txt', con)
        _insert_file(data_dir_formatted + 'stops.txt', 'stops', con)
        _insert_file(data_dir_formatted + 'trips.txt', 'trips', con)

        # compute weights
        _generate_weights(con, force=force)

        con.commit()
        con.close()


def _insert_file(file_path: str, table_name: str, con: sqlite3.Connection) -> None:
    """Insert the specified file into a pre-existing SQLite table in the given Connection.

    DOES NOT commit changes.

    Preconditions:  # TODO EDIT IF NEW TABLES
        - table_name in {'routes', 'stops', 'trips'}
        - table exists in the SQLite database connection
        - os.isfile(file_path)
        - specified file includes a header row
    """
    with open(file_path, mode='r') as f:
        reader = csv.reader(f)
        num_cols = len(next(reader))  # skip header row
        query_str = f'INSERT INTO {table_name} VALUES ({", ".join(["?"] * num_cols)})'
        con.executemany(query_str, reader)


def _insert_stop_times_file(file_path: str, con: sqlite3.Connection) -> None:
    """Insert ``stop_times.txt`` file from the GTFS static format using the given SQLite connection.

    DOES NOT commit changes.

    Preconditions:
        - os.isfile(file_path)
    """
    with open(file_path, mode='r') as f:
        reader = csv.reader(f)
        next(reader)  # skip header row
        for row in reader:
            arr_time_split = row[1].split(':')
            dep_time_split = row[2].split(':')
            values = (row[0],
                      (int(arr_time_split[0]) * 3600 +
                       int(arr_time_split[1]) * 60 +
                       int(arr_time_split[2])),
                      (int(dep_time_split[0]) * 3600 +
                       int(dep_time_split[1]) * 60 +
                       int(dep_time_split[2])),
                      row[3], row[4], row[5], row[6], row[7], row[8])
            con.execute("""INSERT INTO stop_times VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", values)


def _generate_weights(con: sqlite3.Connection, force: bool = False) -> None:
    """Generate edge weights and store in a new table ``weights`` using information from
    the ``stop_times`` table in the given Connection.

    DOES NOT commit changes.

    Preconditions:
        - the ``stop_times`` table exists in the sqlite3 Connection
    """
    if con.execute("""
    SELECT COUNT(name) FROM sqlite_master WHERE type='table' AND name='weights'
    """).fetchone()[0] == 0 or force:  # check if table does NOT exist (or force)
        if force:
            con.execute("""DROP TABLE IF EXISTS weights;""")

        # create table
        con.executescript("""
        CREATE TABLE weights
            (trip_id INTEGER,
            stop_id_start INTEGER,
            stop_id_end INTEGER,
            time_dep INTEGER, -- time in seconds
            time_arr INTEGER, -- time in seconds
            weight REAL);
    
        -- Add index for indexing by start stop, end stop, and departure time
        CREATE INDEX id_stops_time ON weights (stop_id_start, stop_id_end, time_dep);
        """)

        # get number of rows in stop_times
        row_num = con.execute("""SELECT COUNT(trip_id) from stop_times""").fetchone()[0]

        # compute weights and add
        cur = con.execute("""
        SELECT trip_id, arrival_time, departure_time, stop_id, stop_sequence 
        FROM stop_times;
        """)
        next_row = cur.fetchone()
        for _ in range(row_num - 1):
            curr_row = next_row
            next_row = cur.fetchone()

            # check for continued sequence
            if curr_row[0] == next_row[0]:
                values = (curr_row[0],  # trip_id
                          curr_row[3], next_row[3],  # stop_ids
                          curr_row[2], next_row[1],  # dep/arr time
                          next_row[1] - curr_row[2])

                con.execute("""INSERT INTO weights VALUES (?, ?, ?, ?, ?, ?)""", values)


# ---------- DATABASE QUERY ---------- #

class TransitQuery:
    """Used for persisting Transit database connections in order to speed up queries and database
    operations.

    Connects to the SQLite database in the file ``transit.db``

    data_interface.init_db should be called before creating a TransitQuery object to correctly
    create the database.

    Instance Attributes:
        - open: True when the database connection is open, False otherwise

    Representation Invariants:
        - open is True if and only if the sqlite3.Connection is open
    """
    # Private Instance Attributes:
    #   - _con: sqlite3 Connection object. Should only ever be connected to the ``transit.db`` file
    open: bool
    _con: sqlite3.Connection

    def __init__(self) -> None:
        """Initialize a new QueryDB object.
        """
        self._con = sqlite3.connect('transit.db')
        self.open = True

    def __del__(self) -> None:
        """Close database connections during object deletion.
        """
        self.close()

    def close(self) -> None:
        """Close database connection.
        """
        self._con.close()
        self.open = False

    def get_stops(self) -> set[tuple[int, tuple[float, float]]]:
        """Return a set of tuples representing all the stops in the database.

        Returned tuples are in the form: ``(stop_id, (latitude, longitude))`` where
            - ``-90 <= latitude <= 90``
            - ``-180 <= longitude <= 180``
        """
        if not self.open:
            raise ConnectionError('Database is not connected.')

        stops = set()
        for row in self._con.execute("""SELECT stop_id, stop_lat, stop_lon FROM stops"""):
            stops.add((row[0], (row[1], row[2])))

        return stops

    def get_edge_weights(self, stop_id_start: int, stop_id_end: int,
                         time_sec: int) -> list[tuple[int, int, int, int, int, float]]:
        """Return a list of the next vehicles to travel between the two stops after the
        given time (in seconds).

        Returned tuples are in the form: ``(trip_id, stop_id_start, stop_id_end,
        time_dep, time_arr, weight)`` where
            - ``time_dep >= time_sec``

        If there are no edges between the start and end stops, an empty list is returned.

        For example, if you wanted to get the weights for the vehicles to travel between stop 100
        and stop 200 after 1:00 AM, you would call: ``TransitDB.get_edge_weights(100, 200, 3600)``

        Preconditions:
            - time_sec >= 0
        """
        if not self.open:
            raise ConnectionError('Database is not connected.')

        weights = []
        cur = self._con.execute("""
        SELECT trip_id,
            stop_id_start,
            stop_id_end,
            time_dep,
            time_arr,
            weight,
            time_dep - :time AS time_diff
        FROM weights
        WHERE 
            stop_id_start = :start AND
            stop_id_end = :end AND 
            time_diff >= 0;
        """, {'time': time_sec, 'start': stop_id_start, 'end': stop_id_end})
        for row in cur:
            weights.append((row[0], row[1], row[2], row[3], row[4], row[5]))

        return weights


if __name__ == '__main__':
    # TODO ADD PYTA CHECK

    # init_db('data/', force=True)
    init_db('data/')

    q = TransitQuery()
