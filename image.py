"""TTC Route Planner for Toronto, Ontario -- Image class

This module provides the functions and class for displaying a base map and its zoom levels.

This file is Copyright (c) 2021 Anna Cho, Charles Wong, Grace Tian, Raymond Li
"""

import csv


class Image:
    """An image of the map at a certain zoom level.

    Instance Attributes:
        - file: file name of the image
        - zoom: int for the zoom level
        - width: width of image
        - height: height of image
        - lat_top: float for the latitude of the top of the map image
        - lat_bottom: float for the latitude of the bottom of the map image
        - lon_left: float for the longitude of the left of the map image
        - lon_right: float for the longitude of the right of the map image

    Representation Invariants:
        - self.width >= 0
        - self.height >= 0
        - self.zoom >= 0
        - self.lon_left <= self.lon_right
        - self.lat_bottom <= self.lat_top
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
        """Initialize an Image object.

        Preconditions:
            - width >= 0
            - height >= 0
            - zoom >= 0
            - lon_left <= lon_right
            - lat_bottom <= lat_top
        """
        self.file = file
        self.zoom = zoom
        self.width = width
        self.height = height
        self.lat_top = lat_top
        self.lat_bottom = lat_bottom
        self.lon_left = lon_left
        self.lon_right = lon_right

    def get_file(self) -> str:
        """Return file name."""
        return self.file

    def lat_lon_to_coord(self, lat: float, lon: float,
                         orig_x: int = 0, orig_y: int = 0) -> tuple[float, float]:
        """Returns the tuple of the corresponding coordinate of the given latitude and longitude.
        The coordinate is (x, y), where the x-coordinate starts from 0 on left of the image
            and the y-coordinate starts from 0 on the top of the image."""
        x_unit = (self.lon_right - self.lon_left) / self.width
        y_unit = (self.lat_bottom - self.lat_top) / self.height
        x = (lon - self.lon_left) / x_unit + orig_x
        y = (lat - self.lat_top) / y_unit + orig_y
        return (x, y)

    def coord_to_lat_lon(self, x: float, y: float, orig_x: int = 0, orig_y: int = 0) \
            -> tuple[float, float]:
        """Returns the tuple of the corresponding (latitude, longitude) of the given coordinate
        on the Image.
        """
        x_unit = (self.lon_right - self.lon_left) / self.width
        y_unit = (self.lat_bottom - self.lat_top) / self.height
        lon = x_unit * (x - orig_x) + self.lon_left
        lat = y_unit * (y - orig_y) + self.lat_top
        return (lat, lon)


def load_images(filename: str) -> dict[int, Image]:
    """Return dictionary of the zoom number to its corresponding Image object.

    Loads Image objects from the given csv file.
    File should be in the format:
        - Every entry is one image to use as a base map
        - Each entry contains the following info in the given order:
            - file_name: str of the file name of the image to be used
            - zoom: int of the zoom level
            - width: width of the image
            - height: height of the image
            - lat_top: latitude of the top of the map image
            - lat_bottom: latitude of the bottom of the map image
            - lon_left: longitude of the left of the map image
            - lon_right: longitude of the right of the map image
    """
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
        'disable': ['E1136', 'R0913', 'R0902']
    })
