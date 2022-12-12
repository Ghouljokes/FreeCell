from typing import TYPE_CHECKING
import pygame
from constants import CARD_WIDTH, CARD_HEIGHT, STACK_OFFSET
from stack import Stack

if TYPE_CHECKING:
    from stack import MoveStack
    from card import Card


SLOT_COLOR = "#1e4632"


class Space:
    """Space on the game board."""

    def __init__(self, x: int, y: int, index: int):
        """Create space at position x, y"""
        self._rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        self._stack = Stack(self)
        self._index = index

    def __repr__(self):
        return f"Free cell {self._index}"

    @property
    def stack(self):
        """Stack containing the space's cards."""
        return self._stack

    @property
    def is_empty(self):
        """If no cards in card stack"""
        return self._stack.is_empty

    @property
    def next_card_pos(self):
        """Return position a card would move to if added to stack."""
        return self._rect.topleft

    @property
    def top_card(self):
        """Return card at top of the space's stack."""
        return self._stack.top_card

    @property
    def top_rect(self):
        """Return rect of highest card if exists. Base just returns self rect."""
        return self._rect

    def add_card(self, card: "Card"):
        """Add a card to space's stack."""
        self._stack.add_card(card)

    def check_for_target(self, cursor_pos: tuple[int, int]):
        """Check for and return a target to be clicked by the cursor."""
        if self._rect.collidepoint(cursor_pos) and self.top_card:
            return self._stack.make_stack(self.top_card)
        return None

    def draw(self, screen: pygame.surface.Surface):
        """Draw space to screen, including cards if they exist."""
        if not self.is_empty:
            self._stack.draw(screen)
        else:
            pygame.draw.rect(screen, SLOT_COLOR, self._rect)

    def is_valid_drop_point(self, stack: "MoveStack"):
        """Check if movestack can be dropped off here."""
        return stack.in_range(self.top_rect) and self.valid_dest(stack)

    def make_sub_stack(self, card):
        """Make sub stack off of the given card."""
        return self._stack.make_stack(card)

    def valid_dest(self, stack: "MoveStack"):
        """Check if space is a valid destination for the movestack."""
        return self.is_empty and stack.length == 1


class Foundation(Space):
    """Specialized space for the foundations."""

    def __repr__(self):
        return f"Foundation {self._index}"

    def valid_dest(self, stack: "MoveStack"):
        """Check if stack abides by foundation rules."""
        return stack.length == 1 and stack.piles_up(self._stack)


class Tableau(Space):
    """Specialized Tableau space."""

    def __repr__(self):
        return f"Tableau {self._index}"

    @property
    def next_card_pos(self):
        """Get next position a card would move to."""
        x = self._rect.x
        y = self.top_rect.y + STACK_OFFSET if self.top_card else self._rect.y
        return (x, y)

    @property
    def top_rect(self):
        """Get rect of top card if it exists."""
        return self.top_card.rect if self.top_card else self._rect

    def check_for_target(self, cursor_pos: tuple[int, int]):
        """Try and get MoveStack from lowest card the cursor clicked."""
        return self._stack.get_mouse_target(cursor_pos)

    def valid_dest(self, stack: "MoveStack"):
        """Check if space is a valid point for the MoveStack."""
        if self.is_empty:
            return True
        return stack.stacks_down(self._stack)
