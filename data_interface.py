"""TTC Route Planner for Toronto, Ontario -- Data Interface

This module provides the functions and classes for interacting with the TTC GTFS static data.

Then, ``init_db`` should be called to initialize the ``transit.db`` SQLite database file and
create the required tables. ``init_db`` also has a ``force`` parameter, allowing the database file
to be forcefully remade by dropping pre-existing tables and recreating them.

This file is Copyright (c) 2021 Anna Cho, Charles Wong, Grace Tian, Raymond Li
"""

import csv
import logging
import os
import sqlite3
from typing import Optional, Union

import util


# ---------- DATABASE CREATION ---------- #

def init_db(data_dir: str, force: bool = False) -> None:
    """Initialize a new database in a file called ``transit.db`` containing the GTFS static tables
    from the given data_directory. If one already exists, this function does nothing, but
    if ``force is True``, this function will overwrite tables in the ``transit.db`` file.

    Preconditions:
        - os.isfile(data_dir + 'calendar.txt')
        - os.isfile(data_dir + 'routes.txt')
        - os.isfile(data_dir + 'shapes.txt')
        - os.isfile(data_dir + 'stop_times.txt')
        - os.isfile(data_dir + 'stops.txt')
        - os.isfile(data_dir + 'trips.txt')
        - files in the data_dir directory are formatted according to the GTFS static format.
    """
    if not os.path.isfile('transit.db') or force:
        logger = logging.getLogger(__name__)
        logger.info('Initializing database into "transit.db"')

        con = sqlite3.connect('transit.db')

        if force:  # remove existing files in database
            logger.debug('Database force enabled -- dropping pre-existing tables')
            con.executescript("""
            DROP TABLE IF EXISTS calendar;
            DROP TABLE IF EXISTS routes;
            DROP TABLE IF EXISTS shapes;
            DROP TABLE IF EXISTS stop_times;
            DROP TABLE IF EXISTS stops;
            DROP TABLE IF EXISTS trips;
            
            VACUUM;
            """)

        # create tables corresponding to GTFS files
        logger.debug('Creating database tables')
        con.executescript("""
        CREATE TABLE calendar
            (service_id INTEGER PRIMARY KEY ASC UNIQUE, 
            monday INTEGER, 
            tuesday INTEGER, 
            wednesday INTEGER, 
            thursday INTEGER, 
            friday INTEGER, 
            saturday INTEGER, 
            sunday INTEGER, 
            start_date TEXT, 
            end_date TEXT)
        WITHOUT ROWID;
        
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
        logger.debug('Inserting data into tables')
        _insert_file(data_dir_formatted + 'calendar.txt', 'calendar', con)
        _insert_file(data_dir_formatted + 'routes.txt', 'routes', con)
        _insert_file(data_dir_formatted + 'shapes.txt', 'shapes', con)
        _insert_stop_times_file(data_dir_formatted + 'stop_times.txt', con)
        _insert_file(data_dir_formatted + 'stops.txt', 'stops', con)
        _insert_file(data_dir_formatted + 'trips.txt', 'trips', con)

        # compute edge distances
        logger.debug('Generating edges table')
        _compute_distances(con, force=force)

        con.commit()
        con.close()

        logger.info('Database initialization completed')


def _insert_file(file_path: str, table_name: str, con: sqlite3.Connection) -> None:
    """Insert the specified file into a pre-existing SQLite table in the given Connection.

    DOES NOT commit changes.

    Preconditions:
        - table_name in {'calendar', 'routes', 'shapes', 'stops', 'trips'}
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
                      (int(arr_time_split[0]) * 3600
                       + int(arr_time_split[1]) * 60
                       + int(arr_time_split[2])),
                      (int(dep_time_split[0]) * 3600
                       + int(dep_time_split[1]) * 60
                       + int(dep_time_split[2])),
                      row[3], row[4], row[5], row[6], row[7],
                      0 if row[8] == '' else row[8])
            con.execute("""INSERT INTO stop_times VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", values)


def _compute_distances(con: sqlite3.Connection, force: bool = False) -> None:
    """Compute edge shape distances and store in a new table ``edges`` using information from
    the ``stop_times`` table in the given Connection.

    DOES NOT commit changes.

    Preconditions:
        - the ``stop_times`` table exists in the sqlite3 Connection
    """
    if con.execute("""
    SELECT COUNT(name) FROM sqlite_master WHERE type='table' AND name='edges'
    """).fetchone()[0] == 0 or force:  # check if table does NOT exist (or force)
        if force:
            con.execute("""DROP TABLE IF EXISTS edges;""")

        # create table
        con.executescript("""
        CREATE TABLE edges
            (trip_id INTEGER,
            stop_id_start INTEGER,
            stop_id_end INTEGER,
            time_dep INTEGER, -- time in seconds
            time_arr INTEGER, -- time in seconds
            shape_dist_traveled_start REAL,
            shape_dist_traveled_end REAL,
            service_id INTEGER);
    
        -- Add index for indexing by start stop, end stop, and departure time
        CREATE INDEX id_stops_time ON edges (stop_id_start, stop_id_end, time_dep);
        CREATE INDEX id_trip_stops ON edges (trip_id, stop_id_start, stop_id_end);
        """)

        # get number of rows in stop_times
        row_num = con.execute("""SELECT COUNT(trip_id) from stop_times""").fetchone()[0]

        # compute edge distances and add
        cur = con.execute("""
        SELECT 
            stop_times.trip_id, 
            arrival_time, 
            departure_time, 
            stop_id, 
            stop_sequence, 
            shape_dist_traveled,
            service_id
        FROM stop_times
        INNER JOIN trips ON trips.trip_id = stop_times.trip_id;
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
                          curr_row[5], next_row[5],  # shape distances
                          curr_row[6]  # service_id
                          )

                con.execute("""INSERT INTO edges VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", values)


# ---------- DATABASE QUERY ---------- #

class TransitQuery:
    """Used for persisting Transit database connections in order to speed up queries and database
    operations.

    Connects to the SQLite database in the file ``transit.db``.

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

    def __init__(self, db_file: str = 'transit.db') -> None:
        """Initialize a new TransitQuery object.
        """
        self._con = sqlite3.connect(db_file)
        self.open = True

        # create spherical distance function
        self._con.create_function('SPH_DIST', 4,
                                  lambda a, b, c, d: util.distance((a, b), (c, d)),
                                  deterministic=True)

        # create modulus function
        self._con.create_function('MOD', 2,
                                  lambda a, b: a % b,
                                  deterministic=True)

        logging.getLogger(__name__).debug('Initialized new TransitQuery object')

    def __del__(self) -> None:
        """Close database connections during object deletion.
        """
        self.close()

    def close(self) -> None:
        """Close database connection.
        """
        self._con.close()
        self.open = False
        logging.getLogger(__name__).debug('Closed TransitQuery connection')

    def get_stops(self) -> set[tuple[int, tuple[float, float]]]:
        """Return a set of tuples representing all the stops in the database.

        Returned tuples are in the form: ``(stop_id, (latitude, longitude))`` where
            - ``-90 <= latitude <= 90``
            - ``-180 <= longitude <= 180``

        Raises ConnectionError if database is not connected.
        """
        if not self.open:
            raise ConnectionError('Database is not connected.')

        stops = set()
        for row in self._con.execute("""SELECT stop_id, stop_lat, stop_lon FROM stops"""):
            stops.add((row[0], (row[1], row[2])))

        return stops

    def get_edges(self) -> set[tuple[int, int]]:
        """Return a set of tuples representing directed edges between stops.

        Returned tuples are in the form: ``(stop_id_start, stop_id_end)``.

        Raise ConnectionError if database is not connected.
        """
        if not self.open:
            raise ConnectionError('Database is not connected.')

        cur = self._con.execute("""SELECT DISTINCT stop_id_start, stop_id_end FROM edges""")
        return set(cur.fetchall())

    def get_closest_stops(self, lat: float, lon: float, radius: float = -1) -> list[int]:
        """Return a list of ``stop_id``s corresponding to the closest stops to the given
        latitude and longitude.

        Radius parameter allows for restricting the closest stops to a certain radius around the
        given latitude and longitude. If not included, this function returns a list of length 1
        with the single closest stop.

        Stops are returned in increasing distance away from the given lat/lon in kilometers.

        Returns an empty list if no stops are in the radius.

        Raises ConnectionError if database is not connected.

        Preconditions:
            - radius == -1 or radius >= 0
        """
        if not self.open:
            raise ConnectionError('Database is not connected.')

        cur = self._con.execute("""
        SELECT stop_id FROM 
            (SELECT 
                stop_id, 
                stop_lat, 
                stop_lon,
                SPH_DIST(stop_lat, stop_lon, :ref_lat, :ref_lon) AS dist
            FROM stops
            WHERE (dist <= :radius OR :radius = -1)
            ORDER BY 
                dist ASC)
        """, {'ref_lat': lat, 'ref_lon': lon, 'radius': radius})

        if radius == -1:
            return [cur.fetchone()[0]]
        else:  # radius != -1
            return [stop[0] for stop in cur]

    def get_edge_data(self, stop_id_start: int, stop_id_end: int,
                      time_sec: int, day: int) -> Optional[tuple[int, int, int, int, float]]:
        """Return the edge information for the next vehicle that travels between the two stops
        after the given time (in seconds) on the specified day. Distance is the actual distance
        traveled by the vehicle--not the direct straight line distance between the two stops.

        Returns None if no edge is found.

        Time is considered over a rolling window. For example, 25 * 3600 [25:00] is considered to
        be equivalent to 1 * 3600 [1:00].

        Day counting starts from 1 on Monday:
            - 1: Monday
            - 2: Tuesday
            - ...
            - 6: Saturday
            - 7: Sunday

        Day counting also deals with ``time_sec >= 24 * 3600``. For example, the following are
        considered to be equivalent:
            - ``time_sec == 25 * 3600`` and ``day == 5`` (Friday 25:00)
            - ``time_sec == 3600`` and ``day == 6`` (Saturday 1:00)

        Returned tuples are in the form: ``(trip_id, day, time_dep, time_arr, dist)`` where
            - ``1 <= day <= 7'
            - ``0 <= time_dep < 86400``
            - ``0 <= time_arr < 86400``
        Day is used as a 'midnight reference' for ``time_dep``. For example, if
            - ``day == 1 and time_dep == 28800``, the vehicle departs at 8:00 on Monday
        Note that it is possible for ``time_dep >= time_arr``. This can occur when ``time_dep`` is
        close to midnight of the previous day, and the vehicle arrives at the next stop midnight
        the next day.

        For example, if you wanted to get the edge for the vehicles that travel between stop 100
        and stop 200 after 1:00 AM on Sunday,
        you would call: ``TransitQuery.get_edge_data(100, 200, 3600, 7)``

        Raises ValueError if no edge found.

        Raises ConnectionError if database is not connected.

        Preconditions:
            - time_sec >= 0
            - 1 <= day <= 7
        """
        if not self.open:
            raise ConnectionError('Database is not connected.')

        # check if edge exists
        cur = self._con.execute("""
        SELECT * 
        FROM edges
        WHERE 
            stop_id_start = :start AND
            stop_id_end = :end AND
            time_dep >= 0
        """, {'start': stop_id_start, 'end': stop_id_end})

        if cur.fetchone() is None:
            raise ValueError(f'Edge from {stop_id_start} to {stop_id_end} does not exist.')

        time_in_week = (day - 1) * 86400 + time_sec  # time in sec after Monday 00:00

        actual_time = time_in_week % 86400  # adjust for "time overscroll"
        actual_day = time_in_week // 86400  # adjust for "day + time overscroll"

        for _ in range(7):  # runs at most 7 times (prevents infinite loops)
            actual_day = actual_day % 7 + 1
            prev_day = util.stringify_day_num((actual_day + 5) % 7 + 1)
            curr_day = util.stringify_day_num(actual_day)
            cur = self._con.execute(f"""
            SELECT trip_id, time_dep, time_arr, dist FROM
                (SELECT 
                    trip_id,
                    stop_id_start, 
                    stop_id_end, 
                    time_dep, 
                    time_arr, 
                    shape_dist_traveled_end - shape_dist_traveled_start AS dist, 
                    monday, tuesday, wednesday, thursday, friday, saturday, sunday, 
                    MOD(time_dep, 86400) AS abs_time
                FROM edges
                INNER JOIN calendar ON edges.service_id = calendar.service_id
                WHERE 
                    stop_id_start = :start AND
                    stop_id_end = :end AND 
                    (({prev_day} = 1 AND time_dep >= 86400) OR
                        ({curr_day} = 1 AND time_dep <= 86400)) AND
                    abs_time >= :time
                ORDER BY
                    abs_time ASC);
            """, {'time': actual_time, 'start': stop_id_start, 'end': stop_id_end})
            actual_time = 0  # setup for next iteration

            res = cur.fetchone()

            if res is not None:
                return (res[0],  # trip_id
                        actual_day,  # day
                        res[1] % 86400,  # time_dep (adjusted for overscroll)
                        res[2] % 86400,  # time_arr (adjusted for overscroll)
                        res[3])  # dist

        return None

    def get_route_id(self, trip_id: int) -> int:
        """Return ``route_id`` from the given ``trip_id`.

        Raises ConnectionError if database is not connected.

        Raises ValueError if no trip with the given ``trip_id`` exists.
        """
        if not self.open:
            raise ConnectionError('Database is not connected.')

        cur = self._con.execute("""
        SELECT route_id
        FROM trips
        WHERE trip_id = ?;
        """, (trip_id,))
        route_info = cur.fetchone()

        if route_info is None:
            raise ValueError(f'Trip with id {trip_id} not found.')

        return route_info[0]

    def get_route_info(self, route_id: int) -> dict[str, Union[str, int]]:
        """Return route info of the given ``route_id``.

        Returned dictionary contains the following keys:
            - route_short_name: TTC public route code (integer)
            - route_long_name: full TTC route name (string)
            - route_type: GTFS defined route_type codes (integer). The TTC transit dataset includes
                - 0 -> Tram, Streetcar, Light rail
                - 1 -> Subway, Metro
                - 3 -> Bus
            - route_color: hexadecimal route colour (string)
            - route_text_color: hexadecimal route text colour (string)

        Raises ConnectionError if database is not connected.

        Raises ValueError if no route of the given ``route_id`` exists.
        """
        if not self.open:
            raise ConnectionError('Database is not connected.')

        cur = self._con.execute("""
        SELECT route_short_name, route_long_name, route_type, route_color, route_text_color
        FROM routes
        WHERE route_id = ?;
        """, (route_id,))
        route_info = cur.fetchone()

        if route_info is None:
            raise ValueError(f'Route with id {route_id} not found.')

        return {'route_short_name': route_info[0],
                'route_long_name': route_info[1],
                'route_type': route_info[2],
                'route_color': route_info[3],
                'route_text_color': route_info[4]}

    def get_stop_info(self, stop_id: int) -> dict[str, Union[int, str, float]]:
        """Return stop info of the given ``stop_id``.

        Returned dictionary contains the following keys:
            - stop_code: Short number that identifies the stop for riders. (This should be used
              for publicly displayed information rather than  ``stop_id``.
            - stop_name: Name of the stop location.
            - stop_lat: Latitude of the stop location.
            - stop_lon: Longitude of the stop location.
            - wheelchair_boarding: Indicates whether wheelchair boarding is possible from this
              stop. The GTFS static defines the following values for this column:
                - 0 -> No accessibility information
                - 1 -> Some vehicles can be boarded by a rider in a wheelchair
                - 2 -> Wheelchair boarding is not possible at this stop

        Raises ConnectionError if database is not connected.

        Raises ValueError if no stop of the given ``stop_id`` exists.
        """
        if not self.open:
            raise ConnectionError('Database is not connected.')

        cur = self._con.execute("""
        SELECT stop_code, stop_name, stop_lat, stop_lon, wheelchair_boarding
        FROM stops
        WHERE stop_id = ?;
        """, (stop_id,))
        stop_info = cur.fetchone()

        if stop_info is None:
            raise ValueError(f'Stop with id {stop_id} not found.')

        return {'stop_code': stop_info[0],
                'stop_name': stop_info[1],
                'stop_lat': stop_info[2],
                'stop_lon': stop_info[3],
                'wheelchair_boarding': stop_info[4]}

    def get_shape_data(self, trip_id: int,
                       stop_id_start: int,
                       stop_id_end: int) -> dict[str, Union[int, list[tuple[float, float]]]]:
        """Return the ``route_id`` and shape data between the two stops.

        Shape data is used to plot points in between each of the stops.

        Returned dictionary contains the following keys:
            - route_id: ``route_id`` of the traveled path between two stops (int)
            - shape: list of ``tuple[float, float]`` containing the shape/path as
            (latitude, longitude) between the given stops. The element at the 0th index is
            always the start stop, and the element at the -1th index is always the end stop.

        Raises ConnectionError if database is not connected.

        Raises ValueError if:
            - Invalid ``trip_id``
            - Start and end stops do not exist in the given valid ``trip_id``
            - Start stop is later in the shape than the end stop
        """
        if not self.open:
            raise ConnectionError('Database is not connected.')

        trip_info = self._con.execute("""
        SELECT route_id, shape_id
        FROM trips
        WHERE trip_id = ?
        """, (trip_id,)).fetchone()

        # check for invalid trip
        if trip_info is None:
            raise ValueError(f'Trip with id {trip_id} not found.')

        route_id, shape_id = trip_info

        shape_dist_start = self._con.execute("""
        SELECT shape_dist_traveled_start 
        FROM edges
        WHERE trip_id = :t_id AND stop_id_start = :s_id_start
        """, {'t_id': trip_id, 's_id_start': stop_id_start}).fetchone()

        shape_dist_end = self._con.execute("""
        SELECT shape_dist_traveled_end
        FROM edges
        WHERE trip_id = :t_id AND stop_id_end = :s_id_end
        """, {'t_id': trip_id, 's_id_end': stop_id_end}).fetchone()

        # check for bad queries where stops are missing
        if shape_dist_start is None and shape_dist_start is None:
            raise ValueError(f'Start and end stops of {stop_id_start} and {stop_id_end} not found.')
        elif shape_dist_start is None:
            raise ValueError(f'No start stop with id {stop_id_start} found in trip {trip_id}.')
        elif shape_dist_end is None:
            raise ValueError(f'No end stop with id {stop_id_end} found in trip {trip_id}.')

        shape_dist_start = shape_dist_start[0]
        shape_dist_end = shape_dist_end[0]

        # check for reversed stops
        if shape_dist_start >= shape_dist_end:
            raise ValueError(f'Start and edge stops of {stop_id_start} and '
                             f'{stop_id_end} may be reversed.')

        # query for shape points in between stops
        shape_coords_cursor = self._con.execute("""
        SELECT shape_pt_lat, shape_pt_lon
        FROM shapes
        WHERE 
            shape_id = :s_id AND
            shape_dist_traveled BETWEEN :s_dist_start AND :s_dist_end;
        """, {'s_id': shape_id, 's_dist_start': shape_dist_start, 's_dist_end': shape_dist_end})

        # query start and end stop coordinates
        stop_start_coords = self._con.execute("""
        SELECT stop_lat, stop_lon
        FROM stops
        WHERE stop_id = ?
        """, (stop_id_start,)).fetchone()

        stop_end_coords = self._con.execute("""
        SELECT stop_lat, stop_lon
        FROM stops
        WHERE stop_id = ?
        """, (stop_id_end,)).fetchone()

        return {'route_id': route_id,
                'shape': [stop_start_coords] + shape_coords_cursor.fetchall() + [stop_end_coords]}


if __name__ == '__main__':
    import python_ta.contracts
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()

    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['csv', 'logging', 'os', 'sqlite3', 'pathlib', 'typing', 'zipfile',
                          'requests', 'util'],
        'allowed-io': ['download_data', 'init_db', '_insert_file', '_insert_stop_times_file'],
        'max-line-length': 100,
        'disable': ['E1136']
    })

    # logging.basicConfig(level=logging.DEBUG)
    # logging.basicConfig(level=logging.INFO)

    data_directory = 'data/'

    # init_db(data_directory, force=True)
    init_db(data_directory)

    q = TransitQuery()
