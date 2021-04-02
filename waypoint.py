"""..."""


class _Waypoint:
    """..."""
    lat: float
    long: float
    chosen_start: bool
    chosen_end: bool

    def __init__(self, lat: float, long: float,
                 chosen_start: bool = False, chosen_end: bool = False) -> None:
        """..."""
        self.lat = lat
        self.long = long
        self.chosen_start = chosen_start
        self.chosen_end = chosen_end
