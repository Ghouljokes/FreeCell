"""Hold base space, and tableau, foundation, and free space."""
import pygame
from constants import CARD_WIDTH, CARD_HEIGHT


class Space:
    """Base object for spaces."""

    def __init__(self, screen: pygame.surface.Surface, x: int, y: int):
        """Create a space where a card would be put."""
        self._screen = screen  # Game window
        self._x = x  # coordinate of left edge of space
        self._y = y  # coordinate of upper edge of space

    @property
    def rectangle(self):
        """Get rectangle of self at location."""
        rectangle = pygame.Rect(self._x, self._y, CARD_WIDTH, CARD_HEIGHT)
        return rectangle
