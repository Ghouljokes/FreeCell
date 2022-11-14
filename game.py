from random import shuffle
from typing import Optional
import time
import pygame
from space import Space, Foundation, Tableau, FreeCell, StackSpace
from cards import Card, create_deck
from constants import CARD_WIDTH, BUFFER_SIZE


BG_COLOR = "#35654d"
SLOT_COLOR = "#1e4632"

# How close clicks have to be in seconds to count as double
CLICKRELEASETIME = 0.2


class Game:
    """Game of freecell."""

    def __init__(self):
        """Start game."""
        self._screen = self.create_screen()
        self._foundation = self.create_foundation()
        self._free_cells = self.create_free_cells()
        self._tableau = self.create_tableau()
        self.deal_cards()
        self._held_card: Optional["Card"] = None
        self._running = True
        self._last_click_time = time.time()
        self._moves: list[dict] = []

    @property
    def column_spaces(self):
        """Return top space in each column."""
        return [space.top_space for space in self._tableau]

    @property
    def empty_cells(self):
        """Get amount of empty cells to put cards in."""
        empty_cells = 0
        for space in self._free_cells + self._tableau:
            if not space.card:
                empty_cells += 1
        return empty_cells

    def auto_move(self, card):
        """Automatically try and move a card to an ideal position."""
        for space in self._foundation + self.column_spaces + self._free_cells:
            if self.valid_dest(card, space):
                self.make_move(card, space)
                return

    def check_release_type(self):
        """Check if release is from a click or a hold."""
        click_time = time.time()
        time_between = click_time - self._last_click_time
        # Needs to be on the same target to count
        if time_between <= CLICKRELEASETIME:
            return "click_release"
        else:
            return "hold_release"

    def click_card(self, target):
        """Pick up the target."""
        if isinstance(target, Card) and target.is_valid_stack():
            self._held_card = target
            target.click(pygame.mouse.get_pos())

    def create_foundation(self):
        """Create foundation spaces on left side of the screen."""
        foundations: list[Space] = []
        x = BUFFER_SIZE
        y = BUFFER_SIZE
        for _ in range(4):
            space = Foundation(x, y)
            foundations.append(space)
            x += BUFFER_SIZE + CARD_WIDTH
        return foundations

    def create_free_cells(self):
        """Create free cells on the right side of the screen."""
        free_cells = []
        for i in range(4):
            x = self._screen.get_width() - (i + 1) * (BUFFER_SIZE + CARD_WIDTH)
            y = BUFFER_SIZE
            space = FreeCell(x, y)
            free_cells.append(space)
        free_cells.reverse()  # So the list goes left to right.
        return free_cells

    def create_screen(self):
        """Create main window for the game."""
        screen = pygame.display.set_mode((450, 500))
        pygame.display.set_caption("Freecell")
        return screen

    def create_tableau(self):
        """Create tableau spaces."""
        center = self._screen.get_rect().centerx
        x = int(center - (3.5 * BUFFER_SIZE + 4 * CARD_WIDTH))
        y = 120
        tableau = []
        for _ in range(8):
            space = Tableau(x, y)
            tableau.append(space)
            x += BUFFER_SIZE + CARD_WIDTH
        return tableau

    def deal_cards(self):
        """Deal all cards to the tableau"""
        deck = create_deck()
        shuffle(deck)
        column = 0  # To iterate through columns
        for card in deck:
            self._tableau[column].stack_card(card)
            card.go_home()
            if column < len(self._tableau) - 1:
                column += 1
            else:  # Return to first column if last one was reached.
                column = 0

    def draw(self):
        """Draw everything to the screen."""
        self._screen.fill(BG_COLOR)  # Reset screen
        for space in self._foundation + self._free_cells + self._tableau:
            space.draw(self._screen)
        if self._held_card:  # Draw held card last so it is always visible.
            self._held_card.draw(self._screen)
        pygame.display.update()

    def get_mouse_target(self):
        """Check to see if the mouse clicked on anything."""
        cursor_pos = pygame.mouse.get_pos()
        spaces = self._foundation + self._free_cells + self._tableau
        for space in spaces:
            target = space.check_for_target(cursor_pos)
            if target:
                return target
        return None

    def get_release_destination(self, card: "Card"):
        """If a card would release from being held into a certain space, return space."""
        for space in self._foundation + self._free_cells + self.column_spaces:
            if card.can_drop_off(space):
                return space
        return None

    def handle_events(self):
        """Handle all player actions."""
        for event in pygame.event.get():
            self.handle_event(event)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.handle_mouse_down()
        elif event.type == pygame.MOUSEBUTTONUP:
            self.handle_mouse_up()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_z:
            self.undo()

    def handle_click_release(self):
        """Handle if the user performed a single click."""
        if self._held_card:
            self.auto_move(self._held_card)
            self._held_card.release()
            self._held_card = None

    def handle_hold_release(self):
        """Handle if user released mouse after holding."""
        if not self._held_card:
            return
        dest = self.get_release_destination(self._held_card)
        if dest and self.valid_dest(self._held_card, dest):
            self.make_move(self._held_card, dest)
        self._held_card.release()
        self._held_card = None

    def handle_mouse_down(self):
        """Handle if the player clicks down on the mouse."""
        target = self.get_mouse_target()
        self._last_click_time = time.time()
        if target:
            self.click_card(target)

    def handle_mouse_up(self):
        """Handle event where mouse is released."""
        release_type = self.check_release_type()
        if release_type == "click_release":
            self.handle_click_release()
        else:
            self.handle_hold_release()

    def make_move(self, card: "Card", space: "Space", undo=False):
        """
        Move card to a new space. Undo is for if it's undoing a move.
        Returns bool indicating if a move was successfuly made or not.
        """
        if not undo:
            # Store move so it can be undone later.
            move_dict = {
                "card": card,
                "source": card._home_space,
                "dest": space,
            }
            self._moves.append(move_dict)
        card.switch_space(space)

    def room_for_move(self, card: "Card", space: "Space"):
        """Check if there are enough spaces to move a stack."""
        available_space = self.empty_cells
        # Since moving to a card or foundation doesn't use up an empty space,
        # It counts for an extra available space to move.
        if isinstance(space, StackSpace) or isinstance(space, Foundation):
            available_space += 1
        return card.stack_size <= available_space

    def run(self):
        """Run game until it is closed."""
        while self._running:
            self.tick()

    def tick(self):
        """Handle an individual tick of the game."""
        self.draw()
        self.handle_events()
        self.update()

    def undo(self):
        """Undo the last move in the move list."""
        if self._moves:  # If any moves have been made.
            last_move = self._moves[-1]
            card, dest = last_move["card"], last_move["source"]
            self.make_move(card, dest, undo=True)  # Reverse the move.
            self._moves.pop()  # Remove undone move.

    def update(self):
        """Update for the current frame."""
        if self._held_card:
            cursor_pos = pygame.mouse.get_pos()
            self._held_card.drag(cursor_pos)

    def valid_dest(self, card: "Card", space: "Space"):
        """Return whether card can be moved to space."""
        return self.room_for_move(card, space) and space.valid_dest(card)


if __name__ == "__main__":
    game = Game()
    game.run()
