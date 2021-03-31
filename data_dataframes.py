"""Data Loading

TODO ADD MODULE DOCSTRING

Script solely for data loading. No additional functions.

This file is Copyright (c) 2021 Anna Cho, Charles Wong, Grace Tian, Raymond Li
"""

import numpy as np
import pandas as pd

import warnings

# SUPPRESSING FUTURE WARNINGS. PANDAS INDEX CREATION RAISES ERROR ABOUT ELEMENTWISE COMPARISON
warnings.simplefilter(action='ignore', category=FutureWarning)

# ---------------------------------------------------------------------- #

# Pandas Dataframe: GFTS static ``stops.txt``
#
# Column information: TODO UPDATE TYPES IF NEEDED
#   - INDEX: stop_id: ``np.uint16``
#   - stop_code: ``np.uint16``
#   - stop_name: ``str``
#   - stop_lat: ``np.float32``
#   - stop_lon: ``np.float32``
STOPS_DF = pd.read_csv('data/stops.txt',
                       usecols=['stop_id', 'stop_code', 'stop_name', 'stop_lat', 'stop_lon'],
                       dtype={'stop_id': np.uint16,  # 0 to 65_535
                              'stop_code': np.uint16,  # 0 to 65_535
                              'stop_name': str,
                              'stop_lat': np.float32,
                              'stop_lon': np.float32
                              },
                       index_col='stop_id'
                       )
STOPS_DF.sort_index(inplace=True)

# Pandas Dataframe: GFTS static ``routes.txt``
#
# Column information: TODO UPDATE TYPES IF NEEDED
#   - INDEX: route_id: ``np.uint32``
#   - route_short_name: ``np.uint16``
#   - route_long_name: ``str``
#   - route_type: ``np.uint8``
#   - route_colour: ``str``
ROUTES_DF = pd.read_csv('data/routes.txt',
                        usecols=['route_id', 'route_short_name', 'route_long_name', 'route_type',
                                 'route_color'],
                        dtype={'route_id': np.uint32,  # 0 to 4_294_967_295
                               'route_short_name': np.uint16,  # 0 to 65_535
                               'route_long_name': str,
                               'route_type': np.uint8,  # 0 to 255
                               'route_color': str
                               },
                        index_col='route_id'
                        )
ROUTES_DF.sort_index(inplace=True)

# Pandas Dataframe: GFTS static ``stop_times.txt``
#
# Column information: TODO UPDATE TYPES IF NEEDED
#   - INDEX: trip_id: ``np.uint32``
#   - time: ``pd.timedelta64``
#   - stop_id: ``np.uint16``
#   - stop_sequence: ``np.uint8``
STOP_TIMES_DF = pd.read_csv('data/stop_times.txt',
                            usecols=['trip_id', 'arrival_time', 'stop_id', 'stop_sequence'],
                            dtype={'trip_id': np.uint32,  # 0 to 4_294_967_295
                                   'arrival_time': str,
                                   'stop_id': np.uint16,  # 0 to 65_535
                                   'stop_sequence': np.uint8  # 0 to 255
                                   },
                            index_col='trip_id'
                            )
STOP_TIMES_DF.rename(columns={'arrival_time': 'time'}, inplace=True)
STOP_TIMES_DF.time = pd.to_timedelta(STOP_TIMES_DF.time)
# only stable algorithm, maintains stop ordering
STOP_TIMES_DF.sort_index(kind='mergesort', inplace=True)

# ---------------------------------------------------------------------- #

if __name__ == '__main__':
    # TODO ADD PYTA CHECK
    pass
