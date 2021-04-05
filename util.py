"""Utility functions

This file is Copyright (c) 2021 Anna Cho, Charles Wong, Grace Tian, Raymond Li
"""


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


if __name__ == '__main__':
    # TODO ADD PYTA CHECK

    import doctest
    doctest.testmod()
