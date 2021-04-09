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
    item: Any
    location: tuple[int, int]
    neighbours: set[_Vertex]

    def __init__(self, item: Any, location: tuple) -> None:
        """Initialize a new vertex with the given item and location.

        This vertex is initialized with no neighbours.
        """
        self.item = item
        self.location = location
        self.neighbours = set()

    def degree(self) -> int:
        """Return the degree of this vertex."""
        return len(self.neighbours)


class Graph:
    """A graph used to represent a transit system network."""

    _vertices: dict[Any, _Vertex]

    def __init__(self) -> None:
        """Initialize an empty graph (no vertices or edges)."""
        self._vertices = {}

    def add_vertex(self, item: Any, location: tuple) -> None:
        """Add a vertex with the given item and location to this graph.

        The new vertex is not adjacent to any other vertices.
        Do nothing if the given item is already in this graph.
        """
        if item not in self._vertices:
            self._vertices[item] = _Vertex(item, location)

    def add_edge(self, item1: Any, item2: Any) -> None:
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

    def get_weight(self, item1: Any, item2: Any, time_sec: int, q: data_interface.TransitQuery()) \
            -> list[tuple[int, int, float]]:
        """Return the weight of the edge between the given items.

        Return 0 if item1 and item2 are not adjacent.

        Preconditions:
            - item1 and item2 are vertices in this graph
        """
        weights = []

        for edge_weight in q.get_edge_weights(item1, item2, time_sec):
            weights.append((edge_weight[2], edge_weight[3], edge_weight[4]))

        return weights

    def adjacent(self, item1: Any, item2: Any) -> bool:
        """Return whether item1 and item2 are adjacent vertices in this graph.

        Return False if item1 or item2 do not appear as vertices in this graph.
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            return any(v2.item == item2 for v2 in v1.neighbours)
        else:
            return False

    def get_neighbours(self, item: Any) -> set:
        """Return a set of the neighbours of the given item.

        Note that the *items* are returned, not the _Vertex objects themselves.

        Raise a ValueError if item does not appear as a vertex in this graph.
        """
        if item in self._vertices:
            v = self._vertices[item]
            return {neighbour.item for neighbour in v.neighbours}
        else:
            raise ValueError

    def get_all_vertices(self) -> set:
        """Return a set of all vertex items in this graph."""
        return set(self._vertices.keys())


if __name__ == '__main__':
    # TODO ADD PYTA CHECK
    pass
