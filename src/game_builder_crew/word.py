
import pygame
import random
import sys

# --- Constants ---
# Screen Dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0) # For typed letters
DARK_GRAY = (50, 50, 50) # Background color
LIGHT_GRAY = (200, 200, 200) # Button background color

# Game Parameters
INITIAL_LIVES = 3
INITIAL_SCORE = 0
WORD_POINTS = 10
LETTER_POINTS = 1 # Per letter in a successfully typed word

# Speed in pixels per millisecond (for frame-rate independent movement)
INITIAL_WORD_SPEED = 0.08 # e.g., 0.08 px/ms * 1000 ms/s = 80 px/s
MAX_WORD_SPEED = 0.5 # e.g., 0.5 px/ms * 1000 ms/s = 500 px/s
SPEED_INCREASE_INTERVAL_MS = 30000 # Increase speed every 30 seconds
SPEED_INCREASE_AMOUNT = 0.01 # Increase by 0.01 px/ms

# Spawn interval in milliseconds
INITIAL_SPAWN_INTERVAL_MS = 2000 # Spawn a word every 2 seconds
MIN_SPAWN_INTERVAL_MS = 500 # Minimum spawn interval
SPAWN_INTERVAL_DECREASE_AMOUNT_MS = 50
SPAWN_INTERVAL_DECREASE_TRIGGER_WORDS = 5 # Decrease interval every 5 words typed

# List of words for the game
WORD_LIST = [
    "cat", "dog", "sun", "moon", "star", "tree", "bird", "fish", "book", "pen",
    "apple", "grape", "house", "car", "cloud", "river", "ocean", "happy", "sad",
    "quick", "brown", "fox", "jumps", "over", "lazy", "water", "light", "heavy",
    "smile", "dream", "magic", "brave", "quiet", "spark", "swift", "frost", "bloom",
    "python", "pygame", "coding", "engineer", "senior", "develop", "software",
    "project", "design", "document", "keyboard", "display", "screen", "element",
    "control", "system", "program", "execute", "function", "variable", "string",
    "challenge", "solution", "algorithm", "interface", "monitor", "console",
    "terminal", "resource", "optimize", "efficiency", "security", "network",
    "database", "framework", "library", "module", "package", "version", "release",
    "feature", "bugfix", "testing", "deploy", "server", "client", "request",
    "response", "protocol", "internet", "website", "application", "desktop",
    "mobile", "tablet", "device", "hardware", "firmware", "software"
]

# --- Game States ---
GAME_STATE_MENU = "MENU"
GAME_STATE_PLAYING = "PLAYING"
GAME_STATE_GAME_OVER = "GAME_OVER"

# --- Classes ---

class FallingWord:
    """
    Represents a single word falling on the screen.
    """
    def __init__(self, text, x, y, speed, font, color_untyped, color_typed):
        self.original_text = text
        self.x = x
        self.y = y
        self.speed = speed # Pixels per millisecond
        self.font = font
        self.color_untyped = color_untyped
        self.color_typed = color_typed
        self.current_typed_index = 0

        # Calculate initial rect for bounding box and accurate drawing position
        # Use the full word to determine its total width for rect
        temp_surface = self.font.render(self.original_text, True, self.color_untyped)
        self.rect = temp_surface.get_rect(topleft=(int(self.x), int(self.y)))

    def update(self, dt, screen_height):
        """
        Moves the word down by speed * dt.
        Returns True if it hits the bottom of the screen, False otherwise.
        """
        self.y += self.speed * dt
        self.rect.y = int(self.y) # Update rect's y position

        if self.rect.bottom >= screen_height:
            return True # Word hit bottom
        return False

    def draw(self, screen):
        """
        Renders the word, drawing typed letters in one color and untyped in another.
        """
        # Render the typed part
        typed_part = self.original_text[:self.current_typed_index]
        typed_surface = self.font.render(typed_part, True, self.color_typed)
        screen.blit(typed_surface, (self.x, self.y))
        
        # Render the untyped part, positioned after the typed part
        untyped_part = self.original_text[self.current_typed_index:]
        untyped_surface = self.font.render(untyped_part, True, self.color_untyped)
        untyped_x = self.x + typed_surface.get_width() # Offset by width of typed part
        screen.blit(untyped_surface, (untyped_x, self.y))

    def check_input(self, char):
        """
        Checks if the given character matches the next expected letter.
        If it matches, increments current_typed_index and returns True.
        """
        if not self.is_fully_typed() and char.lower() == self.original_text[self.current_typed_index].lower():
            self.current_typed_index += 1
            return True
        return False

    def is_fully_typed(self):
        """
        Returns True if all letters of the word have been typed.
        """
        return self.current_typed_index == len(self.original_text)

    def get_next_letter(self):
        """
        Returns the next character the player needs to type, or None if fully typed.
        """
        if not self.is_fully_typed():
            return self.original_text[self.current_typed_index].lower()
        return None

    def get_width(self):
        """
        Returns the total width of the word's rendered surface.
        """
        return self.rect.width

class Game:
    """
    Manages the overall game state, main loop, event handling, updating all game objects, and rendering.
    """
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Falling Words")
        self.clock = pygame.time.Clock()

        # Fonts for UI and words
        self.font_large = pygame.font.Font(None, 74) # For titles
        self.font_medium = pygame.font.Font(None, 50) # For words and buttons
        self.font_small = pygame.font.Font(None, 36) # For score/lives

        self.game_state = GAME_STATE_MENU
        self.running = True

        # Game attributes, initialized here and reset by reset_game()
        self.score = INITIAL_SCORE
        self.lives = INITIAL_LIVES
        self.active_words = [] # List of FallingWord objects
        self.word_list = WORD_LIST # The predefined list of words

        # Difficulty scaling attributes
        self.base_word_speed = INITIAL_WORD_SPEED
        self.spawn_interval = INITIAL_SPAWN_INTERVAL_MS
        self.next_word_spawn_time = 0 # Will be set in reset_game
        self.last_speed_increase_time = 0 # Will be set in reset_game
        self.words_typed_since_last_interval_decrease = 0 # Counter for spawn interval scaling

        # Rect objects for clickable UI elements (buttons)
        self.start_button_rect = None
        self.quit_button_rect = None
        self.play_again_button_rect = None

        self.reset_game() # Call once at init to set initial values

    def reset_game(self):
        """
        Resets all game parameters to their initial state for a new game.
        """
        self.score = INITIAL_SCORE
        self.lives = INITIAL_LIVES
        self.active_words = []
        self.base_word_speed = INITIAL_WORD_SPEED
        self.spawn_interval = INITIAL_SPAWN_INTERVAL_MS
        
        # Reset timers for difficulty scaling and word spawning
        current_time = pygame.time.get_ticks()
        self.next_word_spawn_time = current_time + self.spawn_interval
        self.last_speed_increase_time = current_time
        self.words_typed_since_last_interval_decrease = 0

    def run(self):
        """
        The main game loop.
        """
        while self.running:
            dt = self.clock.tick(FPS) # dt is milliseconds since last frame
            self.handle_events()
            self.update_game_state(dt)
            self.draw_elements()

        pygame.quit()
        sys.exit()

    def handle_events(self):
        """
        Processes all Pygame events (keyboard, mouse, quit).
        Transitions game states based on user input.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif self.game_state == GAME_STATE_PLAYING:
                    # Check if the pressed key is an alphabetic character
                    if event.unicode.isalpha():
                        self.process_typed_char(event.unicode.lower())
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left mouse button
                    mouse_pos = event.pos
                    if self.game_state == GAME_STATE_MENU:
                        if self.start_button_rect and self.start_button_rect.collidepoint(mouse_pos):
                            self.game_state = GAME_STATE_PLAYING
                            self.reset_game() # Start a fresh game
                        elif self.quit_button_rect and self.quit_button_rect.collidepoint(mouse_pos):
                            self.running = False
                    elif self.game_state == GAME_STATE_GAME_OVER:
                        if self.play_again_button_rect and self.play_again_button_rect.collidepoint(mouse_pos):
                            self.game_state = GAME_STATE_PLAYING
                            self.reset_game() # Start a fresh game
                        elif self.quit_button_rect and self.quit_button_rect.collidepoint(mouse_pos):
                            self.running = False

    def process_typed_char(self, char):
        """
        Processes a typed character, attempting to match it with falling words.
        Prioritizes words based on current_typed_index and y-position.
        """
        if not self.active_words:
            return

        candidate_words = []
        for word in self.active_words:
            if word.get_next_letter() == char:
                candidate_words.append(word)

        if not candidate_words:
            return # No word found that matches the typed character

        # Prioritization:
        # 1. Smallest current_typed_index (word closest to being completed)
        # 2. Closest to bottom (highest y value) if current_typed_index is the same
        candidate_words.sort(key=lambda w: (w.current_typed_index, -w.y))

        chosen_word = candidate_words[0] # Select the highest priority word
        
        # Attempt to type the character in the chosen word
        if chosen_word.check_input(char):
            if chosen_word.is_fully_typed():
                # Word completed: award points and remove from active words
                self.score += WORD_POINTS + (len(chosen_word.original_text) * LETTER_POINTS)
                self.active_words.remove(chosen_word)
                self.words_typed_since_last_interval_decrease += 1

                # Check if it's time to decrease spawn interval (increase frequency)
                if self.words_typed_since_last_interval_decrease >= SPAWN_INTERVAL_DECREASE_TRIGGER_WORDS:
                    self.spawn_interval = max(MIN_SPAWN_INTERVAL_MS, self.spawn_interval - SPAWN_INTERVAL_DECREASE_AMOUNT_MS)
                    self.words_typed_since_last_interval_decrease = 0 # Reset counter

    def update_game_state(self, dt):
        """
        Updates all game objects, checks for collisions, spawns new words,
        updates score/lives, and handles difficulty scaling.
        """
        if self.game_state == GAME_STATE_PLAYING:
            current_time = pygame.time.get_ticks()

            # Word Spawning Logic
            if current_time >= self.next_word_spawn_time:
                self.spawn_word()
                self.next_word_spawn_time = current_time + self.spawn_interval

            # Update Falling Words and check for words hitting the bottom
            words_to_keep = []
            for word in self.active_words:
                if word.update(dt, SCREEN_HEIGHT): # Word hit bottom
                    self.lives -= 1
                    # Word is not added to words_to_keep, effectively removing it
                else:
                    words_to_keep.append(word)
            self.active_words = words_to_keep # Update the list of active words

            # Difficulty Scaling (Word Speed Increase)
            if current_time - self.last_speed_increase_time >= SPEED_INCREASE_INTERVAL_MS:
                self.base_word_speed = min(MAX_WORD_SPEED, self.base_word_speed + SPEED_INCREASE_AMOUNT)
                self.last_speed_increase_time = current_time

            # Game Over Check
            if self.lives <= 0:
                self.game_state = GAME_STATE_GAME_OVER

    def spawn_word(self):
        """
        Creates a new FallingWord object and adds it to the active_words list.
        """
        word_text = random.choice(self.word_list)
        
        # Calculate word width to ensure it spawns fully on screen
        # Need to render it once to get its dimensions
        temp_surface = self.font_medium.render(word_text, True, WHITE)
        word_width = temp_surface.get_width()

        # Random X position, ensuring the word doesn't go off the right edge
        max_x = SCREEN_WIDTH - word_width
        x = random.randint(0, max_x) if max_x > 0 else 0
        y = -50 # Start slightly above the top of the screen

        new_word = FallingWord(word_text, x, y, self.base_word_speed, self.font_medium, WHITE, YELLOW)
        self.active_words.append(new_word)

    def draw_elements(self):
        """
        Clears the screen and draws all elements based on the current game state.
        """
        self.screen.fill(DARK_GRAY) # Fill background

        if self.game_state == GAME_STATE_MENU:
            self.draw_menu()
        elif self.game_state == GAME_STATE_PLAYING:
            self.draw_playing()
        elif self.game_state == GAME_STATE_GAME_OVER:
            self.draw_game_over()

        pygame.display.flip() # Update the full display Surface to the screen

    def draw_menu(self):
        """
        Renders the main menu screen with "Start Game" and "Quit" options.
        """
        title_text = self.font_large.render("Falling Words", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        self.screen.blit(title_text, title_rect)

        # Start Game Button
        start_text = self.font_medium.render("Start Game", True, GREEN)
        # Create a rect for the button, slightly larger than the text, centered
        self.start_button_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        pygame.draw.rect(self.screen, LIGHT_GRAY, self.start_button_rect.inflate(20, 10), border_radius=5)
        self.screen.blit(start_text, self.start_button_rect)

        # Quit Button
        quit_text = self.font_medium.render("Quit", True, RED)
        self.quit_button_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70))
        pygame.draw.rect(self.screen, LIGHT_GRAY, self.quit_button_rect.inflate(20, 10), border_radius=5)
        self.screen.blit(quit_text, self.quit_button_rect)

    def draw_playing(self):
        """
        Renders the active gameplay screen, including score, lives, and falling words.
        """
        # Draw Score
        score_text = self.font_small.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        # Draw Lives
        lives_text = self.font_small.render(f"Lives: {self.lives}", True, WHITE)
        # Position lives text on the top right
        lives_text_x = SCREEN_WIDTH - lives_text.get_width() - 10
        self.screen.blit(lives_text, (lives_text_x, 10))

        # Draw all currently active falling words
        for word in self.active_words:
            word.draw(self.screen)

    def draw_game_over(self):
        """
        Renders the game over screen, displaying the final score and options to play again or quit.
        """
        game_over_text = self.font_large.render("Game Over!", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        self.screen.blit(game_over_text, game_over_rect)

        final_score_text = self.font_medium.render(f"Final Score: {self.score}", True, WHITE)
        final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(final_score_text, final_score_rect)

        # Play Again Button
        play_again_text = self.font_medium.render("Play Again", True, GREEN)
        self.play_again_button_rect = play_again_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        pygame.draw.rect(self.screen, LIGHT_GRAY, self.play_again_button_rect.inflate(20, 10), border_radius=5)
        self.screen.blit(play_again_text, self.play_again_button_rect)

        # Quit Button (re-using the same rect variable, but it's set for this state)
        quit_text = self.font_medium.render("Quit", True, RED)
        self.quit_button_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 90))
        pygame.draw.rect(self.screen, LIGHT_GRAY, self.quit_button_rect.inflate(20, 10), border_radius=5)
        self.screen.blit(quit_text, self.quit_button_rect)

# --- Main Game Execution ---
if __name__ == "__main__":
    game = Game()
    game.run()