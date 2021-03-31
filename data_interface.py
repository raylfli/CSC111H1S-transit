"""Data Interface

TODO COMPLETE MODULE DOCSTRING

This file is Copyright (c) 2021 Anna Cho, Charles Wong, Grace Tian, Raymond Li
"""

# Data processing
import numpy as np
import pandas as pd

# Data source
from data_dataframes import STOP_TIMES_DF, STOPS_DF


def get_stops() -> set[tuple[np.uint16, tuple[np.float32, np.float32]]]:
    """Return a set of tuples representing transit stops.

    Returned tuples are in the form: ``(stop_id, (latitude, longitude))``.
        - ``-90 <= latitude <= 90``
        - ``-180 <= longitude <= 180``
    """
    stops = set()
    for row in STOPS_DF.iterrows():
        stops.add((row[0], (row[1]['stop_lat'], row[1]['stop_lon'])))

    return stops


def get_edge_weights() -> pd.DataFrame:
    """Return a Pandas DataFrame of directed edges and their corresponding edge weights.

    Column information:
        - INDEX: stop_id_start (root of the directed edge)
        - stop_id_end (end of the directed edge)
        - time (departure time from root station)
        - weight (edge weight)
    """
    df = pd.DataFrame(columns=['stop_id_start', 'stop_id_end', 'time', 'weight'])
    temp_storage = []

    stop_times_iterator = STOP_TIMES_DF.itertuples()
    # curr_row = None
    next_row = next(stop_times_iterator)

    # for row_num in range(100):  # TODO REMOVE - testing purposes
    for _ in range(len(STOP_TIMES_DF) - 1):
        curr_row = next_row
        next_row = next(stop_times_iterator)

        if len(temp_storage) >= 2000:  # number arbitrarily chosen, can adjust for memory usage
            df = df.append(pd.DataFrame(temp_storage, columns=['stop_id_start', 'stop_id_end',
                                                               'time', 'weight']))
            temp_storage = []

        if curr_row[3] + 1 == next_row[3]:  # stop_sequence comparison
            temp_storage.append((curr_row[2], next_row[2], curr_row[1],
                                 (next_row[1] - curr_row[1]).seconds / 60))

    df = df.append(pd.DataFrame(temp_storage, columns=['stop_id_start', 'stop_id_end',
                                                       'time', 'weight']))
    df.set_index('stop_id_start', inplace=True)
    df.sort_index(inplace=True)

    return df


if __name__ == '__main__':
    # TODO ADD PYTA CHECK

    pass
    # weights = get_edge_weights()
