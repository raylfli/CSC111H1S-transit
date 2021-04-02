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

    def lat_lon_to_coord(self, lat: float, lon: float) -> tuple[float, float]:
        """..."""
        # lon_delta = self.lon_right - self.lon_left
        # lat_rad = lat * math.pi / 180
        # lat_bottom_rad = self.lat_bottom * math.pi / 180
        # x = (lon - self.lon_left) * (self.width / lon_delta)
        # world_map_width = (self.width / lon_delta * 360) / (2 * math.pi)
        # map_offset_y = self.width / 2 * math.log((1 + math.sin(lat_bottom_rad)) / (1 - math.sin(lat_bottom_rad)))
        # y = self.height - ((world_map_width / 2 * math.log(1 + math.sin(lat))) / (1 - math.sin(lat)) - map_offset_y)
        # mercator proj w sphere
        # # get x value
        # x = (lon + 180) * (self.width / 360)
        #
        # # convert from degrees to radians
        # lat_rad = (lat * math.pi) / 180
        #
        # # get y value
        # mercator_proj = math.log(math.tan((math.pi / 4) + (lat_rad / 2)), math.e)
        # y = (self.height / 2) - (self.width * mercator_proj / (2 * math.pi))

        x_unit = (self.lon_right - self.lon_left) / self.width
        y_unit = (self.lat_bottom - self.lat_top) / self.height
        x = (lon - self.lon_left) / x_unit
        y = (lat - self.lat_top) / y_unit
        return (x, y)

    def coord_to_lat_lon(self, x, y) -> tuple[float, float]:
        """..."""
        x_unit = (self.lon_right - self.lon_left) / self.width
        y_unit = (self.lat_bottom - self.lat_top) / self.height
        lon = x_unit * x + self.lon_left
        lat = y_unit * y + self.lat_top
        return (lat, lon)
        # lon_delta = self.lon_right - self.lon_left
        # lat_bottom_rad = self.lat_bottom * math.pi / 180
        # word_map_radius = self.width / lon_delta * 360 / (2 * math.pi)
        # map_offset_y = (word_map_radius / 2 * math.log(1 + math.sin(lat_bottom_rad)) /
        #                 (1 - math.sin(lat_bottom_rad)))
        # equator_y = self.height + map_offset_y
        # a = equator_y / word_map_radius
        #
        # lat = 180 / math.pi * (2 * math.atan(math.exp(a)) - math.pi / 2)
        # lon = self.lon_left + x / self.width * lon_delta


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
