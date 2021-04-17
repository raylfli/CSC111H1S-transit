"""TTC Route Planner for Toronto, Ontario -- Path class

This file contains the Path class, which is the path that is generated
given a starting and ending point.

This file is Copyright (c) 2021 Anna Cho, Charles Wong, Grace Tian, Raymond Li
"""

from typing import Union
import pygame
from data_interface import TransitQuery
from image import Image


class Path:
    """The path to be drawn.

    Instance Attributes:
        - shapes: list of tuples of type of path and list of coordinates relating to that type
            in correct order,
            path types are as follows:
                - -1 -> Walk
                - 0 -> Tram, Streetcar, Light rail
                - 1 -> Subway, Metro
                - 3 -> Bus
        - routes: list of dictionary of ordered route info of the path,
            each dictionary is in the following format:
                - start: stop ID of the starting stop of a route in this path
                - end: stop ID of the ending stop of a route in this path
                - route_short_name: TTC public route code (integer)
                - route_long_name: full TTC route name (string)
                - route_type: GTFS defined route_type codes (integer).
                    The TTC transit dataset includes
                    - 0 -> Tram, Streetcar, Light rail
                    - 1 -> Subway, Metro
                    - 3 -> Bus
                - route_color: hexadecimal route colour (string)
                - route_text_color: hexadecimal route text colour (string)
    """
    # Private Instance Attributes:
    #    - _routes_info: dictionary of information for each route
    #    - _visible: bool for if the path is visible or not
    _routes_info: dict[int, dict[str, Union[dict, str]]]
    _visible: bool
    routes: list[dict[str, Union[str, int]]]
    shapes: list[tuple[int, list[tuple[float, float]]]]

    def __init__(self, visible: bool = False) -> None:
        """Initialize a Path object."""
        self.routes = []
        self._routes_info = {}
        self.shapes = []
        self._visible = visible

    def draw(self, screen: pygame.Surface, image: Image,
             orig_x: int, orig_y: int, line_width: int = 2) -> None:
        """Draw the path on the given screen."""
        if self._visible:
            for i in range(0, len(self.shapes)):
                for j in range(0, len(self.shapes[i][1]) - 1):
                    start_lat, start_lon = self.shapes[i][1][j]
                    end_lat, end_lon = self.shapes[i][1][j + 1]
                    start = image.lat_lon_to_coord(start_lat, start_lon, orig_x, orig_y)
                    end = image.lat_lon_to_coord(end_lat, end_lon, orig_x, orig_y)
                    color = '#' + self._routes_info[self.shapes[i][0]]['route_color'] \
                        if self.shapes[i][0] != -1 else 'black'
                    pygame.draw.line(screen, pygame.Color(color), start, end, line_width)

    def set_visible(self, value: bool) -> None:
        """Set visibility of path."""
        self._visible = value

    def get_shapes(self, start: tuple[float, float], end: tuple[float, float],
                   stops: list[tuple[int, int, int]]) -> None:
        """Get shapes for a path given the start and end location (in latitude/longitude) and
        a list of stops of tuples in the format (trip_id, stop_id_start, stop_id_end)
        in reverse order of the path.
        """
        # Add origin
        self.shapes = [(-1, [start])]
        self.routes = []
        if stops != []:
            shapes = []

            # Create TransitQuery
            query = TransitQuery()

            # Add path in order (originally given in reverse)
            for j in range(len(stops) - 1, -1, -1):
                trip_id, stop_id_start, stop_id_end = stops[j]
                if trip_id != 0:
                    shapes.append(query.get_shape_data(trip_id, stop_id_start, stop_id_end))
                    self.routes.append({'start': stop_id_start, 'end': stop_id_end})

            # Set route and path information
            for i in range(0, len(shapes)):
                if shapes[i]['route_id'] not in self._routes_info:
                    self._routes_info[shapes[i]['route_id']] = \
                        query.get_route_info(shapes[i]['route_id'])

                self.routes[i].update(self._routes_info[shapes[i]['route_id']])
                if shapes[i]['route_id'] == self.shapes[-1][0]:
                    for lat_lon in shapes[i]['shape']:
                        self.shapes[-1][1].append(lat_lon)
                else:
                    self.shapes.append((shapes[i]['route_id'], [self.shapes[-1][1][-1]]))
                    for lat_lon in shapes[i]['shape']:
                        self.shapes[-1][1].append(lat_lon)

            # Close TransitQuery
            query.close()

        # Add destination
        if self.shapes[-1][0] != -1:
            self.shapes.append((-1, [self.shapes[-1][1][-1], end]))
        else:
            self.shapes[-1][1].append(end)

    def routes_to_text(self) -> list[str]:
        """Returns a list of steps for the user to take for this path.
         Returned list to be used in PygPageLabel.
        """
        if self.routes == []:
            return ['1.',
                    'Walk directly from origin to destination']
        else:
            stops = {}
            route_types = {0: 'Tram', 1: 'Subway', 3: 'Bus'}

            # Open TransitQuery
            query = TransitQuery()

            # Add walking to first stop info
            if self.routes[0]['start'] not in stops:
                stops[self.routes[0]['start']] = query.get_stop_info(self.routes[0]['start'])
            routes_text = ['1.',
                           'Walk from origin to stop '
                           + str(stops[self.routes[0]['start']]['stop_name'])
                           + ' (' + str(stops[self.routes[0]['start']]['stop_code']) + ')',
                           '']

            # Add each step info
            for i in range(0, len(self.routes)):
                routes_text.append(str(i + 2) + '.')
                routes_text.append('Route Name: ' + self.routes[i]['route_long_name'])
                routes_text.append('Route Type: ' + route_types[self.routes[i]['route_type']])
                if self.routes[i]['start'] not in stops:
                    stops[self.routes[i]['start']] = query.get_stop_info(self.routes[i]['start'])
                if self.routes[i]['end'] not in stops:
                    stops[self.routes[i]['end']] = query.get_stop_info(self.routes[i]['end'])
                routes_text.append('Stop ' + str(stops[self.routes[i]['start']]['stop_name'])
                                   + ' (' + str(stops[self.routes[i]['start']]['stop_code']) + ') '
                                   + ' to stop ' + str(stops[self.routes[i]['end']]['stop_name'])
                                   + ' (' + str(stops[self.routes[i]['end']]['stop_code']) + ') ')
                routes_text.append('')

            # Add walking from last stop to destination info
            if self.routes[-1]['end'] not in stops:
                stops[self.routes[-1]['end']] = query.get_stop_info(self.routes[-1]['end'])
            routes_text.extend([str(len(self.routes) + 2) + '.',
                                'Walk from stop ' + str(stops[self.routes[-1]['end']]['stop_name'])
                                + ' (' + str(stops[self.routes[-1]['end']]['stop_code']) + ')'
                                + ' to destination'])

            return routes_text


if __name__ == '__main__':
    import python_ta.contracts
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()

    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['pygame', 'data_interface', 'image', 'typing'],
        'allowed-io': [],
        'max-line-length': 100,
        'max-nested-blocks': 4,
        'disable': ['E1136', 'E1121', 'R0913']})
