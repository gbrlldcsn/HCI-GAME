import pygame
import random
import string
import math
import os
import subprocess
import sys
from pygame import mixer

# Get the directory of the current script (DEADLINE CHRONICLES)
current_script_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the SnakeGame directory
snake_game_module_dir = os.path.join(current_script_dir, "SnakeGame", "Code")

# Add the SnakeGame directory to sys.path to allow direct import
if snake_game_module_dir not in sys.path:
    sys.path.insert(0, snake_game_module_dir)

import SnakeGame  # Now SnakeGame module can be imported

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1280, 720
FPS = 60
FONT_SIZE = 24
COLUMNS = WIDTH // FONT_SIZE
CAMERA_SMOOTHING = 0.1  # Camera smoothing factor (increased for tighter follow/zoom effect)

# Colors
BLACK = (0, 0, 0)
RED = (209, 51, 55)  # #D13337
BLUE = (81, 163, 184)  # #51A3B8
WHITE = (255, 255, 255)
GREY = (128, 128, 128)  # Define GREY color
DARK_GREY = (60, 60, 60)  # Define DARK_GREY color
MATRIX_GREEN = (0, 255, 0)  # Define MATRIX_GREEN for effects

# New: Platform texture
PLATFORM_TEXTURE = None  # Will be loaded in main

COLORS = [BLUE, RED]
SHAPE_COLORS = [(RED[0], RED[1], RED[2], 30), (BLUE[0], BLUE[1], BLUE[2], 30)]  # Semi-transparent

# Characters for the matrix effect
MATRIX_CHARS = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;':\",./<>?`~"

# Portal settings
PORTAL_SIZE = 250
PORTAL_ROTATION_SPEED = 1

# Portal state constants (moved to module level)
PORTAL_DISAPPEARING = 0
PORTAL_APPEARING = 1
PORTAL_LOOPING = 2

# New: Footprint constants
FOOTPRINT_SIZE = (12, 4)  # Width, Height of the footprint
FOOTPRINT_COLOR = GREY  # Color of the footprint
FOOTPRINT_LIFETIME = 1500  # milliseconds for the footprint to fade
FOOTPRINT_INTERVAL = 100  # milliseconds between new footprints
# New: Range for random vertical offset for footprints (e.g., -2 to 2 pixels)
FOOTPRINT_Y_RANDOM_OFFSET_RANGE = (-2, 2)


class Character:
    def __init__(self, platform_y=None):
        self.x = 100
        self.width = 60 * 1.5  # Increased width by 1.5
        self.height = 90 * 1.5  # Increased height by 1.5
        self.speed = 5
        # Place character so feet touch the platform
        if platform_y is not None:
            self.y = platform_y - self.height + 10  # Added +10 offset to push character down onto the platform
        else:
            self.y = HEIGHT // 2
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # Load character sprites
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.sprites = {
            'left': [],
            'right': [],
            'up': [],
            'down': []
        }

        # Load sprites for each direction, using underscore filenames
        for direction in ['left', 'right', 'up', 'down']:
            sprites_for_direction = []
            for i in range(1, 5):  # Try to load sprites 1-4
                sprite_path = os.path.join(script_dir, f"{direction}mc_{i}.png")
                try:
                    sprite = pygame.image.load(sprite_path).convert_alpha()  # Use convert_alpha for transparency
                    sprite = pygame.transform.scale(sprite,
                                                    (int(self.width), int(self.height)))  # Scale to new dimensions
                    sprites_for_direction.append(sprite)
                except FileNotFoundError:
                    print(f"Warning: Sprite not found at {sprite_path} for direction '{direction}'.")

            # After trying to load all 4 sprites for a direction:
            if not sprites_for_direction:
                print(f"Error: No sprites loaded for direction '{direction}'. Creating a magenta placeholder.")
                # Create a clearly visible placeholder if no sprites were loaded for this direction
                placeholder_sprite = pygame.Surface((int(self.width), int(self.height)), pygame.SRCALPHA)
                placeholder_sprite.fill((255, 0, 255, 128))  # Magenta semi-transparent placeholder
                pygame.draw.rect(placeholder_sprite, WHITE, (0, 0, int(self.width), int(self.height)),
                                 2)  # White outline
                sprites_for_direction.append(placeholder_sprite)

            self.sprites[direction] = sprites_for_direction

        # This extra check ensures every direction always has at least ONE sprite for animation logic
        for direction in ['left', 'right', 'up', 'down']:
            if not self.sprites[direction]:
                print(
                    f"Critical: Fallback placeholder for {direction} not created. Creating emergency red placeholder.")
                sprite = pygame.Surface((int(self.width), int(self.height)), pygame.SRCALPHA)
                sprite.fill((255, 0, 0, 150))  # Red semi-transparent emergency placeholder
                self.sprites[direction].append(sprite)

        self.current_direction = 'right'
        self.animation_index = 0
        self.animation_timer = 0
        self.animation_speed = 100  # milliseconds per frame
        self.last_footstep_time = 0  # To control footprint frequency

    def move(self, keys, dt, platform_y=None, footprints_list=None, current_time=0):
        # Store previous position to detect actual movement
        prev_x = self.x
        prev_y = self.y

        moving = False
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:  # Add A key for left
            # Add left boundary check (100 pixels from left edge)
            if self.x > 100:
                self.x -= self.speed
                self.current_direction = 'left'
                moving = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:  # Add D key for right
            # Add right boundary check (100 pixels from right edge)
            if self.x < WIDTH - self.width - 100:
                self.x += self.speed
                self.current_direction = 'right'
                moving = True

        # Always align y so feet touch the platform
        if platform_y is not None:
            self.y = platform_y - self.height + 10  # Added +10 offset to push character down onto the platform
        else:
            self.y = HEIGHT // 2
        self.rect.x = self.x
        self.rect.y = self.y

        if moving:
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                # Ensure there are sprites to animate
                if self.sprites[self.current_direction]:
                    self.animation_index = (self.animation_index + 1) % len(self.sprites[self.current_direction])
                else:
                    self.animation_index = 0  # Fallback if no sprites

            # Create footprint if character moved significantly and cooldown is over
            if footprints_list is not None and (
                    abs(self.x - prev_x) > 1 or abs(self.y - prev_y) > 1):  # Check for actual position change
                if current_time - self.last_footstep_time > FOOTPRINT_INTERVAL:
                    # Calculate footprint position (bottom center of character)
                    footprint_x = self.x + self.width // 2 - (FOOTPRINT_SIZE[0] // 2)

                    # Apply base elevation (e.g., 3 pixels up) and then a random offset
                    random_y_offset = random.randint(FOOTPRINT_Y_RANDOM_OFFSET_RANGE[0],
                                                     FOOTPRINT_Y_RANDOM_OFFSET_RANGE[1])
                    footprint_y = self.y + self.height - FOOTPRINT_SIZE[1] - 10 + random_y_offset

                    footprints_list.append(Footprint(footprint_x, footprint_y))
                    self.last_footstep_time = current_time
        else:
            self.animation_index = 0  # Reset animation index when not moving

    def draw(self, screen, offset_x=0, offset_y=0):
        # Draw the current sprite frame
        # Ensure there are sprites to draw
        if self.sprites[self.current_direction]:
            screen.blit(self.sprites[self.current_direction][self.animation_index],
                        (self.rect.x + offset_x, self.rect.y + offset_y))
        else:
            # Fallback for drawing if no sprites are available (should be covered by init's placeholders now)
            pygame.draw.rect(screen, WHITE,
                             (self.rect.x + offset_x, self.rect.y + offset_y, self.rect.width, self.rect.height), 2)


class Footprint:
    def __init__(self, x, y, color=FOOTPRINT_COLOR, lifetime_ms=FOOTPRINT_LIFETIME):
        self.x = x
        self.y = y
        self.color = color
        self.lifetime_ms = lifetime_ms
        self.creation_time = pygame.time.get_ticks()

        self.surface = pygame.Surface(FOOTPRINT_SIZE, pygame.SRCALPHA)
        self.surface.fill(self.color)
        self.alpha = 255  # Start fully opaque
        self.surface.set_alpha(self.alpha)  # Set initial alpha on surface

        self.rect = self.surface.get_rect(topleft=(x, y))

    def update(self, current_time):
        elapsed_time = current_time - self.creation_time
        fade_progress = min(1.0, elapsed_time / self.lifetime_ms)  # Clamp to 1.0
        self.alpha = max(0, 255 - int(255 * fade_progress))
        self.surface.set_alpha(self.alpha)

    def draw(self, screen, offset_x=0, offset_y=0):
        if self.alpha > 0:
            screen.blit(self.surface, (self.rect.x + offset_x, self.rect.y + offset_y))

    def is_faded_out(self):
        return self.alpha <= 0


class TransitionEffect:
    def __init__(self):
        self.angle = 0
        self.alpha = 0
        self.transition_surface = pygame.Surface((WIDTH, HEIGHT))
        self.transition_surface.fill(WHITE)
        self.transition_surface.set_alpha(0)
        self.pixel_size = 8  # Increased from 4 to 8 for more pixelated look
        self.rotation_speed = 1.5
        self.expansion_rate = 0.4

    def update(self):
        self.angle += self.rotation_speed
        self.alpha = min(255, self.alpha + 2)
        self.transition_surface.set_alpha(self.alpha)

    def draw(self, screen):
        # Create whirl effect
        whirl_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        center = (WIDTH // 2, HEIGHT // 2)

        # Draw multiple layers of pixelated elements
        for layer in range(8):  # Increased from 6 to 8 layers for more depth
            for i in range(0, 360, 12):  # Changed from 10 to 12 for more pixelated spacing
                angle = math.radians(i + self.angle + (layer * 15))
                base_radius = 40 + (i // 12) * 12 + (layer * 30)  # Adjusted for new spacing
                radius = base_radius * (1 + (self.alpha / 255) * self.expansion_rate)
                x = center[0] + radius * math.cos(angle)
                y = center[1] + radius * math.sin(angle)

                # Create more pixelated squares with varying sizes
                pixel_size = self.pixel_size + layer * 3  # Increased size increment
                alpha = 220 - (layer * 25)

                # Draw main pixel square with pixelated edges
                rect = pygame.Rect(
                    int(x - pixel_size / 2),
                    int(y - pixel_size / 2),
                    pixel_size,
                    pixel_size
                )
                pygame.draw.rect(whirl_surface, (*BLUE, alpha), rect)

                # Add pixelated details
                if layer < 4:  # Increased from 3 to 4 for more detail layers
                    # Add smaller pixel squares
                    for offset in [(0, 0), (pixel_size // 4, pixel_size // 4), (-pixel_size // 4, -pixel_size // 4)]:
                        small_rect = pygame.Rect(
                            int(x - pixel_size / 4 + offset[0]),
                            int(y - pixel_size / 4 + offset[1]),
                            pixel_size // 2,
                            pixel_size // 2
                        )
                        pygame.draw.rect(whirl_surface, (*BLUE, min(255, alpha + 40)), small_rect)

                # Add pixelated accent pixels
                if random.random() < 0.4:  # Increased from 0.3 to 0.4 for more accents
                    for _ in range(2):  # Add multiple accent pixels
                        accent_size = pixel_size // 2
                        accent_x = x + random.randint(-pixel_size // 2, pixel_size // 2)
                        accent_y = y + random.randint(-pixel_size // 2, pixel_size // 2)
                        accent_rect = pygame.Rect(
                            int(accent_x - accent_size / 2),
                            int(accent_y - accent_size / 2),
                            accent_size,
                            accent_size
                        )
                        pygame.draw.rect(whirl_surface, (*WHITE, max(0, alpha - 50)), accent_rect)

        # Add a pixelated central glow effect
        glow_radius = 50 + (self.alpha / 255) * 100
        glow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for r in range(int(glow_radius), 0, -4):  # Changed from -2 to -4 for more pixelated steps
            alpha_glow = int(100 * (r / glow_radius))
            # Draw pixelated glow using squares instead of circles
            for angle in range(0, 360, 45):  # 8 directions for pixelated look
                rad = math.radians(angle)
                x = center[0] + r * math.cos(rad)
                y = center[1] + r * math.sin(rad)
                glow_rect = pygame.Rect(
                    int(x - r / 4),
                    int(y - r / 4),
                    r // 2,
                    r // 2
                )
                pygame.draw.rect(glow_surface, (*BLUE, alpha_glow), glow_rect)

        # Combine all effects
        screen.blit(glow_surface, (0, 0))
        screen.blit(whirl_surface, (0, 0))
        screen.blit(self.transition_surface, (0, 0))

    def is_complete(self):
        return self.alpha >= 255


class HelloWindow:
    def __init__(self):
        self.alpha = 0
        self.surface = pygame.Surface((WIDTH, HEIGHT))
        self.surface.fill(BLACK)
        self.font = pygame.font.Font(None, 74)
        self.text = self.font.render("HEWO", True, WHITE)
        self.text_rect = self.text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    def update(self):
        self.alpha = min(255, self.alpha + 5)
        self.surface.set_alpha(self.alpha)

    def draw(self, screen):
        self.surface.fill(BLACK)
        self.surface.blit(self.text, self.text_rect)
        screen.blit(self.surface, (0, 0))

    def is_complete(self):
        return self.alpha >= 255


class Camera:
    def __init__(self):
        self.offset_x = 0
        self.offset_y = 0
        self.target_x = 0
        self.target_y = 0

    def update(self, target_x, target_y):
        # Calculate target position (center of screen)
        self.target_x = target_x - WIDTH // 2
        self.target_y = target_y - HEIGHT // 2

        # Smoothly move camera towards target
        self.offset_x += (self.target_x - self.offset_x) * CAMERA_SMOOTHING
        self.offset_y += (self.target_y - self.offset_y) * CAMERA_SMOOTHING

    def apply(self, rect):
        # Return a new rect with camera offset applied
        return pygame.Rect(
            rect.x - self.offset_x,
            rect.y - self.offset_y,
            rect.width,
            rect.height
        )

    def apply_pos(self, x, y):
        # Return position with camera offset applied
        return (x - self.offset_x, y - self.offset_y)


def load_portal_frames(script_dir, prefix):
    frames = []
    for i in range(1, 9):
        frame_path = os.path.join(script_dir, f"{prefix}{i}_dr.png")
        # Handle FileNotFoundError for portal frames gracefully
        try:
            frame_img = pygame.image.load(frame_path)
            frame_img = pygame.transform.scale(frame_img, (PORTAL_SIZE, PORTAL_SIZE))
            frame_img = pygame.transform.flip(frame_img, True, False)
            frames.append(frame_img)
        except FileNotFoundError:
            print(f"Warning: Portal frame not found at {frame_path}. Skipping.")
            # If no frames are loaded, return an empty list or a list with a placeholder
            if not frames and i == 8:  # If this is the last frame and no frames loaded yet
                print("Error: No portal frames loaded. Portal animation will not be visible.")
                return [
                    pygame.Surface((PORTAL_SIZE, PORTAL_SIZE), pygame.SRCALPHA)]  # Return a single transparent surface
    return frames if frames else [pygame.Surface((PORTAL_SIZE, PORTAL_SIZE), pygame.SRCALPHA)]


def draw_matrix_platform(screen, y, height, camera):
    # Platform is now invisible - no drawing needed
    pass


class PulsingText:
    def __init__(self):
        self.texts = [
            "YOU WILL NEVER GET OUT",
            "YOU CAN'T GO BACK",
            "DETERMINATION WON'T SAVE YOU",
            "YOU'RE NOT READY",
            "DEADLINE",
            "DEADLINE",
            "YOUR EFFORTS ARE FUTILE",
            "NO ESCAPE",
            "FOREVER TRAPPED",
            "NO WAY OUT",
            "YOUR TIME IS OVER",
        ]
        self.font = pygame.font.Font(None, 26)  # Smaller font size
        self.alpha = 0
        self.pulse_speed = 2
        self.pulse_direction = 1
        self.visible = False
        self.visibility_timer = 0
        self.visibility_duration = 3000  # 3 seconds
        self.hide_duration = 3000  # Reduced from 5000 to 3000 for more frequent appearances
        self.last_visibility_change = pygame.time.get_ticks()
        self.positions = []  # Store positions for each text
        self.shake_offsets = []  # Store shake offsets for each text
        self.shake_intensity = 2  # Intensity of the shake effect
        self.update_positions()

    def update_positions(self):
        self.positions = []
        self.shake_offsets = []
        for _ in self.texts:
            # Random position within the window, with padding
            x = random.randint(50, WIDTH - 50)
            y = random.randint(50, HEIGHT - 50)
            self.positions.append((x, y))
            self.shake_offsets.append((0, 0))  # Initialize shake offsets

    def update(self):
        current_time = pygame.time.get_ticks()

        # Handle visibility timing
        if self.visible:
            if current_time - self.last_visibility_change > self.visibility_duration:
                self.visible = False
                self.last_visibility_change = current_time
                self.update_positions()  # Update positions when text becomes invisible
        else:
            if current_time - self.last_visibility_change > self.hide_duration:
                self.visible = True
                self.last_visibility_change = current_time

        # Update pulse effect
        if self.visible:
            self.alpha += self.pulse_speed * self.pulse_direction
            if self.alpha >= 255:
                self.alpha = 255
                self.pulse_direction = -1
            elif self.alpha <= 50:  # Minimum alpha value
                self.alpha = 50
                self.pulse_direction = 1

            # Update shake offsets
            for i in range(len(self.shake_offsets)):
                # Generate random offsets for x and y
                offset_x = random.randint(-self.shake_intensity, self.shake_intensity)
                offset_y = random.randint(-self.shake_intensity, self.shake_intensity)
                self.shake_offsets[i] = (offset_x, offset_y)

    def draw(self, screen):
        if self.visible:
            for text, (x, y), (offset_x, offset_y) in zip(self.texts, self.positions, self.shake_offsets):
                text_surface = self.font.render(text, True, RED)
                text_surface.set_alpha(self.alpha)
                text_rect = text_surface.get_rect(center=(x + offset_x, y + offset_y))
                screen.blit(text_surface, text_rect)


class DistortingShape:
    def __init__(self, x, y, size, color):
        self.x = x
        self.y = y
        self.base_size = size
        self.size = size
        self.color = color
        self.alpha = random.randint(30, 70)  # Slightly more visible transparency
        self.distortion_speed = random.uniform(0.03, 0.07)  # Increased speed
        self.distortion_phase = random.uniform(0, 2 * math.pi)
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-0.8, 0.8)  # Increased rotation speed

    def update(self):
        # Update distortion phase
        self.distortion_phase += self.distortion_speed
        # Calculate size variation using sine wave (increased magnitude)
        size_variation = math.sin(self.distortion_phase) * 0.35  # Increased from 0.2 to 0.35
        self.size = self.base_size * (1 + size_variation)
        # Update rotation
        self.rotation += self.rotation_speed

    def draw(self, surface):
        # Create a surface for the shape
        shape_surface = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)

        # Draw the shape (using a polygon for more interesting distortion)
        points = []
        num_points = 6  # Hexagon shape
        for i in range(num_points):
            angle = (2 * math.pi * i / num_points) + math.radians(self.rotation)
            # Add some distortion to the radius (increased magnitude)
            radius = self.size * (1 + math.sin(
                self.distortion_phase + i * 2) * 0.15)  # Increased from 0.1 to 0.15, added i*2 for more varied distortion
            x = self.size + radius * math.cos(angle)
            y = self.size + radius * math.sin(angle)
            points.append((x, y))

        # Draw the shape with the current color and alpha
        pygame.draw.polygon(shape_surface, (self.color[0], self.color[1], self.color[2], self.alpha), points)

        # Blit the shape to the main surface
        surface.blit(shape_surface, (self.x - self.size, self.y - self.size))


class MatrixRain:
    # Define discrete alpha levels for pre-rendering characters to optimize performance
    DEPTH_ALPHA_LEVELS = [60, 120, 180, 240]

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.font_size = 20
        self.columns = width // self.font_size
        self.font = pygame.font.Font(None, self.font_size)
        self.pre_rendered_chars = {}
        self.pre_render_characters()  # Call pre-rendering function

        # Create gradient surfaces for top and bottom shadows
        self.top_gradient = pygame.Surface((width, 150), pygame.SRCALPHA)
        self.bottom_gradient = pygame.Surface((width, 150), pygame.SRCALPHA)
        self.create_gradients()

        # Create depth effect surface - this is where characters are drawn before blitting to screen
        self.depth_surface = pygame.Surface((width, height), pygame.SRCALPHA)

        # New: Manage active drops and available columns
        self.active_drops = []
        self.all_column_indices = list(range(self.columns))
        random.shuffle(self.all_column_indices)  # Shuffle to randomize initial column order for drops

        # Initialize distorting shapes
        self.distorting_shapes = []
        self.initialize_distorting_shapes()

        # Fill all columns initially with a rain drop
        self.initialize_drops()

    def pre_render_characters(self):
        """Pre-renders all possible characters for different colors and alpha levels."""
        for color_tuple in [RED, BLUE]:  # Iterate through defined colors
            self.pre_rendered_chars[color_tuple] = {}
            for alpha_value in self.DEPTH_ALPHA_LEVELS:  # Iterate through defined alpha levels
                self.pre_rendered_chars[color_tuple][alpha_value] = {}
                for char in MATRIX_CHARS:  # Iterate through all matrix characters
                    # Render the character with the base color (alpha will be set on the surface)
                    char_surface = self.font.render(char, True, color_tuple)
                    char_surface.set_alpha(alpha_value)  # Set the specific alpha
                    self.pre_rendered_chars[color_tuple][alpha_value][char] = char_surface

    def create_gradients(self):
        # Create top gradient (fade from black to transparent)
        for y in range(150):
            alpha = int(255 * (1 - y / 150))
            pygame.draw.line(self.top_gradient, (0, 0, 0, alpha), (0, y), (self.width, y))

        # Create bottom gradient (fade from black to transparent)
        for y in range(150):
            alpha = int(255 * (y / 150))
            pygame.draw.line(self.bottom_gradient, (0, 0, 0, alpha), (0, y), (self.width, y))

    def _create_new_drop(self, column_index):
        """Creates a single new rain drop for a given column index."""
        y = random.randint(-self.height * 2, 0)  # Start even higher up for more falling distance
        speed = random.uniform(2, 5)
        length = random.randint(5, 20)
        color = random.choice([RED, BLUE])
        # Assign a depth level index instead of a continuous depth value
        depth_level_index = random.randint(0, len(self.DEPTH_ALPHA_LEVELS) - 1)

        new_drop = {
            'x': column_index * self.font_size,  # Use provided column_index for its x position
            'y': y,
            'speed': speed,
            'length': length,
            'color': color,
            'depth_level_index': depth_level_index,
            'column_index': column_index  # Store the column index for re-use
        }
        self.active_drops.append(new_drop)

    def initialize_distorting_shapes(self):
        # Create 15-20 subtle distorting shapes
        num_shapes = random.randint(15, 20)
        for _ in range(num_shapes):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(30, 80)
            # Use subtle colors that complement the matrix theme
            color = random.choice([
                (81, 163, 184, 40),  # Blue with low alpha
                (209, 51, 55, 40)  # Red with low alpha
            ])
            self.distorting_shapes.append(DistortingShape(x, y, size, color))

    def initialize_drops(self):
        """Initializes one rain drop for each available column."""
        # Initialize one drop per column using the shuffled column indices
        for col_idx in self.all_column_indices:
            self._create_new_drop(col_idx)

    def update(self):
        # Update existing drops
        drops_to_remove = []
        for drop in self.active_drops:
            drop['y'] += drop['speed']

            # Check if the entire length of the drop has fallen off the screen
            if drop['y'] > self.height + drop['length'] * self.font_size:
                drops_to_remove.append(drop)

        # Remove drops that have fallen off and recreate them in the same column
        for drop in drops_to_remove:
            self.active_drops.remove(drop)
            # Recreate a new drop in the same column index to maintain constant rain density per column
            self._create_new_drop(drop['column_index'])

        # Update distorting shapes
        for shape in self.distorting_shapes:
            shape.update()

    def draw(self, screen):
        """Draws all active rain drops, gradients, and blits to the screen."""
        # Clear depth surface with transparent to allow new characters to be drawn cleanly
        self.depth_surface.fill((0, 0, 0, 0))

        # Draw distorting shapes first (in the background)
        for shape in self.distorting_shapes:
            shape.draw(self.depth_surface)

        # Draw drops with depth effect
        for drop in self.active_drops:
            # Get the alpha value from the pre-defined levels using the drop's index
            current_alpha = self.DEPTH_ALPHA_LEVELS[drop['depth_level_index']]

            # Draw each character in the drop
            for i in range(drop['length']):
                y = drop['y'] + (i * self.font_size)

                # Randomly choose a character for each segment every tick
                char = random.choice(MATRIX_CHARS)

                # Retrieve the pre-rendered surface for the character, color, and alpha level
                text_surface = self.pre_rendered_chars[drop['color']][current_alpha][char]

                # Blit the pre-rendered character to the depth surface
                self.depth_surface.blit(text_surface, (drop['x'], y))

        # Draw depth surface to the main screen
        screen.blit(self.depth_surface, (0, 0))

        # Draw gradients on top of the matrix rain to create the shadow effect
        screen.blit(self.top_gradient, (0, 0))
        screen.blit(self.bottom_gradient, (0, self.height - 150))


class PortalText:
    def __init__(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(script_dir, "pixel_mania.ttf")
        self.font = pygame.font.Font(font_path, 15)  # Larger font for portal text
        self.text = "QUANTUM SLITHER"
        self.alpha = 0
        self.fade_speed = 5
        self.visible = False
        self.pulse_speed = 2
        self.pulse_direction = 1
        self.shake_intensity = 1
        self.shake_offset = (0, 0)

    def update(self, distance, PORTAL_ACTIVATION_DISTANCE):
        # Show text when player is within portal activation distance
        if distance <= PORTAL_ACTIVATION_DISTANCE:
            self.visible = True
            # Fade in
            if self.alpha < 200:
                self.alpha = min(200, self.alpha + self.fade_speed)

            # Pulse effect
            self.alpha += self.pulse_speed * self.pulse_direction
            if self.alpha >= 255:
                self.alpha = 255
                self.pulse_direction = -1
            elif self.alpha <= 150:  # Minimum alpha value
                self.alpha = 150
                self.pulse_direction = 1

            # Shake effect
            self.shake_offset = (
                random.randint(-self.shake_intensity, self.shake_intensity),
                random.randint(-self.shake_intensity, self.shake_intensity)
            )
        else:
            # Fade out
            if self.alpha > 0:
                self.alpha = max(0, self.alpha - self.fade_speed)
            if self.alpha == 0:
                self.visible = False

    def draw(self, screen, portal_rect_camera):
        if self.visible:
            text_surface = self.font.render(self.text, True, WHITE)  # Changed from cyan to white
            text_surface.set_alpha(self.alpha)
            text_rect = text_surface.get_rect(center=(portal_rect_camera.centerx + self.shake_offset[0],
                                                      portal_rect_camera.top - 30 + self.shake_offset[1]))
            screen.blit(text_surface, text_rect)


class MessageBox:
    def __init__(self):
        self.font = pygame.font.Font(None, 20)  # Smaller font
        self.visible = False
        self.width = 200  # Smaller width
        self.height = 100  # Smaller height
        self.padding = 10  # Smaller padding
        self.button_width = 60  # Smaller buttons
        self.button_height = 25  # Smaller buttons
        self.button_padding = 10  # Smaller padding

        # Create message box surface
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.surface.fill((0, 0, 0, 200))  # Semi-transparent black background

        # Create buttons
        self.yes_button = pygame.Rect(
            self.padding,
            self.height - self.button_height - self.padding,
            self.button_width,
            self.button_height
        )
        self.no_button = pygame.Rect(
            self.width - self.button_width - self.padding,
            self.height - self.button_height - self.padding,
            self.button_width,
            self.button_height
        )

        # Button states
        self.yes_hovered = False
        self.no_hovered = False

    def draw(self, screen, x, y):
        if not self.visible:
            return

        # Draw box background
        box_rect = pygame.Rect(x, y, self.width, self.height)
        pygame.draw.rect(screen, (0, 0, 0, 200), box_rect)

        # Draw message
        message = self.font.render("Enter portal?", True, WHITE)
        message_rect = message.get_rect(centerx=x + self.width // 2, top=y + self.padding)
        screen.blit(message, message_rect)

        # Draw buttons with hover effects
        yes_color = (100, 200, 100) if self.yes_hovered else (50, 150, 50)  # Brighter green when hovered
        no_color = (200, 100, 100) if self.no_hovered else (150, 50, 50)  # Brighter red when hovered

        pygame.draw.rect(screen, yes_color, (x + self.yes_button.x, y + self.yes_button.y,
                                             self.button_width, self.button_height))
        pygame.draw.rect(screen, no_color, (x + self.no_button.x, y + self.no_button.y,
                                            self.button_width, self.button_height))

        # Draw button text
        yes_text = self.font.render("Yes", True, WHITE)
        no_text = self.font.render("No", True, WHITE)

        yes_text_rect = yes_text.get_rect(center=(x + self.yes_button.centerx, y + self.yes_button.centery))
        no_text_rect = no_text.get_rect(center=(x + self.no_button.centerx, y + self.no_button.centery))

        screen.blit(yes_text, yes_text_rect)
        screen.blit(no_text, no_text_rect)

    def handle_click(self, pos, box_pos):
        if not self.visible:
            return None

        # Adjust click position relative to box position
        rel_x = pos[0] - box_pos[0]
        rel_y = pos[1] - box_pos[1]

        # Check if click is within box bounds
        if not (0 <= rel_x <= self.width and 0 <= rel_y <= self.height):
            return None

        # Check button clicks
        if self.yes_button.collidepoint(rel_x, rel_y):
            return "yes"
        elif self.no_button.collidepoint(rel_x, rel_y):
            return "no"
        return None

    def handle_hover(self, pos, box_pos):
        if not self.visible:
            return

        # Adjust hover position relative to box position
        rel_x = pos[0] - box_pos[0]
        rel_y = pos[1] - box_pos[1]

        # Update button hover states
        self.yes_hovered = self.yes_button.collidepoint(rel_x, rel_y)
        self.no_hovered = self.no_button.collidepoint(rel_x, rel_y)


def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("DEVREALM")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, FONT_SIZE)

    # Initialize camera
    camera = Camera()

    # Get the directory of the current script for resource loading
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Load and play background music
    pygame.mixer.init()
    music_path = os.path.join(script_dir, "dev_realm_music.wav")
    try:
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play(-1)  # -1 means loop indefinitely
        pygame.mixer.music.set_volume(0.5)  # Set volume to 50%
    except pygame.error as e:
        print(f"Warning: Could not load background music from {music_path}: {e}")

    # Load portal sound effect - ensure mixer is initialized
    portal_sound_path = os.path.join(script_dir, "portal_sound.mp3")
    portal_sound = None
    try:
        portal_sound = pygame.mixer.Sound(portal_sound_path)
    except pygame.error as e:
        print(f"Warning: Could not load portal sound from {portal_sound_path}: {e}")
        # Create a dummy sound to prevent crashes if file is missing
        portal_sound = pygame.mixer.Sound(pygame.sndarray.make_sound(pygame.sndarray.make_zero_array(100)))

    # Load portal animation frames
    dispportal_frames = load_portal_frames(script_dir, "dispportal")
    portal_frames = load_portal_frames(script_dir, "portal")

    # Set up portal rectangles - use the same rect for both portal types
    portal_rect = pygame.Rect(0, 0, PORTAL_SIZE, PORTAL_SIZE)
    portal_rect.right = WIDTH - 50  # Position from right edge
    # Lower platform to bottom of window
    platform_y = HEIGHT // 2 + 100  # Current platform top position
    # Align portal's bottom with the platform's top
    portal_rect.bottom = platform_y + 30  # Adjusted to move the portal slightly lower
    # Now character stands on platform
    character = Character(platform_y=platform_y)

    # Create a smaller collision box for the portal
    portal_collision_rect = pygame.Rect(0, 0, PORTAL_SIZE * 0.10, PORTAL_SIZE * 0.03)  # 10% of portal size
    portal_collision_rect.center = portal_rect.center  # Center it on the portal

    # Portal animation variables
    portal_frame_idx = 0
    dispportal_frame_idx = 0
    portal_anim_timer = 0
    portal_anim_speed = 100  # milliseconds per frame

    # Portal state
    portal_state = PORTAL_DISAPPEARING
    portal_visible = True
    portal_animation_started = False
    PORTAL_ACTIVATION_DISTANCE = 400  # Distance at which portal animation starts

    # Create transition effect
    transition = TransitionEffect()
    hello_window = HelloWindow()

    # Create Matrix Rain background
    matrix_rain = MatrixRain(WIDTH, HEIGHT)

    # Create portal text effect
    portal_text = PortalText()

    # Create message box
    message_box = MessageBox()

    # List to hold active footprints
    footprints = []

    # Game states
    GAME_RUNNING = 0
    TRANSITIONING = 1
    SHOWING_HELLO = 2
    current_state = GAME_RUNNING

    # Initialize transition flag
    transition_triggered = False

    # Load UPMC image
    try:
        upmc_image = pygame.image.load(os.path.join(os.path.dirname(__file__), "upmc_1.png"))
        upmc_image = pygame.transform.scale(upmc_image, (WIDTH, HEIGHT))
        upmc_alpha = 0  # Start fully transparent
        upmc_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    except:
        print("Warning: Could not load UPMC image")
        upmc_image = None

    running = True
    while running:
        dt = clock.tick(FPS)
        current_time = pygame.time.get_ticks()  # Get current time once per frame

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Check for K_ESCAPE correctly
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Fill screen with black (this is largely covered by matrix rain now)
        screen.fill(BLACK)

        # Update and draw matrix rain background first (static, not affected by camera)
        matrix_rain.update()
        matrix_rain.draw(screen)

        if current_state == GAME_RUNNING:
            # Update camera to follow character
            camera.update(character.x + character.width // 2, character.y + character.height // 2)

            # Draw matrix platform before character (still invisible)
            platform_height = HEIGHT - platform_y  # Calculate height to go to the bottom of the window
            draw_matrix_platform(screen, platform_y, height=platform_height, camera=camera)  # This function is empty

            # Update character movement (but don't draw yet)
            keys = pygame.key.get_pressed()
            # Only allow movement if message box is not visible
            if not message_box.visible:
                # Pass footprints_list and current_time to character.move
                character.move(keys, dt, platform_y=platform_y, footprints_list=footprints, current_time=current_time)

            # Calculate character's camera-applied rectangle after movement
            character_rect_camera = camera.apply(character.rect)

            # New: Update and draw footprints
            new_footprints = []
            for fp in footprints:
                fp.update(current_time)
                if not fp.is_faded_out():
                    new_footprints.append(fp)
                    # Apply camera offset to footprint's position for drawing
                    fp_pos_camera = camera.apply_pos(fp.x, fp.y)
                    fp.draw(screen, fp_pos_camera[0] - fp.x, fp_pos_camera[1] - fp.y)
            footprints = new_footprints  # Update the list to remove faded footprints

            # Calculate distance between character and portal
            char_center_x = character.x + character.width // 2
            char_center_y = character.y + character.height // 2
            portal_center_x = portal_rect.centerx
            portal_center_y = portal_rect.centery
            distance = math.sqrt((char_center_x - portal_center_x) ** 2 + (char_center_y - portal_center_y) ** 2)

            # Update portal text
            portal_text.update(distance, PORTAL_ACTIVATION_DISTANCE)

            # Check if character is close enough to activate portal animation
            if distance <= PORTAL_ACTIVATION_DISTANCE and not portal_animation_started:
                portal_animation_started = True
                portal_state = PORTAL_DISAPPEARING  # Start with disappearing animation
                dispportal_frame_idx = 0
                portal_frame_idx = 0

            # Animate and draw portal only if animation has started
            if portal_animation_started:
                portal_anim_timer += dt
                if portal_anim_timer >= portal_anim_speed:
                    portal_anim_timer = 0

                    if portal_state == PORTAL_DISAPPEARING:
                        # Check if dispportal_frames is not empty to avoid index error
                        if dispportal_frames:
                            dispportal_frame_idx += 1
                            if dispportal_frame_idx >= len(dispportal_frames):
                                portal_state = PORTAL_APPEARING
                                portal_frame_idx = 0
                    elif portal_state == PORTAL_APPEARING:
                        # Check if portal_frames is not empty to avoid index error
                        if portal_frames:
                            portal_frame_idx += 1
                            if portal_frame_idx >= len(portal_frames):
                                portal_state = PORTAL_LOOPING
                                portal_frame_idx = 0
                    else:  # PORTAL_LOOPING
                        # Check if portal_frames is not empty to avoid index error
                        if portal_frames:
                            portal_frame_idx = (portal_frame_idx + 1) % len(portal_frames)

                # Draw the appropriate portal frame with camera offset
                portal_rect_camera = camera.apply(portal_rect)

                # Draw portal text
                portal_text.draw(screen, portal_rect_camera)

                # Add scattered glowing effect
                glow_color = (85, 214, 255)  # Cyan-like color for the glow
                glow_surface = pygame.Surface((PORTAL_SIZE * 1.5, PORTAL_SIZE * 1.5),
                                              pygame.SRCALPHA)  # Larger surface for scattered glow
                glow_surface_rect = glow_surface.get_rect(center=portal_rect_camera.center)

                num_particles = 250  # Increased number of small glow particles
                for _ in range(num_particles):
                    x_offset = random.randint(-int(PORTAL_SIZE * 0.75), int(PORTAL_SIZE * 0.75))
                    y_offset = random.randint(-int(PORTAL_SIZE * 0.75), int(PORTAL_SIZE * 0.75))
                    particle_x = glow_surface.get_width() // 2 + x_offset
                    particle_y = glow_surface.get_height() // 2 + y_offset

                    distance_from_center = math.sqrt(x_offset ** 2 + y_offset ** 2)
                    # Fade particles based on distance from portal center, less aggressive fade
                    base_alpha = max(0, 100 - int(
                        distance_from_center / (PORTAL_SIZE * 0.75) * 80))  # Increased base alpha
                    particle_alpha = random.randint(int(base_alpha * 0.5), base_alpha)  # Randomize alpha for flicker
                    particle_size = random.randint(3, 6)  # Slightly increased particle size

                    if particle_alpha > 0:
                        particle_color = (*glow_color, particle_alpha)
                        pygame.draw.rect(glow_surface, particle_color,
                                         (particle_x, particle_y, particle_size, particle_size))

                screen.blit(glow_surface, glow_surface_rect)

                if portal_state == PORTAL_DISAPPEARING:
                    # Check if dispportal_frames is not empty to avoid index error
                    if dispportal_frames:
                        screen.blit(dispportal_frames[dispportal_frame_idx], portal_rect_camera)
                else:
                    # Check if portal_frames is not empty to avoid index error
                    if portal_frames:
                        screen.blit(portal_frames[portal_frame_idx], portal_rect_camera)

            # Handle regular events (including Enter key) when message box is not visible
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    # Check for Enter key when near portal
                    elif event.key == pygame.K_RETURN and distance <= PORTAL_ACTIVATION_DISTANCE and not transition_triggered:
                        if portal_sound:
                            portal_sound.play()
                        # Stop background music when player chooses to enter portal
                        pygame.mixer.music.stop()
                        current_state = TRANSITIONING
                        transition_triggered = True  # Set flag to prevent multiple transitions

            # Animate UPMC image when player is in portal collision box
            if upmc_image and character_rect_camera.colliderect(portal_collision_rect):
                # Fade in UPMC image
                upmc_alpha = min(255, upmc_alpha + 5)  # Gradually increase alpha
                upmc_surface.fill((0, 0, 0, 0))  # Clear the surface
                upmc_surface.blit(upmc_image, (0, 0))  # Draw the image
                upmc_surface.set_alpha(upmc_alpha)  # Set the alpha
                screen.blit(upmc_surface, (0, 0))  # Draw the semi-transparent image
            else:
                # Fade out UPMC image
                upmc_alpha = max(0, upmc_alpha - 5)  # Gradually decrease alpha
                if upmc_alpha > 0:
                    upmc_surface.fill((0, 0, 0, 0))  # Clear the surface
                    upmc_surface.blit(upmc_image, (0, 0))  # Draw the image
                    upmc_surface.set_alpha(upmc_alpha)  # Set the alpha
                    screen.blit(upmc_surface, (0, 0))  # Draw the semi-transparent image

            # Draw character last, so it appears on top of everything
            character.draw(screen, character_rect_camera.x - character.rect.x,
                           character_rect_camera.y - character.rect.y)

        elif current_state == TRANSITIONING:
            transition.update()
            transition.draw(screen)
            if transition.is_complete():
                try:
                    # Launch SnakeGame after transition is complete
                    SnakeGame.main(screen, clock)
                    # After SnakeGame finishes, reset the game state
                    character = Character(platform_y=platform_y)  # Reinitialize character to original position
                    camera = Camera()  # Reset camera
                    footprints.clear()  # Clear all footprints when returning from game
                    current_state = GAME_RUNNING
                    transition_triggered = False
                except Exception as e:
                    print(f"Error launching SnakeGame: {e}")
                    running = False

        elif current_state == SHOWING_HELLO:
            # This state is no longer needed since we're using the transition effect
            current_state = GAME_RUNNING

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
