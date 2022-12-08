"""Hold code for mantaining spritesheet for cards."""
import pygame
from constants import CARD_HEIGHT, CARD_WIDTH


class SpriteSheet:
    """Spritesheet used for card images."""

    def __init__(self):
        """Load the sheet."""
        filename = "./sprites/Deck.png"
        try:
            self.sheet = pygame.image.load(filename).convert()
        except pygame.error as e:
            print(f"Unable to load spritesheet image: {filename}")
            raise SystemExit(e)
        self.suits = ["clubs", "diamonds", "hearts", "spades"]

    def image_at(self, rectangle):
        """Load a specific image from a specific rectangle."""
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        return image

    def card_rect(self, suit: str, value: int):
        """Get coordinates for card rectangle."""
        # Translate suit and value to coordinates for card sprite.
        upper_y = self.suits.index(suit) * CARD_HEIGHT
        left_x = (value - 1) * CARD_WIDTH
        return (left_x, upper_y, CARD_WIDTH, CARD_HEIGHT)

    def card_image(self, suit: str, value: int) -> pygame.surface.Surface:
        """Get the image for a given card from the spritesheet."""
        rectangle = self.card_rect(suit, value)
        return self.image_at(rectangle)
