"""A* shenanigans"""
from collections import defaultdict
from queue import PriorityQueue
from math import inf

from graph import _Vertex, Graph
from data_interface import TransitQuery
from util import distance


def find_route(start_loc: float, end_loc: float, time: int, graph: Graph)\
        -> list[tuple[int, int, int]]:
    """Given a start location, end location, and time block, compute the quickest transit route."""
    query = TransitQuery()

    start_id = start_loc  # TODO: find closest stop_id
    end_id = end_loc  # TODO: find closest stop_id

    return a_star(graph.get_vertex(start_id), graph.get_vertex(end_id), time, graph, query)


def a_star(start: _Vertex, goal: _Vertex, time: int, graph: Graph, query: TransitQuery)\
        -> list[tuple[int, int, int]]:
    """A* algorithm for graph pathfinding.

    The inputs to this function are given as stop_ids.
    """

    # heap of nodes to look at, sorted by f_score. The f_score of any given node n is g_score(n) +
    # h(n), i.e. the shortest path currently known to this node + estimated distance to the goal
    # based on the heuristic
    open_set = PriorityQueue()
    open_set.put((h(start, goal), start))

    # For a stop_id n, path_bin[n] is the information for the trip/edge connecting it to the
    # previous node. The information is given as a tuple: (trip_id, start stop_id, end stop_id)
    path_bin = {}

    # score of cheapest path from start to curr currently known
    g_score = defaultdict(lambda: inf)
    g_score[start] = 0

    curr_time = time

    while not open_set.empty():
        curr = open_set.get()[1]

        if curr == goal:
            return reconstruct_path(path_bin, curr.item)

        for neighbour in curr.neighbours:
            # (trip_id, time_dep, time_arr, weight)
            edge = graph.get_weight(curr, neighbour, curr_time, query)[0]
            edge_weight = edge[3]  # distance(curr, neighbour)  # TODO change to shape distance
            temp_gscore = g_score[curr] + edge_weight

            if temp_gscore < g_score[neighbour]:
                # record optimum path
                path_bin[neighbour.item] = (edge[0], curr.item, neighbour.item)
                g_score[neighbour] = temp_gscore  # update g_score for neighbour

                # Calculate f_score for neighbour and push onto open_set. If h is consistent, any
                # node removed from open_set is guaranteed to be optimal. Then by extension we know
                # we are not pushing any duplicate nodes.
                f_score = g_score[neighbour] + h(curr, goal)
                open_set.put((f_score, neighbour))
                curr_time = edge[2]


def h(curr: _Vertex, goal: _Vertex) -> float:
    """A* heuristic function.

    In this particular case, calculate the great-circle distance between the curr and goal nodes
    using the haversine formula.
    """
    return distance(curr.location, goal.location)


def construct_path(path_bin: dict[int, tuple[int, int, int]], goal_id: int)\
        -> list[tuple[int, int, int]]:
    """Return a path constructed using path_bin. Note that the path returned is in reverse order:
    the first element is the final stop.
    """
    path = [goal_id]

    id = goal_id
    while id in path_bin.keys():
        id = path_bin[id][1]
        path.append(path_bin[id])

    return path
