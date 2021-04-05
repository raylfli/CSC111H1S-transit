"""Data Interface

TODO COMPLETE MODULE DOCSTRING

This file is Copyright (c) 2021 Anna Cho, Charles Wong, Grace Tian, Raymond Li
"""

# Data processing
import numpy as np
import pandas as pd

# TODO REMOVE BEFORE COMMIT
import math

# Data source
from data_dataframes import STOP_TIMES_DF, STOPS_DF


def get_stops() -> set[tuple[np.uint16, tuple[np.float32, np.float32]]]:
    """Return a set of tuples representing transit stops.

    Returned tuples are in the form: ``(stop_id, (latitude, longitude))``.
        - ``-90 <= latitude <= 90``
        - ``-180 <= longitude <= 180``
    """
    stops = set()
    for row in STOPS_DF.itertuples():
        # print(row)
        stops.add((row[0], (row[3], row[4])))

    return stops


def get_edge_weights() -> pd.DataFrame:
    """Return a Pandas DataFrame of directed edges and their corresponding edge weights.

    Column information:
        - INDEX: stop_id_start (root of the directed edge)
        - stop_id_end (end of the directed edge)
        - time_dep (departure time from root station)
        - time_arr (arrival time to the other station)
        - weight (edge weight)
    """
    # cols = ['stop_id_start', 'stop_id_end', 'time_dep', 'time_arr', 'weight']
    cols = ['stop_id_start', 'stop_id_end', 'time_dep', 'time_arr', 'weight', 'dist']
    df = pd.DataFrame(columns=cols)
    temp_storage = []

    stop_times_iterator = STOP_TIMES_DF.itertuples()
    # curr_row = None
    next_row = next(stop_times_iterator)

    for row_num in range(100):  # TODO REMOVE - testing purposes
    # for _ in range(len(STOP_TIMES_DF) - 1):
        curr_row = next_row
        next_row = next(stop_times_iterator)

        if len(temp_storage) >= 2000:  # number arbitrarily chosen, can adjust for memory usage
            df = df.append(pd.DataFrame(temp_storage, columns=cols))
            temp_storage = []

        if curr_row[3] + 1 == next_row[3]:  # stop_sequence comparison
            curr_stop = STOPS_DF.loc[curr_row[2]]
            next_stop = STOPS_DF.loc[next_row[2]]
            temp_storage.append((curr_row[2], next_row[2], curr_row[1], next_row[1],
                                 (next_row[1] - curr_row[1]).seconds / 60,
                                 distance((curr_stop[2], curr_stop[3]), (next_stop[2], next_stop[3]))
                                 )
                                )

    df = df.append(pd.DataFrame(temp_storage, columns=cols))
    df.set_index('stop_id_start', inplace=True)
    df.sort_index(inplace=True)

    return df


# TODO TEMP REMOVE BEFORE COMMIT
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


if __name__ == '__main__':
    # TODO ADD PYTA CHECK

    # pass
    weights = get_edge_weights()
    # weights.to_pickle('data/edge_weights_dump.pkl')
    # weights = pd.read_pickle('data/edge_weights_dump.pkl')  # TODO REMOVE - pickle dump file

    # arr = [list(weights.index), list(weights.stop_id_end), list(weights.time)]
    # multi = pd.MultiIndex.from_arrays(arr)
    # weights_multi = pd.Series(data=weights.weight, index=multi)
