
import pygame
import sys
import time

# --- Constants ---
# Screen dimensions and cell size
CELL_SIZE = 32 # Example: 20x13 grid for 640x416 screen with 32 cell size

# Maze definition (1 is wall, 0 is path)
MAZE_GRID_DATA = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], # 20 cells wide
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1],
    [1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]  # 13 cells high
]

GRID_WIDTH = len(MAZE_GRID_DATA[0])
GRID_HEIGHT = len(MAZE_GRID_DATA)

SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE

# Game positions
PLAYER_START_POS = (1, 1)  # Grid (x, y)
MONSTER_START_POS = (GRID_WIDTH - 2, GRID_HEIGHT - 2) # e.g., (18, 11)
MAZE_EXIT_POS = (GRID_WIDTH - 2, 1) # e.g., (18, 1)

# Colors (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)

FPS = 60

# --- Game Classes ---

class Maze:
    def __init__(self, grid_data, cell_size, wall_color, path_color, start_pos, exit_pos):
        self.grid = grid_data
        self.grid_width = len(grid_data[0])
        self.grid_height = len(grid_data)
        self.cell_size = cell_size
        self.wall_color = wall_color
        self.path_color = path_color
        self.start_pos = start_pos
        self.exit_pos = exit_pos

    def draw(self, screen):
        # Draw paths (background) implicitly by clearing screen or drawing path_color
        # Then draw walls
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                pixel_x, pixel_y = self.get_pixel_coords(x, y)
                if self.grid[y][x] == 1: # It's a wall
                    pygame.draw.rect(screen, self.wall_color, (pixel_x, pixel_y, self.cell_size, self.cell_size))
                # For path, it's typically the background, or could explicitly draw path_color if needed
                # else:
                #    pygame.draw.rect(screen, self.path_color, (pixel_x, pixel_y, self.cell_size, self.cell_size))

        # Draw start and exit points
        start_pixel_x, start_pixel_y = self.get_pixel_coords(self.start_pos[0], self.start_pos[1])
        pygame.draw.rect(screen, GREEN, (start_pixel_x, start_pixel_y, self.cell_size, self.cell_size))

        exit_pixel_x, exit_pixel_y = self.get_pixel_coords(self.exit_pos[0], self.exit_pos[1])
        pygame.draw.rect(screen, YELLOW, (exit_pixel_x, exit_pixel_y, self.cell_size, self.cell_size))

    def is_wall(self, grid_x, grid_y):
        if not (0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height):
            return True # Out of bounds is considered a wall
        return self.grid[grid_y][grid_x] == 1

    def get_pixel_coords(self, grid_x, grid_y):
        return grid_x * self.cell_size, grid_y * self.cell_size

    def get_grid_coords(self, pixel_x, pixel_y):
        return pixel_x // self.cell_size, pixel_y // self.cell_size


class Player:
    def __init__(self, start_grid_x, start_grid_y, cell_size, color):
        self.size = cell_size
        self.color = color
        self.speed = 1 # Moves 1 cell per input
        self.set_position(start_grid_x, start_grid_y)

    def set_position(self, grid_x, grid_y):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.pixel_x = self.grid_x * self.size
        self.pixel_y = self.grid_y * self.size

    def move(self, dx, dy, maze):
        new_grid_x = self.grid_x + dx
        new_grid_y = self.grid_y + dy
        if not maze.is_wall(new_grid_x, new_grid_y):
            self.set_position(new_grid_x, new_grid_y)

    def update(self, maze, input_direction):
        if input_direction:
            self.move(input_direction[0], input_direction[1], maze)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.pixel_x, self.pixel_y, self.size, self.size))

    def get_rect(self):
        return pygame.Rect(self.pixel_x, self.pixel_y, self.size, self.size)


class Monster:
    def __init__(self, start_grid_x, start_grid_y, cell_size, color, frames_per_move):
        self.size = cell_size
        self.color = color
        self.frames_per_move = frames_per_move
        self.move_timer = 0
        self.set_position(start_grid_x, start_grid_y)

    def set_position(self, grid_x, grid_y):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.pixel_x = self.grid_x * self.size
        self.pixel_y = self.grid_y * self.size

    def move_towards_player(self, player_grid_x, player_grid_y, maze):
        dx_to_player = player_grid_x - self.grid_x
        dy_to_player = player_grid_y - self.grid_y

        # Determine primary and secondary movement directions
        move_x, move_y = 0, 0
        preferred_axis = None

        if abs(dx_to_player) > abs(dy_to_player):
            preferred_axis = 'x'
            move_x = 1 if dx_to_player > 0 else -1
        else: # This covers abs(dy_to_player) >= abs(dx_to_player)
            preferred_axis = 'y'
            move_y = 1 if dy_to_player > 0 else -1

        # Attempt to move along the primary axis
        new_grid_x_primary = self.grid_x + move_x
        new_grid_y_primary = self.grid_y + move_y

        if not maze.is_wall(new_grid_x_primary, new_grid_y_primary):
            self.set_position(new_grid_x_primary, new_grid_y_primary)
            return

        # If primary axis is blocked, attempt to move along the secondary axis
        if preferred_axis == 'x':
            move_y = 1 if dy_to_player > 0 else -1
            if dy_to_player == 0: # If player is on same y, try up/down to get around block
                if not maze.is_wall(self.grid_x, self.grid_y - 1): move_y = -1
                elif not maze.is_wall(self.grid_x, self.grid_y + 1): move_y = 1
                else: move_y = 0 # Cannot move vertically either
            new_grid_y_secondary = self.grid_y + move_y
            if not maze.is_wall(self.grid_x, new_grid_y_secondary):
                self.set_position(self.grid_x, new_grid_y_secondary)
        else: # preferred_axis == 'y'
            move_x = 1 if dx_to_player > 0 else -1
            if dx_to_player == 0: # If player is on same x, try left/right to get around block
                if not maze.is_wall(self.grid_x - 1, self.grid_y): move_x = -1
                elif not maze.is_wall(self.grid_x + 1, self.grid_y): move_x = 1
                else: move_x = 0 # Cannot move horizontally either
            new_grid_x_secondary = self.grid_x + move_x
            if not maze.is_wall(new_grid_x_secondary, self.grid_y):
                self.set_position(new_grid_x_secondary, self.grid_y)

    def update(self, player_grid_x, player_grid_y, maze):
        self.move_timer += 1
        if self.move_timer >= self.frames_per_move:
            self.move_towards_player(player_grid_x, player_grid_y, maze)
            self.move_timer = 0

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.pixel_x, self.pixel_y, self.size, self.size))

    def get_rect(self):
        return pygame.Rect(self.pixel_x, self.pixel_y, self.size, self.size)


class GameManager:
    def __init__(self, width, height, cell_size):
        pygame.init()
        pygame.font.init()

        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Maze Runner: The Hunter's Chase")
        self.clock = pygame.time.Clock()

        self.font = pygame.font.Font(None, 48) # Default font, size 48
        self.small_font = pygame.font.Font(None, 36) # Default font, size 36

        self.maze = Maze(MAZE_GRID_DATA, self.cell_size, GRAY, BLACK, PLAYER_START_POS, MAZE_EXIT_POS)
        self.player = Player(PLAYER_START_POS[0], PLAYER_START_POS[1], self.cell_size, BLUE)
        self.monster = Monster(MONSTER_START_POS[0], MONSTER_START_POS[1], self.cell_size, RED, frames_per_move=30) # Monster moves every 30 frames

        self.game_state = "MENU" # "MENU", "PLAYING", "GAME_OVER", "WIN", "QUIT"
        self.start_time = 0.0
        self.elapsed_time = 0

        self.player_input_direction = None # Stores (dx, dy) for player movement this frame

    def reset_game(self):
        self.player.set_position(PLAYER_START_POS[0], PLAYER_START_POS[1])
        self.monster.set_position(MONSTER_START_POS[0], MONSTER_START_POS[1])
        self.monster.move_timer = 0 # Reset monster's internal timer
        self.start_time = time.time()
        self.elapsed_time = 0
        self.game_state = "PLAYING"
        self.player_input_direction = None

    def handle_events(self):
        self.player_input_direction = None # Reset input for current frame

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_state = "QUIT"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game_state = "QUIT"
                
                if self.game_state == "MENU":
                    if event.key == pygame.K_SPACE:
                        self.reset_game()
                elif self.game_state == "PLAYING":
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.player_input_direction = (0, -1)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.player_input_direction = (0, 1)
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.player_input_direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.player_input_direction = (1, 0)
                elif self.game_state in ["WIN", "GAME_OVER"]:
                    if event.key == pygame.K_r:
                        self.reset_game()

    def update(self):
        if self.game_state == "PLAYING":
            self.player.update(self.maze, self.player_input_direction)
            self.monster.update(self.player.grid_x, self.player.grid_y, self.maze)

            # Update elapsed time
            self.elapsed_time = int(time.time() - self.start_time)

            # Check win condition
            if self.player.grid_x == self.maze.exit_pos[0] and self.player.grid_y == self.maze.exit_pos[1]:
                self.game_state = "WIN"

            # Check lose condition (monster catches player)
            if self.player.grid_x == self.monster.grid_x and self.player.grid_y == self.monster.grid_y:
                self.game_state = "GAME_OVER"

    def draw_text(self, text, size, color, x, y, center=False):
        font = pygame.font.Font(None, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        self.screen.blit(text_surface, text_rect)

    def draw(self):
        self.screen.fill(BLACK) # Fill screen with path_color (or background)

        self.maze.draw(self.screen)

        if self.game_state == "PLAYING" or self.game_state == "GAME_OVER" or self.game_state == "WIN":
            self.player.draw(self.screen)
            self.monster.draw(self.screen)
            # Draw elapsed time
            self.draw_text(f"Time: {self.elapsed_time}s", 30, WHITE, 10, 10)

        if self.game_state == "MENU":
            self.draw_text("Maze Runner: The Hunter's Chase", 50, WHITE, self.width // 2, self.height // 2 - 50, center=True)
            self.draw_text("Press SPACE to Start", 36, GREEN, self.width // 2, self.height // 2 + 20, center=True)
            self.draw_text("Press ESC to Quit", 24, WHITE, self.width // 2, self.height // 2 + 70, center=True)
        elif self.game_state == "GAME_OVER":
            self.draw_text("GAME OVER!", 60, RED, self.width // 2, self.height // 2 - 50, center=True)
            self.draw_text(f"You lasted {self.elapsed_time} seconds!", 40, WHITE, self.width // 2, self.height // 2, center=True)
            self.draw_text("Press R to Restart", 36, GREEN, self.width // 2, self.height // 2 + 50, center=True)
        elif self.game_state == "WIN":
            self.draw_text("YOU ESCAPED!", 60, YELLOW, self.width // 2, self.height // 2 - 50, center=True)
            self.draw_text(f"Time: {self.elapsed_time} seconds", 40, WHITE, self.width // 2, self.height // 2, center=True)
            self.draw_text("Press R to Play Again", 36, GREEN, self.width // 2, self.height // 2 + 50, center=True)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            self.handle_events()
            self.update()
            self.draw()

            self.clock.tick(FPS)

            if self.game_state == "QUIT":
                running = False

        pygame.quit()
        sys.exit()

# --- Main Game Execution ---
if __name__ == "__main__":
    game_manager = GameManager(SCREEN_WIDTH, SCREEN_HEIGHT, CELL_SIZE)
    game_manager.run()
