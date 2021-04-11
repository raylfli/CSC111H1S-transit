"""Path class"""
import pygame
from data_interface import TransitQuery
from image import Image


class Path:
    """The path to be drawn."""
    _routes: dict
    shapes: dict

    def __init__(self) -> None:
        """Initialize a Path object."""
        self._routes = {}
        self.shapes = {}

    def draw(self, screen: pygame.Surface, image: Image,
             orig_x: int, orig_y: int, line_width: int = 2) -> None:
        """Draw the path"""
        for route in self.shapes:
            points = self.shapes[route]
            for i in range(0, len(points) - 1):
                start_lat, start_lon = points[i]
                end_lat, end_lon = points[i + 1]
                start = image.lat_lon_to_coord(start_lat, start_lon, orig_x, orig_y)
                end = image.lat_lon_to_coord(end_lat, end_lon, orig_x, orig_y)
                pygame.draw.line(screen, pygame.Color('black'), start, end, line_width)

    def get_shapes(self, query: TransitQuery, stops: list[tuple[int, int, int]]) -> None:
        """Get shapes for a path.

        points is a list of tuples of (trip_id, stop_id_start, stop_id_end)
        """
        shapes = []
        for i in range(len(stops) - 1, -1, -1):
            trip_id, stop_id_start, stop_id_end = stops[i]
            shapes.append(query.get_shape_data(trip_id, stop_id_start, stop_id_end))

        for shape in shapes:
            if shape['route_id'] not in self._routes:
                self._routes[shape['route_id']] = query.get_route_info(shape['route_id'])
            if shape['route_id'] not in self.shapes:
                self.shapes[shape['route_id']] = shape['shape']
            else:
                for lat_lon in shape['shape']:
                    self.shapes[shape['route_id']].append(lat_lon)


if __name__ == '__main__':
    # TODO pyta
    ...
