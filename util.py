"""Fun utility things"""
import math


def distance(location1: tuple[float, float], location2: tuple[float, float]) -> float:
    """Great-circle distance between two points location1 and location2, calculated using
     the haversine formula.

    location1 and location2 are tuples of coordinates given in degrees north and degrees east.
    """
    earth_radius = 6368  # radius of the earth in km

    delta_phi = math.radians(location2[0] - location1[0])
    delta_lambda = math.radians(location2[1] - location1[1])

    central_angle = 2 * math.asin(math.sqrt((math.sin(delta_phi / 2)) ** 2
                                            + math.cos(math.radians(location1[0]))
                                            * math.cos(math.radians(location2[0]))
                                            * (math.sin(delta_lambda / 2)) ** 2))

    return central_angle * earth_radius
