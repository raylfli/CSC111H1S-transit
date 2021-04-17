"""TTC Route Planner for Toronto, Ontario -- Waypoint class

This file contains the Waypoint class to determine the start and stop points of a path.
The class stores the location of the point and draws the point.

This file is Copyright (c) 2021 Anna Cho, Charles Wong, Grace Tian, Raymond Li
"""

import pygame
from image import Image


class Waypoint:
    """Waypoint object that stores for a point on the map.

    Instance Attributes:
        - lat: float of the latitude of the point
        - lon: float of the longitude of the points
        - chosen_start: bool determining if this point is the start of a path
        - chosen_end: bool determining if this point is the end of a path
    """
    lat: float
    lon: float
    chosen_start: bool
    chosen_end: bool

    def __init__(self, lat: float, long: float,
                 chosen_start: bool = False, chosen_end: bool = False) -> None:
        """Initialize a Waypoint object."""
        self.lat = lat
        self.lon = long
        self.chosen_start = chosen_start
        self.chosen_end = chosen_end

    def get_lat_lon(self) -> tuple[float, float]:
        """Return a tuple of the latitude and longitude of the point."""
        return (self.lat, self.lon)

    def draw(self, screen: pygame.surface, image: Image,
             orig_x: int, orig_y: int, radius: int = 4) -> None:
        """Draw waypoints on a given screen."""
        x, y = image.lat_lon_to_coord(self.lat, self.lon, orig_x=orig_x, orig_y=orig_y)
        # Draw a blue circle for start point
        if self.chosen_start:
            pygame.draw.circle(screen, pygame.Color('blue'), (x, y), radius)
        # Draw a red circle for end point
        elif self.chosen_end:
            pygame.draw.circle(screen, pygame.Color('red'), (x, y), radius)


if __name__ == "__main__":
    import python_ta.contracts
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()

    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['pygame', 'image'],
        'allowed-io': [],
        'max-line-length': 100,
        'disable': ['E1136', 'E1121', 'R0913']})
