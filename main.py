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
import requests
from zipfile import ZipFile

import data_interface
from graph import Graph
from pathfinding import find_route


def download_data() -> None:
    """Download and extract TTC Routes and Schedules Data.
    Link: https://open.toronto.ca/dataset/ttc-routes-and-schedules/
    """
    url = "https://ckan0.cf.opendata.inter.prod-toronto.ca/download_resource/c1264e07-3c27-490f" \
          "-9362-42c1c8f03708"
    zip_file = 'data/data.zip'

    r = requests.get(url, stream=True)
    with open(zip_file, 'wb') as f:
        for chunk in r.iter_content(chunk_size=128):
            f.write(chunk)

    with ZipFile(zip_file, 'r') as zip:
        zip.extractall('data/')

    os.remove(zip_file)


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
    # download_data()
    print(find_route((43.776222, -79.347048), (43.787739, -79.334818), 62429, 7, load_graph()))

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
