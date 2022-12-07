from typing import TYPE_CHECKING
from random import shuffle
import time
import pygame
from card import create_deck
from constants import BUFFER_SIZE, CARD_WIDTH
from space import Space, Foundation, Tableau
from stack import MoveStack

BG_COLOR = "#35654d"

CLICKRELEASETIME = 0.2


class Game:
    """Main game object."""

    def __init__(self):
        """Set up game board."""
        self._screen = self.create_screen()
        self._foundation: list[Space] = self.create_foundations()
        self._free_cells: list[Space] = self.create_free_cells()
        self._tableau: list[Space] = self.create_tableau()
        self._held_stack: "MoveStack" | None = None
        self._last_click = time.time()
        self._moves: list[dict] = []
        self._running = True
        self._event_methods = {
            pygame.QUIT: self.quit,
            pygame.MOUSEBUTTONDOWN: self.handle_mouse_down,
            pygame.MOUSEBUTTONUP: self.handle_mouse_up,
            pygame.K_z: self.undo,
        }

    @property
    def empty_spaces(self):
        """Return amount of empty spaces in tableau and free cells."""
        empty_count = 0
        for space in self._free_cells + self._tableau:
            if space.is_empty:
                empty_count += 1
        return empty_count

    @property
    def sorted_tableau(self):
        """Return list of tableau spaces sorted so empty ones come last.
        Used for prioritizing spaces in auto_dest."""
        return sorted(self._tableau, key=lambda space: space.is_empty)

    @property
    def spaces(self):
        """Return all spaces."""
        return self._foundation + self._free_cells + self._tableau

    def auto_dest(self, stack: "MoveStack"):
        """Automatically move stack to first available space if it exists.
        Priority is Foundations, Tableau, then Free cells."""
        for space_list in [self._foundation, self.sorted_tableau, self._free_cells]:
            space = self.get_valid_space(stack, space_list)
            if space:
                return space
        return None

    def clear_hand(self):
        """Remove held stack from hand."""
        self._held_stack = None

    def click_stack(self, move_stack: "MoveStack"):
        """Click a given stack, setting it to held."""
        self._held_stack = move_stack
        move_stack.click(pygame.mouse.get_pos())

    def create_foundations(self):
        """Create foundation spaces."""
        foundations = []
        x_pos = BUFFER_SIZE
        for i in range(4):
            foundation = Foundation(x_pos, BUFFER_SIZE, i)
            foundations.append(foundation)
            x_pos += (
                CARD_WIDTH + BUFFER_SIZE
            )  # Shift x pos over one card and one buffer.
        return foundations

    def create_free_cells(self):
        """Create freecell spaces."""
        free_cells = []
        # Start from left.
        x_pos = self._screen.get_width() - (CARD_WIDTH + BUFFER_SIZE)
        for i in range(4):
            free_cell = Space(x_pos, BUFFER_SIZE, i)
            free_cells.insert(0, free_cell)
            x_pos -= CARD_WIDTH + BUFFER_SIZE
        return free_cells

    def create_screen(self):
        """Create the main game surface."""
        screen = pygame.display.set_mode((450, 500))
        pygame.display.set_caption("FreeCell")
        return screen

    def create_tableau(self):
        """Create tableau spaces."""
        center = self._screen.get_width() // 2
        # Tableau is 8 cards + 7 buffers wide. Since tableau is centered,
        # Starting x pos will be center x - half the tab width.
        x_pos = int(center - (3.5 * BUFFER_SIZE + 4 * CARD_WIDTH))
        y_pos = 120
        tableaus = []
        for i in range(8):
            tableau = Tableau(x_pos, y_pos, i)
            tableaus.append(tableau)
            x_pos += CARD_WIDTH + BUFFER_SIZE
        return tableaus

    def deal_cards(self):
        """Deal cards to the tableaus."""
        deck = create_deck()
        shuffle(deck)
        for i in range(8):
            tab = self._tableau[i]
            stack_length = 6 + (i < 4)  # First four columns are 7 cards high.
            stack = MoveStack(tab, deck[:stack_length])
            stack.go_home()
            deck = deck[stack_length:]

    def draw(self):
        """Draw game."""
        self._screen.fill(BG_COLOR)  # reset screen.
        for space in self.spaces:
            space.draw(self._screen)
        if self._held_stack:  # Draw held stack last.
            self._held_stack.draw(self._screen)
        pygame.display.update()

    def get_mouse_target(self):
        """Get target based off mouse position."""
        cursor_pos = pygame.mouse.get_pos()
        for space in self.spaces:
            target = space.check_for_target(cursor_pos)
            if target:
                return target

    def get_release_dest(self):
        """Check to see if there is a valid space to move held stack to."""
        if self._held_stack:
            for space in self.spaces:
                if space.is_valid_drop_point(self._held_stack) and self.room_for_move(
                    self._held_stack, space
                ):
                    return space
        return None

    def get_valid_space(self, stack: "MoveStack", space_list: list["Space"]):
        """Check for a valid space in the given space list."""
        for space in space_list:
            if space == stack.home_space:
                continue
            if self.room_for_move(stack, space) and space.valid_dest(stack):
                return space
        return None

    def handle_click_release(self):
        """Handle release from a click rather than a hold."""
        if self._held_stack:
            # A single click will try to automatically move a stack.
            dest = self.auto_dest(self._held_stack)
            if dest:
                self.make_move(self._held_stack, dest)
            else:
                self._held_stack.go_home()
            self.clear_hand()

    def handle_events(self):
        """Handle game events."""
        for event in pygame.event.get():
            self.handle_event(event)

    def handle_event(self, event: pygame.event.Event):
        """Take event and perform the relevant event action."""
        if event.type == pygame.KEYDOWN:
            event_key = event.key
        else:
            event_key = event.type
        if event_key in self._event_methods:
            method = self._event_methods[event_key]
            method()  # Call method.

    def handle_hold_release(self):
        """Handle mouse release from being held down."""
        if self._held_stack:
            dest = self.get_release_dest()
            if dest:
                self.make_move(self._held_stack, dest)
            else:  # If no valid location, return to original position.
                self._held_stack.go_home()
            self.clear_hand()

    def handle_mouse_down(self):
        """Check to see if user clicked something."""
        self._last_click = time.time()
        target_stack = self.get_mouse_target()
        if target_stack:
            self.click_stack(target_stack)

    def handle_mouse_up(self):
        """Determine type of mouse release and act accordingly."""
        time_between = time.time() - self._last_click
        if time_between <= CLICKRELEASETIME:
            self.handle_click_release()
        else:
            self.handle_hold_release()

    def make_move(self, stack: "MoveStack", space: "Space"):
        """Move stack over to new space and record it."""
        move_dict = stack.make_move(space)
        self._moves.append(move_dict)

    def quit(self):
        """End the game."""
        self._running = False

    def room_for_move(self, stack: "MoveStack", space: "Space"):
        """Check if there are enough empty spaces to manage a move."""
        max_stack_length = self.empty_spaces
        if stack.home_space.is_empty:
            # Don't count home space as empty since it tehnically still has the stack in it.
            max_stack_length -= 1
        if not space.is_empty:  # Moving to empty space would take up a space.
            max_stack_length += 1
        return stack.length <= max_stack_length

    def run(self):
        """Run game until close."""
        self.set_up_game()
        while self._running:
            self.tick()

    def set_up_game(self):
        """Prepare new game."""
        self.deal_cards()

    def tick(self):
        """Run a single game tick."""
        self.draw()
        self.handle_events()
        self.update()

    def undo(self):
        """Undo last made move."""
        if self._moves:  # If there are moves to undo.
            last_move = self._moves[-1]
            undo_stack = last_move["dest"]._stack.make_stack(last_move["card"])
            undo_stack.make_move(last_move["source"])
            self._moves.pop()  # Remove undone move from moves.

    def update(self):
        """Update for new tick."""
        if self._held_stack:
            self._held_stack.drag(pygame.mouse.get_pos())


if __name__ == "__main__":
    game = Game()
    game.run()
