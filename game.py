from random import shuffle
import time
import pygame
from card import create_deck
from constants import BUFFER_SIZE, CARD_WIDTH
from space import Space, Foundation, Tableau
from stack import MoveStack

pygame.init()

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
        self._won = False
        self._win_text = self.create_win_text()
        self._event_methods = {
            pygame.QUIT: self.quit,
            pygame.MOUSEBUTTONDOWN: self.handle_mouse_down,
            pygame.MOUSEBUTTONUP: self.handle_mouse_up,
            pygame.K_q: self.quit,
            pygame.K_z: self.undo,
            pygame.K_a: self.handle_a_key,
        }

    @property
    def empty_spaces(self):
        """Return amount of empty spaces in tableau and free cells."""
        valid_spaces = self._tableau + self._free_cells  # Don't count founds.
        whether_empty = [space.is_empty for space in valid_spaces]
        return sum(whether_empty)  # Sum of bool list is amount of True values.

    @property
    def has_won(self):
        """Check if game has been won."""
        # Since there are 8 tabs and 4 freecells, an empty_space count of 12
        # means they're all empty.
        return self.empty_spaces == 12

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
        Priority is Foundations, (sorted) Tableau, then Free cells."""
        spaces = [self._foundation, self.sorted_tableau, self._free_cells]
        for space_list in spaces:
            space = self.get_valid_space(stack, space_list)
            if space:
                return space
        return None

    def auto_foundation(self):
        """Try to move all currently exposed cards to foundation.

        returns:
            bool: Whether or not a move was made.
        """
        moves_made = False
        for space in self._tableau + self._free_cells:
            if self.try_move_to_found(space):
                moves_made = True
        return moves_made

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
            # Shift x pos over one card and one buffer.
            x_pos += CARD_WIDTH + BUFFER_SIZE
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

    def create_win_text(self):
        """create win message in center of screen."""
        font = pygame.font.Font("freesansbold.ttf", 16)
        message = "Congratulations! Press q to quit."
        text = font.render(message, True, (255, 255, 0))
        return text

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
        if self._won:
            self.draw_win_text()
        pygame.display.update()

    def draw_win_text(self):
        """Draw the winning message."""
        # Center text rectangle on screen center.
        text_rect = self._win_text.get_rect()
        text_rect.center = self._screen.get_rect().center
        self._screen.blit(self._win_text, text_rect)

    def get_mouse_target(self):
        """Get target based off mouse position."""
        cursor_pos = pygame.mouse.get_pos()
        for space in self.spaces:
            target = space.check_for_target(cursor_pos)
            if target:
                return target
        return None

    def get_release_dest(self):
        """Check to see if there is a valid space to move held stack to."""
        if not self._held_stack:
            raise Exception("Method get_release_dest called with empty hand.")
        for space in self.spaces:
            if space.is_valid_drop_point(self._held_stack, self.empty_spaces):
                return space
        return None

    def get_valid_space(self, stack: "MoveStack", space_list: list["Space"]):
        """Check for a valid space in the given space list."""
        for space in space_list:
            if space == stack.home_space:
                continue
            if space.valid_dest(stack, self.empty_spaces):
                return space
        return None

    def handle_a_key(self):
        """Move all exposed cards to foundations if possible."""
        moves_made = True
        while moves_made:  # Continue until no more moves are made.
            moves_made = self.auto_foundation()

    def handle_click_release(self):
        """Handle release from a click rather than a hold."""
        if not self._held_stack:
            return
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
        if event_key not in self._event_methods:
            return
        method = self._event_methods[event_key]
        method()

    def handle_hold_release(self):
        """Handle mouse release from being held down."""
        if not self._held_stack:
            return
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

    def try_move_to_found(self, space: "Space"):
        """Try moving top card in space to founds and return if successful."""
        if space.is_empty:
            return False
        top_stack = space.make_sub_stack(space.top_card)
        if not top_stack:
            raise Exception(f"Failed to make top stack from {space}.")
        destination = self.get_valid_space(top_stack, self._foundation)
        if not destination:
            top_stack.go_home()
            return False
        self.make_move(top_stack, destination)
        return True

    def undo(self):
        """Undo last made move."""
        if not self._moves:
            return
        last_move = self._moves[-1]
        undo_stack = last_move["dest"].make_sub_stack(last_move["card"])
        undo_stack.make_move(last_move["source"])
        self._moves.pop()  # Remove undone move from moves.

    def update(self):
        """Update for new tick."""
        if self.has_won:
            self._won = True
        if self._held_stack:
            self._held_stack.drag(pygame.mouse.get_pos())


if __name__ == "__main__":
    game = Game()
    game.run()
