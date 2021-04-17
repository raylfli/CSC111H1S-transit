"""
CSC111 Final Project: TTC Transit Graph

This module provides the implementation for the main visualizations and computations of
this project.

Running the main block of this module will:
# TODO replace the following!
#     1. Retrieve the necessary HURDAT2 data.
#     2. Convert the raw data (.txt) into a usable .csv file.
#     3. Parse the usable .csv into a list of Storm dataclasses.
#     4. Create all visualizations.
#     5. Generate HTML file that contains all the visualizations.

This file is Copyright (c) 2021 Anna Cho, Charles Wong, Grace Tian, Raymond Li
"""
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'HIDE'
from map import run_map


if __name__ == '__main__':
    run_map()

    # import python_ta
    #
    # python_ta.check_all(config={
    #     'max-line-length': 1000,
    #     'disable': ['E1136'],
    #     'extra-imports': ['csv', 'networkx'],
    #     'allowed-io': ['load_review_graph'],
    #     'max-nested-blocks': 4
    # })
