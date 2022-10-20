"""Hold main game object and play freecell."""
import random
from typing import Optional
import pygame
from cards import Card
from space import Space, Tableau
from spritesheet import SpriteSheet
from constants import CARD_WIDTH, BUFFER_SIZE

BG_COLOR = "#35654d"
SLOT_COLOR = "#1e4632"


class Game:
    """Main game object."""

    def __init__(self):
        """Set up game."""
        self._screen = self.create_screen()
        self._sprite_sheet = SpriteSheet()
        self._foundation: list[Space] = self.create_foundation()
        self._free_cells: list[Space] = self.create_free()
        self._tableau: list[Tableau] = self.create_tableau()
        self._cards = self.create_cards()
        self.place_cards()
        self._running = True
        self._held_card: Optional[Card] = None

    def create_cards(self):
        """Create the full deck of cards."""
        cards = []
        for suit in ["clubs", "diamonds", "hearts", "spades"]:
            for value in range(1, 14):
                sprite = self._sprite_sheet.card_sprite(suit, value)
                card = Card(value, suit, sprite)
                cards.append(card)
        return cards

    def create_screen(self):
        """Create main screen for the game."""
        screen = pygame.display.set_mode((450, 400))
        pygame.display.set_caption("Freecell")
        return screen

    def create_foundation(self):
        """Create foundation spaces on the left side of the screen."""
        foundations = []
        for i in range(4):
            x = BUFFER_SIZE + (CARD_WIDTH + BUFFER_SIZE) * i
            y = BUFFER_SIZE
            space = Space(self._screen, x, y)
            foundations.append(space)
        return foundations

    def create_free(self):
        """Create free cells on the right side of the screen."""
        free_cells = []
        for i in range(4):
            x = self._screen.get_width() - (i + 1) * (BUFFER_SIZE + CARD_WIDTH)
            y = BUFFER_SIZE
            space = Space(self._screen, x, y)
            free_cells.append(space)
        return free_cells

    def create_tableau(self):
        """Create tableau spaces."""
        center = self._screen.get_width() // 2
        x = int(center - (3.5 * BUFFER_SIZE + 4 * CARD_WIDTH))
        y = 120
        tableau = []
        for _ in range(8):
            space = Tableau(self._screen, x, y)
            tableau.append(space)
            x += BUFFER_SIZE + CARD_WIDTH
        return tableau

    def draw(self):
        """Draw the game screen."""
        self._screen.fill(BG_COLOR)  # Reset screen
        self.draw_board()
        self.draw_cards()
        pygame.display.update()

    def draw_board(self):
        """Draw the board and the spaces."""
        space_collections = [self._foundation, self._free_cells, self._tableau]
        for space_collection in space_collections:
            for space in space_collection:
                pygame.draw.rect(self._screen, SLOT_COLOR, space.rectangle)

    def draw_cards(self):
        """Draw the cards onto the game."""
        for column in self._tableau:
            column.draw_cards()
        if self._held_card:
            self._held_card.draw(self._screen)

    def get_card_at_position(self, pos: tuple[int, int]):
        """Get the topmost card at a position, if it exists."""
        for column in self._tableau:
            card = column.get_card_at_position(pos)
            if card:
                return card

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        elif pygame.mouse.get_pressed()[0]:
            self.handle_mouse_down()
        elif event.type == pygame.MOUSEBUTTONUP:
            self.handle_mouse_up()

    def handle_mouse_down(self):
        """Handle if the player clicked a card."""
        cursor_pos = pygame.mouse.get_pos()
        if not self._held_card:  # If the player isn't already moving a card
            card = self.get_card_at_position(cursor_pos)
            if card:
                self._held_card = card
                self._held_card.center_on_point(cursor_pos)
        else:
            self._held_card.center_on_point(cursor_pos)

    def handle_mouse_up(self):
        """If the player releases the mouse."""
        if self._held_card:
            self._held_card.return_to_base()
            self._held_card = None

    def place_cards(self):
        """Shuffle cards into the tableau columns."""
        random.shuffle(self._cards)
        column = 0
        for card in self._cards:
            self._tableau[column].add_card(card)
            if column < 7:
                column += 1
            else:
                column = 0

    def run(self):
        """Run game until close."""
        while self._running:
            self.draw()
            for event in pygame.event.get():
                self.handle_event(event)


if __name__ == "__main__":
    game = Game()
    game.run()
