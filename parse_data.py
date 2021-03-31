"""SQL shenanigans  [DEV FILE --- NOT TO BE USED IN PROD]

Example to run after creating db:

con = sqlite3.connect('stoptimes.db')
cur = con.cursor()
for row in cur.execute("SELECT * FROM stoptimes WHERE stop_id='1277'"):
    print(row)
con.close()
"""

import sqlite3


def create_db() -> None:
    """Create database for stoptimes1. One time use only. Hardcoded.
    TODO: make not hardcoded
    """
    con = sqlite3.connect('dev.db')
    cur = con.cursor()
    cur.execute('''CREATE TABLE [IF NOT EXISTS] stoptimes 
                (trip_id, arrival_time, departure_time, stop_id, stop_sequence, stop_headsign, 
                pickup_type, drop_off_type, shape_dist_traveled)''')
    con.commit()
    con.close()


def populate_db() -> None:
    """Populate database for stoptimes 1. One time use only. Hardcoded.
    TODO: make not hardcoded?
    """
    con = sqlite3.connect('dev.db')
    cur = con.cursor()

    with open('data/stop_times_1.txt', 'r') as f:
        f.readline()

        for line in f:
            entry = line.strip('\n').split(',')
            entry[1] = entry[1].rjust(8, '0')
            entry[2] = entry[2].rjust(8, '0')
            entry[3] = entry[3].rjust(5, '0')
            cur.execute("INSERT INTO stoptimes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", tuple(entry))

    with open('data/stop_times_2.txt', 'r') as f:
        f.readline()

        for line in f:
            entry = line.strip('\n').split(',')
            entry[1] = entry[1].rjust(8, '0')
            entry[2] = entry[2].rjust(8, '0')
            entry[3] = entry[3].rjust(5, '0')
            cur.execute("INSERT INTO stoptimes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", tuple(entry))

    with open('data/stop_times_3.txt', 'r') as f:
        f.readline()

        for line in f:
            entry = line.strip('\n').split(',')
            entry[1] = entry[1].rjust(8, '0')
            entry[2] = entry[2].rjust(8, '0')
            entry[3] = entry[3].rjust(5, '0')
            cur.execute("INSERT INTO stoptimes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", tuple(entry))
    con.commit()
    con.close()


# DOESN'T WORK TOO LAZY TO FIGURE OUT RN
# def select_column_value(db_file: str, db: str, column: str, value: str) -> list:
#     """TODO: make the method name better lol"""
#     con = sqlite3.connect(db_file)
#     cur = con.cursor()
#
#     cur.execute("SELECT * FROM stoptimes WHERE ?=?", (column, "'" + value + "'"))
#
#     return cur.fetchall()


# This might not work either idk y i thought i would need it i've never tried using it.
def nuke(db_file: str, db: str) -> None:
    """Deletes everything from a database. USE WITH EXTREME CAUTION. FOR DEV ONLY."""
    con = sqlite3.connect(db_file)
    cur = con.cursor()

    print('*******THIS METHOD DELTES EVERYTHING IN YOUR DATABASE*******')
    print('Are you sure you wish to proceed? (y/n)')
    inp = input()

    if inp == 'y':
        cur.execute(f'DELETE FROM ?', db)
        con.commit()


if __name__ == '__main__':
    import timeit

    setup = '''
import sqlite3
con = sqlite3.connect('dev.db')
cur = con.cursor()
    '''

    code = '''cur.execute("SELECT * FROM stoptimes WHERE stop_id='01277' AND departure_time>'23:00:00'")'''
    print(
        timeit.timeit(setup=setup, stmt=code, number=100000)
    )
