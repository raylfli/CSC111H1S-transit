"""

To-do:
    - Pass location to backend for path finding
    - Get path from locations chosen (get from backend)
    - Display path (draw lines for path)
    - Display sidebar for path info
    - Get larger zoom images

"""
import pygame
from image import Image, load_images
from pygui import PygButton, PygDropdown
from waypoint import Waypoint
from typing import Union

ALLOWED = [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP,
           pygame.MOUSEMOTION, pygame.KEYDOWN]
MAX_ZOOM = 3
PADDING = 50
ZOOM = 'zoom'
SETTINGS = 'settings'
GET_PATH = 'path'
PATH_TEXT = 'Get path'
RESET_PATH_TEXT = 'Reset'
DROPDOWN_TEXT = ['Morning', 'Afternoon', 'Evening']
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


def draw_zoom(screen: pygame.Surface, buttons: list[PygButton], width: int, height: int) -> None:
    """ ...

    Precondition:
        - button[0].height > button[1].height

    """
    for button in buttons:
        button.draw(screen)
    # pygame.draw.rect(screen, pygame.Color('white'), (width - 100, height - 150, 50, 100))
    pygame.draw.line(screen, pygame.Color('black'),
                     (width - 2 * PADDING, height - PADDING), (width - PADDING, height - PADDING))
    pygame.draw.line(screen, pygame.Color('black'),
                     (width - 2 * PADDING + 10, height - 3 * PADDING + 25),
                     (width - 2 * PADDING + 40, height - 3 * PADDING + 25), 7)
    pygame.draw.line(screen, pygame.Color('black'), (width - 100 + 10, height - 150 + 75),
                     (width - 100 + 40, height - 150 + 75), 7)
    pygame.draw.line(screen, pygame.Color('black'), (width - 100 + 25, height - 150 + 10),
                     (width - 100 + 25, height - 150 + 40), 7)


def draw_settings(screen: pygame.Surface, settings: list[PygDropdown]) -> None:
    """..."""
    for setting in settings:
        setting.draw(screen)


def draw_check_path(screen: pygame.Surface, buttons: list[PygButton]) -> None:
    """..."""
    for button in buttons:
        button.draw(screen)


def draw_buttons(screen: pygame.Surface, buttons: dict, width: int, height: int) -> None:
    """..."""
    draw_zoom(screen, buttons[ZOOM], width, height)
    draw_settings(screen, buttons[SETTINGS])
    draw_check_path(screen, buttons[GET_PATH])


def draw_waypoints(screen: pygame.Surface, image: Image, waypoints: dict,
                   orig_x: int, orig_y: int) -> None:
    """dkm this isn't acc drawing waypoints"""
    for waypoint in waypoints['pts']:
        draw_waypoint(screen, image, waypoint, orig_x, orig_y)


def draw_waypoint(screen: pygame.Surface, image: Image,
                  waypoint: Waypoint, orig_x: int, orig_y: int) -> None:
    """..."""
    x, y = image.lat_lon_to_coord(waypoint.lat, waypoint.lon, orig_x=orig_x, orig_y=orig_y)
    pygame.draw.circle(screen, pygame.Color('black'), (x, y), 4)


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


def check_points_clicked(lat: float, lon: float,
                         waypoints: dict, button: PygButton) -> None:
    """Mutate points to reflect if the point is the starting or ending destination"""
    if waypoints['pts'] == []:
        waypoints['pts'].append(Waypoint(lat, lon, chosen_start=True))
    elif len(waypoints['pts']) == 1:
        button.set_visible(True)
        waypoints['pts'].append(Waypoint(lat, lon, chosen_end=True))
    else:
        button.set_text(text=RESET_PATH_TEXT)


def reset_points(button: PygButton) -> dict:
    """..."""
    button.set_visible(False)
    button.set_text(text=PATH_TEXT)
    return {'selected': DROPDOWN_TEXT[0], 'pts': []}


def run_map(filename: str = "data/image_data/images_data.csv",
            width: int = 800, height: int = 600,
            button_width: int = 50, button_height: int = 50) -> None:
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
    # points = {'start': (False, (0, 0)), 'stop': (False, (0, 0)), 'selected': DROPDOWN_TEXT[0]}
    waypoints = {'selected': DROPDOWN_TEXT[0], 'pts': []}
    buttons = {ZOOM: [PygButton(x=width - PADDING - button_width,
                                y=height - PADDING - 2 * button_height,
                                width=button_width, height=button_height),
                      PygButton(x=width - PADDING - button_width,
                                y=height - PADDING - button_height,
                                width=button_width, height=button_height)],
               SETTINGS: [PygDropdown(x=PADDING, y=PADDING,
                                      width=PADDING * 2, height=PADDING // 2,
                                      options=DROPDOWN_TEXT)],
               GET_PATH: [PygButton(x=PADDING, y=height - PADDING - button_height,
                                    width=button_width, height=button_height,
                                    text=PATH_TEXT, visible=False)]
               }

    # load image
    images = load_images(filename)
    tile = load_zoom_image(images, zoom)

    # Start the event loop
    while True:
        # Display
        draw_map(screen, tile, x, y)
        draw_buttons(screen, buttons, width, height)
        draw_waypoints(screen, images[zoom], waypoints, x, y)
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

            # Zoom in
            if buttons[ZOOM][0].on_click(event):
                if clamp(zoom + 1) != zoom:
                    zoom = clamp(zoom + 1)
                    x, y = 0, 0
                    tile = load_zoom_image(images, zoom)

            # Zoom out
            elif buttons[ZOOM][1].on_click(event):
                if clamp(zoom - 1) != zoom:
                    zoom = clamp(zoom - 1)
                    x, y = 0, 0
                    tile = load_zoom_image(images, zoom)

            # dropdown for settings
            elif buttons[SETTINGS][0].on_click(event):
                buttons[SETTINGS][0].on_select(event)
                waypoints['selected'] = buttons[SETTINGS][0].selected

            elif buttons[GET_PATH][0].on_click(event):
                if buttons[GET_PATH][0].get_text() == PATH_TEXT:
                    print('points: ' + str(waypoints['pts'][0].get_lat_lon()) +
                          ', ' + str(waypoints['pts'][1].get_lat_lon()) +
                          '; time: ' + waypoints['selected'])
                    # give to algorithm
                else:
                    waypoints = reset_points(buttons[GET_PATH][0])

            # Clicked point or scroll
            else:
                # get lat/lon
                user_lat, user_lon = images[zoom].coord_to_lat_lon(mouse_x, mouse_y, x, y)
                check_points_clicked(user_lat, user_lon, waypoints, buttons[GET_PATH][0])

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