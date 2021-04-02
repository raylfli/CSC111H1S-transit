"""..."""
import pygame
from image import Image, load_images
from typing import Union

ALLOWED = [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP,
           pygame.MOUSEMOTION, pygame.KEYDOWN]
MAX_ZOOM = 3


def initialize_screen(allowed: list, width: int, height: int) -> pygame.Surface:
    """..."""
    pygame.display.init()
    pygame.font.init()
    screen = pygame.display.set_mode((width, height))

    pygame.event.clear()
    pygame.event.set_blocked(None)
    pygame.event.set_allowed([pygame.QUIT] + allowed)
    return screen


def load_zoom_image(images: dict[int, Image], zoom: int = 0) -> pygame.Surface:
    """..."""
    # Choose image to load based on zoom
    image = images[zoom]
    return pygame.image.load(image.file)


def draw_map(screen: pygame.Surface, tile: Union[pygame.Surface, pygame.SurfaceType],
             x: int, y: int) -> None:
    """..."""
    # Draw image
    screen.blit(tile, (x, y))


def draw_zoom(screen: pygame.Surface, width: int, height: int) -> None:
    """..."""
    # Draw two squares: https://www.pygame.org/docs/ref/draw.html
    # Draw + and - sign
    pygame.draw.rect(screen, pygame.Color('white'), (width - 100, height - 150, 50, 100))
    pygame.draw.line(screen, pygame.Color('black'),
                     (width - 100, height - 50), (width - 50, height - 50))
    pygame.draw.line(screen, pygame.Color('black'), (width - 100 + 10, height - 150 + 25),
                     (width - 100 + 40, height - 150 + 25), 7)
    pygame.draw.line(screen, pygame.Color('black'), (width - 100 + 10, height - 150 + 75),
                     (width - 100 + 40, height - 150 + 75), 7)
    pygame.draw.line(screen, pygame.Color('black'), (width - 100 + 25, height - 150 + 10),
                     (width - 100 + 25, height - 150 + 40), 7)


def draw_settings(screen: pygame.Surface) -> None:
    """..."""
    # Draw original box


def draw_waypoints(screen: pygame.Surface, image: Image, lat: float, lon: float,
                   orig_x: int, orig_y: int) -> None:
    """dkm this isn't acc drawing waypoints"""
    x, y = image.lat_lon_to_coord(lat, lon)
    pygame.draw.circle(screen, pygame.Color('black'), (orig_x + x, orig_y + y), 4)


def scroll_diff(p: int, mouse_p) -> int:
    """..."""
    return p - mouse_p


def continue_scroll(image: Image, width: int, height: int, x: int, y: int,
                    mouse_x: int, mouse_y: int, x_diff: int, y_diff: int) -> tuple[int, int]:
    """..."""
    new_x, new_y = mouse_x + x_diff, mouse_y + y_diff
    if not (new_x > 0 or new_x + image.width < width) and \
            not (new_y > 0 or new_y + image.height < height):
        return new_x, new_y
    else:
        return x, y


def zoom_in(zoom: int, max: int) -> int:
    """..."""
    if zoom < max:
        return zoom + 1
    else:
        return zoom


def zoom_out(zoom: int) -> int:
    """..."""
    if zoom > 0:
        return zoom - 1
    else:
        return zoom


def can_zoom(zoom: int, max_zoom: int, direction: str) -> bool:
    """...

    Preconditions:
        - direction in {'in', 'out'}
    """
    return (direction == 'in' and zoom < max_zoom) or (direction == 'out' and zoom > 0)


def run_map(filename: str = "data/image_data/images_data.csv",
            width: int = 800, height: int = 600,
            lat: float = 43.725163, lon: float = -79.457222) -> None:
    """...

    Preconditions:
        - 150 <= width <= 1000
        - 150 <= height <= 800
        - 43.52434 <= lat <= 43.96036
        - -79.81884 <= lon <= -79.06096
    """
    screen = initialize_screen(ALLOWED, width, height)
    x, y = 0, 0
    scroll = False
    x_diff, y_diff = 0, 0
    zoom = 0

    # load image
    images = load_images(filename)
    tile = load_zoom_image(images, zoom)

    # Start the event loop
    while True:
        # Display
        draw_map(screen, tile, x, y)
        draw_zoom(screen, width, height)
        draw_waypoints(screen, images[zoom], lat, lon, x, y)
        pygame.display.flip()

        # ---------------------------------------------------------------
        # Process events
        # ---------------------------------------------------------------
        event = pygame.event.wait()

        # End
        if event.type == pygame.QUIT or \
                (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            # Exit the event loop
            pygame.quit()
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Get location data
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # Zoom out
            if (width - 100) <= mouse_x <= (width - 50) \
                    and (height - 100) <= mouse_y <= (height - 50):
                if can_zoom(zoom, MAX_ZOOM, 'out'):
                    zoom = zoom_out(zoom)
                    x, y = 0, 0
                    tile = load_zoom_image(images, zoom)

            # Zoom in
            elif (width - 100) <= mouse_x <= (width - 50) \
                    and (height - 150) <= mouse_y <= (height - 100):  # Check if clicked zoom in
                if can_zoom(zoom, MAX_ZOOM, 'in'):
                    zoom = zoom_in(zoom, MAX_ZOOM)
                    x, y = 0, 0
                    tile = load_zoom_image(images, zoom)
            # elif ...:  # Check if clicked settings (dropdown for time block)
            #     ...
            # elif ...:  # Check if clicked waypoint
            #     ...

            # Clicked point or scroll
            else:
                # get lat/lon
                user_lat, user_lon = images[zoom].coord_to_lat_lon(mouse_x, mouse_y)
                # to pass to algorithm

                # get scroll info
                x_diff, y_diff = scroll_diff(x, mouse_x), scroll_diff(y, mouse_y)
                scroll = True

        if event.type == pygame.MOUSEBUTTONUP:
            scroll = False

        if event.type == pygame.MOUSEMOTION:
            # scroll if mouse down
            if scroll:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                new_x, new_y = continue_scroll(images[zoom], width, height, x, y,
                                               mouse_x, mouse_y, x_diff, y_diff)
                if new_x == x:
                    x_diff = scroll_diff(x, mouse_x)
                else:
                    x = new_x
                if new_y == y:
                    y_diff = scroll_diff(y, mouse_y)
                else:
                    y = new_y


if __name__ == "__main__":
    # pyta

    # run map
    run_map()
