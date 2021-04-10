"""

To-do:
    - Add dropdown to choose time
    - Add location chooser (start, end)
    - Pass location to backend for path finding
    - Get path from locations chosen (get from backend)
    - Display path (draw lines for path)
    - Display sidebar for path info
    - Get larger zoom images
    - Create button class (for zoom and dropdown)

"""
import pygame
from image import Image, load_images
from typing import Union

ALLOWED = [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP,
           pygame.MOUSEMOTION, pygame.KEYDOWN]
MAX_ZOOM = 3
TEST_POINTS = [(43.74735, -79.1994),
               (43.81984, -79.21122),
               (43.768204, -79.412796),
               (43.684044, -79.3207),
               (43.828785, -79.275375),
               (43.708115, -79.31103),
               (43.680065, -79.34497),
               (43.785343, -79.31073),
               (43.698895, -79.4398),
               (43.69683, -79.4914)
               ]


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


def draw_waypoints(screen: pygame.Surface, image: Image, waypoints: list[tuple],
                   orig_x: int, orig_y: int) -> None:
    """dkm this isn't acc drawing waypoints"""
    for lat_lon in waypoints:
        lat, lon = lat_lon
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


def clamp(num, min_value: int = 0, max_value: int = 3):
    """..."""
    return max(min(num, max_value), min_value)


def run_map(filename: str = "data/image_data/images_data.csv",
            width: int = 800, height: int = 600) -> None:
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
        draw_waypoints(screen, images[zoom], TEST_POINTS, x, y)
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
                if clamp(zoom + 1) != zoom:
                    zoom = clamp(zoom + 1)
                    x, y = 0, 0
                    tile = load_zoom_image(images, zoom)

            # Zoom in
            elif (width - 100) <= mouse_x <= (width - 50) \
                    and (height - 150) <= mouse_y <= (height - 100):  # Check if clicked zoom in
                if clamp(zoom - 1) != zoom:
                    zoom = clamp(zoom - 1)
                    x, y = 0, 0
                    tile = load_zoom_image(images, zoom)

            # elif ...:  # Check if clicked settings (dropdown for time block)
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
