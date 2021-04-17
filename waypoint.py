"""..."""
import pygame
from image import Image


class Waypoint:
    """..."""
    lat: float
    lon: float
    chosen_start: bool
    chosen_end: bool

    def __init__(self, lat: float, long: float,
                 chosen_start: bool = False, chosen_end: bool = False) -> None:
        """..."""
        self.lat = lat
        self.lon = long
        self.chosen_start = chosen_start
        self.chosen_end = chosen_end

    def get_lat_lon(self) -> tuple[float, float]:
        """..."""
        return (self.lat, self.lon)

    def draw(self, screen: pygame.surface, image: Image, orig_x: int, orig_y: int) -> None:
        """Draw waypoints."""
        x, y = image.lat_lon_to_coord(self.lat, self.lon, orig_x=orig_x, orig_y=orig_y)
        if self.chosen_start:
            pygame.draw.circle(screen, pygame.Color('blue'), (x, y), 4)
        elif self.chosen_end:
            pygame.draw.circle(screen, pygame.Color('red'), (x, y), 4)


if __name__ == "__main__":
    # pyta
    ...
