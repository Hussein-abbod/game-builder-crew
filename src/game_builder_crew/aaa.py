
import pygame
import sys

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
GREY = (100, 100, 100)
LIGHT_BLUE = (173, 216, 230) # Background color

# Player properties
PLAYER_WIDTH = 30
PLAYER_HEIGHT = 50
PLAYER_SPEED = 5
PLAYER_JUMP_POWER = -12  # Negative for upward velocity
GRAVITY = 0.5
TERMINAL_VELOCITY = 10
WALL_SLIDE_SPEED = 1.5 # How fast player slides down a wall
WALL_JUMP_X_VELOCITY = 8 # Horizontal speed when wall jumping
WALL_JUMP_Y_VELOCITY = -10 # Vertical speed when wall jumping
DASH_SPEED = 15
DASH_DURATION = 10 # Frames (approx 0.16 seconds at 60 FPS)
MAX_DASHES = 1
INITIAL_HEALTH = 3
INVULNERABILITY_DURATION = 90 # Frames (1.5 seconds at 60 FPS)

# --- Level Data ---
LEVEL_DATA = [
    # Level 1
    {
        "player_start": (50, 500),
        "platforms": [
            (0, 550, 800, 50),  # Ground
            (150, 400, 100, 20),
            (300, 300, 150, 20),
            (500, 200, 80, 20),
            (700, 100, 50, 20), # Wall for wall jump
            (650, 350, 100, 20)
        ],
        "hazards": [
            (200, 530, 50, 20), # Spikes on ground
            (400, 280, 50, 20) # Spikes on platform
        ],
        "collectables": [
            (170, 380, 'coin'),
            (350, 280, 'coin'),
            (530, 180, 'coin')
        ],
        "exit_gate": (700, 50, 50, 50)
    },
    # Level 2
    {
        "player_start": (50, 500),
        "platforms": [
            (0, 550, 800, 50), # Ground
            (100, 450, 100, 20),
            (250, 350, 150, 20),
            (450, 250, 100, 20),
            (600, 150, 80, 20),
            (750, 0, 50, 600) # Right wall
        ],
        "hazards": [
            (120, 430, 30, 20),
            (300, 330, 50, 20),
            (500, 230, 40, 20)
        ],
        "collectables": [
            (130, 430, 'coin'),
            (320, 330, 'coin'),
            (520, 230, 'coin'),
            (630, 130, 'coin')
        ],
        "exit_gate": (620, 100, 50, 50)
    },
    # Level 3 (Win Level)
    {
        "player_start": (50, 500),
        "platforms": [
            (0, 550, 800, 50),  # Ground
            (100, 400, 100, 20),
            (300, 300, 150, 20),
            (500, 200, 80, 20),
            (650, 100, 100, 20) # Final platform
        ],
        "hazards": [
            (120, 380, 30, 20),
            (350, 280, 50, 20),
            (520, 180, 40, 20)
        ],
        "collectables": [
            (130, 380, 'coin'),
            (360, 280, 'coin'),
            (530, 180, 'coin'),
            (700, 80, 'coin')
        ],
        "exit_gate": (700, 50, 50, 50) # Exit on final platform
    }
]


# --- Classes ---

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([PLAYER_WIDTH, PLAYER_HEIGHT])
        self.image.fill(BLUE) # Placeholder player sprite
        self.rect = self.image.get_rect(topleft=(x, y))

        self.start_pos = (x, y) # For respawn

        self.velocity_x = 0
        self.velocity_y = 0
        self.speed = PLAYER_SPEED
        self.jump_power = PLAYER_JUMP_POWER
        self.gravity = GRAVITY

        self.on_ground = False
        self.facing_right = True

        self.health = INITIAL_HEALTH
        self.score = 0

        self.jumps_left = 1 # For potential double jump, currently 1 for standard jump
        self.dashes_left = MAX_DASHES

        self.wall_sliding = False
        self.wall_jump_direction = 0 # -1 for left wall, 1 for right wall

        self.is_dashing = False
        self.dash_timer = 0

        self.invulnerable_timer = 0
        self.game_manager = None # Reference to GameManager, set after creation

    def update(self, platforms, hazards, collectables, exit_gate):
        # Update invulnerability
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1
            # Simple visual feedback for invulnerability (flash)
            if self.invulnerable_timer % 10 < 5:
                self.image.fill(WHITE)
            else:
                self.image.fill(BLUE)
        else:
            self.image.fill(BLUE) # Ensure correct color when not invulnerable

        # Apply gravity
        self.velocity_y += self.gravity
        if self.velocity_y > TERMINAL_VELOCITY:
            self.velocity_y = TERMINAL_VELOCITY

        # Handle dash movement
        if self.is_dashing:
            if self.dash_timer > 0:
                self.dash_timer -= 1
                # Velocity already set by dash() method, just maintain it
            else:
                self.is_dashing = False
                self.velocity_x = 0 # Stop dashing, revert to no horizontal movement
                # Revert to normal movement based on current input keys
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    self.velocity_x = -self.speed
                    self.facing_right = False # Update facing direction
                elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    self.velocity_x = self.speed
                    self.facing_right = True # Update facing direction


        # Horizontal movement
        self.rect.x += self.velocity_x

        # Horizontal collision detection
        self.wall_sliding = False # Reset wall sliding status
        for platform in pygame.sprite.spritecollide(self, platforms, False):
            if self.velocity_x > 0: # Moving right, hit left side of platform
                self.rect.right = platform.rect.left
                if self.velocity_y > 0 and not self.on_ground: # Sliding down a wall
                    self.wall_sliding = True
                    self.wall_jump_direction = -1 # Wall on player's right
            elif self.velocity_x < 0: # Moving left, hit right side of platform
                self.rect.left = platform.rect.right
                if self.velocity_y > 0 and not self.on_ground: # Sliding down a wall
                    self.wall_sliding = True
                    self.wall_jump_direction = 1 # Wall on player's left
            self.velocity_x = 0 # Stop horizontal movement on collision

        # Vertical movement
        self.rect.y += self.velocity_y

        # Vertical collision detection
        was_on_ground = self.on_ground
        self.on_ground = False
        for platform in pygame.sprite.spritecollide(self, platforms, False):
            if self.velocity_y > 0: # Falling, hit top of platform
                self.rect.bottom = platform.rect.top
                self.velocity_y = 0
                self.on_ground = True
            elif self.velocity_y < 0: # Jumping, hit bottom of platform
                self.rect.top = platform.rect.bottom
                self.velocity_y = 0

        # Reset abilities if just landed
        if self.on_ground and not was_on_ground:
            self.reset_abilities()

        # If wall sliding, reduce vertical velocity and reset abilities
        if self.wall_sliding:
            self.velocity_y = min(self.velocity_y, WALL_SLIDE_SPEED)
            self.jumps_left = 1 # Can wall jump even if normal jump used
            self.dashes_left = MAX_DASHES # Can dash off wall


        # Hazard collision
        if self.invulnerable_timer == 0:
            for hazard in pygame.sprite.spritecollide(self, hazards, False):
                hazard.on_hit(self)

        # Collectable collision
        for collectable in pygame.sprite.spritecollide(self, collectables, True): # Kill collectable on collision
            collectable.on_collect(self)

        # Exit Gate collision
        if pygame.sprite.collide_rect(self, exit_gate):
            exit_gate.on_trigger() # Call on_trigger method of ExitGate

        # Check for game over (after all other updates potentially affecting health)
        if self.health <= 0:
            self.game_manager.game_state = 'GAME_OVER'


    def handle_input(self, keys_pressed):
        if not self.is_dashing: # Cannot change horizontal movement during dash
            if keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a]:
                self.velocity_x = -self.speed
                self.facing_right = False
            elif keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]:
                self.velocity_x = self.speed
                self.facing_right = True
            else:
                self.velocity_x = 0

    def jump(self):
        if self.on_ground and self.jumps_left > 0:
            self.velocity_y = self.jump_power
            self.on_ground = False
            self.jumps_left -= 1
        elif self.wall_sliding and self.wall_jump_direction != 0:
            self.wall_jump(self.wall_jump_direction)
            self.wall_sliding = False
            self.wall_jump_direction = 0 # Reset wall jump state

    def wall_jump(self, wall_direction):
        self.velocity_y = WALL_JUMP_Y_VELOCITY
        self.velocity_x = WALL_JUMP_X_VELOCITY * (-wall_direction) # Jump away from the wall
        self.dashes_left = MAX_DASHES # Wall jump resets dash
        self.jumps_left = 1 # Wall jump resets jump count

    def dash(self):
        if self.dashes_left > 0 and not self.is_dashing:
            self.is_dashing = True
            self.dash_timer = DASH_DURATION
            self.velocity_x = DASH_SPEED if self.facing_right else -DASH_SPEED
            self.dashes_left -= 1

    def take_damage(self, amount):
        if self.invulnerable_timer == 0:
            self.health -= amount
            self.invulnerable_timer = INVULNERABILITY_DURATION
            if self.health <= 0:
                self.game_manager.game_state = 'GAME_OVER'

    def reset_abilities(self):
        if self.on_ground:
            self.jumps_left = 1 # Reset to 1 for single jump
            self.dashes_left = MAX_DASHES

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(GREY) # Placeholder platform sprite
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Collectable(pygame.sprite.Sprite):
    def __init__(self, x, y, c_type):
        super().__init__()
        self.type = c_type
        self.value = 0
        if self.type == 'coin':
            self.image = pygame.Surface([20, 20], pygame.SRCALPHA)
            pygame.draw.circle(self.image, YELLOW, (10, 10), 10) # Placeholder coin
            self.value = 10
        elif self.type == 'heart': # Example for future expansion
            self.image = pygame.Surface([20, 20], pygame.SRCALPHA)
            pygame.draw.rect(self.image, RED, (0,5,20,10))
            pygame.draw.circle(self.image, RED, (5,5), 5)
            pygame.draw.circle(self.image, RED, (15,5), 5)
            self.value = 0 # Hearts restore health, not score
        else:
            self.image = pygame.Surface([20, 20])
            self.image.fill(ORANGE) # Generic powerup
            self.value = 0

        self.rect = self.image.get_rect(center=(x, y))

    def on_collect(self, player):
        if self.type == 'coin':
            player.score += self.value
        elif self.type == 'heart':
            player.health = min(INITIAL_HEALTH, player.health + 1) # Restore 1 health, max initial health
        # For future powerups, apply effects here
        self.kill() # Remove collectable from all sprite groups


class Hazard(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(RED) # Placeholder hazard sprite (e.g., spikes/lava)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.damage_amount = 1

    def on_hit(self, player):
        player.take_damage(self.damage_amount)

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class ExitGate(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(GREEN) # Placeholder exit gate sprite
        self.rect = self.image.get_rect(topleft=(x, y))
        self.game_manager = None # Will be set by GameManager

    def on_trigger(self):
        if self.game_manager:
            self.game_manager.next_level()

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class GameManager:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Parkour Peril")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)

        self.running = True
        self.game_state = 'PLAYING' # 'PLAYING', 'GAME_OVER', 'LEVEL_COMPLETE', 'GAME_WIN'

        self.current_level_index = 0
        self.player = None
        self.exit_gate = None # Reference to the current exit gate

        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.hazards = pygame.sprite.Group()
        self.collectables = pygame.sprite.Group()

        self.load_level(self.current_level_index)

    def reset_current_level(self):
        # Reload the current level, resetting player state and objects specific to that level.
        # load_level already resets player health and score.
        self.load_level(self.current_level_index)

    def next_level(self):
        self.current_level_index += 1
        if self.current_level_index < len(LEVEL_DATA):
            self.load_level(self.current_level_index)
            self.game_state = 'LEVEL_COMPLETE' # Transition to level complete screen
        else:
            self.game_state = 'GAME_WIN'

    def load_level(self, level_index):
        # Clear existing sprites
        self.all_sprites.empty()
        self.platforms.empty()
        self.hazards.empty()
        self.collectables.empty()

        if level_index >= len(LEVEL_DATA):
            self.game_state = 'GAME_WIN'
            return

        level = LEVEL_DATA[level_index]

        # Player
        player_x, player_y = level["player_start"]
        self.player = Player(player_x, player_y)
        self.player.game_manager = self # Give player reference to game manager
        self.player.health = INITIAL_HEALTH # Reset health on new level
        self.player.score = 0 # Reset score for the level
        self.all_sprites.add(self.player)

        # Platforms
        for p_data in level["platforms"]:
            platform = Platform(*p_data)
            self.all_sprites.add(platform)
            self.platforms.add(platform)

        # Hazards
        for h_data in level["hazards"]:
            hazard = Hazard(*h_data)
            self.all_sprites.add(hazard)
            self.hazards.add(hazard)

        # Collectables
        for c_data in level["collectables"]:
            collectable = Collectable(c_data[0], c_data[1], c_data[2])
            self.all_sprites.add(collectable)
            self.collectables.add(collectable)

        # Exit Gate
        eg_data = level["exit_gate"]
        self.exit_gate = ExitGate(*eg_data)
        self.exit_gate.game_manager = self # Give exit gate reference to game manager
        self.all_sprites.add(self.exit_gate)

        self.game_state = 'PLAYING' # Ensure game state is playing after loading

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False # For now, escape quits the game
                if event.key == pygame.K_r: # Restart current level (from PLAYING or GAME_OVER) or Continue (from LEVEL_COMPLETE)
                    if self.game_state == 'GAME_OVER' or self.game_state == 'PLAYING':
                        self.reset_current_level()
                    elif self.game_state == 'LEVEL_COMPLETE':
                        # Already called load_level in next_level(), just need to set state
                        self.game_state = 'PLAYING'
                if self.game_state == 'PLAYING':
                    if event.key == pygame.K_SPACE or event.key == pygame.K_w:
                        self.player.jump()
                    if event.key == pygame.K_LSHIFT or event.key == pygame.K_j:
                        self.player.dash()

    def update(self):
        if self.game_state == 'PLAYING':
            keys_pressed = pygame.key.get_pressed()
            self.player.handle_input(keys_pressed)
            self.player.update(self.platforms, self.hazards, self.collectables, self.exit_gate)

    def draw(self):
        self.screen.fill(LIGHT_BLUE)

        # Draw all sprites if game is playing or level complete (to show final state)
        if self.game_state in ['PLAYING', 'LEVEL_COMPLETE', 'GAME_OVER', 'GAME_WIN']:
            self.all_sprites.draw(self.screen)

        # Draw UI
        if self.player: # Ensure player exists before trying to draw UI
            health_text = self.font.render(f"Health: {self.player.health}", True, BLACK)
            score_text = self.font.render(f"Score: {self.player.score}", True, BLACK)
            level_text = self.font.render(f"Level: {self.current_level_index + 1}/{len(LEVEL_DATA)}", True, BLACK)
            self.screen.blit(health_text, (10, 10))
            self.screen.blit(score_text, (10, 40))
            self.screen.blit(level_text, (10, 70))


        if self.game_state == 'GAME_OVER':
            self.show_game_over_screen()
        elif self.game_state == 'LEVEL_COMPLETE':
            self.show_level_complete_screen()
        elif self.game_state == 'GAME_WIN':
            self.show_game_win_screen()


        pygame.display.flip()

    def show_game_over_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150)) # Semi-transparent black
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.font.render("GAME OVER", True, RED)
        restart_text = self.font.render("Press 'R' to Restart Level", True, WHITE)
        quit_text = self.font.render("Press 'Esc' to Quit", True, WHITE)

        go_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))

        self.screen.blit(game_over_text, go_rect)
        self.screen.blit(restart_text, restart_rect)
        self.screen.blit(quit_text, quit_rect)

    def show_level_complete_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150)) # Semi-transparent black
        self.screen.blit(overlay, (0, 0))

        level_complete_text = self.font.render("LEVEL COMPLETE!", True, GREEN)
        next_level_text = self.font.render("Press 'R' to Continue", True, WHITE)
        quit_text = self.font.render("Press 'Esc' to Quit", True, WHITE)

        lc_rect = level_complete_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        next_rect = next_level_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))

        self.screen.blit(level_complete_text, lc_rect)
        self.screen.blit(next_level_text, next_rect) # Corrected blit
        self.screen.blit(quit_text, quit_rect)

    def show_game_win_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150)) # Semi-transparent black
        self.screen.blit(overlay, (0, 0))

        game_win_text = self.font.render("YOU WIN! CONGRATULATIONS!", True, YELLOW)
        # Note: Current score is only for the last level. For total, scores would need to be accumulated.
        final_score_text = self.font.render(f"Final Level Score: {self.player.score}", True, WHITE)
        quit_text = self.font.render("Press 'Esc' to Quit", True, WHITE)

        gw_rect = game_win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        fs_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))

        self.screen.blit(game_win_text, gw_rect)
        self.screen.blit(fs_rect, fs_rect)
        self.screen.blit(quit_text, quit_rect)


    def run_game_loop(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = GameManager()
    game.run_game_loop()