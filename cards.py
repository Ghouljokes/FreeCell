"""Hold card class."""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pygame.surface import Surface


class Card:
    """Represent a playing card."""

    def __init__(self, value: int, suit: str, sprite: "Surface"):
        """Create card."""
        self._value = value
        self._suit = suit
        self._surface = sprite
        self._x = 0
        self._y = 0

    @property
    def suit(self):
        """Getter method for suit."""
        return self._suit

    @property
    def value(self):
        """Getter method for value."""
        return self._value

    def draw(self, screen: "Surface"):
        """Draw card to screen."""
        dest = self._x, self._y
        screen.blit(self._surface, dest)

    def set_new_base(self, x: int, y: int):
        """Set the card's new base location."""
        self._x, self._y = x, y
