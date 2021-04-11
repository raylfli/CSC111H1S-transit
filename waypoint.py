"""..."""


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


if __name__ == "__main__":
    # pyta
    ...
