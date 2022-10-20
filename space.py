"""Hold base space, and tableau, foundation, and free space."""
import pygame
from constants import CARD_WIDTH, CARD_HEIGHT
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cards import Card


STACK_OFFSET = 20  # How far down a card is plaed from the one it's atop.


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


class Tableau(Space):
    """Space in the tableau that holds a card column."""

    def __init__(self, screen, x, y):
        super().__init__(screen, x, y)
        self._cards: list[
            "Card"
        ] = []  # Cards in the column, left is closest to the base.

    @property
    def highest_y(self):
        """Highest location a card can be placed."""
        return self._y + STACK_OFFSET * len(self._cards)

    def add_card(self, card: "Card"):
        """Add card to the next space in the column."""
        card.set_new_base(self._x, self.highest_y)
        self._cards.append(card)

    def draw_cards(self):
        """Draw entire column of cards."""
        for card in self._cards:
            card.draw(self._screen)
