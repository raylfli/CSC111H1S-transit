"""TTC Route Planner for Toronto, Ontario -- Map Visualization

This module packages the pygame visualization functions and provides code for running
the map visualization.

This file is Copyright (c) 2021 Anna Cho, Charles Wong, Grace Tian, Raymond Li
"""

import logging
import queue
from multiprocessing import Manager, Process
from typing import Union

import pygame

import pathfinding
from image import Image, load_images
from path import Path
from pygui import draw_dec, draw_inc, PygButton, PygDropdown, PygLabel, PygPageLabel, Rect
from waypoint import Waypoint

ALLOWED = [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP,
           pygame.MOUSEMOTION, pygame.KEYDOWN]
DAYS_TEXT = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
DAY_TO_INT = {'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4,
              'Friday': 5, 'Saturday': 6, 'Sunday': 7}


def initialize_screen(allowed: list, width: int, height: int) -> pygame.Surface:
    """Initialize a pygame screen."""
    pygame.display.init()
    pygame.font.init()
    screen = pygame.display.set_mode((width, height))

    pygame.event.clear()
    pygame.event.set_blocked(None)
    pygame.event.set_allowed([pygame.QUIT] + allowed)
    return screen


def load_zoom_image(images: dict[int, Image], zoom: int = 0) -> pygame.Surface:
    """Return image corresponding to the given zoom level as a pygame.Surface."""
    # Choose image to load based on zoom
    image = images[zoom]
    return pygame.image.load(image.file)


def draw_map(screen: pygame.Surface, tile: Union[pygame.Surface, pygame.SurfaceType],
             x: int, y: int) -> None:
    """Draw the map on the given screen."""
    # Draw image
    screen.blit(tile, (x, y))


def draw_zoom_in(screen: pygame.Surface, x: int, y: int, width: int, height: int) -> None:
    """Draw function for zoom in button.
    """
    pygame.draw.line(screen, pygame.Color('black'),  # horizontal line
                     (x + width / 10, y + height / 2), (x + width - width / 10, y + height / 2), 7)
    pygame.draw.line(screen, pygame.Color('black'),  # vertical line
                     (x + width / 2, y + height / 10), (x + width / 2, y + height - height / 10), 7)


def draw_zoom_out(screen: pygame.Surface, x: int, y: int, width: int, height: int) -> None:
    """Draw function for zoom out button."""
    pygame.draw.line(screen, pygame.Color('black'),  # horizontal line
                     (x + width / 10, y + height / 2), (x + width - width / 10, y + height / 2), 7)


def draw_waypoints(screen: pygame.Surface, image: Image, waypoints: list,
                   orig_x: int, orig_y: int) -> None:
    """Draw function for waypoints."""
    for i in range(min(len(waypoints), 2)):
        waypoints[i].draw(screen, image, orig_x, orig_y)


def draw_path(screen: pygame.Surface, image: Image,
              path: Path, orig_x: int, orig_y: int) -> None:
    """Draw path."""
    path.draw(screen, image, orig_x, orig_y)


def draw_progress(screen: pygame.Surface, x: int, y: int,
                  width: int, height: int, text: str) -> None:
    """Draw progressed section for progress bar."""
    pygame.draw.rect(screen, (180, 180, 180), (x, y, int(width * float(text[:-1]) / 100), height))


def continue_scroll(image: Image, width: int, height: int, x: int, y: int,
                    mouse_x: int, mouse_y: int, x_diff: int, y_diff: int) -> tuple[int, int]:
    """Return the (x, y) coordinates of the top left corner of the image after scrolling."""
    new_x, new_y = mouse_x + x_diff, mouse_y + y_diff
    if not (new_x > 0 or new_x + image.width < width) and \
            not (new_y > 0 or new_y + image.height < height):
        return new_x, new_y
    else:
        return x, y


def clamp(num: int, min_value: int = 0, max_value: int = 3) -> int:
    """Return the clamped value."""
    return max(min(num, max_value), min_value)


def check_points_clicked(lat: float, lon: float, waypoints: list) -> None:
    """Mutate points to reflect if the point is the starting or ending destination"""
    if waypoints == []:
        waypoints.append(Waypoint(lat, lon, chosen_start=True))
    elif len(waypoints) <= 1:
        waypoints.append(Waypoint(lat, lon, chosen_end=True))


def run_map(filename: str = "data/image_data/images_data.csv") -> None:
    """Run main map.

    Preconditions:
        - 43.52434 <= lat <= 43.96036
        - -79.81884 <= lon <= -79.06096
    """
    screen = initialize_screen(ALLOWED, 1000, 600)

    # map screen
    map_bound = Rect(200, 0, 800, 600)
    map_screen = pygame.Surface((map_bound.width, map_bound.height))

    x, y = 0, 0
    down, scroll, clicked, calculating = False, False, False, False
    x_diff, y_diff = 0, 0
    zoom = 0

    font = ("Calibri", 20)
    sidebar_font = ("Calibri", 11)

    waypoints = []

    zoom_b = [PygButton(x=map_bound.width - 80,
                        y=map_bound.height - 120,
                        width=30, height=30,
                        x_adjust=-200, draw_func=draw_zoom_in),
              PygButton(x=map_bound.width - 80,
                        y=map_bound.height - 80,
                        width=30, height=30,
                        x_adjust=-200, draw_func=draw_zoom_out)]

    progress_bar = PygLabel(int(map_bound.x + map_bound.width / 18),
                            int(map_bound.y + map_bound.height * 17 / 18), 100, 20, '0%',
                            ('Calibri', 12), background_color=(255, 255, 255), txt_align=1,
                            draw_func=draw_progress, visible=False)
    total_prog = 1
    curr_prog = 0

    time_nums = [0, 0, 0]

    settings_l = [PygLabel(20, 50, 50, 20, "Day:", font, background_color=(255, 255, 255)),
                  PygLabel(20, 100, 70, 20, "Hours:", font, background_color=(255, 255, 255)),
                  PygLabel(20, 125, 70, 20, "Minute:", font, background_color=(255, 255, 255)),
                  PygLabel(20, 150, 70, 20, "Second:", font, background_color=(255, 255, 255)),
                  PygLabel(100, 100, 30, 20, str(time_nums[0]), font,
                           background_color=(255, 255, 255), txt_align=2),
                  PygLabel(100, 125, 30, 20, str(time_nums[1]), font,

                           background_color=(255, 255, 255), txt_align=2),
                  PygLabel(100, 150, 30, 20, str(time_nums[2]), font,
                           background_color=(255, 255, 255), txt_align=2)]

    settings_b = [PygButton(25, 500, 150, 20, "Get Route", font, txt_align=1),
                  PygButton(25, 540, 150, 20, "Reset", font, txt_align=1),
                  PygButton(135, 100, 9, 9, draw_func=draw_inc),  # hour inc
                  PygButton(135, 111, 9, 9,
                            draw_func=draw_dec),  # hour dec
                  PygButton(135, 125, 9, 9,
                            draw_func=draw_inc),  # minute inc
                  PygButton(135, 136, 9, 9,
                            draw_func=draw_dec),  # minute dec
                  PygButton(135, 150, 9, 9,
                            draw_func=draw_inc),  # second inc
                  PygButton(135, 161, 9, 9,
                            draw_func=draw_dec)]  # second dec

    settings_dd = PygDropdown(80, 50, 100, 20, DAYS_TEXT, font)

    routes = PygPageLabel(20, 200, 160, 250, [],
                          font=sidebar_font, background_color=(255, 255, 255))

    # load image
    images = load_images(filename)
    tile = load_zoom_image(images, zoom)

    # create path
    path = Path()

    # create objects for multiprocessing
    manager = Manager()
    result_queue = manager.Queue()

    logger = logging.getLogger(__name__)

    # Start the event loop
    while True:
        # Draw map area
        draw_map(map_screen, tile, x, y)
        draw_path(map_screen, images[zoom], path, x, y)
        draw_waypoints(map_screen, images[zoom], waypoints, x, y)
        for button in zoom_b:
            button.draw(map_screen)

        # blit map onto screen
        screen.blit(map_screen, (map_bound.x, map_bound.y))

        progress_bar.draw(screen)

        # Draw settings bar area
        pygame.draw.rect(screen, (0, 100, 0), (0, 0, 200, 600))
        for button in settings_b:
            button.draw(screen)

        for label in settings_l:
            label.draw(screen)

        settings_dd.draw(screen)

        routes.draw(screen)

        pygame.display.flip()

        # ---------------------------------------------------------------
        # Process events
        # ---------------------------------------------------------------

        # multiprocessing message checks
        try:
            message = result_queue.get_nowait()
            logger.debug('Child process message recv: %s' % (message, ))
            if message[0] == 'DONE':
                logger.info('Displaying path')
                path.get_shapes(waypoints[0].get_lat_lon(), waypoints[1].get_lat_lon(),
                                message[1])
                path.set_visible(True)
                routes = PygPageLabel(20, 200, 160, 250, path.routes_to_text(),
                                      font=font, background_color=(255, 255, 255), visible=True)
                progress_bar.set_visible(False)
                progress_bar.set_text('0%')
                curr_prog = 0
                calculating = False
                settings_b[0].on_click(pygame.event.Event(pygame.MOUSEBUTTONUP))
                waypoints.append(0)
            elif message[0] == 'INFO':
                # setup route find progress bar
                total_prog = message[1]
                logger.info('Setup progress bar with total steps %d' % total_prog)
            elif message[0] == 'INC':
                # increase progress bar
                curr_prog += 1
                progress_bar.set_text(f'{curr_prog / total_prog * 100:.2f}%')
                logger.info('Incremented progress bar to progress %d / %d' %
                            (curr_prog, total_prog))
        except queue.Empty:
            pass

        event = pygame.event.poll()

        # End
        if event.type == pygame.QUIT or \
                (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            # Exit the event loop
            logger.info('QUITTING')
            pygame.quit()
            return

        if zoom_b[0].on_click(event):  # Zoom in
            if (new_zoom := clamp(zoom + 1)) != zoom:

                x = clamp(int(-((map_bound.width / 2 - x) / images[zoom].width
                                * images[new_zoom].width - map_bound.width / 2)),
                          -images[new_zoom].width + map_bound.width, 0)
                y = clamp(int(-((map_bound.height / 2 - y) / images[zoom].height
                                * images[new_zoom].height - map_bound.height / 2)),
                          -images[new_zoom].height + map_bound.height, 0)
                zoom = new_zoom
                tile = load_zoom_image(images, zoom)
            clicked = True
        elif zoom_b[1].on_click(event):  # Zoom out
            if (new_zoom := clamp(zoom - 1)) != zoom:
                x = clamp(int(-((map_bound.width / 2 - x) / images[zoom].width
                                * images[new_zoom].width - map_bound.width / 2)),
                          -images[new_zoom].width + map_bound.width, 0)
                y = clamp(int(-((map_bound.height / 2 - y) / images[zoom].height
                                * images[new_zoom].height - map_bound.height / 2)),
                          -images[new_zoom].height + map_bound.height, 0)
                zoom = new_zoom
                tile = load_zoom_image(images, zoom)
            clicked = True

        if not calculating:
            if settings_b[0].on_click(event) and len(waypoints) == 2:  # Get Routes
                time = int(settings_l[4].text) * 3600 + int(settings_l[5].text) * 60 + int(
                    settings_l[6].text)

                route_find_process = Process(target=pathfinding.find_route,
                                             args=(waypoints[0].get_lat_lon(),
                                                   waypoints[1].get_lat_lon(),
                                                   time,
                                                   DAY_TO_INT[settings_dd.selected],
                                                   result_queue))

                progress_bar.set_visible(True)
                calculating = True
                route_find_process.start()

            elif settings_b[1].on_click(event):  # Reset
                waypoints = []
                path.set_visible(False)
                routes.set_visible(False)
            elif settings_b[2].on_click(event):  # hour inc
                time_nums[0] = (time_nums[0] + 1) % 24
                settings_l[4].set_text(str(time_nums[0]))  # refresh time label
            elif settings_b[3].on_click(event):  # hour dec
                time_nums[0] = (time_nums[0] - 1) % 24
                settings_l[4].set_text(str(time_nums[0]))  # refresh time label
            elif settings_b[4].on_click(event):  # minute inc
                time_nums[1] = (time_nums[1] + 1) % 60
                settings_l[5].set_text(str(time_nums[1]))  # refresh time label
            elif settings_b[5].on_click(event):  # minute dec
                time_nums[1] = (time_nums[1] - 1) % 60
                settings_l[5].set_text(str(time_nums[1]))  # refresh time label
            elif settings_b[6].on_click(event):  # second inc
                time_nums[2] = (time_nums[2] + 1) % 60
                settings_l[6].set_text(str(time_nums[2]))  # refresh time label
            elif settings_b[7].on_click(event):  # second dec
                time_nums[2] = (time_nums[2] - 1) % 60
                settings_l[6].set_text(str(time_nums[2]))  # refresh time label
            elif routes.on_click(event):
                routes.on_select(event)

            settings_dd.on_select(event)  # Day selection

        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Scroll and point logic
        if event.type == pygame.MOUSEBUTTONDOWN \
                and pygame.mouse.get_pressed(3) == (True, False, False):

            if map_bound.contains(mouse_x, mouse_y) and not clicked:
                x_diff, y_diff = x - (mouse_x - map_bound.x), y - (mouse_y - map_bound.y)
                down = True

        if event.type == pygame.MOUSEBUTTONUP:
            # Clicked point
            if not (scroll or clicked) and map_bound.contains(mouse_x, mouse_y) and down:
                mouse_x -= map_bound.x
                mouse_y -= map_bound.y
                # get lat/lon
                user_lat, user_lon = images[zoom].coord_to_lat_lon(mouse_x, mouse_y, x, y)
                check_points_clicked(user_lat, user_lon, waypoints)
            else:
                scroll = False
                clicked = False
            down = False

        if event.type == pygame.MOUSEMOTION:
            # scroll if mouse down
            if down:
                mouse_x -= map_bound.x
                mouse_y -= map_bound.y
                scroll = True
                new_x, new_y = continue_scroll(images[zoom], map_bound.width, map_bound.height,
                                               x, y, mouse_x, mouse_y, x_diff, y_diff)
                if new_x == x:
                    x_diff = x - mouse_x
                else:
                    x = new_x
                if new_y == y:
                    y_diff = y - mouse_y
                else:
                    y = new_y


if __name__ == "__main__":
    import python_ta.contracts
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()

    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['pygame', 'pathfinding', 'image', 'pygui', 'waypoint', 'path', 'graph',
                          'logging', 'queue', 'multiprocessing'],
        'allowed-io': [],
        'max-line-length': 100,
        'max-nested-blocks': 4,
        'disable': ['E1136', 'R0913', 'R0914', 'R0912', 'R0914', 'R0915', 'E1101']})
