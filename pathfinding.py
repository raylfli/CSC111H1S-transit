"""A* shenanigans"""
from collections import defaultdict
from queue import PriorityQueue
from math import inf

from graph import _Vertex, Graph
from data_interface import TransitQuery
from util import distance


def find_route(start_loc: tuple[float, float], end_loc: tuple[float, float], time: int, day: int,
               graph: Graph) -> list[tuple[int, int, int]]:
    """Given a start location, end location, and time block, compute the quickest transit route.
    Returns a list of tuples (trip_id, start stop_id, end stop_id).
    Note that the list is in reverse order of the actual route, i.e. element 0 of the returned list
    is the most recent trip one must take

    Coordinates are given as (latitude, longitude), in degrees north and degrees east.
    Time is given in the number of seconds from the most recent midnight.
    Day is given as integers [1, 7], where 1 is Monday and 7 is Sunday.
    """
    query = TransitQuery()

    start_id = query.get_closest_stop(start_loc[0], start_loc[1])
    end_id = query.get_closest_stop(end_loc[0], end_loc[1])

    return a_star(graph.get_vertex(start_id), graph.get_vertex(end_id), time, day, query)


def a_star(start: _Vertex, goal: _Vertex, time: int, day: int, query: TransitQuery)\
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
    # previous node. The information is given as a tuple:
    # (trip_id, start stop_id, end stop_id, time arrived)
    path_bin = {}

    # score of cheapest path from start to curr currently known
    g_score = defaultdict(lambda: inf)
    g_score[start] = 0

    while not open_set.empty():
        curr = open_set.get()[1]

        if curr == goal:
            # Use construct_path for a path with all stops included
            # Use construct_filtered_path for a path that only describe entire trip segments
            return construct_path(path_bin, curr.stop_id)

        for neighbour in curr.get_neighbours():
            # Note that this only works if the heuristic is both consistent and admissible. Then
            # the arrival time to the current stop will be on the optimal path, and therefore we
            # want to query all stops connected to this stop after this time
            t = time if curr.stop_id not in path_bin else path_bin[curr.stop_id][3]
            # If the time rolls over to the next day, query using the next day's timetable
            d = (day + 1) % 7 if t - time < 0 else day
            # Returned as (trip_id, day, time_dep, time_arr, dist)
            edge = query.get_edge_data(curr.stop_id, neighbour.stop_id, t, d)
            # optimize for both distance travelled between stops and time taken to reach next stop
            # if (delta_t := edge[2]86400 - t) >= 0:
            #     edge_weight = edge[3] * delta_t
            # else:
            #     edge_weight = edge[3] * (delta_t + 86400)
            edge_weight = edge[4] * (86400 - t + (edge[1] - d - 1) * 86400 + edge[3])
            temp_gscore = g_score[curr] + edge_weight

            if temp_gscore < g_score[neighbour]:
                # record optimum path
                path_bin[neighbour.stop_id] = (edge[0], curr.stop_id, neighbour.stop_id, edge[3])
                g_score[neighbour] = temp_gscore  # update g_score for neighbour

                # Calculate f_score for neighbour and push onto open_set. If h is consistent, any
                # node removed from open_set is guaranteed to be optimal. Then by extension we know
                # we are not pushing any "bad" nodes.
                f_score = g_score[neighbour] + h(curr, goal)
                open_set.put((f_score, neighbour))


def h(curr: _Vertex, goal: _Vertex) -> float:
    """A* heuristic function.

    In this particular case, calculate the great-circle distance between the curr and goal nodes
    using the haversine formula.
    """
    return distance(curr.location, goal.location)


def construct_path(path_bin: dict[int, tuple[int, int, int, int]], goal_id: int)\
        -> list[tuple[int, int, int]]:
    """Return a path constructed using path_bin. Note that the path returned is in reverse order:
    the first element is the final stop.
    """
    path = [path_bin[goal_id][:3]]

    curr_id = path_bin[goal_id][1]
    while curr_id in path_bin.keys():
        path.append(path_bin[curr_id][:3])
        curr_id = path_bin[curr_id][1]

    return path


def construct_filtered_path(path_bin: dict[int, tuple[int, int, int, int]], goal_id: int)\
        -> list[tuple[int, int, int]]:
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
            curr_trip = path_bin[curr_id][0]
        curr_id = path_bin[curr_id][1]

    path.append((curr_trip, start_stop, end_stop))
    return path
