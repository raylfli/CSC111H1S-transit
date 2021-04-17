"""TTC Route Planner for Toronto, Ontario -- Pathfinding

This module provides the functions for computing an optimal path through TTC transit using the
A* pathfinding algorithm. The returned path can either include every stop on the route, or only
the start and end stops of distinct routes.

This file is Copyright (c) 2021 Anna Cho, Charles Wong, Grace Tian, Raymond Li
"""

from collections import defaultdict
from math import inf
from multiprocessing import Pool
from queue import PriorityQueue, Queue
from typing import Optional, Union
import logging

from data_interface import TransitQuery
from graph import _Vertex, load_graph
from util import distance


def find_route(start_loc: tuple[float, float], end_loc: tuple[float, float], time: int,
               day: int, message_queue: Queue) -> list[tuple[int, int, int]]:
    """Given a start location, end location, and time block, compute the quickest transit route.
    Returns a list of tuples (trip_id, start stop_id, end stop_id).
    Note that the list is in reverse order of the actual route, i.e. element 0 of the returned list
    is the most recent trip one must take

    Coordinates are given as (latitude, longitude), in degrees north and degrees east.
    Time is given in the number of seconds from the most recent midnight.
    Day is given as integers [1, 7], where 1 is Monday and 7 is Sunday.
    """
    query = TransitQuery()
    graph = load_graph()

    start_id = query.get_closest_stops(start_loc[0], start_loc[1])
    end_id = query.get_closest_stops(end_loc[0], end_loc[1])

    start_stop_coords = graph.get_vertex(start_id[0]).location
    end_stop_coords = graph.get_vertex(end_id[0]).location

    start_ids = query.get_closest_stops(start_stop_coords[0], start_stop_coords[1], 0.1)
    end_ids = query.get_closest_stops(end_stop_coords[0], end_stop_coords[1], 0.1)

    message_queue.put(f'INFO {len(start_ids) * len(end_ids)}')

    with Pool(maxtasksperchild=1) as p:
        paths = p.starmap(a_star, ((id1, id2, time, day, message_queue) for id1 in start_ids for id2 in end_ids))

    path = min(paths, key=lambda x: x[1])
    message_queue.put(f'DONE {path[0]}')  # tell parent process pathfinding complete
    return path[0]


def a_star(id1: int, id2: int, time: int, day: int, message_queue: Queue) \
        -> Optional[tuple[list[tuple[int, int, int]], Union[int, float]]]:
    """A* algorithm for graph pathfinding.

    The inputs to this function are given as stop_ids.

    Returns a tuple of the path and the time the path takes, in seconds.
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Finding path from {id1} -> {id2}")

    query = TransitQuery()
    graph = load_graph()
    logger.debug(f"Graph loaded for {id1} -> {id2}")

    start = graph.get_vertex(id1)
    goal = graph.get_vertex(id2)

    # heap of nodes to look at, sorted by f_score. The f_score of any given node n is g_score(n) +
    # h(n), i.e. the shortest path currently known to this node + estimated distance to the goal
    # based on the heuristic
    open_set = PriorityQueue()
    open_set.put((h(start, goal), 0, start))

    # For a stop_id n, path_bin[n] is the information for the trip/edge connecting it to the
    # previous node. The information is given as a tuple:
    # (trip_id, start stop_id, end stop_id, time arrived, day)
    path_bin = {}

    # score of cheapest path from start to curr currently known
    g_score = defaultdict(lambda: inf)
    g_score[start] = 0

    push_counter = 0
    while not open_set.empty():
        curr = open_set.get()[2]

        if curr == goal:
            # Use construct_path for a path with all stops included
            # Use construct_filtered_path for a path that only describe entire trip segments
            delta_t = 86400 - time + (((path_bin[curr.stop_id][4] - day) % 7) - 1) * 86400 + \
                      path_bin[curr.stop_id][3]
            logger.info(f'Found path for {id1} -> {id2}')
            message_queue.put('INC')
            return (construct_filtered_path(path_bin, curr.stop_id), delta_t)

        # Note that this only works if the heuristic is both consistent and admissible. Then
        # the arrival time to the current stop will be on the optimal path, and therefore we
        # want to query all stops connected to this stop after this time
        # If the time rolls over to the next day, query using the next day's timetable
        # Returned as (trip_id, day, time_dep, time_arr, dist)
        t = time if curr.stop_id not in path_bin else path_bin[curr.stop_id][3]
        d = day if curr.stop_id not in path_bin else path_bin[curr.stop_id][4]

        neighbour_id = set()

        for neighbour in curr.get_neighbours():
            neighbour_id.add(neighbour.stop_id)
            edge = query.get_edge_data(curr.stop_id, neighbour.stop_id, t, d)
            if edge is not None:
                # optimize for both distance travelled between stops and time taken to reach
                # next stop
                if edge[3] - edge[2] >= 0:
                    day_arrival = edge[1]
                else:
                    day_arrival = edge[1] + 1
                edge_weight = edge[4] * (
                        86400 - t + (((day_arrival - d) % 7) - 1) * 86400 + edge[3])
                temp_gscore = g_score[curr] + edge_weight

                if temp_gscore < g_score[neighbour]:
                    # record optimum path
                    path_bin[neighbour.stop_id] = (
                        edge[0], curr.stop_id, neighbour.stop_id, edge[3],
                        (day_arrival - 1) % 7 + 1)
                    g_score[neighbour] = temp_gscore  # update g_score for neighbour

                    # Calculate f_score for neighbour and push onto open_set. If h is consistent,
                    # any node removed from open_set is guaranteed to be optimal. Then by extension
                    # we know we are not pushing any "bad" nodes.
                    f_score = g_score[neighbour] + h(neighbour, goal)
                    open_set.put((f_score, push_counter, neighbour))
                    push_counter += 1

        for stop in query.get_closest_stops(curr.location[0], curr.location[1], 0.05):
            if stop != curr.stop_id and stop not in neighbour_id:
                node = graph.get_vertex(stop)

                delta_d = distance(curr.location, node.location)
                delta_t = delta_d / 0.0014
                edge_weight = delta_d * delta_t
                temp_gscore = g_score[curr] + edge_weight

                if temp_gscore < g_score[node]:
                    if t + delta_t > 86400:
                        d += 1
                    # record optimum path
                    path_bin[stop] = (0, curr.stop_id, stop, (t + delta_t) % 86400, (d - 1) % 7 + 1)
                    g_score[node] = temp_gscore  # update g_score for neighbour

                    # Calculate f_score for neighbour and push onto open_set. If h is consistent,
                    # any node removed from open_set is guaranteed to be optimal. Then by extension
                    # we know we are not pushing any "bad" nodes.
                    f_score = g_score[node] + h(node, goal)
                    open_set.put((f_score, push_counter, node))
                    push_counter += 1

    return ([(0, 0, 0)], inf)


def h(curr: _Vertex, goal: _Vertex) -> float:
    """A* heuristic function.

    In this particular case, calculate the great-circle distance between the curr and goal nodes
    using the haversine formula.
    """
    return distance(curr.location, goal.location)


def construct_path(path_bin: dict[int, tuple[int, int, int, int, int]],
                   goal_id: int) -> list[tuple[int, int, int]]:
    """Return a path constructed using path_bin. Note that the path returned is in reverse order:
    the first element is the final stop.
    """
    path = [path_bin[goal_id][:3]]

    curr_id = path_bin[goal_id][1]
    while curr_id in path_bin.keys():
        path.append(path_bin[curr_id][:3])
        curr_id = path_bin[curr_id][1]

    return path


def construct_filtered_path(path_bin: dict[int, tuple[int, int, int, int, int]],
                            goal_id: int) -> list[tuple[int, int, int]]:
    """Return a path constructed using path_bin. Note that the path returned is in reverse order:
    the first element is the final stop. The stops returned in each tuple are the start and end
    of each trip.
    """
    # path_bin: (trip_id, start stop_id, end stop_id, time arrived)
    path = []

    curr_trip = path_bin[goal_id][0]
    curr_id = path_bin[goal_id][1]
    start_stop = path_bin[goal_id][1]
    end_stop = path_bin[goal_id][2]

    while curr_id in path_bin.keys():
        if path_bin[curr_id][0] == curr_trip:
            start_stop = path_bin[curr_id][1]
        else:
            path.append((curr_trip, start_stop, end_stop))
            end_stop = start_stop
            start_stop = path_bin[curr_id][1]
            curr_trip = path_bin[curr_id][0]
        curr_id = path_bin[curr_id][1]

    path.append((curr_trip, start_stop, end_stop))
    return path


if __name__ == '__main__':
    import python_ta.contracts
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()

    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['collections', 'math', 'multiprocessing', 'queue', 'typing',
                          'data_interface', 'graph', 'util'],
        'allowed-io': [],
        'max-line-length': 100,
        'disable': ['E1136']}
    )
