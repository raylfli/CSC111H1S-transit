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

import data_interface
from graph import Graph
from pathfinding import a_star


def load_graph() -> Graph():
    """Return a transit system graph using the processed data from data_interface.py.

    The transit system graph stores one vertex for each stop in the dataset.
    Each vertex stores as its item either a Stop ID, and the "location" _Vertex attribute stores
    the latitude and longitude of each stop.

    Edges represent a one-way connection between two existing stops.
    """
    g = Graph()
    data_interface.init_db('data/')
    q = data_interface.TransitQuery()

    for vertex in q.get_stops():
        g.add_vertex(vertex[0], vertex[1])

    for edge in q.get_edges():
        g.add_edge(edge[0], edge[1])

    return g


if __name__ == '__main__':

    g = load_graph()
    # todo complete this section

    q = data_interface.TransitQuery()
    print(a_star(g.get_vertex(14155), g.get_vertex(2160), 62429, g, q))

    # import python_ta
    # # todo modify the PyTA check
    #
    # python_ta.check_all(config={
    #     'max-line-length': 1000,
    #     'disable': ['E1136'],
    #     'extra-imports': ['csv', 'networkx'],
    #     'allowed-io': ['load_review_graph'],
    #     'max-nested-blocks': 4
    # })
