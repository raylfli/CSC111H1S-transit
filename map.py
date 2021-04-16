"""

To-do:
    - Display sidebar for path info
    - Get larger zoom images

"""
import pygame
import pathfinding
from image import Image, load_images
from pygui import PygButton, PygDropdown, PygLabel, Rect
from waypoint import Waypoint
from path import Path
from typing import Union

from graph import Graph

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
DAY_TO_INT = {'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4,
              'Friday': 5, 'Saturday': 6, 'Sunday': 7}


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


def draw_zoom_in(screen: pygame.Surface, x: int, y: int, width: int, height: int) -> None:
    """ ...

    Precondition:
        - button[0].height > button[1].height

    """
    pygame.draw.line(screen, pygame.Color('black'), # horizontal line
                     (x + width / 10, y + height / 2), (x + width - width / 10, y + height / 2), 7)
    pygame.draw.line(screen, pygame.Color('black'), # vertical line
                     (x + width / 2, y + height / 10), (x + width / 2, y + height - height / 10), 7)


def draw_zoom_out(screen: pygame.Surface, x: int, y: int, width: int, height: int) -> None:
    """Draw function for zoom out"""
    pygame.draw.line(screen, pygame.Color('black'), # horizontal line
                     (x + width / 10, y + height / 2), (x + width - width / 10, y + height / 2), 7)


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
    # draw_zoom(screen, buttons[ZOOM], width, height)
    draw_settings(screen, buttons[SETTINGS])
    draw_check_path(screen, buttons[GET_PATH])


def draw_waypoints(screen: pygame.Surface, image: Image, waypoints: list,
                   orig_x: int, orig_y: int) -> None:
    """dkm this isn't acc drawing waypoints"""
    for waypoint in waypoints:
        x, y = image.lat_lon_to_coord(waypoint.lat, waypoint.lon, orig_x=orig_x, orig_y=orig_y)
        pygame.draw.circle(screen, pygame.Color('black'), (x, y), 4)


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
                         waypoints: list) -> None:
    """Mutate points to reflect if the point is the starting or ending destination"""
    # if waypoints['pts'] == []:
    #     waypoints['pts'].append(Waypoint(lat, lon, chosen_start=True))
    if len(waypoints) <= 1:
        # button.set_visible(True)
        waypoints.append(Waypoint(lat, lon, chosen_end=True))


def time_to_sec(time: list[int]) -> int:
    """Return the number of seconds after midnight from a given time.

    Preconditions:
        - len(time) == 3
    """
    hour, minute, second = time[0], time[1], time[2]
    return hour * 3600 + minute * 60 + second


def reset_points(button: PygButton, day_dropdown: PygDropdown, hr_dropdown: PygDropdown,
                 min_dropdown: PygDropdown, sec_dropdown: PygDropdown) -> dict:
    """..."""
    # button.set_visible(False)
    # button.set_text(text=PATH_TEXT)
    time = [int(hr_dropdown.selected), int(min_dropdown.selected), int(sec_dropdown.selected)]
    time_in_sec = time_to_sec(time)
    return {'day': DAY_TO_INT[day_dropdown.selected], 'time': time_in_sec, 'pts': []}


def draw_inc(screen: pygame.Surface, x: int, y: int, width: int, height: int) -> None:
    """Draw increment arrow"""
    pygame.draw.line(screen, pygame.Color('black'), (x, y + height * 3 / 4), (x + width / 2, y), 2)
    pygame.draw.line(screen, pygame.Color('black'), (x + width / 2, y), (x + width, y + height * 3 / 4), 2)


def draw_dec(screen: pygame.Surface, x: int, y: int, width: int, height: int) -> None:
    """Draw decrement arrow"""
    pygame.draw.line(screen, pygame.Color('black'), (x, y + height / 4), (x + width / 2, y + height), 2)
    pygame.draw.line(screen, pygame.Color('black'), (x + width / 2, y + height),
                     (x + width, y + height / 4), 2)


def run_map(graph: Graph, filename: str = "data/image_data/images_data.csv",
            width: int = 1000, height: int = 600,
            button_width: int = 50, button_height: int = 50) -> None:
    """Run main map.

    Preconditions:
        - 150 <= width <= 1000
        - 150 <= height <= 800
        - 43.52434 <= lat <= 43.96036
        - -79.81884 <= lon <= -79.06096
    """
    screen = initialize_screen(ALLOWED, width, height)

    # map screen
    map_bound = Rect(200, 0, 800, 600)
    map_screen = pygame.Surface((map_bound.width, map_bound.height))

    x, y = 0, 0
    down, scroll = False, False
    reset, clicked = False, False
    x_diff, y_diff = 0, 0
    zoom = 0

    font = ("Calibri", 20)

    waypoints = []

    zoom_b = [PygButton(x=map_bound.width - PADDING - 30,
                        y=map_bound.height - PADDING - 2 * 30 - 10,
                        width=30, height=30,
                        x_adjust=-200, draw_func=lambda a, b, c, d, e: draw_zoom_in(a, b, c, d, e)),
              PygButton(x=map_bound.width - PADDING - 30,
                        y=map_bound.height - PADDING - 30,
                        width=30, height=30,
                        x_adjust=-200, draw_func=lambda a, b, c, d, e: draw_zoom_out(a, b, c, d, e))]

    time_nums = [0, 0, 0]

    settings_l = [PygLabel(20, 50, 50, 20, "Day:", font, background_color=(255, 255, 255)),
                  PygLabel(20, 100, 70, 20, "Hours:", font, background_color=(255, 255, 255)),
                  PygLabel(20, 125, 70, 20, "Minute:", font, background_color=(255, 255, 255)),
                  PygLabel(20, 150, 70, 20, "Second:", font, background_color=(255, 255, 255)),
                  PygLabel(100, 100, 20, 20, str(time_nums[0]), font, background_color=(255, 255, 255)),
                  PygLabel(100, 125, 20, 20, str(time_nums[1]), font, background_color=(255, 255, 255)),
                  PygLabel(100, 150, 20, 20, str(time_nums[2]), font, background_color=(255, 255, 255))]

    settings_b = [PygButton(25, 500, 150, 20, "Get Route", font, txt_align=1),
                  PygButton(25, 540, 150, 20, "Reset", font, txt_align=1),
                  PygButton(125, 100, 9, 9, draw_func=lambda a, b, c, d, e: draw_inc(a, b, c, d, e)), # hour inc
                  PygButton(125, 111, 9, 9,
                            draw_func=lambda a, b, c, d, e: draw_dec(a, b, c, d, e)),  # hour dec
                  PygButton(125, 125, 9, 9,
                            draw_func=lambda a, b, c, d, e: draw_inc(a, b, c, d, e)),  # hour inc
                  PygButton(125, 136, 9, 9,
                            draw_func=lambda a, b, c, d, e: draw_dec(a, b, c, d, e)),  # hour inc
                  PygButton(125, 150, 9, 9,
                            draw_func=lambda a, b, c, d, e: draw_inc(a, b, c, d, e)),  # hour inc
                  PygButton(125, 161, 9, 9,
                            draw_func=lambda a, b, c, d, e: draw_dec(a, b, c, d, e))]  # hour inc

    settings_dd = [PygDropdown(80, 50, 100, 20, DAYS_TEXT, font)]

    # buttons = {ZOOM: [PygButton(x=map_bound.width - PADDING - button_width,
    #                             y=map_bound.height - PADDING - 2 * button_height,
    #                             width=button_width, height=button_height,
    #                             x_adjust=-200),
    #                   PygButton(x=map_bound.width - PADDING - button_width,
    #                             y=map_bound.height - PADDING - button_height,
    #                             width=button_width, height=button_height,
    #                             x_adjust=-200)],
    #            SETTINGS: [PygDropdown(x=PADDING, y=PADDING,
    #                                   width=PADDING * 2, height=PADDING // 2,
    #                                   options=DAYS_TEXT),
    #                       PygDropdown(x=PADDING * 4, y=PADDING,
    #                                   width=PADDING, height=PADDING // 2,
    #                                   options=[str(x) for x in range(0, 23)]),
    #                       PygDropdown(x=PADDING * 5, y=PADDING,
    #                                   width=PADDING, height=PADDING // 2,
    #                                   options=[str(x) for x in range(0, 59)]),
    #                       PygDropdown(x=PADDING * 6, y=PADDING,
    #                                   width=PADDING, height=PADDING // 2,
    #                                   options=[str(x) for x in range(0, 59)])],
    #            GET_PATH: [PygButton(x=PADDING, y=height - PADDING - button_height,
    #                                 width=button_width, height=button_height,
    #                                 text=PATH_TEXT, visible=False)]
    #            # 'label': [PygLabel(x=PADDING * 4, y=PADDING,
    #            #                    width=PADDING, height=PADDING // 2,
    #            #                    text='00')]
    #            }

    # load image
    images = load_images(filename)
    tile = load_zoom_image(images, zoom)

    # create path
    path = Path()

    # label = PygLabel(200, 200, 100, 50, 'Lorem Ipsum', background_color=(255, 255, 255))

    # Start the event loop
    while True:
        # Draw map area
        draw_map(map_screen, tile, x, y)
        draw_waypoints(map_screen, images[zoom], waypoints, x, y)
        draw_path(map_screen, images[zoom], path, x, y)
        # draw_zoom(map_screen, zoom_b, map_bound.width, map_bound.height)
        for button in zoom_b:
            button.draw(map_screen)

        # blit map onto screen
        screen.blit(map_screen, (map_bound.x, map_bound.y))

        # Draw settings bar area
        pygame.draw.rect(screen, (0, 100, 0), (0, 0, 200, 600))
        for button in settings_b:
            button.draw(screen)

        for label in settings_l:
            label.draw(screen)

        for dropdown in settings_dd:
            dropdown.draw(screen)
        # draw_buttons(screen, buttons, map_bound.width, map_bound.height)

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

        if zoom_b[0].on_click(event):  # Zoom in
            if (new_zoom := clamp(zoom + 1)) != zoom:
                zoom = new_zoom
                x, y = 0, 0
                tile = load_zoom_image(images, zoom)
            clicked = True
        elif zoom_b[1].on_click(event):  # Zoom out
            if (new_zoom := clamp(zoom - 1)) != zoom:
                zoom = new_zoom
                x, y = 0, 0
                tile = load_zoom_image(images, zoom)
            clicked = True
        elif settings_b[0].on_click(event) and len(waypoints) == 2:
            # print(f'Waypoints num: {len(waypoints["pts"])}')
            time = int(settings_l[4].text) * 3600 + int(settings_l[5].text) * 60 + int(
                settings_l[6].text)
            path.get_shapes(waypoints[0].get_lat_lon(),
                            waypoints[1].get_lat_lon(),
                            pathfinding.find_route(waypoints[0].get_lat_lon(),
                                                   waypoints[1].get_lat_lon(),
                                                   time,
                                                   DAY_TO_INT[settings_dd[0].selected]))
            path.set_visible(True)
        elif settings_b[1].on_click(event):
            waypoints = []
            # print(f'Waypoints num: {len(waypoints["pts"])}')
        elif settings_b[2].on_click(event):  # hour inc
            time_nums[0] = clamp(time_nums[0] + 1, 0, 23)
            settings_l[4].set_text(str(time_nums[0]))  # refresh time label
        elif settings_b[3].on_click(event):  # hour dec
            time_nums[0] = clamp(time_nums[0] - 1, 0, 23)
            settings_l[4].set_text(str(time_nums[0]))  # refresh time label
        elif settings_b[4].on_click(event):  # minute inc
            time_nums[1] = clamp(time_nums[1] + 1, 0, 59)
            settings_l[5].set_text(str(time_nums[1]))  # refresh time label
        elif settings_b[5].on_click(event):  # minute dec
            time_nums[1] = clamp(time_nums[1] - 1, 0, 59)
            settings_l[5].set_text(str(time_nums[1]))  # refresh time label
        elif settings_b[6].on_click(event):  # second inc
            time_nums[2] = clamp(time_nums[2] + 1, 0, 59)
            settings_l[6].set_text(str(time_nums[2]))  # refresh time label
        elif settings_b[7].on_click(event):  # second dec
            time_nums[2] = clamp(time_nums[2] - 1, 0, 59)
            settings_l[6].set_text(str(time_nums[2]))  # refresh time label

        for dropdown in settings_dd:
            dropdown.on_select(event)

        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Scroll and point logic
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            if map_bound.contains(mouse_x, mouse_y) and not clicked:
                # print('In Map')
                x_diff, y_diff = scroll_diff(x, mouse_x - map_bound.x), scroll_diff(y, mouse_y - map_bound.y)
                down = True

        if event.type == pygame.MOUSEBUTTONUP:
            down = False

            # Clicked point
            if not (scroll or clicked) and map_bound.contains(mouse_x, mouse_y):
                mouse_x -= map_bound.x
                mouse_y -= map_bound.y
                # get lat/lon
                user_lat, user_lon = images[zoom].coord_to_lat_lon(mouse_x, mouse_y, x, y)
                check_points_clicked(user_lat, user_lon, waypoints)
            else:
                scroll = False
                clicked = False

        if event.type == pygame.MOUSEMOTION:
            # scroll if mouse down
            if down:
                scroll = True
                new_x, new_y = continue_scroll(images[zoom], map_bound.width, map_bound.height, x, y,
                                               mouse_x, mouse_y, x_diff, y_diff)
                if new_x == x:
                    x_diff = scroll_diff(x, mouse_x)
                else:
                    x = new_x
                if new_y == y:
                    y_diff = scroll_diff(y, mouse_y)
                else:
                    y = new_y

        # if event.type == pygame.MOUSEBUTTONDOWN:
        #     # Get location data
        #     mouse_x, mouse_y = pygame.mouse.get_pos()
        #
        #     for i in range(0, len(buttons[SETTINGS])):
        #         if buttons[SETTINGS][i].on_click(event):
        #             buttons[SETTINGS][i].on_select(event)
        #             if i == 0:
        #                 waypoints['day'] = DAY_TO_INT[buttons[SETTINGS][i].selected]
        #             else:
        #                 time = []
        #                 for j in range(1, len(buttons[SETTINGS])):
        #                     time.append(int(buttons[SETTINGS][j].selected))
        #                 waypoints['time'] = time_to_sec(time)
        #             clicked = True
        #
        #     # Zoom in
        #     if buttons[ZOOM][0].on_click(event):
        #         if clamp(zoom + 1) != zoom:
        #             zoom = clamp(zoom + 1)
        #             x, y = 0, 0
        #             tile = load_zoom_image(images, zoom)
        #         clicked = True
        #
        #     # Zoom out
        #     elif buttons[ZOOM][1].on_click(event):
        #         if clamp(zoom - 1) != zoom:
        #             zoom = clamp(zoom - 1)
        #             x, y = 0, 0
        #             tile = load_zoom_image(images, zoom)
        #         clicked = True
        #
        #     elif buttons[GET_PATH][0].on_click(event):
        #         if buttons[GET_PATH][0].get_text() == PATH_TEXT:
        #             # print('points: ' + str(waypoints['pts'][0].get_lat_lon()) +
        #             #       ', ' + str(waypoints['pts'][1].get_lat_lon()) +
        #             #       '; time: ' + str(waypoints['time']) + '; day: ' + str(waypoints['day']))
        #             path.get_shapes(waypoints['pts'][0].get_lat_lon(),
        #                             waypoints['pts'][1].get_lat_lon(),
        #                             pathfinding.find_route(waypoints['pts'][0].get_lat_lon(),
        #                                                    waypoints['pts'][1].get_lat_lon(),
        #                                                    waypoints['time'],
        #                                                    waypoints['day'], main.load_graph()))
        #             path.set_visible(True)
        #             buttons[GET_PATH][0].set_text(text=RESET_PATH_TEXT)
        #         else:
        #             reset = True
        #             path.set_visible(False)
        #         clicked = True

            # Start scroll
            # else:
            #     x_diff, y_diff = scroll_diff(x, mouse_x), scroll_diff(y, mouse_y)
            #     down = True

        # if event.type == pygame.MOUSEBUTTONUP:
        #     down = False
        #
        #     # Clicked point
        #     if not (scroll or clicked):
        #         mouse_x, mouse_y = pygame.mouse.get_pos()
        #
        #         # get lat/lon
        #         user_lat, user_lon = images[zoom].coord_to_lat_lon(mouse_x, mouse_y, x, y)
        #         check_points_clicked(user_lat, user_lon, waypoints, buttons[GET_PATH][0])
        #     else:
        #         scroll = False
        #         clicked = False
        #
        #     if reset:
        #         waypoints = reset_points(buttons[GET_PATH][0], buttons[SETTINGS][0],
        #                                  buttons[SETTINGS][1], buttons[SETTINGS][2],
        #                                  buttons[SETTINGS][3])
        #         reset = False
        #
        # if event.type == pygame.MOUSEMOTION:
        #     # scroll if mouse down
        #     if down:
        #         scroll = True
        #         mouse_x, mouse_y = pygame.mouse.get_pos()
        #         new_x, new_y = continue_scroll(images[zoom], width, height, x, y,
        #                                        mouse_x, mouse_y, x_diff, y_diff)
        #         if new_x == x:
        #             x_diff = scroll_diff(x, mouse_x)
        #         else:
        #             x = new_x
        #         if new_y == y:
        #             y_diff = scroll_diff(y, mouse_y)
        #         else:
        #             y = new_y


# if __name__ == "__main__":
#     # pyta
#
#     # run map
#     run_map()
