from typing import TYPE_CHECKING
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
        self._cards: list["Card"] = []

    @property
    def card(self):
        """Return the last card in self.cards"""
        if len(self._cards) > 0:
            return self._cards[-1]
        return None

    @property
    def rect(self):
        """Getter for rect"""
        return self._rect

    def add_card(self, card: "Card"):
        """Add a card to the space."""
        self._cards.append(card)
        card.set_space(self)

    def check_for_target(self, cursor_pos: tuple[int, int]):
        """Returns a card if it exists and the cursor is in position."""
        if self._rect.collidepoint(cursor_pos):
            return self.card
        return None

    def draw(self, screen):
        """Draw space and contents."""
        pygame.draw.rect(screen, SLOT_COLOR, self._rect)
        if self.card:
            self.card.draw(screen)

    def move(self, location):
        """Move space and contents to new location."""
        self._rect.topleft = location
        if self.card:  # Move card with space if it exists.
            self.card.move(location)

    def remove_card(self, card):
        """Remove the given card from the space."""
        if card in self._cards:
            self._cards.remove(card)

    def valid_dest(self, _: "Card"):
        """
        If space can hold card, return the space.
        second argument is kept as argument for subclasses.
        """
        return not self.card


class Foundation(Space):
    """Space used for the foundations."""

    def draw(self, screen):
        """Personalized function so cards under dragged card will show."""
        for card in self._cards[::-1]:  # Starting from the top
            if not card.is_clicked:
                card.draw(screen)
                return
        pygame.draw.rect(screen, SLOT_COLOR, self.rect)

    def valid_dest(self, card: "Card"):
        """If suitable, and single card, return True."""
        return card.piles_up(self.card) and not card.above_card


class FreeCell(Space):
    """Free cell space."""

    def valid_dest(self, card: "Card"):
        """Check if card is single ant space is empty."""
        return not self.card and not card.above_card


class StackSpace(Space):
    """Space on a card used for stacking."""

    def __init__(self, parent_card: "Card"):
        """Create the space on top of the card."""
        self._parent_card = parent_card
        x, y = self._parent_card.rect.topleft
        y += STACK_OFFSET
        super().__init__(x, y)

    def __repr__(self):
        return f"{self._parent_card}'s stack_space"

    @property
    def parent_card(self):
        """Getter for parent."""
        return self._parent_card

    def move(self, location: tuple[int, int]):
        """Move the space and contained cards to new location."""
        self._rect.topleft = location
        if self.card:
            self.card.move(location)

    def valid_dest(self, card: "Card"):
        """Check if card can stack down."""
        return card.stacks_down(self._parent_card)


class Tableau(Space):
    """Space used at the bottom of tableau."""

    @property
    def top_card(self):
        """Return highest card in the tableau stack."""
        top_card = self.card
        if top_card:
            while top_card.above_card:  # While card has card above it
                top_card = top_card.above_card
        return top_card

    @property
    def top_space(self):
        """Get top empty space in the column."""
        top_card = self.top_card
        return top_card.stack_space if top_card else self

    def check_for_target(self, cursor_pos: tuple[int, int]):
        """Check if cursor in tableau column and retrieve card."""
        if cursor_pos[0] in range(self.rect.left, self.rect.right):
            target_card = self.top_card
            while target_card:
                if target_card.rect.collidepoint(cursor_pos):
                    return target_card
                target_card = target_card.below_card
        return None

    def stack_card(self, card: "Card"):
        """Add card to the highest available space in the column."""
        self.top_space.add_card(card)
