"""Path class"""
import pygame
from data_interface import TransitQuery, init_db
from image import Image
from typing import Union


class Path:
    """The path to be drawn."""
    _routes: dict[int, dict[str, Union[dict, str]]]
    _visible: bool
    shapes: list[tuple[float, float]]

    def __init__(self, visible: bool = False) -> None:
        """Initialize a Path object."""
        self._routes = {}
        self.shapes = []
        self._visible = False

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
        """..."""
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

        for i in range(len(stops) - 1, -1, -1):
            trip_id, stop_id_start, stop_id_end = stops[i]
            if trip_id != 0:
                shapes.append(query.get_shape_data(trip_id, stop_id_start, stop_id_end))

        for shape in shapes:
            if shape['route_id'] not in self._routes:
                self._routes[shape['route_id']] = query.get_route_info(shape['route_id'])
            for lat_lon in shape['shape']:
                self.shapes.append(lat_lon)
        self.shapes.append(end)
        print(self.shapes)
        query.close()


if __name__ == '__main__':
    # TODO pyta
    ...
    # init_db('data', force=True)
