"""Hold Stack class and MoveStack subclass."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from card import Card
    from space import Space
    import pygame


def is_valid_stack(cards: list["Card"] | None):
    """Check if a list of cards makes a valid movestack.
    To be valid, a stack must alternate in suit, and descend in value."""
    if not cards:
        return False
    if len(cards) == 1:
        return True  # A single card will always be a valid stack.
    for i in range(1, len(cards)):
        card = cards[i]
        prev_card = cards[i - 1]
        if not card.stacks_down(prev_card):
            return False
    return True


class Stack:
    """Stack of card objects."""

    def __init__(self, home_space: "Space", cards=None):
        """Create a stack of cards with home space and list of cards.

        Args:
            home_space (Space): Where stack defaults to.
            cards (list[Card], optional): Cards that go in the stack. Defaults to None.
        """
        self._home_space = home_space
        #  Need to do this because using empty list in args causes issues.
        self._cards: list["Card"] = cards if cards else []

    def __repr__(self):
        return f"{self._home_space}'s stack"

    @property
    def bottom_card(self):
        """Get lowest card in the stack if it exists."""
        if not self.is_empty:
            return self._cards[0]
        return None

    @property
    def cards(self):
        """Getter for list of cards."""
        return self._cards

    @property
    def home_space(self):
        """Getter for home_space."""
        return self._home_space

    @property
    def is_empty(self):
        """If there are no cards in the stack."""
        return self.length == 0

    @property
    def length(self):
        """Return amount of cards in stack."""
        return len(self._cards)

    @property
    def top_card(self):
        """Get highest card in the stack if it exists."""
        if not self.is_empty:
            return self._cards[-1]
        return None

    def add_card(self, card: "Card"):
        """Append card to the end of the stack."""
        self._cards.append(card)

    def draw(self, screen: "pygame.surface.Surface"):
        """Draw each card in order."""
        for card in self._cards:
            card.draw(screen)

    def get_mouse_target(self, cursor_pos: tuple[int, int]):
        """Get a target substack starting from cursor position, if it exists."""
        for card in self._cards[::-1]:
            if card.rect.collidepoint(cursor_pos):
                return self.make_stack(card)
        return None

    def get_sub_stack(self, card: "Card"):
        """Take a card and return a list of it and all cards above it in the stack."""
        if card in self._cards:
            card_index = self._cards.index(card)
            return self._cards[card_index:]
        return None

    def go_home(self):
        """Send stack to its home space."""
        for card in self._cards:
            card.go_to_space(self._home_space)

    def make_stack(self, start_card: "Card"):
        """Try and make a valid movestack starting from the card."""
        substack = self.get_sub_stack(start_card)
        if substack and is_valid_stack(substack):
            for card in substack:
                self.remove_card(card)
            return MoveStack(self._home_space, substack)
        return None

    def remove_card(self, card: "Card"):
        """Remove card from stack if it exists."""
        if card in self._cards:
            self._cards.remove(card)


class MoveStack(Stack):
    """Stack of cards that can be moved between spaces."""

    def __init__(self, home_space: "Space", cards: list["Card"]):
        """Create Stack and set reference point to 0, 0"""
        super().__init__(home_space, cards)
        self._reference_point = (0, 0)  # Used for dragging.

    def __repr__(self):
        return f"MoveStack of {self._cards}"

    def click(self, cursor_pos: tuple[int, int]):
        """Act upon cursor click."""
        self._reference_point = cursor_pos

    def drag(self, cursor_pos: tuple[int, int]):
        """Drag stack so reference point is at new cursor position."""
        d_x = cursor_pos[0] - self._reference_point[0]
        d_y = cursor_pos[1] - self._reference_point[1]
        for card in self._cards:
            card.move(d_x, d_y)
        self._reference_point = cursor_pos  # Set new ref point.

    def in_range(self, rect: "pygame.rect.Rect"):
        """Return if the bottom card is in the given rect."""
        if self.bottom_card:
            return rect.colliderect(self.bottom_card.rect)
        return False

    def make_move(self, space: "Space"):
        """Move stack into space."""
        move_dict = {
            "card": self.bottom_card,
            "dest": space,
            "source": self._home_space,
        }  # For later undoing.
        self._home_space = space
        self.go_home()
        return move_dict

    def piles_up(self, stack):
        """Check if lowest card piles up from stack's top card."""
        if self.bottom_card:
            return self.bottom_card.piles_up(stack.top_card)
        return False

    def stacks_down(self, stack):
        """Check if lowest card stacks down from stack's highest."""
        if self.bottom_card:
            return self.bottom_card.stacks_down(stack.top_card)
        return False
