from spritesheet import SpriteSheet
from typing import Optional, Type
import pygame
from constants import STACK_OFFSET
from space import StackSpace, Space


class Card(pygame.sprite.Sprite):
    """Playing card."""

    def __init__(self, suit: str, value: int, image):
        pygame.sprite.Sprite.__init__(self)
        self._value = value
        self._suit = suit
        self.image: pygame.surface.Surface = image
        self.rect: pygame.rect.Rect = self.image.get_rect()  # Used for drawing
        self._home_space: Optional["Space"] = None
        self._stack_space = StackSpace(self)
        self._anchor_point = (0, 0)

    @property
    def above_card(self):
        """Card above this one in stack, if it exists."""
        return self._stack_space._card

    @property
    def below_card(self):
        """Get card this card is atop, if it exists."""
        if self._home_space and type(self._home_space) == StackSpace:
            return self._home_space._parent_card

    def add_card(self, card):
        """Place a card into the stack space."""
        self._stack_space.add_card(card)

    def center_on_point(self, point):
        """Move the card to be centered on the location."""
        self.rect.center = point
        # Since move handles stuff besides changing the rect, call that.
        self.move(self.rect.topleft)

    def drag(self, cursor_pos):
        """Drag card so anchor point is at cursor_pos"""
        anchor_x_coord = self.rect.left + self._anchor_point[0]
        anchor_y_coord = self.rect.top + self._anchor_point[1]
        dx = cursor_pos[0] - anchor_x_coord
        dy = cursor_pos[1] - anchor_y_coord
        new_position = self.rect.left + dx, self.rect.top + dy
        self.move(new_position)

    def draw(self, screen: pygame.surface.Surface):
        """Draw the card's sprite, then draw the sprite of any cards above."""
        dest = self.rect.topleft
        screen.blit(self.image, dest)
        if self.above_card:  # If card above this one
            self.above_card.draw(screen)

    def get_clicked(self, cursor_pos):
        """Handle card becoming held."""
        self.set_anchor(cursor_pos)

    def go_home(self):
        """Move card back to the home space."""
        if self._home_space:
            self.move(self._home_space.rect.topleft)

    def move(self, location: tuple[int, int]):
        """Move card to new location."""
        self.rect.topleft = location
        stack_location = (location[0], location[1] + STACK_OFFSET)
        self._stack_space.move(stack_location)

    def set_anchor(self, cursor_pos):
        """Set an anchor point on the card based off cursor_pos.
        The anchor point is relative to topleft corner."""
        anchor_x = cursor_pos[0] - self.rect.left
        anchor_y = cursor_pos[1] - self.rect.top
        self._anchor_point = anchor_x, anchor_y

    def set_space(self, space: Space):
        """Set new base space and move card there."""
        if self._home_space:
            self._home_space.remove_card()
        self._home_space = space
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
