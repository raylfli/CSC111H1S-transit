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
from pygui import PygButton, PygDropdown, PygLabel
from waypoint import Waypoint
from path import Path
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
DAYS_TEXT = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


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


def draw_path(screen: pygame.Surface, image: Image,
              path: Path, orig_x: int, orig_y: int) -> None:
    """Draw path."""
    path.draw(screen, image, orig_x, orig_y)


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


def reset_points(button: PygButton, dropdown: PygDropdown) -> dict:
    """..."""
    button.set_visible(False)
    button.set_text(text=PATH_TEXT)
    return {'selected': dropdown.selected, 'pts': []}


def time_to_sec(time: list[int]) -> int:
    """Return the number of seconds after midnight from a given time.

    Preconditions:
        - len(time) == 3
    """
    hour, minute, second = time[0], time[1], time[2]
    return hour * 3600 + minute * 60 + second


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
    down, scroll = False, False
    reset, clicked = False, False
    show_path = False
    x_diff, y_diff = 0, 0
    zoom = 0
    waypoints = {'day': DAYS_TEXT[0], 'time': (0, 0, 0), 'pts': []}
    buttons = {ZOOM: [PygButton(x=width - PADDING - button_width,
                                y=height - PADDING - 2 * button_height,
                                width=button_width, height=button_height),
                      PygButton(x=width - PADDING - button_width,
                                y=height - PADDING - button_height,
                                width=button_width, height=button_height)],
               SETTINGS: [PygDropdown(x=PADDING, y=PADDING,
                                      width=PADDING * 2, height=PADDING // 2,
                                      options=DAYS_TEXT),
                          PygDropdown(x=PADDING * 4, y=PADDING,
                                      width=PADDING, height=PADDING // 2,
                                      options=[str(x) for x in range(0, 23)]),
                          PygDropdown(x=PADDING * 5, y=PADDING,
                                      width=PADDING, height=PADDING // 2,
                                      options=[str(x) for x in range(0, 59)]),
                          PygDropdown(x=PADDING * 6, y=PADDING,
                                      width=PADDING, height=PADDING // 2,
                                      options=[str(x) for x in range(0, 59)])],
               GET_PATH: [PygButton(x=PADDING, y=height - PADDING - button_height,
                                    width=button_width, height=button_height,
                                    text=PATH_TEXT, visible=False)]
               }

    # load image
    images = load_images(filename)
    tile = load_zoom_image(images, zoom)

    # PATH TESTER
    path = Path()
    path._routes = {62667: {}}
    path.shapes = [(43.760348, -79.410691), (43.759892, -79.410757), (43.743248, -79.405991)]

    label = PygLabel(200, 200, 100, 50, 'Lorem Ipsum', background_color=(255, 255, 255))

    # Start the event loop
    while True:
        # Display
        draw_map(screen, tile, x, y)
        draw_waypoints(screen, images[zoom], waypoints, x, y)
        if show_path:
            draw_path(screen, images[zoom], path, x, y)
        draw_buttons(screen, buttons, width, height)

        label.draw(screen)

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

            for i in range(0, len(buttons[SETTINGS])):
                if buttons[SETTINGS][i].on_click(event):
                    buttons[SETTINGS][i].on_select(event)
                    if i == 0:
                        waypoints['day'] = buttons[SETTINGS][i].selected
                    else:
                        time = []
                        for j in range(1, len(buttons[SETTINGS])):
                            time.append(int(buttons[SETTINGS][j].selected))
                        waypoints['time'] = time_to_sec(time)
                    clicked = True

            # Zoom in
            if buttons[ZOOM][0].on_click(event):
                if clamp(zoom + 1) != zoom:
                    zoom = clamp(zoom + 1)
                    x, y = 0, 0
                    tile = load_zoom_image(images, zoom)
                clicked = True

            # Zoom out
            elif buttons[ZOOM][1].on_click(event):
                if clamp(zoom - 1) != zoom:
                    zoom = clamp(zoom - 1)
                    x, y = 0, 0
                    tile = load_zoom_image(images, zoom)
                clicked = True

            elif buttons[GET_PATH][0].on_click(event):
                if buttons[GET_PATH][0].get_text() == PATH_TEXT:
                    print('points: ' + str(waypoints['pts'][0].get_lat_lon()) +
                          ', ' + str(waypoints['pts'][1].get_lat_lon()) +
                          '; time: ' + str(waypoints['time']) + '; day: ' + waypoints['day'])
                    # give to algorithm
                    show_path = True
                else:
                    reset = True
                    show_path = False
                clicked = True

            # Start scroll
            else:
                x_diff, y_diff = scroll_diff(x, mouse_x), scroll_diff(y, mouse_y)
                down = True

        if event.type == pygame.MOUSEBUTTONUP:
            down = False

            # Clicked point
            if not (scroll or clicked):
                mouse_x, mouse_y = pygame.mouse.get_pos()

                # get lat/lon
                user_lat, user_lon = images[zoom].coord_to_lat_lon(mouse_x, mouse_y, x, y)
                check_points_clicked(user_lat, user_lon, waypoints, buttons[GET_PATH][0])
            else:
                scroll = False
                clicked = False

            if reset:
                waypoints = reset_points(buttons[GET_PATH][0], buttons[SETTINGS][0])
                reset = False

        if event.type == pygame.MOUSEMOTION:
            # scroll if mouse down
            if down:
                scroll = True
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
