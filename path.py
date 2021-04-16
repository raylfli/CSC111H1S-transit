"""Path class"""
import pygame
from data_interface import TransitQuery, init_db
from image import Image
from typing import Union


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
    _visible: bool
    routes: list[dict[str, Union[str, int]]]
    shapes: list[tuple[float, float]]

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
            for i in range(0, len(self.shapes) - 1):
                start_lat, start_lon = self.shapes[i]
                end_lat, end_lon = self.shapes[i + 1]
                start = image.lat_lon_to_coord(start_lat, start_lon, orig_x, orig_y)
                end = image.lat_lon_to_coord(end_lat, end_lon, orig_x, orig_y)
                pygame.draw.line(screen, pygame.Color('black'), start, end, line_width)

    def set_visible(self, value: bool) -> None:
        """Set visibility of path."""
        self._visible = value

    def get_shapes(self, start: tuple[float, float], end: tuple[float, float],
                   stops: list[tuple[int, int, int]]) -> None:
        """Get shapes for a path.

        points is a list of tuples of (trip_id, stop_id_start, stop_id_end)
        """
        # init_db('data')
        query = TransitQuery()
        shapes = []
        self.shapes = [start]
        self.routes = []

        for i in range(len(stops) - 1, -1, -1):
            trip_id, stop_id_start, stop_id_end = stops[i]
            if trip_id != 0:
                shapes.append(query.get_shape_data(trip_id, stop_id_start, stop_id_end))
                self.routes.append({'start': stop_id_start, 'end': stop_id_end})

        for i in range(0, len(shapes)):
            if shapes[i]['route_id'] not in self._routes_info:
                self._routes_info[shapes[i]['route_id']] = \
                    query.get_route_info(shapes[i]['route_id'])
            self.routes[i].update(self._routes_info[shapes[i]['route_id']])
            for lat_lon in shapes[i]['shape']:
                self.shapes.append(lat_lon)
        self.shapes.append(end)
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
        route_types = {0: 'Tram', 1: 'Subway', 3: 'Bus'}
        routes_text = []
        for i in range(0, len(self.routes)):
            routes_text.append(str(i + 1) + '.')
            routes_text.append('Route Name: ')
            routes_text.append(self.routes[i]['route_long_name'])
            routes_text.append('Route Type: ')
            routes_text.append(route_types[self.routes[i]['route_type']])
            routes_text.append('Stop ' + str(self.routes[i]['start']) +
                               ' to stop ' + str(self.routes[i]['end']))
            if i < len(self.routes) - 1:
                routes_text.append('')
        return routes_text


if __name__ == '__main__':
    # TODO pyta
    ...
    # init_db('data', force=True)
