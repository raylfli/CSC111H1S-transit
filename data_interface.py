"""Data Interface

TODO ADD DOCSTRING

This file is Copyright (c) 2021 Anna Cho, Charles Wong, Grace Tian, Raymond Li
"""

import csv
import os
import sqlite3


def init_db(data_dir: str, force: bool = False) -> None:
    """Initialize a new database in a file called ``transit.db`` containing the GTFS static tables
    from the given data_directory. If one already exists, this function does nothing, but
    if ``force is True``, this function will overwrite tables in the ``transit.db`` file.

    Preconditions: TODO ADD MORE IF NEEDED
        - os.isfile(data_dir + 'routes.txt')
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
        _insert_routes_file(data_dir_formatted + 'routes.txt', con)
        _insert_stop_times_file(data_dir_formatted + 'stop_times.txt', con)
        _insert_stops_file(data_dir_formatted + 'stops.txt', con)
        _insert_trips_file(data_dir_formatted + 'trips.txt', con)

        # compute weights
        _generate_weights(con, force=force)

        con.commit()
        con.close()


# TODO MAKE THESE INSERT FUNCTIONS UNIVERSAL (SUCH THAT ONLY ONE IS REQUIRED)
def _insert_routes_file(file_path: str, con: sqlite3.Connection) -> None:
    """Insert ``routes.txt`` file from the GTFS static format using the given SQLite connection.

    DOES NOT commit changes.

    Preconditions:
        - os.isfile(file_path)
    """
    with open(file_path, mode='r') as f:
        reader = csv.reader(f)
        next(reader)  # skip header row
        con.executemany("""INSERT INTO routes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", reader)


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

        # con.executemany("""INSERT INTO stop_times VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", reader)


def _insert_stops_file(file_path: str, con: sqlite3.Connection) -> None:
    """Insert ``stops.txt`` file from the GTFS static format using the given SQLite connection.

    DOES NOT commit changes.

    Preconditions:
        - os.isfile(file_path)
    """
    with open(file_path, mode='r') as f:
        reader = csv.reader(f)
        next(reader)  # skip header row
        con.executemany("""INSERT INTO stops VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", reader)


def _insert_trips_file(file_path: str, con: sqlite3.Connection) -> None:
    """Insert ``trips.txt`` file from the GTFS static format using the given SQLite connection.

    DOES NOT commit changes.

    Preconditions:
        - os.isfile(file_path)
    """
    with open(file_path, mode='r') as f:
        reader = csv.reader(f)
        next(reader)  # skip header row
        con.executemany("""INSERT INTO trips VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", reader)


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
            (stop_id_start INTEGER,
            stop_id_end INTEGER,
            time_dep TEXT,
            time_arr TEXT,
            weight REAL);
    
        -- Add index for indexing by start and end stop
        CREATE INDEX id_stops ON weights (stop_id_start, stop_id_end);
        """)

        # get number of rows in stop_times
        row_num = con.execute("""SELECT COUNT(trip_id) from stop_times""").fetchone()[0]

        # compute weights and add
        cur = con.execute("""
        SELECT arrival_time, departure_time, stop_id, stop_sequence 
        FROM stop_times;
        """)
        next_row = cur.fetchone()
        for _ in range(row_num - 1):
            curr_row = next_row
            next_row = cur.fetchone()

            # check for continued sequence
            if curr_row[3] + 1 == next_row[3]:
                values = (curr_row[2], next_row[2],
                          curr_row[1], next_row[0],
                          next_row[0] - curr_row[1])

                con.execute("""INSERT INTO weights VALUES (?, ?, ?, ?, ?)""", values)


if __name__ == '__main__':
    # TODO ADD PYTA CHECK

    init_db('data/', force=True)
    # init_db('data/')
