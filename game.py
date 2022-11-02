from random import shuffle
from typing import Optional
import time
import pygame
from space import Space, Foundation, Tableau, FreeCell
from cards import Card, create_deck
from constants import CARD_WIDTH, BUFFER_SIZE


BG_COLOR = "#35654d"
SLOT_COLOR = "#1e4632"

# How close clicks have to be in seconds to count as double
DOUBLECLICKTIME = 0.5


class Game:
    """Game of freecell."""

    def __init__(self):
        """Start game."""
        self._screen = self.create_screen()
        self._foundation, self._found_region = self.create_foundation()
        self._free_cells, self._free_region = self.create_free_cells()
        self._tableau, self._tab_region = self.create_tableau()
        self._deck = create_deck()
        self.deal_cards()
        self._held_card: Optional["Card"] = None
        self._running = True
        self._last_click_time = time.time()
        self._last_target = None
        self._moves: list[dict] = []

    @property
    def spaces(self):
        return self._foundation + self._free_cells + self._tableau

    def check_click_type(self, target):
        """Check if a click on a target would be single or double."""
        click_time = time.time()
        time_between = click_time - self._last_click_time
        # Needs to be on the same target to count
        if time_between <= DOUBLECLICKTIME and target == self._last_target:
            return "double"
        return "single"

    def check_release_destination(self, card: "Card"):
        """Check if card can be released into any space and return space."""
        stack_base = card.stack_base
        for space in self.spaces:
            # Keep card from trying to move to top of its own stack.
            if space == stack_base:
                continue
            dest = space.get_valid_dest(card)
            if dest and card.in_range(dest):
                return dest
        return None

    def create_foundation(self):
        """Create foundation spaces and region on left side of the screen."""
        foundations: list[Space] = []
        x = BUFFER_SIZE
        y = BUFFER_SIZE
        for _ in range(4):
            space = Foundation(x, y)
            foundations.append(space)
            x += BUFFER_SIZE + CARD_WIDTH
        region = self.create_region(foundations)
        return foundations, region

    def create_free_cells(self):
        """Create free cells on the right side of the screen."""
        free_cells = []
        for i in range(4):
            x = self._screen.get_width() - (i + 1) * (BUFFER_SIZE + CARD_WIDTH)
            y = BUFFER_SIZE
            space = FreeCell(x, y)
            free_cells.append(space)
        free_cells.reverse()  # So the list goes left to right.
        region = self.create_region(free_cells)
        return free_cells, region

    def create_region(self, space_list: list[Space]):
        """Create region for list of spaces. Not for tableau."""
        x1, y1 = space_list[0].rect.topleft
        x2, y2 = space_list[-1].rect.bottomright
        width = x2 - x1
        height = y2 - y1
        return pygame.Rect(x1, y1, width, height)

    def create_screen(self):
        """Create main window for the game."""
        screen = pygame.display.set_mode((450, 450))
        pygame.display.set_caption("Freecell")
        return screen

    def create_tableau(self):
        """Create tableau spaces and region."""
        center = self._screen.get_rect().centerx
        x = int(center - (3.5 * BUFFER_SIZE + 4 * CARD_WIDTH))
        y = 120
        tableau = []
        for _ in range(8):
            space = Tableau(x, y)
            tableau.append(space)
            x += BUFFER_SIZE + CARD_WIDTH
        # Since tableau counts cards, entire main area of screen is region.
        region_height = self._screen.get_height() - y
        region = pygame.Rect(0, y, self._screen.get_width(), region_height)
        return tableau, region

    def deal_cards(self):
        """Deal all cards to the tableau"""
        shuffle(self._deck)
        column = 0  # To iterate through columns
        for card in self._deck:
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

    def get_mouse_target(self, cursor_pos):
        """Check to see if the mouse clicked on anything."""
        spaces = [self._foundation, self._free_cells, self._tableau]
        regions = [self._found_region, self._free_region, self._tab_region]
        for space_list, region in zip(spaces, regions):
            if region.collidepoint(cursor_pos):
                for space in space_list:
                    target = space.check_for_target(cursor_pos)
                    if target:
                        return target
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

    def handle_mouse_down(self):
        """Handle if the player clicks down on the mouse."""
        cursor_pos = pygame.mouse.get_pos()
        target = self.get_mouse_target(cursor_pos)
        if target:
            click_type = self.check_click_type(target)
            if click_type == "single":
                self.handle_single_click(target)
            elif click_type == "double":
                self.handle_double_click(target)

    def handle_single_click(self, target):
        """Pick up the target."""
        if isinstance(target, Card) and target.is_valid_stack():
            self._held_card = target
            self._last_click_time = time.time()
            self._last_target = target
            target.click(pygame.mouse.get_pos())

    def handle_double_click(self, target):
        """Automove the target if it is a card."""
        if isinstance(target, Card) and target.is_valid_stack():
            # Check found first, then tab, then free cells last.
            for space in self._foundation + self._tableau + self._free_cells:
                dest = space.get_valid_dest(target)
                if dest:
                    self.make_move(target, dest)
                    return

    def handle_mouse_up(self):
        """Handle event where mouse is released."""
        if self._held_card:
            dest = self.check_release_destination(self._held_card)
            if dest:
                self.make_move(self._held_card, dest)
            self._held_card.release()
            self._held_card = None

    def make_move(self, card: "Card", space: "Space", logging=True):
        """Move card to a new space. Logging determines if it is added to move list."""
        move_dict = {"card": card, "source": card._home_space, "dest": space}
        card.switch_space(space)
        if logging:
            self._moves.append(move_dict)

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
            self.make_move(card, dest, False)  # Reverse the move w/o logging.
            self._moves.pop()  # Remove undone move.

    def update(self):
        """Update for the current frame."""
        if self._held_card:
            cursor_pos = pygame.mouse.get_pos()
            self._held_card.drag(cursor_pos)


if __name__ == "__main__":
    game = Game()
    game.run()
