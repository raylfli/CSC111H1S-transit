"""SQL shenanigans

Example to run after creating db:

con = sqlite3.connect('stoptimes1.db')
cur = con.cursor()
for row in cur.execute("SELECT * FROM stoptimes1 WHERE stop_id='1277'"):
    print(row)
"""

import sqlite3


def create_db() -> None:
    """Create database for stoptimes1. One time use only. Hardcoded.
    TODO: make not hardcoded
    """
    con = sqlite3.connect('stoptimes1.db')
    cur = con.cursor()
    cur.execute('''CREATE TABLE stoptimes1 
                (trip_id, arrival_time, departure_time, stop_id, stop_sequence, stop_headsign, 
                pickup_type, drop_off_type, shape_dist_traveled)''')
    con.commit()
    con.close()


def populate_db() -> None:
    """Populate database for stoptimes 1. One time use only. Hardcoded.
    TODO: make not hardcoded
    """
    with open('data/stop_times_1.txt', 'r') as f:
        header = f.readline()

        con = sqlite3.connect('stoptimes1.db')
        cur = con.cursor()

        for line in f:
            entry = tuple(line.strip('\n').split(','))
            cur.execute("INSERT INTO stoptimes1 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", entry)

        con.commit()
        con.close()


# DOESN'T WORK TOO LAZY TO FIGURE OUT RN
# def select_column_value(db_file: str, db: str, column: str, value: str) -> list:
#     """TODO: make the method name better lol"""
#     con = sqlite3.connect(db_file)
#     cur = con.cursor()
#
#     cur.execute("SELECT * FROM stoptimes1 WHERE ?=?", (column, "'" + value + "'"))
#
#     return cur.fetchall()


def nuke(db_file: str, db: str) -> None:
    """Deletes everything from a database. USE WITH EXTREME CAUTION. FOR DEV ONLY."""
    con = sqlite3.connect(db_file)
    cur = con.cursor()

    print('*******THIS METHOD DELTES EVERYTHING IN YOUR DATABASE*******')
    print('Are you sure you wish to proceed? (y/n)')
    inp = input()

    if inp == 'y':
        cur.execute(f'DELETE FROM ?', quotify(db))
        con.commit()


def quotify(s):
    """If s is a list of strings, return a tuple of the elements of s with single quotes around them.
    If s is a string, return s with quotes around it.
    """

    if isinstance(s, list):
        newlst = []
        for e in s:
            newlst.append("'" + e + "'")
        return tuple(newlst)
    elif isinstance(s, str):
        return "'" + s + "'"
