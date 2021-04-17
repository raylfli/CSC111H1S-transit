"""TTC Route Planner for Toronto, Ontario -- Main

This module setups and starts up the main program.

This file is Copyright (c) 2021 Anna Cho, Charles Wong, Grace Tian, Raymond Li
"""

import logging
import os

import data_interface
from map import run_map

# hide Pygame support prompts (spams console when opening new processes)
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'HIDE'

if __name__ == '__main__':
    # uncomment/comment for debug messages/info messages in console.
    logging.basicConfig(level=logging.DEBUG)
    # logging.basicConfig(level=logging.INFO)

    logger = logging.getLogger(__name__)

    data_directory = 'data/'
    logger.info(f'Initializing database using data from {data_directory}')
    data_interface.init_db(data_directory)  # setup database (~30-45 secs)

    logger.info('Starting pygame visualization')
    run_map()  # start pygame visualization
