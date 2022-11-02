from spritesheet import SpriteSheet
from typing import Optional
import pygame
from constants import STACK_OFFSET
from space import StackSpace, Space

SUIT_COLORS = {
    "clubs": "black",
    "diamonds": "red",
    "hearts": "red",
    "spades": "black",
}


class Card(pygame.sprite.Sprite):
    """Playing card."""

    def __init__(self, suit: str, value: int, image):
        pygame.sprite.Sprite.__init__(self)
        self._value = value
        self._suit = suit
        self.image: "pygame.surface.Surface" = image
        self.rect: "pygame.rect.Rect" = self.image.get_rect()
        self._home_space: Optional["Space"] = None
        self._stack_space = StackSpace(self)
        self._anchor_point = (0, 0)
        self.is_clicked = False

    def __repr__(self):
        return f"{self._value} of {self._suit}"

    @property
    def above_card(self):
        """Card above this one in stack, if it exists."""
        return self._stack_space.card

    @property
    def below_card(self):
        """Get card this card is atop, if it exists."""
        if self._home_space and isinstance(self._home_space, StackSpace):
            return self._home_space.parent_card
        return None

    @property
    def color(self):
        """Get color of the suit."""
        return SUIT_COLORS[self._suit]

    @property
    def home_space(self):
        """Getter for home."""
        return self._home_space

    @property
    def stack_base(self):
        """Get home_space of lowest card in stack."""
        lowest_card = self
        while lowest_card.below_card:
            lowest_card = lowest_card.below_card
        return lowest_card.home_space

    @property
    def stack_size(self):
        """Return how large a stack down from this card would be."""
        stack_size = 1
        check_card = self
        while check_card.above_card:
            stack_size += 1
            check_card = check_card.above_card
        return stack_size

    @property
    def stack_space(self):
        """Getter for stackspace."""
        return self._stack_space

    @property
    def suit(self):
        """Getter for suit."""
        return self._suit

    @property
    def value(self):
        """Getter for value."""
        return self._value

    def center_on_point(self, point):
        """Move the card to be centered on the location."""
        self.rect.center = point
        # Since move handles stuff besides changing the rect, call that.
        self.move(self.rect.topleft)

    def click(self, cursor_pos):
        """Handle card becoming held."""
        self.set_anchor(cursor_pos)
        self.is_clicked = True

    def drag(self, cursor_pos):
        """Drag card so anchor point is at cursor_pos"""
        anchor_x_coord = self.rect.left + self._anchor_point[0]
        anchor_y_coord = self.rect.top + self._anchor_point[1]
        dx = cursor_pos[0] - anchor_x_coord
        dy = cursor_pos[1] - anchor_y_coord
        new_position = self.rect.left + dx, self.rect.top + dy
        self.move(new_position)

    def draw(self, screen: "pygame.surface.Surface"):
        """Draw the card's sprite, then draw the sprite of any cards above."""
        dest = self.rect.topleft
        screen.blit(self.image, dest)
        if self.above_card:  # If card above this one
            self.above_card.draw(screen)

    def go_home(self):
        """Move card back to the home space."""
        if self._home_space:
            self.move(self._home_space.rect.topleft)

    def in_range(self, space: "Space"):
        """Determine if card overlaps a space."""
        return self.rect.colliderect(space.rect)

    def is_valid_stack(self):
        """Check if card forms a stack of alternating downward cards."""
        checking_card = self
        while checking_card.above_card:
            above_card = checking_card.above_card
            if not above_card.stacks_down(checking_card):
                return False
            checking_card = above_card
        return True

    def move(self, location: tuple[int, int]):
        """Move card to new location."""
        self.rect.topleft = location
        stack_location = (location[0], location[1] + STACK_OFFSET)
        self._stack_space.move(stack_location)

    def piles_up(self, card: Optional["Card"]):
        if not card:  # If no card, check if ace.
            return self._value == 1
        return card.suit == self._suit and card.value == self._value - 1

    def release(self):
        """Release card from cursor."""
        self.is_clicked = False
        self.go_home()

    def set_anchor(self, cursor_pos):
        """Set an anchor point on the card based off cursor_pos.
        The anchor point is relative to topleft corner."""
        anchor_x = cursor_pos[0] - self.rect.left
        anchor_y = cursor_pos[1] - self.rect.top
        self._anchor_point = anchor_x, anchor_y

    def set_space(self, space: Space):
        """Set new base space and move card there.
        TRY NOT TO CALL, USE THE SPACE'S ADD METHOD INSTEAD."""
        if self._home_space:
            self._home_space.remove_card(self)
        self._home_space = space

    def stacks_down(self, card: "Card"):
        """Check if card stacks down from given one."""
        return self.color != card.color and self._value == card.value - 1

    def switch_space(self, space: "Space"):
        """Send the card to a new space."""
        space.add_card(self)
        self.go_home()


def create_deck():
    """Create full deck of 52 cards."""
    deck: list[Card] = []
    sprite_sheet = SpriteSheet()
    for suit in sprite_sheet.suits:
        for value in range(1, 14):
            sprite = sprite_sheet.card_sprite(suit, value)
            card = Card(suit, value, sprite)
            deck.append(card)
    return deck
