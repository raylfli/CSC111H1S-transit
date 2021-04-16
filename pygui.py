"""Pygame UI classes"""
from typing import Union, Optional
import pygame


class Rect:
    """It's a rectangle. Please refer to kindergarten for detailed explanation.
    (x, y) is the coordinate of the top left corner.
    """
    x: int
    y: int
    width: int
    height: int

    def __init__(self, x: int, y: int, width: int, height: int):
        self.x, self.y, self.width, self.height = x, y, width, height

    def contains(self, x: int, y: int) -> bool:
        """Returns whether this rectangle contains the point (x, y).
        Points that are on the edges are not considered inside the rectangle.
        """
        return self.x < x < self.x + self.width and self.y < y < self.y + self.height


class Button:
    """A clickable button."""
    _rect: Rect

    def on_click(self, event: pygame.event.Event) -> bool:
        """Return true if the event clicked this button."""
        raise NotImplementedError


class PygButton(Button):
    """A clickable button."""

    _rect: Rect
    _bg_color: pygame.Color
    _image: Optional[pygame.Surface]
    _image_mode: int
    _text: Optional[str]
    _font: Optional[pygame.font.Font]
    _txt_col: Optional[tuple[int, int, int]]
    _txt_surface: Optional[pygame.Surface]
    _visible: bool

    def __init__(self, x, y, width, height, text: str = None,
                 font: tuple[str, int] = (pygame.font.get_default_font(), 20),
                 txt_col: tuple[int, int, int] = (0, 0, 0),
                 visible: bool = True, color: tuple[int, int, int] = (255, 255, 255),
                 image: str = None, image_mode: int = 0):
        """Initialize a button. Customizable background colour, image.
        Image modes:
            - 0 if you wish for the image to be resized to the button's size (default)
            - 1 if you wish to display the image at native resolution. The image will be anchored
                at its top left corner, and any overflow will be clipped.
        """
        self._rect = Rect(x, y, width, height)
        self._visible = visible
        self._image_mode = image_mode
        self._bg_color = pygame.Color(color)
        self.set_text(text, font, txt_col)

        if image is not None:
            self._image = pygame.image.load(image)
            if image_mode == 0:
                self._image = pygame.transform.scale(self._image,
                                                     (self._rect.width, self._rect.height))
        else:
            self._image = None

    def set_text(self, text: str = None,
                 font: tuple[str, int] = (pygame.font.get_default_font(), 20),
                 txt_col: tuple[int, int, int] = (0, 0, 0)) -> None:
        """..."""
        if text is not None:
            self._text = text
            self._txt_col = txt_col
            self._font = pygame.font.SysFont(font[0], font[1])
            self._txt_surface = self._font.render(text, True, txt_col)
        else:
            self._text = None
            self._font = None
            self._txt_col = None
            self._txt_surface = None

    def draw(self, surface: Union[pygame.Surface, pygame.SurfaceType]):
        """Draw this button."""
        if self._visible:
            pygame.draw.rect(surface, self._bg_color,
                             (self._rect.x, self._rect.y, self._rect.width, self._rect.height))

            if self._text is not None:
                height = self._txt_surface.get_size()[1]
                surface.blit(self._txt_surface, (self._rect.x,
                                                 max(self._rect.y,
                                                     self._rect.y + self._rect.height - height)),
                             pygame.Rect(0, max(0, height - self._rect.height),
                                         self._rect.width, self._rect.height))

            if self._image is not None:
                if self._image_mode == 1:
                    surface.blit(self._image, (self._rect.x, self._rect.y),
                                 pygame.Rect(0, 0, self._rect.width, self._rect.height))

    def on_click(self, event: pygame.event.Event) -> bool:
        """Return true if the event clicked this button."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            return self._rect.contains(x, y)
        return False

    def set_visible(self, value: bool) -> None:
        """Set button as visible."""
        self._visible = value

    def get_text(self) -> str:
        """Return button text."""
        return self._text


class PygDropdown(Button):
    """A dropdown menu."""
    selected: str

    _rect: Rect
    _stack_rect: Rect
    _active: bool

    _font: pygame.font.Font

    _option_surfs: dict[str, pygame.Surface]
    _option_nums: dict[int, str]

    _field_col: pygame.Color
    _dropdown_col: pygame.Color

    def __init__(self, x: int, y: int, width: int, height: int,
                 options: list[str],
                 font: tuple[str, int] = (pygame.font.get_default_font(), 20),
                 txt_col: tuple[int, int, int] = (0, 0, 0),
                 field_col: tuple[int, int, int] = (255, 255, 255),
                 dropdown_col: tuple[int, int, int] = (255, 255, 255)):
        """Initialize this menu. The options in this menu are given as a list of strings. The
        dropdown menu defaults to the first item in the list.
        Fonts are given as a tuple of font name and size.
        """
        self._rect = Rect(x, y, width, height)
        self._stack_rect = Rect(x, y, width, height * len(options))
        self._active = False
        self._font = pygame.font.SysFont(font[0], font[1])
        self._field_col = pygame.Color(field_col)
        self._dropdown_col = pygame.Color(dropdown_col)

        self.selected = options[0]

        self._option_surfs = {}
        self._option_nums = {}
        option_num = 1
        for option in options:
            self._option_surfs[option] = self._font.render(option, True, txt_col)
            self._option_nums[option_num] = option

    def draw(self, surface: Union[pygame.Surface, pygame.SurfaceType]):
        """Draw this menu."""
        if self._active:
            # draw field
            pygame.draw.rect(surface, self._field_col,
                             (self._rect.x, self._rect.y, self._rect.width, self._rect.height))
            height = self._option_surfs[self.selected].get_size()[1]
            surface.blit(self._option_surfs[self.selected], (self._rect.x,
                                                             max(self._rect.y, self._rect.y +
                                                                 self._rect.height - height)),
                         pygame.Rect(0, max(0, height - self._rect.height),
                                     self._rect.width, self._rect.height))

            # draw dropdowns
            for option in self._option_nums:
                if self._option_nums[option] != self.selected:
                    self._draw_option(self._option_nums[option], option, surface)
        else:
            pygame.draw.rect(surface, self._field_col,
                             (self._rect.x, self._rect.y, self._rect.width, self._rect.height))
            height = self._option_surfs[self.selected].get_size()[1]
            surface.blit(self._option_surfs[self.selected], (self._rect.x,
                                                             max(self._rect.y, self._rect.y +
                                                                 self._rect.height - height)),
                         pygame.Rect(0, max(0, height - self._rect.height),
                                     self._rect.width, self._rect.height))

    def _draw_option(self, option: str, option_num: int,
                     surface: Union[pygame.Surface, pygame.SurfaceType]):
        """Draw a single option."""
        y = self._rect.y + self._rect.height * option_num
        pygame.draw.rect(surface, self._dropdown_col,
                         (self._rect.x, y, self._rect.width, self._rect.height))
        height = self._option_surfs[option].get_size()[1]
        surface.blit(self._option_surfs[option], (self._rect.x,
                                                  max(y, y + self._rect.height - height)),
                     pygame.Rect(0, max(0, height - self._rect.height),
                                 self._rect.width, self._rect.height))

    def on_click(self, event: pygame.event.Event) -> bool:
        """Return true if the event clicked this button."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            if self._active:
                return self._rect.contains(x, y) or self._stack_rect.contains(x, y)
            else:
                return self._rect.contains(x, y)
        return False

    def on_select(self, event: pygame.event.Event):
        """On select, either activates or deactivates this dropdown. The activated dropdown
        allows the selection of a new option."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            if not self._active and self._rect.contains(x, y):
                option_num = 1
                for option in self._option_surfs:
                    if option != self.selected:
                        self._option_nums[option_num] = option
                        option_num += 1
                self._active = True
            else:  # is active
                if self._stack_rect.contains(x, y):
                    num = (y - self._rect.y) // self._rect.height
                    if num > 0:
                        self.selected = self._option_nums[num]
                    self._active = False
                else:
                    # print('deactivate')
                    self._active = False


class PygLabel:
    """Text label. Does NOT support multiline labels.
    """
    _rect: Rect
    _font: pygame.font.Font
    _text: str
    _text_col: tuple[int, int, int]
    _bg_col: Optional[pygame.Color]
    _text_surface: Optional[pygame.Surface]

    def __init__(self, x: int, y: int, width: int, height: int,
                 text: str,
                 font: tuple[str, int] = (pygame.font.get_default_font(), 20),
                 text_color: tuple[int, int, int] = (0, 0, 0),
                 background_color: Optional[tuple[int, int, int]] = None) -> None:
        """Initialize PygLabel.
        """
        self._rect = Rect(x, y, width, height)
        self._font = pygame.font.SysFont(font[0], font[1])
        self.set_text(text, font, text_color)

        if background_color is not None:
            self._bg_col = pygame.Color(background_color)
        else:
            self._bg_col = None

    def draw(self, surface: Union[pygame.Surface, pygame.SurfaceType]) -> None:
        """Draw this label
        """
        # draw background
        if self._bg_col is not None:
            pygame.draw.rect(surface, self._bg_col,
                             pygame.Rect(self._rect.x,
                                         self._rect.y,
                                         self._rect.width,
                                         self._rect.height))

        # draw text
        width, height = self._text_surface.get_size()
        surface.blit(self._text_surface,
                     pygame.Rect(self._rect.x + self._rect.width / 2 - width / 2,
                                 self._rect.y + self._rect.height / 2 - height / 2,
                                 self._rect.width,
                                 self._rect.height))

    def set_text(self, text: str = None,
                 font: tuple[str, int] = (pygame.font.get_default_font(), 20),
                 text_col: tuple[int, int, int] = (0, 0, 0)) -> None:
        """Set this label's text."""
        self._text = text
        self._text_col = text_col
        self._font = pygame.font.SysFont(font[0], font[1])
        self._text_surface = self._font.render(text, True, text_col)
