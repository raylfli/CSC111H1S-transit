"""TTC Route Planner for Toronto, Ontario -- Graph

This file contains the _Vertex and Graph classes, and generates a graph by calling the appropriate
functions from the ``data_interface`` module.

Graph implementation is based on CSC111 A3.

This file is Copyright (c) 2021 Anna Cho, Charles Wong, Grace Tian, Raymond Li
"""

from __future__ import annotations

from typing import Any

import data_interface


def load_graph() -> Graph():
    """Return a directed transit system graph using the processed data from data_interface.py.

    The transit system graph stores one vertex for each stop in the dataset.

    Each vertex contains information for the
        - Stop ID
        - Location (latitude, longitude)
    """
    g = Graph()
    data_interface.init_db('data/')
    q = data_interface.TransitQuery()

    for vertex in q.get_stops():
        g.add_vertex(vertex[0], vertex[1])
    for edge in q.get_edges():
        g.add_edge(edge[0], edge[1])

    return g


class _Vertex:
    """A vertex in a transit system graph, used to represent a stop.

    Instance Attributes:
        - item: The data stored in this vertex, representing a stop.
        - location: The latitude and longitude of the stop represented by the vertex.
        - neighbours: The vertices that are connected to this vertex. These connections
          are directed.

    Representation Invariants:
        - self not in self.neighbours
    """
    stop_id: int
    location: tuple[float, float]
    neighbours: set[_Vertex]

    def __init__(self, stop_id: Any, location: tuple[float, float]) -> None:
        """Initialize a new vertex with the given item and location.

        This vertex is initialized with no neighbours.
        """
        self.stop_id = stop_id
        self.location = location
        self.neighbours = set()

    def get_neighbours(self) -> set[_Vertex]:
        """Return the vertices that are directed to from this vertex.
        """
        return self.neighbours


class Graph:
    """A directed graph used to represent a transit system network.
    """

    _vertices: dict[int, _Vertex]

    def __init__(self) -> None:
        """Initialize an empty graph (no vertices or edges).
        """
        self._vertices = {}

    def add_vertex(self, stop_id: int, location: tuple[float, float]) -> None:
        """Add a vertex with the given stop_id and location to this graph.

        The new vertex is not adjacent to any other vertices.
        Do nothing if the given item is already in this graph.
        """
        if stop_id not in self._vertices:
            self._vertices[stop_id] = _Vertex(stop_id, location)

    def add_edge(self, stop_id1: int, stop_id2: int) -> None:
        """Adds a directed edge between the two vertices with the given items in this graph.

        Raise a ValueError if stop_id1 or stop_id2 do not appear as vertices in this graph.

        Preconditions:
            - stop_id1 != stop_id2
        """
        if stop_id1 in self._vertices and stop_id2 in self._vertices:
            v1 = self._vertices[stop_id1]
            v2 = self._vertices[stop_id2]

            v1.neighbours.add(v2)
        else:
            raise ValueError(f'{stop_id1} and/or {stop_id2} not in this graph.')

    def get_vertex(self, stop_id: int) -> _Vertex:
        """Return a vertex given an item (stop_id).
        """
        return self._vertices[stop_id]


if __name__ == '__main__':
    import python_ta.contracts
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()

    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['typing', 'data_interface'],
        'allowed-io': [],
        'max-line-length': 100,
        'disable': ['E1136']})
