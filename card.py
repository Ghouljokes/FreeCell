"""Hold Card Class."""

from typing import TYPE_CHECKING, Optional
import pygame
from spritesheet import SpriteSheet

if TYPE_CHECKING:
    from space import Space

SUIT_COLORS = {
    "clubs": "black",
    "diamonds": "red",
    "hearts": "red",
    "spades": "black",
}


class Card(pygame.sprite.Sprite):
    """Card object."""

    def __init__(self, suit: str, value: int, sprite_sheet: "SpriteSheet"):
        """Set card info and sprite.

        Args:
            suit (str): string of clubs, diamonds, spades, or hearts
            value (int): Numberic value of the card.
            sprite_sheet (SpriteSheet): Where Card will retrieve image from.
        """
        pygame.sprite.Sprite.__init__(self)
        self._suit = suit
        self._value = value
        self.image = sprite_sheet.card_image(suit, value)
        self.rect: pygame.rect.Rect = self.image.get_rect()

    def __repr__(self):
        return f"{self._value} of {self._suit}"

    @property
    def color(self):
        """Get color of the suit."""
        return SUIT_COLORS[self._suit]

    @property
    def suit(self):
        """Getter for suit."""
        return self._suit

    @property
    def value(self):
        """Getter for value."""
        return self._value

    def draw(self, screen: pygame.surface.Surface):
        """Draw the card's image on the screen."""
        dest = self.rect.topleft
        if self.image:
            screen.blit(self.image, dest)

    def go_to_space(self, space: "Space"):
        """Move card to next position in given space."""
        self.rect.topleft = space.next_card_pos
        space.add_card(self)

    def move(self, d_x: int, d_y: int):
        """Translate card by direction dx, dy"""
        self.rect = self.rect.move(d_x, d_y)

    def piles_up(self, card: Optional["Card"]):
        """Check if self piles up in a foundation from given card."""
        if not card:  # If there is no card, treat it as an empty space.
            return self._value == 1
        suits_match = self._suit == card.suit
        is_next_value = self._value == card.value + 1
        return suits_match and is_next_value

    def stacks_down(self, card: Optional["Card"]):
        """Check if self stacks up from a given card."""
        if not card:  # If not card, stack is empty and free to move to
            return True
        suits_alternate = self.color != card.color
        is_lower_value = self._value == card.value - 1
        return suits_alternate and is_lower_value


def create_deck() -> list[Card]:
    """Create and return a full deck of 52 cards."""
    deck = []
    sprite_sheet = SpriteSheet()
    for suit in sprite_sheet.suits:
        for value in range(1, 14):  # Values 1-13
            card = Card(suit, value, sprite_sheet)
            deck.append(card)
    return deck
