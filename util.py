"""TTC Route Planner for Toronto, Ontario -- Utility Functions

This module provides various utility functions that are used in other modules.

This file is Copyright (c) 2021 Anna Cho, Charles Wong, Grace Tian, Raymond Li
"""
import math


# day number mapped to day of the week
DAY_NUM_TO_DAY = {1: 'monday',
                  2: 'tuesday',
                  3: 'wednesday',
                  4: 'thursday',
                  5: 'friday',
                  6: 'saturday',
                  7: 'sunday'}


def distance(location1: tuple[float, float], location2: tuple[float, float]) -> float:
    """Great-circle distance between two points location1 and location2, calculated using
     the haversine formula.

    location1 and location2 are tuples of coordinates given in degrees north and degrees east.
    """
    earth_radius = 6368  # radius of the earth in km

    delta_phi = math.radians(location2[0] - location1[0])
    delta_lambda = math.radians(location2[1] - location1[1])

    central_angle = 2 * math.asin(math.sqrt((math.sin(delta_phi / 2)) ** 2
                                            + math.cos(math.radians(location1[0]))
                                            * math.cos(math.radians(location2[0]))
                                            * (math.sin(delta_lambda / 2)) ** 2))

    return central_angle * earth_radius


def seconds_to_time(secs: int) -> str:
    """Convert to a string representation of the given number of seconds.

    Returned string is in the format: ``hours:minutes:seconds`` where
        - ``0 <= hours``
        - ``0 <= minutes < 60``
        - ``0 <= seconds < 60``
    Minute and second substrings will always be two characters long, padded with zeroes.

    Preconditions:
        - secs >= 0

    >>> seconds_to_time(0)
    '0:00:00'
    >>> seconds_to_time(31)
    '0:00:31'
    >>> seconds_to_time(60)
    '0:01:00'
    >>> seconds_to_time(3600)
    '1:00:00'
    >>> seconds_to_time(62429)
    '17:20:29'
    """
    return f'{secs // 3600}:{((secs // 60) % 60):02}:{(secs % 60):02}'


def stringify_day_num(day_num: int) -> str:
    """Translate ``day_num`` into its corresponding day string in full lowercase.

    Day counting starts from 1 on Monday:
        - 1: Monday
        - 2: Tuesday
        - ...
        - 6: Saturday
        - 7: Sunday

    Preconditions:
        - 1 <= day_num <= 7

    >>> stringify_day_num(1)
    'monday'
    >>> stringify_day_num(5)
    'friday'
    >>> stringify_day_num(7)
    'sunday'
    """
    return DAY_NUM_TO_DAY[day_num]


if __name__ == '__main__':
    import python_ta.contracts
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()

    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['math'],
        'allowed-io': [],
        'max-line-length': 100,
        'disable': ['E1136']
    })
