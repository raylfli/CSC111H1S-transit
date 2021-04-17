"""Path class"""
import pygame
from data_interface import TransitQuery, init_db
from image import Image
from typing import Union
from collections import defaultdict


class Path:
    """The path to be drawn.

    Instance Attributes:
        - shapes: list of tuples of (latitude, longitude) of the path
        - routes: list of dictionary of ordered route info of the path
    """
    # Private Instance Attributes:
    #     - _routes_info: dictionary of information for each route
    #     - _visible: bool for if the path is visible or not
    _routes_info: dict[int, dict[str, Union[dict, str]]]
    _stops_info: dict[int, dict[str, Union[dict, str]]]
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
        """Draw the path"""
        if self._visible:
            for i in range(0, len(self.shapes)):
                for j in range(0, len(self.shapes[i][1]) - 1):
                    start_lat, start_lon = self.shapes[i][1][j]
                    end_lat, end_lon = self.shapes[i][1][j + 1]
                    start = image.lat_lon_to_coord(start_lat, start_lon, orig_x, orig_y)
                    end = image.lat_lon_to_coord(end_lat, end_lon, orig_x, orig_y)
                    color = '#' + self._routes_info[self.shapes[i][0]]['route_color'] if self.shapes[i][0] != 0 else 'black'
                    pygame.draw.line(screen, pygame.Color(color), start, end, line_width)

    def set_visible(self, value: bool) -> None:
        """Set visibility of path."""
        self._visible = value

    def get_shapes(self, start: tuple[float, float], end: tuple[float, float],
                   stops: list[tuple[int, int, int]]) -> None:
        """Get shapes for a path.

        points is a list of tuples of (trip_id, stop_id_start, stop_id_end)
        """
        # init_db('data', force=True)
        query = TransitQuery()
        shapes = []
        self.shapes = [(0, [start])]
        self.routes = []

        for i in range(len(stops) - 1, -1, -1):
            trip_id, stop_id_start, stop_id_end = stops[i]
            if trip_id != 0:
                shapes.append(query.get_shape_data(trip_id, stop_id_start, stop_id_end))
                self.routes.append({'start': stop_id_start, 'end': stop_id_end})
            # else:
            #     self.shapes[0].append((stop_id_start, stop_id_end))

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

        if self.shapes[-1][0] != 0:
            self.shapes.append((0, [self.shapes[-1][1][-1], end]))
        else:
            self.shapes[-1][1].append(end)
        query.close()

    def routes_to_text(self) -> list[str]:
        """Returns a list of strings to be used in PygPageLabel from routes information.

        self.routes is a dictionary of the following format:
            - start: stop ID of the starting stop of a route in this path
            - end: stop ID of the ending stop of a route in this path
            - route_short_name: TTC public route code (integer)
            - route_long_name: full TTC route name (string)
            - route_type: GTFS defined route_type codes (integer). The TTC transit dataset includes
                - 0 -> Tram, Streetcar, Light rail
                - 1 -> Subway, Metro
                - 3 -> Bus
            - route_color: hexadecimal route colour (string)
            - route_text_color: hexadecimal route text colour (string)
        """
        stops = {}
        route_types = {0: 'Tram', 1: 'Subway', 3: 'Bus'}
        query = TransitQuery()
        if self.routes[0]['start'] not in stops:
            stops[self.routes[0]['start']] = query.get_stop_info(self.routes[0]['start'])
        routes_text = ['1.',
                       'Walk from starting point to stop ' +
                       str(stops[self.routes[0]['start']]['stop_name']) +
                       ' (' + str(stops[self.routes[0]['start']]['stop_code']) + ')',
                       '']
        for i in range(0, len(self.routes)):
            routes_text.append(str(i + 2) + '.')
            routes_text.append('Route Name: ' + self.routes[i]['route_long_name'])
            routes_text.append('Route Type: ' + route_types[self.routes[i]['route_type']])
            if self.routes[i]['start'] not in stops:
                stops[self.routes[i]['start']] = query.get_stop_info(self.routes[i]['start'])
            if self.routes[i]['end'] not in stops:
                stops[self.routes[i]['end']] = query.get_stop_info(self.routes[i]['end'])
            routes_text.append('Stop ' + str(stops[self.routes[i]['start']]['stop_name']) +
                               ' (' + str(stops[self.routes[i]['start']]['stop_code']) + ') ' +
                               ' to stop ' + str(stops[self.routes[i]['end']]['stop_name']) +
                               ' (' + str(stops[self.routes[i]['end']]['stop_code']) + ') ')
            routes_text.append('')
        if self.routes[-1]['end'] not in stops:
            stops[self.routes[-1]['end']] = query.get_stop_info(self.routes[-1]['end'])
        routes_text.extend([str(len(self.routes) + 2) + '.',
                            'Walk from stop ' + str(stops[self.routes[-1]['end']]['stop_name']) +
                            ' (' + str(stops[self.routes[-1]['end']]['stop_code']) + ')'])
        query.close()
        return routes_text


if __name__ == '__main__':
    # TODO pyta
    ...
    # init_db('data', force=True)
