"""
This file contains the _Vertex and Graph classes, and generates a graph using data from
get_stops() and get_edge_weights() from data_interface.py.

This file is Copyright (c) 2021 Anna Cho, Charles Wong, Grace Tian, Raymond Li
"""


from __future__ import annotations
from typing import Any

import data_interface


class _Vertex:
    """A vertex in a transit system graph, used to represent a stop.

    Instance Attributes:
        - item: The data stored in this vertex, representing a stop.
        - location: The latitude and longitude of the stop represented by the vertex.
        - neighbours: The vertices that are adjacent to this vertex.

    Representation Invariants:
        - self not in self.neighbours
        - all(self in u.neighbours for u in self.neighbours)
    """
    stop_id: int
    location: tuple[float, float]
    neighbours: set[_Vertex]

    def __init__(self, stop_id: Any, location: tuple) -> None:
        """Initialize a new vertex with the given item and location.

        This vertex is initialized with no neighbours.
        """
        self.stop_id = stop_id
        self.location = location
        self.neighbours = set()

    def get_neighbours(self) -> set[_Vertex]:
        """Return the vertices adjacent to this vertex."""
        return self.neighbours


class Graph:
    """A graph used to represent a transit system network."""

    _vertices: dict[int, _Vertex]

    def __init__(self) -> None:
        """Initialize an empty graph (no vertices or edges)."""
        self._vertices = {}

    def add_vertex(self, item: int, location: tuple[float, float]) -> None:
        """Add a vertex with the given item and location to this graph.

        The new vertex is not adjacent to any other vertices.
        Do nothing if the given item is already in this graph.
        """
        if item not in self._vertices:
            self._vertices[item] = _Vertex(item, location)

    def add_edge(self, item1: int, item2: int) -> None:
        """Adds a directed edge between the two vertices with the given items in this graph.

        Raise a ValueError if item1 or item2 do not appear as vertices in this graph.

        Preconditions:
            - item1 != item2
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]

            v1.neighbours.add(v2)
        else:
            raise ValueError

    def get_vertex(self, item: int) -> _Vertex:
        """Return a vertex given an item (stop_id)."""
        return self._vertices[item]


if __name__ == '__main__':
    # TODO ADD PYTA CHECK
    pass
