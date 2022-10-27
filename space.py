from typing import TYPE_CHECKING, Optional
import pygame
from constants import CARD_WIDTH, CARD_HEIGHT, STACK_OFFSET

if TYPE_CHECKING:
    from cards import Card

SLOT_COLOR = "#1e4632"


class Space:
    """Base class for spaces."""

    def __init__(self, x, y):
        """Create a space at the given position."""
        self._rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        self._card: Optional["Card"] = None

    @property
    def is_empty(self):
        """If no card in space."""
        return self._card == None

    @property
    def rect(self):
        """Getter for rect"""
        return self._rect

    def add_card(self, card: "Card"):
        """Add a card to the space."""
        self.set_card(card)
        card.set_space(self)

    def check_for_target(self, cursor_pos: tuple[int, int]):
        """Returns a card if it exists and the cursor is in position."""
        if self._rect.collidepoint(cursor_pos) and self._card:
            return self._card

    def draw(self, screen):
        """Draw space and contents."""
        pygame.draw.rect(screen, SLOT_COLOR, self._rect)
        if self._card:
            self._card.draw(screen)

    def move(self, location):
        """Move space and contents to new location."""
        self._rect.topleft = location
        if self._card:  # Move card with space if it exists.
            self._card.move(location)

    def remove_card(self):
        """Empty the space."""
        self._card = None

    def set_card(self, card):
        """Set _card to given card."""
        self._card = card

    def valid_dest(self, card: "Card"):
        """If space can hold card, return the space."""
        if self.is_empty and self.rect.colliderect(card.rect):
            return self


class StackSpace(Space):
    """Space on a card used for stacking."""

    def __init__(self, card: "Card"):
        """Create the space on top of the card."""
        self._parent_card = card
        x, y = self._parent_card.rect.topleft
        y += STACK_OFFSET
        super().__init__(x, y)

    def move(self, location: tuple[int, int]):
        """Move the space and contained cards to new location."""
        self._rect.topleft = location
        if self._card:
            self._card.move(location)


class Tableau(Space):
    """Space used at the bottom of tableau."""

    @property
    def top_card(self):
        """Return highest card in the tableau stack."""
        if not self._card:
            return None
        top_card = self._card
        while top_card.above_card:  # While card has card above it
            top_card = top_card.above_card  # Move to next card
        return top_card

    def check_for_target(self, cursor_pos: tuple[int, int]):
        """Check if cursor in tableau column and retrieve card."""
        if cursor_pos[0] in range(self.rect.left, self.rect.right):
            target_card = self.top_card
            while target_card:
                if target_card.rect.collidepoint(cursor_pos):
                    return target_card
                else:
                    target_card = target_card.below_card

    def stack_card(self, card: "Card"):
        """Add card to the highest available space in the column."""
        if not self._card:  # If column is empty, do a normal add.
            self.add_card(card)
        else:
            self.top_card.add_card(card)

    def top_space(self):
        """Get top empty space in the column."""
        if self.is_empty:
            return self
        else:
            return self.top_card.stack_space

    def valid_dest(self, card):
        """Check validity of top card in the column."""
        if self.is_empty:
            return super().valid_dest(card)
        return self.top_space().valid_dest(card)
