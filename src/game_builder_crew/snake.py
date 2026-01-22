
import pygame
import random
import sys

# 1. Technical Specification (Pygame)
# 3.1. Display & Window
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Colors
DARK_GREY = (50, 50, 50)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

# 3.4. Timing
FPS = 15
SNAKE_SPEED_MS = 150

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Game States
START_SCREEN = "START_SCREEN"
PLAYING = "PLAYING"
GAME_OVER = "GAME_OVER"

# 4.1. Snake Class
class Snake:
    def __init__(self):
        # Default: 3 segments long, starting near screen center, moving right.
        # Screen center grid: (GRID_WIDTH // 2, GRID_HEIGHT // 2)
        # For 3 segments moving right, head at (15, 12), body at (14, 12), (13, 12)
        self.body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2),
                     (GRID_WIDTH // 2 - 1, GRID_HEIGHT // 2),
                     (GRID_WIDTH // 2 - 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.color = GREEN
        self.grow_pending = False

    def move(self):
        # Calculates new head position based on direction.
        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction
        # CRITICAL FIX: The original code used modulo for wrapping here.
        # The design document states that wall collision should end the game.
        # This line is changed to calculate the new head position directly,
        # allowing the Game class to detect out-of-bounds collisions.
        new_head = (head_x + dir_x, head_y + dir_y)

        self.body.insert(0, new_head) # Inserts new head at body[0].

        # If grow_pending is False, removes the last segment (body.pop()).
        if not self.grow_pending:
            self.body.pop()
        else:
            # Resets grow_pending to False.
            self.grow_pending = False

    def change_direction(self, new_direction):
        # Updates self.direction to new_direction.
        # Must include logic to prevent immediate 180-degree turns.
        if (self.direction == UP and new_direction == DOWN) or \
           (self.direction == DOWN and new_direction == UP) or \
           (self.direction == LEFT and new_direction == RIGHT) or \
           (self.direction == RIGHT and new_direction == LEFT):
            return  # Prevent 180-degree turn
        self.direction = new_direction

    def draw(self, surface):
        # Draws each segment of the snake as a filled rectangle.
        for segment in self.body:
            x, y = segment
            pygame.draw.rect(surface, self.color, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

    def get_head_position(self):
        # Returns the (x, y) tuple of the snake's head.
        return self.body[0]

    def check_collision_self(self):
        # Returns True if self.get_head_position() is in self.body[1:], False otherwise.
        return self.body[0] in self.body[1:]

    def reset(self):
        # Resets the snake to its initial state (position, length, direction).
        self.body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2),
                     (GRID_WIDTH // 2 - 1, GRID_HEIGHT // 2),
                     (GRID_WIDTH // 2 - 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.grow_pending = False

# 4.2. Food Class
class Food:
    def __init__(self):
        self.position = (0, 0) # Placeholder, will be randomized by game
        self.color = RED

    def randomize_position(self, occupied_positions):
        # Generates a new random (x, y) grid coordinate within screen bounds.
        # Ensures the new position is not present in occupied_positions.
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            new_position = (x, y)
            if new_position not in occupied_positions:
                self.position = new_position
                break

    def draw(self, surface):
        # Draws the food item as a filled rectangle.
        x, y = self.position
        pygame.draw.rect(surface, self.color, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

    def get_position(self):
        # Returns the (x, y) tuple of the food's position.
        return self.position

# 4.3. Game Class
class Game:
    def __init__(self):
        # Initializes Pygame modules.
        pygame.init()

        # Sets up display, caption.
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("PySnake")

        # Creates Snake and Food instances.
        self.snake = Snake()
        self.food = Food()
        self.food.randomize_position(self.snake.body) # Initial food position

        # Initializes score = 0, game_state = START_SCREEN.
        self.score = 0
        self.game_state = START_SCREEN

        # Loads fonts.
        # Default font sizes, as not specified in document.
        self.font_large = pygame.font.Font(None, 48) # For titles
        self.font_medium = pygame.font.Font(None, 24) # For score and messages

        # Sets last_move_time to 0.
        self.last_move_time = 0

        # Pygame time.Clock object.
        self.clock = pygame.time.Clock()

    def handle_input(self, event):
        # Processes Pygame event objects.
        if event.type == pygame.QUIT:
            return False # Signal to exit game

        if event.type == pygame.KEYDOWN:
            # Handles state transitions
            if self.game_state == START_SCREEN or self.game_state == GAME_OVER:
                self.reset_game()
                self.game_state = PLAYING
                self.last_move_time = pygame.time.get_ticks() # Reset timer for new game
                return True # Event handled, continue game loop

            # Updates snake.direction based on arrow keys. (Only if PLAYING)
            if self.game_state == PLAYING:
                if event.key == pygame.K_UP:
                    self.snake.change_direction(UP)
                elif event.key == pygame.K_DOWN:
                    self.snake.change_direction(DOWN)
                elif event.key == pygame.K_LEFT:
                    self.snake.change_direction(LEFT)
                elif event.key == pygame.K_RIGHT:
                    self.snake.change_direction(RIGHT)
        return True # Continue game loop

    def update(self):
        # If game_state == PLAYING:
        if self.game_state == PLAYING:
            current_time = pygame.time.get_ticks()
            # If current_time - self.last_move_time > SNAKE_SPEED_MS:
            if current_time - self.last_move_time > SNAKE_SPEED_MS:
                self.last_move_time = current_time
                self.snake.move() # Call self.snake.move().

                # Collision Detection:
                head_x, head_y = self.snake.get_head_position()

                # Check snake.get_head_position() against SCREEN_WIDTH/SCREEN_HEIGHT boundaries.
                wall_collision = not (0 <= head_x < GRID_WIDTH and 0 <= head_y < GRID_HEIGHT)

                # Check snake.check_collision_self().
                self_collision = self.snake.check_collision_self()

                # If any collision, set self.game_state = GAME_OVER.
                if wall_collision or self_collision:
                    self.game_state = GAME_OVER

                # Food Consumption:
                # If snake.get_head_position() == food.get_position():
                if self.snake.get_head_position() == self.food.get_position():
                    self.snake.grow_pending = True # Set snake.grow_pending = True.
                    self.food.randomize_position(self.snake.body) # Call food.randomize_position(self.snake.body).
                    self.score += 10 # Increment self.score by 10.
                    # (Optional: Increase SNAKE_SPEED_MS slightly here for progressive difficulty) - Not implemented as per instructions.

    def draw_text_centered(self, surface, text, font, color, y_offset=0):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + y_offset))
        surface.blit(text_surface, text_rect)

    def draw(self):
        # Fills the screen with the background color.
        self.screen.fill(DARK_GREY)

        # Drawing based on game_state
        if self.game_state == PLAYING:
            self.snake.draw(self.screen) # Calls self.snake.draw(self.screen).
            self.food.draw(self.screen) # Calls self.food.draw(self.screen).
            # Draws the current score text on the screen (e.g., top-left).
            score_text = self.font_medium.render(f"Score: {self.score}", True, WHITE)
            self.screen.blit(score_text, (10, 10))
        elif self.game_state == START_SCREEN:
            # Draws "PySnake" title and "Press any key to start" message centered.
            self.draw_text_centered(self.screen, "PySnake", self.font_large, WHITE, -50)
            self.draw_text_centered(self.screen, "Press any key to start", self.font_medium, WHITE, 20)
        elif self.game_state == GAME_OVER:
            # Draws "Game Over!", final score, and "Press any key to restart" message centered.
            self.draw_text_centered(self.screen, "Game Over!", self.font_large, WHITE, -70)
            self.draw_text_centered(self.screen, f"Final Score: {self.score}", self.font_medium, WHITE, -20)
            self.draw_text_centered(self.screen, "Press any key to restart", self.font_medium, WHITE, 30)

        pygame.display.flip() # pygame.display.flip().

    def reset_game(self):
        # Calls self.snake.reset().
        self.snake.reset()
        # Calls self.food.randomize_position(self.snake.body).
        self.food.randomize_position(self.snake.body)
        # Sets self.score = 0.
        self.score = 0
        # Sets self.game_state = PLAYING.
        self.game_state = PLAYING
        # Resets self.last_move_time = pygame.time.get_ticks().
        self.last_move_time = pygame.time.get_ticks()

    def run(self):
        # The main game loop, handles running boolean.
        running = True
        while running:
            for event in pygame.event.get():
                # Calls handle_input
                running = self.handle_input(event)
                if not running:
                    break # Exit inner loop if game quits

            if not running:
                break # Exit outer loop if game quits

            self.update() # Calls update
            self.draw() # Calls draw
            self.clock.tick(FPS) # pygame.time.Clock().tick(FPS) to cap frame rate.

        pygame.quit() # pygame.quit() when running is False.
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
