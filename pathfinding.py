"""A* shenanigans"""
from collections import defaultdict
from queue import PriorityQueue
from math import inf


def find_route(start_loc, end_loc, time_bloc):
    """Given a start location, end location, and time block, compute the quickest transit route."""


def a_star(start, goal) -> None:
    """A* algorithm for graph pathfinding."""

    # heap of nodes to look at, sorted by f_score. The f_score of any given node n is g_score(n) +
    # h(n), i.e. the shortest path currently known to this node + estimated distance to the goal
    # based on the heuristic
    open_set = PriorityQueue()
    open_set.put((h(start, goal), start))

    # TODO: data structure to record path
    # reconstructing using came_from seems slow because you're always inserting into the beginning?

    # score of cheapest path from start to curr currently known
    g_score = defaultdict(lambda: inf)
    g_score[start] = 0

    while not open_set.empty():
        curr = open_set.get()[1]

        if curr == goal:
            return  # TODO some path

        for neighbour in curr:
            temp_gscore = g_score[curr]  # TODO: + edge weight from neighbour to curr

            if temp_gscore < g_score[neighbour]:
                # TODO: record path
                g_score[neighbour] = temp_gscore  # update g_score for neighbour

                # Calculate f_score for neighbour and push onto open_set. If h is consistent, any
                # node removed from open_set is guaranteed to be optimal. Then by extension we know
                # we are not pushing any duplicate nodes.
                f_score = g_score[neighbour] + h(curr, goal)
                open_set.put((f_score, neighbour))


def h(curr, goal) -> float:
    """A* heuristic function.

    In this particular case, calculate the great-circle distance between the curr and goal nodes
    using the haversine formula.
    """
