"""Data Interface

TODO COMPLETE MODULE DOCSTRING

This file is Copyright (c) 2021 Anna Cho, Charles Wong, Grace Tian, Raymond Li
"""

# Data processing
import pandas as pd
import numpy as np

# Data source
from data_dataframes import STOP_TIMES_DF, STOPS_DF, ROUTES_DF


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


def get_edge_weights() -> set[tuple[np.uint16, np.uint16, np.float16]]:
    """Return a set of directed edges and their corresponding edge weights.

    Returned tuples are in the form: ``(stop_id1, stop_id2, weight)``, where edges are directed
    from ``stop_id1`` to ``stop_id2``.
    """


if __name__ == '__main__':
    # TODO ADD PYTA CHECK
    pass
