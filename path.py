"""Path class"""
import pygame
from data_interface import TransitQuery, init_db
from image import Image
from typing import Union


class Path:
    """The path to be drawn."""
    _routes: dict[int, dict[str, Union[dict, str]]]
    shapes: list[tuple[float, float]]

    def __init__(self) -> None:
        """Initialize a Path object."""
        self._routes = {}
        self.shapes = []

    def draw(self, screen: pygame.Surface, image: Image,
             orig_x: int, orig_y: int, line_width: int = 2) -> None:
        """Draw the path"""
        for point in self.shapes:
            start_lat, start_lon = point[0]
            end_lat, end_lon = point[1]
            start = image.lat_lon_to_coord(start_lat, start_lon, orig_x, orig_y)
            end = image.lat_lon_to_coord(end_lat, end_lon, orig_x, orig_y)
            pygame.draw.line(screen, pygame.Color('black'), start, end, line_width)

    def get_shapes(self, stops: list[tuple[int, int, int]]) -> None:
        """Get shapes for a path.

        points is a list of tuples of (trip_id, stop_id_start, stop_id_end)
        """
        init_db('data')
        query = TransitQuery()
        shapes = []

        for i in range(len(stops) - 1, -1, -1):
            trip_id, stop_id_start, stop_id_end = stops[i]
            shapes.append(query.get_shape_data(trip_id, stop_id_start, stop_id_end))

        for shape in shapes:
            if shape['route_id'] not in self._routes:
                self._routes[shape['route_id']] = query.get_route_info(shape['route_id'])
            for lat_lon in shape['shape']:
                self.shapes.append(lat_lon)
        print(self.shapes)


if __name__ == '__main__':
    # TODO pyta

    # init_db('data', force=True)
    q = TransitQuery()
    p = Path()
    test_path = [(41910034, 3981, 9392), (41910034, 4206, 3981), (0, 3981, 4206),
                 (41910034, 4206, 3981), (0, 3981, 4206), (41910034, 4206, 3981), (0, 3981, 4206),
                 (41910034, 4206, 3981)]
