"""Hold card class."""
from typing import TYPE_CHECKING, Optional
import pygame
from constants import CARD_WIDTH, CARD_HEIGHT

if TYPE_CHECKING:
    from pygame.surface import Surface


class Card(pygame.sprite.Sprite):
    """Represent a playing card."""

    def __init__(self, value: int, suit: str, image: "Surface"):
        """Create card."""

        pygame.sprite.Sprite.__init__(self)
        self.image: "Surface" = image
        self.rect: pygame.rect.Rect = self.image.get_rect()
        self._value = value
        self._suit = suit
        self._base_x = 0  # Where card will default to
        self._base_y = 0  # Where card will default to
        self.above_card: Optional["Card"] = None

    def center_on_point(self, pos: tuple[int, int]):
        """Update the card's current position so it is centered on point."""
        self.rect.center = pos

    def draw(self, screen: "Surface"):
        """Draw card to screen."""
        dest = self.rect.x, self.rect.y
        screen.blit(self.image, dest)

    def point_on_card(self, point: tuple[int, int]):
        """Return whether a given point lies on the surface of the card."""
        return self.rect.collidepoint(point)

    def return_to_base(self):
        """Place the card back into its original spot."""
        self.update_position((self._base_x, self._base_y))

    def set_new_base(self, x: int, y: int):
        """Set the card's new base location."""
        self._base_x, self._base_y = x, y

    def update_position(self, pos: tuple[int, int]):
        self.rect.x, self.rect.y = pos
