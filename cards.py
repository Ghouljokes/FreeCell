"""Hold card class."""
from typing import TYPE_CHECKING, Optional
from constants import CARD_WIDTH, CARD_HEIGHT

if TYPE_CHECKING:
    from pygame.surface import Surface


class Card:
    """Represent a playing card."""

    def __init__(self, value: int, suit: str, sprite: "Surface"):
        """Create card."""
        self._value = value
        self._suit = suit
        self._surface = sprite
        self._base_x = 0  # Where card will default to
        self._base_y = 0  # Where card will default to
        self._current_x = 0
        self._current_y = 0
        self.above_card: Optional["Card"] = None

    def center_on_point(self, pos: tuple[int, int]):
        """Update the card's current position so it is centered on point."""
        new_x = pos[0] - CARD_WIDTH // 2
        new_y = pos[1] - CARD_HEIGHT // 2
        self._current_x, self._current_y = new_x, new_y

    def draw(self, screen: "Surface"):
        """Draw card to screen."""
        dest = self._current_x, self._current_y
        screen.blit(self._surface, dest)

    def point_on_card(self, point: tuple[int, int]):
        """Return whether a given point lies on the surface of the card."""
        x_range = range(self._current_x, self._current_x + CARD_WIDTH)
        y_range = range(self._current_y, self._current_y + CARD_HEIGHT)
        return point[0] in x_range and point[1] in y_range

    def return_to_base(self):
        """Place the card back into its original spot."""
        self._current_x, self._current_y = self._base_x, self._base_y

    def set_new_base(self, x: int, y: int):
        """Set the card's new base location."""
        self._base_x, self._base_y = x, y
