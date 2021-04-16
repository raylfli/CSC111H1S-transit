"""Pygame UI classes"""
from typing import Union, Optional, Callable
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


class PygButton:
    """A clickable button."""

    _rect: Rect
    _bg_color: pygame.Color
    _image: Optional[pygame.Surface]
    _image_mode: int
    _text: Optional[str]
    _font: Optional[pygame.font.Font]
    _txt_col: Optional[tuple[int, int, int]]
    _txt_align: int
    _txt_surface: Optional[pygame.Surface]
    _visible: bool
    _adjust: tuple[int, int]
    _draw_func: Callable

    def __init__(self, x, y, width, height, text: str = None,
                 font: tuple[str, int] = (pygame.font.get_default_font(), 20),
                 txt_col: tuple[int, int, int] = (0, 0, 0),
                 txt_align: int = 0,
                 visible: bool = True, color: tuple[int, int, int] = (255, 255, 255),
                 image: str = None, image_mode: int = 0,
                 x_adjust: int = 0, y_adjust: int = 0,
                 draw_func: Callable = None):
        """Initialize a button. Customizable background colour, image.
        Image modes:
            - 0 if you wish for the image to be resized to the button's size (default)
            - 1 if you wish to display the image at native resolution. The image will be anchored
                at its top left corner, and any overflow will be clipped.

        Text align:
            - 0 for left align, bottom align
            - 1 for center align, middle align
            - 2 for right align, bottom align # TODO
        """
        self._rect = Rect(x, y, width, height)
        self._visible = visible
        self._image_mode = image_mode
        self._bg_color = pygame.Color(color)
        self._set_text(text, font, txt_col, txt_align)
        self._adjust = (x_adjust, y_adjust)
        self._draw_func = draw_func

        if image is not None:
            self._image = pygame.image.load(image)
            if image_mode == 0:
                self._image = pygame.transform.scale(self._image,
                                                     (self._rect.width, self._rect.height))
        else:
            self._image = None

    def _set_text(self, text: str = None,
                  font: tuple[str, int] = (pygame.font.get_default_font(), 20),
                  txt_col: tuple[int, int, int] = (0, 0, 0), txt_align: int = 0) -> None:
        """..."""
        if text is not None:
            self._text = text
            self._txt_col = txt_col
            self._font = pygame.font.SysFont(font[0], font[1])
            self._txt_surface = self._font.render(text, True, txt_col)
            self._txt_align = txt_align
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
                width, height = self._txt_surface.get_size()
                if self._txt_align == 0:
                    surface.blit(self._txt_surface, (self._rect.x + self._rect.width / 15,
                                                     max(self._rect.y,
                                                         self._rect.y + self._rect.height - height)),
                                 pygame.Rect(0, max(0, height - self._rect.height),
                                             self._rect.width, self._rect.height))
                elif self._txt_align == 1:
                    surface.blit(self._txt_surface, (max(self._rect.x, (self._rect.width - width) / 2 + self._rect.x),
                                                     max(self._rect.y,
                                                         self._rect.y + (self._rect.height - height) / 2)),
                                 pygame.Rect(max(0, (width - self._rect.width) / 2), max(0, (height - self._rect.height) / 2),
                                             self._rect.width, self._rect.height))
                elif self._txt_align == 2:
                    surface.blit(self._txt_surface, (max(self._rect.x, self._rect.x + self._rect.width - width) - self._rect.width / 15,
                                                     max(self._rect.y,
                                                         self._rect.y + self._rect.height - height)),
                                 pygame.Rect(max(0, width - self._rect.width), max(0, height - self._rect.height),
                                             self._rect.width, self._rect.height))

            if self._image is not None:
                if self._image_mode == 1:
                    surface.blit(self._image, (self._rect.x, self._rect.y),
                                 pygame.Rect(0, 0, self._rect.width, self._rect.height))

            if self._draw_func is not None:
                self._draw_func(surface, self._rect.x, self._rect.y, self._rect.width, self._rect.height)

    def on_click(self, event: pygame.event.Event) -> bool:
        """Return true if the event clicked this button."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            return self._rect.contains(x + self._adjust[0], y + self._adjust[1])
        return False

    def set_visible(self, value: bool) -> None:
        """Set button as visible."""
        self._visible = value

    def get_text(self) -> str:
        """Return button text."""
        return self._text


class PygDropdown:
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
        # draw field
        pygame.draw.rect(surface, self._field_col,
                         (self._rect.x, self._rect.y, self._rect.width, self._rect.height))
        height = self._option_surfs[self.selected].get_size()[1]
        surface.blit(self._option_surfs[self.selected], (self._rect.x + self._rect.width / 15,
                                                         max(self._rect.y, self._rect.y +
                                                             self._rect.height - height)),
                     pygame.Rect(0, max(0, height - self._rect.height),
                                 self._rect.width, self._rect.height))

        if self._active:
            # draw dropdowns
            for option in self._option_nums:
                if self._option_nums[option] != self.selected:
                    self._draw_option(self._option_nums[option], option, surface)

    def _draw_option(self, option: str, option_num: int,
                     surface: Union[pygame.Surface, pygame.SurfaceType]):
        """Draw a single option."""
        y = self._rect.y + self._rect.height * option_num
        pygame.draw.rect(surface, self._dropdown_col,
                         (self._rect.x, y, self._rect.width, self._rect.height))
        height = self._option_surfs[option].get_size()[1]
        surface.blit(self._option_surfs[option], (self._rect.x + self._rect.width / 15,
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
            elif self._active:  # is active
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

    Text align:
            - 0 for left align, bottom align
            - 1 for center align, middle align
            - 2 for right align, bottom align # TODO
            - 3 for left align, top align
    """
    _rect: Rect
    _font: pygame.font.Font
    text: str
    _text_col: tuple[int, int, int]
    _bg_col: Optional[pygame.Color]
    _text_surface: Optional[pygame.Surface]
    _txt_align: int

    def __init__(self, x: int, y: int, width: int, height: int,
                 text: str,
                 font: tuple[str, int] = (pygame.font.get_default_font(), 20),
                 text_color: tuple[int, int, int] = (0, 0, 0),
                 background_color: Optional[tuple[int, int, int]] = None,
                 txt_align: int = 0) -> None:
        """Initialize PygLabel.
        """
        self._rect = Rect(x, y, width, height)
        self._font = pygame.font.SysFont(font[0], font[1])
        self._set_text(text, font, text_color, txt_align)

        if background_color is not None:
            self._bg_col = pygame.Color(background_color)
        else:
            self._bg_col = None

    def draw(self, surface: Union[pygame.Surface, pygame.SurfaceType], padding: int = 5) -> None:
        """Draw this label.
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
        if self._txt_align == 0:
            surface.blit(self._text_surface, (self._rect.x + self._rect.width / 15,
                                             max(self._rect.y,
                                                 self._rect.y + self._rect.height - height)),
                         pygame.Rect(0, max(0, height - self._rect.height),
                                     self._rect.width, self._rect.height))
        elif self._txt_align == 1:
            surface.blit(self._text_surface,
                         (max(self._rect.x, (self._rect.width - width) / 2 + self._rect.x),
                          max(self._rect.y,
                              self._rect.y + (self._rect.height - height) / 2)),
                         pygame.Rect(max(0, (width - self._rect.width) / 2),
                                     max(0, (height - self._rect.height) / 2),
                                     self._rect.width, self._rect.height))
        elif self._txt_align == 2:
            surface.blit(self._text_surface, (
                max(self._rect.x, self._rect.x + self._rect.width - width) - self._rect.width / 15,
                max(self._rect.y,
                    self._rect.y + self._rect.height - height)),
                         pygame.Rect(max(0, width - self._rect.width),
                                     max(0, height - self._rect.height),
                                     self._rect.width, self._rect.height))
        elif self._txt_align == 3:
            surface.blit(self._text_surface, (self._rect.x + padding,
                                              self._rect.y + padding))

    def _set_text(self, text: str = None,
                  font: tuple[str, int] = (pygame.font.get_default_font(), 20),
                  text_col: tuple[int, int, int] = (0, 0, 0), txt_align: int = 0) -> None:
        """Set this label's text."""
        self.text = text
        self._text_col = text_col
        self._font = pygame.font.SysFont(font[0], font[1])
        self._text_surface = self._font.render(text, True, text_col)
        self._txt_align = txt_align

    def set_text(self, text: str = None):
        """Public set text"""
        if text is not None:
            self.text = text
            self._text_surface = self._font.render(text, True, self._text_col)

    def get_dimensions(self) -> tuple[int, int]:
        """Return the width and height of the PygLabel."""
        return self._text_surface.get_size()


class PygMultiLabel:
    """Multiline pygame label."""
    _rect: Rect
    _visible: bool
    labels: list[PygLabel]
    shown_text: list[str]
    not_shown_text: list[str]
    cont: bool

    def __init__(self, x: int, y: int, width: int, height: int,
                 text, font: tuple[str, int] = (pygame.font.get_default_font(), 20),
                 text_color: tuple[int, int, int] = (0, 0, 0),
                 background_color: Optional[tuple[int, int, int]] = None,
                 txt_align: int = 3, visible: bool = False) -> None:
        """Initialize PygMultiLabel."""
        self._rect = Rect(x, y, width, height)
        self._visible = visible
        self._set_text(text, font, text_color, background_color, txt_align)

    def draw(self, surface: Union[pygame.Surface, pygame.SurfaceType]) -> None:
        """Draw labels in pygame."""
        if self._visible:
            for label in self.labels:
                label.draw(surface)

    def _set_text(self, text: list[str] = None,
                  font: tuple[str, int] = (pygame.font.get_default_font(), 20),
                  background_color: Optional[tuple[int, int, int]] = None,
                  text_col: tuple[int, int, int] = (0, 0, 0), txt_align: int = 3,
                  padding: int = 5) -> None:
        """Set this label's text."""
        self.labels = []
        self.shown_text = []
        i = 0
        text_height = 0
        while (i < len(text)) and \
                (self._rect.y + i * (text_height + padding) < self._rect.y + self._rect.height):
            self.shown_text.append(text[i])
            if i == 0:
                new_label = PygLabel(self._rect.x, self._rect.y,
                                     self._rect.width, self._rect.height, text[i],
                                     font, text_col, background_color, txt_align)
                self.labels.append(new_label)
            else:
                text_width, text_height = self.labels[i - 1].get_dimensions()
                new_label = PygLabel(self._rect.x,
                                     self._rect.y + i * (text_height + padding),
                                     self._rect.width, text_height + padding, text[i],
                                     font, text_col, background_color, txt_align)
                self.labels.append(new_label)
            i += 1

        if i >= len(text):
            self.cont = False
            self.not_shown_text = []
        else:
            self.cont = True
            self.not_shown_text = text[i:]

    def set_visible(self, value: bool) -> None:
        """Set visibility of PygMultiLine."""
        self._visible = value


class PygPageLabel:
    """Pages of Multiline Labels."""
    _visible: bool
    _selected: int
    pages: list[PygMultiLabel]
    buttons: Optional[tuple[PygButton, PygButton]]

    def __init__(self, x: int, y: int, width: int, height: int,
                 text: list[str], font: tuple[str, int] = (pygame.font.get_default_font(), 20),
                 text_color: tuple[int, int, int] = (0, 0, 0),
                 background_color: Optional[tuple[int, int, int]] = None,
                 txt_align: int = 3, visible: bool = False,
                 button_width: int = 9) -> None:
        """Initialize a PygPageLabel object."""
        self._visible = visible
        self.pages = []
        self._selected = 0
        label = PygMultiLabel(x, y, width, height, text, font,
                              text_color, background_color, txt_align, visible)
        self.pages.append(label)

        if label.cont:
            self.buttons = (PygButton(x - button_width, y + height // 2,
                                      button_width, button_width, font=font, text='<'),
                            PygButton(x + width, y + height // 2,
                                      button_width, button_width, font=font, text='>'))
        else:
            self.buttons = None

        while label.cont:
            label = PygMultiLabel(x, y, width, height, label.not_shown_text, font,
                                  text_color, background_color, txt_align, visible)
            self.pages.append(label)

    def draw(self, surface: Union[pygame.Surface, pygame.SurfaceType]):
        """Draw pages."""
        if self._visible:
            self.pages[self._selected].draw(surface)
            if self.buttons is not None:
                for button in self.buttons:
                    button.draw(surface)

    def on_click(self, event: pygame.event) -> bool:
        """Return true if a button is clicked."""
        if self.buttons is not None:
            return self.buttons[0].on_click(event) or self.buttons[1].on_click(event)
        else:
            return False

    def on_select(self, event: pygame.event) -> None:
        """Change page when selected."""
        if self.buttons is not None:
            if self.buttons[0].on_click(event):
                self._selected = max(min(self._selected - 1, len(self.pages) - 1), 0)
            elif self.buttons[1].on_click(event):
                self._selected = max(min(self._selected + 1, len(self.pages) - 1), 0)

    def set_visible(self, value: bool) -> None:
        """Set visibility."""
        self._visible = value
