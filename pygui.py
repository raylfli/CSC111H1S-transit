"""TTC Route Planner for Toronto, Ontario -- Pygame UI classes

This file contains all Pygame GUI classes:
    - Rect
    - PygButton
    - PygDropdown
    - PygLabel
    - PygMultiLabel
    - PygPageLabel

This file is Copyright (c) 2021 Anna Cho, Charles Wong, Grace Tian, Raymond Li
"""

from typing import Union, Optional, Callable
import pygame


# -------------------------------------------------------------------------------------------
# PyGUI Classes
# -------------------------------------------------------------------------------------------
class Rect:
    """A rectangle object.

    Instance Attributes:
        - x: int of the left-most x-coordinate
        - y: int of the top-most y-coordinate
        - width: int for the width of the rectangle
        - height: int for the height of the rectangle

    Representation Invariants:
        - self.width >= 0
        - self.height >= 0
    """
    x: int
    y: int
    width: int
    height: int

    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        """Initialize a Rect object.

        Preconditions:
            - width >= 0
            - height >= 0
        """
        self.x, self.y, self.width, self.height = x, y, width, height

    def contains(self, x: int, y: int) -> bool:
        """Returns whether this rectangle contains the point (x, y).
        Points that are on the edges are not considered inside the rectangle.
        """
        return self.x < x < self.x + self.width and self.y < y < self.y + self.height


class PygButton:
    """A clickable button.
    The button can display text and draw additional objects on top of it.

    Representation Invariants:
        - 0 <= self._txt_align <= 2
    """
    # Private Instance Attributes:
    #   - _rect: Rect object of the area of the button
    #   - _bg_color: pygame.Color of the colour of the background
    #   - _depress_color: pygame.Color of the colour of the button when clicked
    #   - _dep: bool if the button is clicked (true if clicked)
    #   - _text: optional string of the text displayed on the button
    #   - _font: pygame.font.Font for the optional text
    #   - _txt_col: tuple of ints for text colour in RBG of optional text
    #   - _txt_align: int for the alignment of the text, more detail in initializer
    #   - _adjust: tuple of ints for the x-, y-adjustments for the Rect object coordinates
    #   - _draw_func: custom draw function for any additional objects to draw
    _rect: Rect
    _bg_color: pygame.Color
    _depress_color: pygame.Color
    _dep: bool
    _text: Optional[str]
    _font: Optional[pygame.font.Font]
    _txt_col: Optional[tuple[int, int, int]]
    _txt_align: int
    _txt_surface: Optional[pygame.Surface]
    _adjust: tuple[int, int]
    _draw_func: Callable

    def __init__(self, x: int, y: int, width: int, height: int, text: str = None,
                 font: tuple[str, int] = (pygame.font.get_default_font(), 20),
                 txt_col: tuple[int, int, int] = (0, 0, 0),
                 txt_align: int = 0,
                 color: tuple[int, int, int] = (255, 255, 255),
                 depress_color: tuple[int, int, int] = (200, 200, 200),
                 x_adjust: int = 0, y_adjust: int = 0,
                 draw_func: Callable = None) -> None:
        """Initialize a button. Customizable background colour, image.

        Text align:
            - 0 for left align, bottom align
            - 1 for center align, middle align
            - 2 for right align, bottom align

        Preconditions:
            - width >= 0
            - height >= 0
            - 0 <= txt_align <= 2
            - all{0 <= c <= 255 for c in txt_col}
            - all{0 <= c <= 255 for c in color}
            - all{0 <= c <= 255 for c in depress_color}
        """
        self._rect = Rect(x, y, width, height)
        self._bg_color = pygame.Color(color)
        self._depress_color = pygame.Color(depress_color)
        self._dep = False
        self._set_text(text, font, txt_col, txt_align)
        self._adjust = (x_adjust, y_adjust)
        self._draw_func = draw_func

    def _set_text(self, text: str = None,
                  font: tuple[str, int] = (pygame.font.get_default_font(), 20),
                  txt_col: tuple[int, int, int] = (0, 0, 0), txt_align: int = 0) -> None:
        """Set text of this button."""
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

    def draw(self, surface: Union[pygame.Surface, pygame.SurfaceType]) -> None:
        """Draw this button."""
        # Draw when button is depressed or not
        if not self._dep:
            pygame.draw.rect(surface, self._bg_color,
                             (self._rect.x, self._rect.y, self._rect.width, self._rect.height))
        else:
            pygame.draw.rect(surface, self._depress_color,
                             (self._rect.x, self._rect.y, self._rect.width, self._rect.height))

        # Draw text if necessary
        if self._text is not None:
            width, height = self._txt_surface.get_size()
            # bottom left align
            if self._txt_align == 0:
                surface.blit(self._txt_surface, (self._rect.x + self._rect.width / 15,
                                                 max(self._rect.y,
                                                     self._rect.y + self._rect.height - height)),
                             pygame.Rect(0, max(0, height - self._rect.height),
                                         self._rect.width, self._rect.height))
            # center align
            elif self._txt_align == 1:
                surface.blit(self._txt_surface, (max(self._rect.x,
                                                     (self._rect.width - width) // 2
                                                     + self._rect.x),
                                                 max(self._rect.y,
                                                     self._rect.y
                                                     + (self._rect.height - height) // 2)),
                             pygame.Rect(max(0, (width - self._rect.width) // 2),
                                         max(0, (height - self._rect.height) // 2),
                                         self._rect.width, self._rect.height))
            # bottom right align
            elif self._txt_align == 2:
                surface.blit(self._txt_surface, (max(self._rect.x,
                                                     self._rect.x + self._rect.width - width)
                                                 - self._rect.width / 15,
                                                 max(self._rect.y,
                                                     self._rect.y + self._rect.height - height)),
                             pygame.Rect(max(0, width - self._rect.width),
                                         max(0, height - self._rect.height),
                                         self._rect.width, self._rect.height))

        # Draw using custom draw function
        if self._draw_func is not None:
            self._draw_func(surface, self._rect.x, self._rect.y,
                            self._rect.width, self._rect.height)

    def on_click(self, event: pygame.event.Event) -> bool:
        """Return true if the event clicked this button."""
        if event.type == pygame.MOUSEBUTTONDOWN and \
                pygame.mouse.get_pressed(3) == (True, False, False):
            x, y = pygame.mouse.get_pos()
            if self._rect.contains(x + self._adjust[0], y + self._adjust[1]):
                self._dep = True
                return True
        if event.type == pygame.MOUSEBUTTONUP:
            self._dep = False
        return False


class PygDropdown:
    """A dropdown menu.

    Instance Attributes:
        - selected: string of the current selected option in the dropdown
    """
    # Private Instance Attributes:
    #   - _rect: Rect object of the area of the selected option of the menu
    #   - _stack_rect: Rect object of the area of the rest of the options
    #   - _active: bool of if the dropdown menu is active (showing dropdown options)
    #   - _font: pygame.font.Font of the text font
    #   - option_surfs: dictionary of the option to the pygame.Surface of the surface
    #       containing the text of its key
    #   - _option_nums: dictionary of option number to the option string
    #   - field_col: pygame.Color of the colour of the field (selected option)
    #   - _dropdown_col: pygame.Color of the colour of the dropdown (all options)
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
                 dropdown_col: tuple[int, int, int] = (255, 255, 255)) -> None:
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

    def draw(self, surface: Union[pygame.Surface, pygame.SurfaceType]) -> None:
        """Draw this menu."""
        # Draw field
        pygame.draw.rect(surface, self._field_col,
                         (self._rect.x, self._rect.y, self._rect.width, self._rect.height))
        height = self._option_surfs[self.selected].get_size()[1]
        surface.blit(self._option_surfs[self.selected], (self._rect.x + self._rect.width / 15,
                                                         max(self._rect.y, self._rect.y
                                                             + self._rect.height - height)),
                     pygame.Rect(0, max(0, height - self._rect.height),
                                 self._rect.width, self._rect.height))

        if self._active:
            # Draw dropdowns
            for option in self._option_nums:
                if self._option_nums[option] != self.selected:
                    self._draw_option(self._option_nums[option], option, surface)

    def _draw_option(self, option: str, option_num: int,
                     surface: Union[pygame.Surface, pygame.SurfaceType]) -> None:
        """Draw a single option on the given surface."""
        y = self._rect.y + self._rect.height * option_num
        pygame.draw.rect(surface, self._dropdown_col,
                         (self._rect.x, y, self._rect.width, self._rect.height))
        height = self._option_surfs[option].get_size()[1]
        surface.blit(self._option_surfs[option], (self._rect.x + self._rect.width / 15,
                                                  max(y, y + self._rect.height - height)),
                     pygame.Rect(0, max(0, height - self._rect.height),
                                 self._rect.width, self._rect.height))

    def on_select(self, event: pygame.event.Event) -> None:
        """On select, either activates or deactivates this dropdown. The activated dropdown
        allows the selection of a new option."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            if not self._active and self._rect.contains(x, y):
                option_num = 1
                # display each option for the dropdown
                for option in self._option_surfs:
                    if option != self.selected:
                        self._option_nums[option_num] = option
                        option_num += 1
                self._active = True

            # dropdown is active
            elif self._active:
                if self._stack_rect.contains(x, y):
                    num = (y - self._rect.y) // self._rect.height
                    if num > 0:
                        self.selected = self._option_nums[num]
                    self._active = False
                else:
                    self._active = False


class PygLabel:
    """Text label. Does NOT support multiline labels.

    Instance Attributes:
        - text: string of the text to be displayed in the label
    """
    # Private Instance Attributes:
    #   - _rect: Rect object for the area of this label
    #   - _font: pygame font for the text
    #   - _text_col: tuple of int for text colour in RGB
    #   - _bg_col: optional pygame.Color for the background colour
    #   - _text_surface: pygame.Surface where the text is displayed
    #   - _txt_align: int for the text alignment, described in more detail in initializer
    _rect: Rect
    _font: pygame.font.Font
    text: str
    _text_col: tuple[int, int, int]
    _bg_col: Optional[pygame.Color]
    _text_surface: pygame.Surface
    _txt_align: int

    def __init__(self, x: int, y: int, width: int, height: int,
                 text: str,
                 font: tuple[str, int] = (pygame.font.get_default_font(), 20),
                 text_color: tuple[int, int, int] = (0, 0, 0),
                 background_color: Optional[tuple[int, int, int]] = None,
                 txt_align: int = 0) -> None:
        """Initialize PygLabel.

        txt_align values:
            - 0 for left align, bottom align
            - 1 for center align, middle align
            - 2 for right align, bottom align
            - 3 for left align, top align

        Preconditions:
            - 0 <= txt_align <= 3
            - all{0 <= c <= 255 for c in text_color}
        """
        self._rect = Rect(x, y, width, height)
        self._font = pygame.font.SysFont(font[0], font[1])
        self._set_text(text, font, text_color, txt_align)

        if background_color is not None:
            self._bg_col = pygame.Color(background_color)
        else:
            self._bg_col = None

    def draw(self, surface: Union[pygame.Surface, pygame.SurfaceType], padding: int = 5) -> None:
        """Draw this label on the given surface.
        """
        # draw background ----------------------------------------------
        if self._bg_col is not None:
            pygame.draw.rect(surface, self._bg_col,
                             pygame.Rect(self._rect.x,
                                         self._rect.y,
                                         self._rect.width,
                                         self._rect.height))

        # draw text ---------------------------------------------------
        width, height = self._text_surface.get_size()
        # bottom left align
        if self._txt_align == 0:
            surface.blit(self._text_surface, (self._rect.x + self._rect.width / 15,
                                              max(self._rect.y,
                                                  self._rect.y + self._rect.height - height)),
                         pygame.Rect(0, max(0, height - self._rect.height),
                                     self._rect.width, self._rect.height))
        # center align
        elif self._txt_align == 1:
            surface.blit(self._text_surface,
                         (max(self._rect.x, (self._rect.width - width) // 2 + self._rect.x),
                          max(self._rect.y,
                              self._rect.y + (self._rect.height - height) // 2)),
                         pygame.Rect(max(0, (width - self._rect.width) // 2),
                                     max(0, (height - self._rect.height) // 2),
                                     self._rect.width, self._rect.height))
        # bottom right align
        elif self._txt_align == 2:
            surface.blit(self._text_surface, (
                max(self._rect.x, self._rect.x + self._rect.width - width) - self._rect.width / 15,
                max(self._rect.y,
                    self._rect.y + self._rect.height - height)),
                         pygame.Rect(max(0, width - self._rect.width),
                                     max(0, height - self._rect.height),
                                     self._rect.width, self._rect.height))
        # top left align
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
        """Public set text."""
        if text is not None:
            self.text = text
            self._text_surface = self._font.render(text, True, self._text_col)

    def get_dimensions(self) -> tuple[int, int]:
        """Return a tuple of the width and height of the PygLabel."""
        return self._text_surface.get_size()


class PygMultiLabel:
    """Multiline pygame label.

    Instance Attributes:
        - labels: list of PygLabel objects
        - text: list of strings of all text that should be displayed
        - shown_text: list of strings of text that fits in this PygMultiLabel object
        - not_shown_text: list of strings of text that cannot fit
        - cont: boolean of if there is a continuation of text that has not been shown yet

    Representation Invariants:
        - 0 <= self.txt_align <= 3
        - all{0 <= c <= 255 for c in self.text_color}
    """
    # Private Instance Attributes
    #   - _rect: Rect object for the background
    #   - _visible: boolean for if this object is visible when drawn
    _rect: Rect
    _visible: bool
    labels: list[PygLabel]
    text: list[str]
    shown_text: list[str]
    not_shown_text: list[str]
    cont: bool

    def __init__(self, x: int, y: int, width: int, height: int,
                 text: list[str], font: tuple[str, int] = (pygame.font.get_default_font(), 20),
                 text_color: tuple[int, int, int] = (0, 0, 0),
                 background_color: Optional[tuple[int, int, int]] = None,
                 txt_align: int = 3, visible: bool = False) -> None:
        """Initialize PygMultiLabel.

        Preconditions:
            - 0 <= txt_align <= 3
            - all{0 <= c <= 255 for c in text_color}
        """
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
        """Set this label's text.
        This includes setting self.labels, self.text, self.shown_text, self.not_shown_text,
        and self.cont.
        """
        self.labels = []
        self.text = []
        self.shown_text = []

        # Get list of wrapped text
        for j in range(0, len(text)):
            self.text.extend(self._get_wrap_text(text[j], font, padding))

        # Add PygLabels for each line of text
        i = 0
        text_height = 0
        while (i < len(self.text)) and \
                (self._rect.y + i * (text_height + padding) < self._rect.y + self._rect.height):
            # Add to self.shown_text
            self.shown_text.append(self.text[i])

            # First label (topmost PygLabel)
            if i == 0:
                new_label = PygLabel(self._rect.x, self._rect.y,
                                     self._rect.width, self._rect.height, self.text[i],
                                     font, text_col, background_color, txt_align)
                self.labels.append(new_label)

            # Other labels (depends on previous PygLabel)
            else:
                text_height = self.labels[i - 1].get_dimensions()[1]
                new_label = PygLabel(self._rect.x,
                                     self._rect.y + i * (text_height + padding),
                                     self._rect.width, text_height + padding, self.text[i],
                                     font, text_col, background_color, txt_align)
                self.labels.append(new_label)

            # Increase index
            i += 1

        # Determine if there's leftover text that's not shown
        if i >= len(self.text):
            self.cont = False
            self.not_shown_text = []
        else:
            self.cont = True
            self.not_shown_text = self.text[i:]

    def _get_wrap_text(self, text: str, given_font: tuple[str, int], padding: int) -> list[str]:
        """Return a list of strings for text that can fit in the PygMultiLabel object to
        represent wrapped text."""
        font = pygame.font.SysFont(given_font[0], given_font[1])
        text_width = font.size(text)[0]
        box_width = self._rect.width

        if text_width > box_width - (2 * padding):
            # wrap text
            words = text.split()
            return self._wrap_text(words, [], font, box_width, padding)[0]
        else:
            return [text]

    def _wrap_text(self, words: list[str], finished_text: list[str],
                   font: pygame.font.SysFont, box_width: int, padding: int) \
            -> tuple[list[str], list[str]]:
        """Return a tuple of a list of strings that fit in the MultiLabel object
        and a list of strings to not be displayed."""
        if words == []:
            return (finished_text, [])
        else:
            i = 1
            new_words = words[0]
            while i < len(words) - 1 and \
                    font.size(new_words + ' ' + words[i])[0] < box_width - (2 * padding):
                new_words += ' ' + words[i]
                i += 1
            return self._wrap_text(words[i:], finished_text + [new_words], font, box_width, padding)

    def set_visible(self, value: bool) -> None:
        """Set visibility of PygMultiLine."""
        self._visible = value


class PygPageLabel:
    """Pages of Multiline Labels.

    Instance Attributes:
        - pages: list of PygMultiLabel objects
        - buttons: Optional tuple of PygButtons to scroll between pages
    """
    _visible: bool
    _selected: int
    pages: list[PygMultiLabel]
    buttons: Optional[tuple[PygButton, PygButton]]

    def __init__(self, x: int, y: int, width: int, height: int,
                 text: list[str], font: tuple[str, int] = (pygame.font.get_default_font(), 20),
                 text_color: tuple[int, int, int] = (0, 0, 0),
                 background_color: Optional[list[tuple[int, int, int]]] = None,
                 txt_align: int = 3, visible: bool = False,
                 button_width: int = 9) -> None:
        """Initialize a PygPageLabel object.

        Preconditions:
            - 0 <= txt_align <= 3
            - all{0 <= c <= 255 for c in text_color}
        """
        self._visible = visible
        self.pages = []
        self._selected = 0
        label = PygMultiLabel(x, y, width, height, text, font,
                              text_color, background_color, txt_align, visible)
        self.pages.append(label)

        # Create buttons if necessary
        if label.cont:
            self.buttons = (PygButton(x + width // 2 - button_width // 2, y - button_width,
                                      button_width, button_width, font=font,
                                      draw_func=draw_inc),
                            PygButton(x + width // 2 - button_width // 2, y + height,
                                      button_width, button_width, font=font,
                                      draw_func=draw_dec))
        else:
            self.buttons = None

        # Create multiple pages of info
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


# -------------------------------------------------------------------------------------------
# Functions for drawing on increment labels
# -------------------------------------------------------------------------------------------
def draw_inc(screen: pygame.Surface, x: int, y: int, width: int, height: int) -> None:
    """Draw increment arrow."""
    pygame.draw.line(screen, pygame.Color('black'), (x, y + height * 3 / 4), (x + width / 2, y), 2)
    pygame.draw.line(screen, pygame.Color('black'), (x + width / 2, y),
                     (x + width, y + height * 3 / 4), 2)


def draw_dec(screen: pygame.Surface, x: int, y: int, width: int, height: int) -> None:
    """Draw decrement arrow."""
    pygame.draw.line(screen, pygame.Color('black'), (x, y + height / 4),
                     (x + width / 2, y + height), 2)
    pygame.draw.line(screen, pygame.Color('black'), (x + width / 2, y + height),
                     (x + width, y + height / 4), 2)


if __name__ == "__main__":
    import python_ta.contracts
    python_ta.contracts.check_all_contracts()

    import doctest
    doctest.testmod()

    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['pygame', 'typing'],
        'allowed-io': [],
        'max-line-length': 100,
        'disable': ['E1136', 'E1121', 'R0902']
    })
