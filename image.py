"""..."""
import csv


class Image:
    """

    Wtv it was called here lol:
        - file: File name
        - width: width of image
        - height: height of image
    """
    file: str
    zoom: int
    width: int
    height: int
    lat_top: float
    lat_bottom: float
    lon_left: float
    lon_right: float

    def __init__(self, file: str, zoom: int, width: int, height: int,
                 lat_top: float, lat_bottom: float, lon_left: float, lon_right: float) -> None:
        """..."""
        self.file = file
        self.zoom = zoom
        self.width = width
        self.height = height
        self.lat_top = lat_top
        self.lat_bottom = lat_bottom
        self.lon_left = lon_left
        self.lon_right = lon_right

    def get_file(self) -> str:
        """Return file."""
        return self.file

    def lat_lon_to_coord(self, lat: float, lon: float,
                         orig_x: int = 0, orig_y: int = 0) -> tuple[float, float]:
        """..."""
        x_unit = (self.lon_right - self.lon_left) / self.width
        y_unit = (self.lat_bottom - self.lat_top) / self.height
        x = (lon - self.lon_left) / x_unit + orig_x
        y = (lat - self.lat_top) / y_unit + orig_y
        return (x, y)

    def coord_to_lat_lon(self, x, y, orig_x: int = 0, orig_y: int = 0) -> tuple[float, float]:
        """..."""
        x_unit = (self.lon_right - self.lon_left) / self.width
        y_unit = (self.lat_bottom - self.lat_top) / self.height
        lon = x_unit * (x - orig_x) + self.lon_left
        lat = y_unit * (y - orig_y) + self.lat_top
        return (lat, lon)


def load_images(filename: str) -> dict[int, Image]:
    """..."""
    images_so_far = {}  # map zoom to Image
    with open(filename) as file:
        reader = csv.reader(file)

        for row in reader:
            file = row[0]
            zoom = int(row[1])
            width, height = int(row[2]), int(row[3])
            lat_top, lat_bottom = float(row[4]), float(row[5])
            lon_left, lon_right = float(row[6]), float(row[7])
            images_so_far[zoom] = Image(file, zoom, width, height,
                                        lat_top, lat_bottom, lon_left, lon_right)

    return images_so_far


if __name__ == "__main__":
    import python_ta.contracts
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()

    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['csv'],
        'allowed-io': ['load_images'],
        'max-line-length': 100,
        'disable': ['E1136', 'R0913', 'R0902']})
