import pygame
import random
import time
import os
import math
import cv2
import sys

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Music tracks
MENU_MUSIC = "menu_music.mp3"
GAME_MUSIC = "game_music.mp3"
PAUSE_MUSIC = "pause_music.mp3"
GAME_OVER_MUSIC = "game_over_music.mp3"
WIN_MUSIC = "win_music.mp3"

# Background
video_menu = "menu_background.mp4"
video_game_over = "video_game_over.mp4"
video_game = "game_background.mp4 "
video_cap = cv2.VideoCapture(video_menu)
video_cap2 = cv2.VideoCapture(video_game_over)
video_cap3 = cv2.VideoCapture(video_game)

# Load and play menu music initially
pygame.mixer.music.load(MENU_MUSIC)
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.5)

# Sound effects
drop_sound = pygame.mixer.Sound("drop.wav")
clear_sound = pygame.mixer.Sound("clear.wav")
pause_sound = pygame.mixer.Sound("pause.wav")
unpause_sound = pygame.mixer.Sound("unpause.wav")
menu_select_sound = pygame.mixer.Sound("select.wav")
game_over_sound = pygame.mixer.Sound("game_over.wav")
win_sound = pygame.mixer.Sound("win.wav")


def get_next_video_frame():
    global video_cap
    ret, frame = video_cap.read()
    if not ret:
        video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = video_cap.read()

    frame = cv2.resize(frame, (SCREEN_WIDTH, SCREEN_HEIGHT))
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return pygame.surfarray.make_surface(frame.swapaxes(0, 1))


def get_next_video_game_over():
    global video_cap2
    ret, frame = video_cap2.read()
    if not ret:
        video_cap2.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = video_cap2.read()

    frame = cv2.resize(frame, (SCREEN_WIDTH, SCREEN_HEIGHT))
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return pygame.surfarray.make_surface(frame.swapaxes(0, 1))


def get_next_video_game():
    global video_cap3
    ret, frame = video_cap3.read()
    if not ret:
        video_cap3.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = video_cap.read()

    frame = cv2.resize(frame, (SCREEN_WIDTH, SCREEN_HEIGHT))
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return pygame.surfarray.make_surface(frame.swapaxes(0, 1))


def change_music(track, position=None):
    global music_position
    if pygame.mixer.music.get_busy() and position is None:
        music_position = pygame.mixer.music.get_pos() / 1000.0
    play_position = position if position is not None else music_position

    pygame.mixer.music.load(track)
    pygame.mixer.music.play(-1, play_position)
    pygame.mixer.music.set_volume(current_volume / VOLUME_LEVELS)


class FloatingText:
    def __init__(self, text, x, y, color=(255, 255, 255)):
        self.text = font.render(text, True, color)
        self.x = x
        self.y = y
        self.alpha = 255
        self.scale = 1.0
        self.growing = True

    def update(self):
        self.y -= 1
        self.alpha -= 5

        # Add pulsing effect
        if self.growing:
            self.scale += 0.01
            if self.scale >= 1.2:
                self.growing = False
        else:
            self.scale -= 0.01
            if self.scale <= 1.0:
                self.growing = True

    def draw(self, surface):
        if self.alpha > 0:
            temp = pygame.transform.scale_by(self.text.copy(), self.scale)
            temp.set_alpha(self.alpha)
            surface.blit(temp, (self.x - temp.get_width() // 2, self.y - temp.get_height() // 2))


class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = random.uniform(-1, 1)
        self.dy = random.uniform(-2, -0.5)
        self.life = 30
        self.size = random.randint(2, 4)
        self.color = (random.randint(200, 255), random.randint(200, 255), random.randint(0, 100))

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= 1
        self.size = max(0, self.size - 0.05)

    def draw(self, surface):
        if self.life > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))


def draw_glowing_ghost(surface, ghost_block, offset_x, offset_y):
    for y, row in enumerate(ghost_block.shape):
        for x, cell in enumerate(row):
            if cell:
                glow_surf = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
                glow_color = (255, 255, 255, 80)  # translucent white
                pygame.draw.rect(glow_surf, glow_color, (0, 0, BLOCK_SIZE, BLOCK_SIZE), border_radius=4)
                surface.blit(glow_surf, (offset_x + (ghost_block.x + x) * BLOCK_SIZE,
                                         offset_y + (ghost_block.y + y) * BLOCK_SIZE))


def draw_modern_block(surface, color, rect, text="", style="pixel"):
    block_font = pygame.font.Font("pixel_font.otf", int(rect.height * 0.4))  # Slightly smaller text

    # Create a surface for the block
    block_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

    # Define pixel size for the block
    pixel_size = 4

    # Calculate lighter and darker shades for the pixel art effect
    light_color = tuple(min(255, c + 80) for c in color)
    dark_color = tuple(max(0, c - 80) for c in color)

    # Fill the main block area with base color
    pygame.draw.rect(block_surf, color, (pixel_size, pixel_size,
                                         rect.width - 2 * pixel_size, rect.height - 2 * pixel_size))

    # Draw pixel art edges
    # Top light edge
    pygame.draw.rect(block_surf, light_color, (0, 0, rect.width - pixel_size, pixel_size))
    pygame.draw.rect(block_surf, light_color, (0, 0, pixel_size, rect.height - pixel_size))

    # Bottom dark edge
    pygame.draw.rect(block_surf, dark_color, (pixel_size, rect.height - pixel_size,
                                              rect.width - pixel_size, pixel_size))
    pygame.draw.rect(block_surf, dark_color, (rect.width - pixel_size, pixel_size,
                                              pixel_size, rect.height - pixel_size))

    # Add corner pixels for a cleaner look
    pygame.draw.rect(block_surf, color, (0, 0, pixel_size, pixel_size))
    pygame.draw.rect(block_surf, color, (rect.width - pixel_size, 0, pixel_size, pixel_size))
    pygame.draw.rect(block_surf, color, (0, rect.height - pixel_size, pixel_size, pixel_size))
    pygame.draw.rect(block_surf, dark_color, (rect.width - pixel_size,
                                              rect.height - pixel_size, pixel_size, pixel_size))

    # Apply the block to the surface
    surface.blit(block_surf, rect.topleft)

    # Add text with improved visibility
    if text:
        # Create a background for the text
        text_surf = block_font.render(text, True, BLACK)  # White text
        text_rect = text_surf.get_rect(center=rect.center)

        # Draw dark outline for better visibility
        outline_size = 2
        for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:  # Diagonal outlines
            surface.blit(text_surf, (text_rect.x + dx * outline_size,
                                     text_rect.y + dy * outline_size))
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:  # Cross outlines
            surface.blit(text_surf, (text_rect.x + dx * outline_size,
                                     text_rect.y + dy * outline_size))

        # Draw the main text
        text_surf = block_font.render(text, True, BLACK)  # Black main text
        surface.blit(text_surf, text_rect)


def draw_glowing_background(surface, frame):
    for y in range(0, SCREEN_HEIGHT, BLOCK_SIZE):
        for x in range(0, SCREEN_WIDTH - INFO_PANEL_WIDTH, BLOCK_SIZE):
            intensity = int(20 + 20 * (1 + math.sin((frame + x + y) * 0.01)))
            color = (intensity, intensity, intensity)
            pygame.draw.rect(surface, color, (x, y, BLOCK_SIZE, BLOCK_SIZE), 1)


def show_controls_screen(surface):
    # Clear screen with black background
    surface.fill(BLACK)

    # Title with pulse animation
    title_text = big_font.render("GAME CONTROLS", True, GREEN)
    pulse = 1.0 + 0.05 * math.sin(pygame.time.get_ticks() / 200)
    scaled_title = pygame.transform.scale_by(title_text, pulse)
    # Calculate the centered position for the scaled title
    title_rect = scaled_title.get_rect(center=(SCREEN_WIDTH // 2, 100))
    surface.blit(scaled_title, title_rect)

    # Controls information (text only)
    controls = [
        "MOVE LEFT:  LEFT ARROW or  A",
        "MOVE RIGHT: RIGHT ARROW or  D",
        "ROTATE:     UP ARROW or  W",
        "SOFT DROP:   DOWN ARROW or  S",
        "HARD DROP:   SPACE",
        "HOLD PIECE:  L-SHIFT",
        "PAUSE:      ESC"

    ]

    # Draw controls
    for i, control in enumerate(controls):
        control_text = font.render(control, True, WHITE)
        surface.blit(control_text, (SCREEN_WIDTH // 2 - control_text.get_width() // 2, 200 + i * 50))

    # Continue prompt
    continue_text = font.render("PRESS ANY KEY TO START", True, WHITE)
    surface.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, SCREEN_HEIGHT - 100))

    pygame.display.flip()

    # Wait for any key press
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                waiting = False
        pygame.time.delay(50)


def show_controls_screen_settings(surface):
    # Clear screen with black background
    surface.fill(BLACK)

    # Title with pulse animation
    title_text = big_font.render("GAME CONTROLS", True, GREEN)
    pulse = 1.0 + 0.05 * math.sin(pygame.time.get_ticks() / 200)
    scaled_title = pygame.transform.scale_by(title_text, pulse)
    # Calculate the centered position for the scaled title
    title_rect = scaled_title.get_rect(center=(SCREEN_WIDTH // 2, 100))
    surface.blit(scaled_title, title_rect)

    # Controls information (text only)
    controls = [
        "MOVE LEFT:  LEFT ARROW or  A",
        "MOVE RIGHT: RIGHT ARROW or  D",
        "ROTATE:     UP ARROW or  W",
        "SOFT DROP:   DOWN ARROW or  S",
        "HARD DROP:   SPACE",
        "HOLD PIECE:  L-SHIFT",
        "PAUSE:      ESC"

    ]

    # Draw controls
    for i, control in enumerate(controls):
        control_text = font.render(control, True, WHITE)
        surface.blit(control_text, (SCREEN_WIDTH // 2 - control_text.get_width() // 2, 200 + i * 50))

    # Continue prompt
    continue_text = font.render("PRESS ANY KEY TO GO BACK TO SETTINGS", True, WHITE)
    surface.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, SCREEN_HEIGHT - 100))

    pygame.display.flip()

    # Wait for any key press
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                waiting = False
        pygame.time.delay(50)


def draw_settings_menu(selected_option, from_pause=False):
    # Use the same background as other menus
    if from_pause:
        # Semi-transparent overlay for pause menu
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
    else:
        # Animated video background for main menu
        video_frame = get_next_video_frame()
        screen.blit(video_frame, (0, 0))

    # Pulsing title (matches main/pause menu style)
    title_text = big_font.render("SETTINGS", True, GREEN)
    pulse = 1.0 + 0.05 * math.sin(pygame.time.get_ticks() / 200)
    scaled_title = pygame.transform.scale_by(title_text, pulse)
    screen.blit(scaled_title, (SCREEN_WIDTH // 2 - scaled_title.get_width() // 2, 100))

    # Menu options with same animation as other menus
    options = [
        f"Volume: {current_volume}/{VOLUME_LEVELS}",
        "View Controls",
        "Back"
    ]

    for i, option in enumerate(options):
        y_offset = 0
        if i == selected_option:
            y_offset = 5 * math.sin(pygame.time.get_ticks() / 200)  # Same floating effect

        y_pos = 250 + i * 80
        color = BRIGHT_WHITE if i == selected_option else GRAY

        option_text = font.render(option, True, color)
        text_rect = option_text.get_rect(center=(SCREEN_WIDTH // 2, y_pos + y_offset))
        screen.blit(option_text, text_rect)

        # Same selection indicators as other menus
        if i == selected_option:
            indicator_size = 10 + 3 * math.sin(pygame.time.get_ticks() / 150)
            pygame.draw.polygon(screen, GREEN, [
                (text_rect.left - 30, text_rect.centery),
                (text_rect.left - 30 - indicator_size, text_rect.centery - indicator_size),
                (text_rect.left - 30 - indicator_size, text_rect.centery + indicator_size)
            ])
            pygame.draw.polygon(screen, GREEN, [
                (text_rect.right + 30, text_rect.centery),
                (text_rect.right + 30 + indicator_size, text_rect.centery - indicator_size),
                (text_rect.right + 30 + indicator_size, text_rect.centery + indicator_size)
            ])

    # Version text at bottom (matches other menus)
    version_text = small_font.render("Use xLEFT/RIGHT to adjust volume", True, WHITE)
    screen.blit(version_text, (20, SCREEN_HEIGHT - 30))

    pygame.display.flip()


# BLOCK_IMAGES = {
#     'I': pygame.image.load(os.path.join('I.png')),
#     'J': pygame.image.load(os.path.join('J.png')),
#     'L': pygame.image.load(os.path.join('L.png')),
#     'O': pygame.image.load(os.path.join('O.png')),
#     'S': pygame.image.load(os.path.join('S.png')),
#     'T': pygame.image.load(os.path.join('T.png')),
#     'Z': pygame.image.load(os.path.join('Z.png')),
# }

# Game constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
GRID_WIDTH = 15
GRID_HEIGHT = 19
BLOCK_SIZE = 36
BORDER_SIZE = 5
INFO_PANEL_WIDTH = 350
MINI_BLOCK_SIZE = 20  # Reduced size to fit better in slimmer panel
music_position = 0
VOLUME_LEVELS = 24  # 0-24 volume steps
current_volume = 12  # Default to middle volume
volume_key_held = False
volume_key_timer = 0
volume_key_delay = 0.3  # Initial delay before continuous adjustment starts
volume_key_repeat = 0.05  # Repeat rate after initial delay

# Colors
BLACK = (10, 10, 15)
WHITE = (240, 240, 245)
BRIGHT_WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (30, 30, 30)
LIGHT_BLUE = (100, 200, 255)
LIME = (50, 205, 50)
GOLD = (255, 215, 0)
DARK_BLUE = (20, 30, 50)
NEON_BLUE = (0, 200, 255)
NEON_PINK = (255, 50, 150)
NEON_GREEN = (50, 255, 150)
NEON_PURPLE = (180, 50, 255)
NEON_YELLOW = (255, 230, 0)
NEON_ORANGE = (255, 100, 0)
NEON_RED = (255, 50, 50)
SHADOW_COLOR = (0, 0, 0, 100)
GHOST_COLOR = (255, 255, 255, 150)  # Bright white with transparency
BLOCK_SHINE = (255, 255, 255, 100)  # Semi-transparent white for shine
BLOCK_OUTLINE = (0, 0, 0, 180)  # Semi-transparent black for outline

# Colors and dimensions for playfield and info panel
GRID_BACKGROUND_COLOR = (25, 25, 35)  # Darker background
GRID_LINE_COLOR = (0, 0, 0)  # Pure black grid lines
BORDER_COLOR = (80, 80, 95)  # Border color
BORDER_THICKNESS = 6  # Reduced border thickness for slimmer look
BORDER_RADIUS = 4  # Smaller border radius for a sharper look

PANEL_BACKGROUND = (20, 20, 30)
SECTION_BORDER_COLOR = (80, 80, 95)
SECTION_BORDER_THICKNESS = 2
SECTION_MARGIN = 10  # Reduced margin for slimmer panel
SECTION_PADDING = 8   # Reduced padding for slimmer panel
LABEL_COLOR = (180, 180, 180)  # Lighter gray for labels
VALUE_COLOR = WHITE  # White for values
HOLD_NEXT_BOX_HEIGHT = 85  # Reduced height for slimmer panel
STATS_SECTION_HEIGHT = 200

# Block shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]]  # Z
]

# Block colors
COLORS = [GREEN, GREEN, GREEN, GREEN, GREEN, GREEN, GREEN]

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("TASKTRIS")

# Game background
game_background = pygame.image.load("game_background.jpg").convert()
game_background = pygame.transform.scale(game_background, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Font setup
try:
    font_path = "pixel_font.otf"
    small_font = pygame.font.Font(font_path, 25)
    font = pygame.font.Font(font_path, 35)
    big_font = pygame.font.Font(font_path, 90)

    # Optionally unify if you want a default font reference
    default_font = font

    # Add after other font loads
    try:
        win_font = pygame.font.Font("pixel_font.otf", 110)
    except Exception as e:
        print("Could not load win_font.ttf, using big_font instead.")
        win_font = big_font

except Exception as e:
    print(f"Error initializing fonts: {e}")
    pygame.quit()
    exit()

# Highscore file
HIGHSCORE_FILE = "highscore.txt"


def load_highscore():
    if os.path.exists(HIGHSCORE_FILE):
        with open(HIGHSCORE_FILE, 'r') as f:
            return int(f.read())
    return 0


def save_highscore(score):
    highscore = load_highscore()
    if score > highscore:
        with open(HIGHSCORE_FILE, 'w') as f:
            f.write(str(score))


class Block:
    def __init__(self):
        self.shape_idx = random.randint(0, len(SHAPES) - 1)
        self.shape = SHAPES[self.shape_idx]
        self.color = COLORS[self.shape_idx]
        self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0
        self.landing_time = 0
        self.landing_alpha = 0
        self.rotation = 0

    def rotate(self):
        # Transpose the matrix and reverse each row to get a 90-degree rotation
        return [list(row)[::-1] for row in zip(*self.shape)]

    # def draw(self, surface, offset_x=0, offset_y=0):
    #     for y, row in enumerate(self.image()):
    #         for x, cell in enumerate(row):
    #             if cell == "0":
    #                 px = self.x + x
    #                 py = self.y + y
    #                 if 0 <= px < 10 and 0 <= py < 20:
    #                     draw_x = px * BLOCK_SIZE + offset_x
    #                     draw_y = py * BLOCK_SIZE + offset_y
    #                     if self.shape in BLOCK_IMAGES:
    #                         surface.blit(BLOCK_IMAGES[self.shape], (draw_x, draw_y))
    #                     else:
    #                         pygame.draw.rect(surface, self.color, (draw_x, draw_y, BLOCK_SIZE, BLOCK_SIZE))

    def draw(self, surface, offset_x, offset_y, ghost=False):
        text_map = {
            0: "PLAN", 1: "SYNC", 2: "LOOP",
            3: "CODE", 4: "DOCS", 5: "ART", 6: "BUGS"
        }

        # Load custom font relative to BLOCK_SIZE
        block_font = pygame.font.Font("pixel_font.otf", int(BLOCK_SIZE * 0.45))

        for y, row in enumerate(self.shape):
            for x, cell in enumerate(row):
                if not cell:
                    continue

                block_x = offset_x + (self.x + x) * BLOCK_SIZE
                block_y = offset_y + (self.y + y) * BLOCK_SIZE
                rect = pygame.Rect(block_x, block_y, BLOCK_SIZE, BLOCK_SIZE)

                if ghost:
                    # Draw ghost block
                    ghost_surf = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
                    pygame.draw.rect(ghost_surf, GHOST_COLOR, ghost_surf.get_rect(), border_radius=4)
                    surface.blit(ghost_surf, rect.topleft)
                    pygame.draw.rect(surface, GHOST_COLOR, rect, 1, border_radius=4)
                    continue

                # Draw block body with pixel glow
                draw_modern_block(surface, self.color, rect, "", style="pixel")

                # Draw label using custom font
                label = text_map.get(self.shape_idx, "")
                if label:
                    text = block_font.render(label, True, BLACK)
                    tx = rect.left + (BLOCK_SIZE - text.get_width()) // 2
                    ty = rect.top + (BLOCK_SIZE - text.get_height()) // 2
                    surface.blit(text, (tx, ty))

    def draw_landing_effect(self, surface, offset_x, offset_y):
        if self.landing_alpha > 0:
            s = pygame.Surface((BLOCK_SIZE * len(self.shape[0]), BLOCK_SIZE * len(self.shape)), pygame.SRCALPHA)
            pygame.draw.rect(s, (*WHITE[:3], self.landing_alpha),
                             (0, 0, BLOCK_SIZE * len(self.shape[0]), BLOCK_SIZE * len(self.shape)), 3)
            surface.blit(s, (offset_x + self.x * BLOCK_SIZE, offset_y + self.y * BLOCK_SIZE))
            self.landing_alpha = max(0, self.landing_alpha - 15)

    def trigger_landing_effect(self):
        self.landing_alpha = 150


class Game:
    def __init__(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = Block()
        self.next_pieces = [Block() for _ in range(3)]
        self.hold_piece = None
        self.can_hold = True
        self.score = 0
        self.lines = 0
        self.level = 1
        self.fall_time = 0
        self.fall_speed = 0.4  # Initial fall speed
        self.last_time = time.time()

        # Calculate dimensions for the combined game and info box
        gap_between_grid_and_info = 10 # Small gap between the grid and info panel
        combined_content_width = GRID_WIDTH * BLOCK_SIZE + gap_between_grid_and_info + INFO_PANEL_WIDTH
        combined_content_height = GRID_HEIGHT * BLOCK_SIZE

        # Calculate total size including border
        total_box_width = combined_content_width + 2 * BORDER_THICKNESS
        total_box_height = combined_content_height + 2 * BORDER_THICKNESS

        # Calculate the top-left corner of the combined box
        combined_box_x = (SCREEN_WIDTH - total_box_width) // 2
        combined_box_y = (SCREEN_HEIGHT - total_box_height) // 2

        # Calculate the offset for the game grid (relative to the screen)
        # The grid starts after the left border thickness of the combined box
        self.offset_x = combined_box_x + BORDER_THICKNESS
        self.offset_y = combined_box_y + BORDER_THICKNESS

        self.clear_animation_timer = 0
        self.lines_to_clear = []
        self.flash_alpha = 0
        self.flash_increasing = True
        self.ghost_y = 0
        self.lock_timer = 0
        self.soft_drop_points = 0
        self.combo_count = 0
        self.last_was_tspin = False
        self.floating_texts = []
        self.particles = []
        self.frame_count = 0
        # Base movement timing parameters
        self.base_move_delay = 0.08  # Base movement delay
        self.base_move_initial_delay = 0.15  # Base initial delay
        self.base_move_repeat_delay = 0.05  # Base repeat delay
        self.move_delay = self.base_move_delay  # Current movement delay
        self.move_initial_delay = self.base_move_initial_delay  # Current initial delay
        self.move_repeat_delay = self.base_move_repeat_delay  # Current repeat delay
        self.last_move_time = 0
        self.move_keys_pressed = {'left': False, 'right': False, 'down': False}
        self.position_snap = True
        self.last_valid_x = 0
        self.last_valid_y = 0
        self.grid_snap_threshold = 0.1
        self.move_cooldown = 0
        self.move_cooldown_time = 0.05
        self.speed_multiplier = 1.0  # Speed scaling factor

        # Score and level animation attributes
        self.score_pulse = 1.0
        self.score_growing = False
        self.level_pulse = 1.0
        self.level_growing = False

        # Lock delay attributes
        self.lock_delay = 0.5  # Standard lock delay
        self.lock_delay_extension = 0.5  # Additional lock delay on movement
        self.max_lock_delay = 1.0  # Maximum lock delay
        self.last_rotation = False  # Track if last move was rotation
        self.last_move = None  # Track last move type

    def update_movement_speed(self):
        # Calculate speed multiplier based on level
        # As level increases, movement becomes faster
        self.speed_multiplier = 1.0 + (self.level * 0.1)  # 10% faster per level

        # Update movement delays based on speed multiplier
        self.move_delay = max(0.02, self.base_move_delay / self.speed_multiplier)
        self.move_initial_delay = max(0.04, self.base_move_initial_delay / self.speed_multiplier)
        self.move_repeat_delay = max(0.01, self.base_move_repeat_delay / self.speed_multiplier)
        self.move_cooldown_time = max(0.01, 0.04 / self.speed_multiplier)

    def calculate_ghost_position(self):
        self.ghost_y = self.current_piece.y
        while self.valid_position(self.current_piece.shape,
                                  self.current_piece.x,
                                  self.ghost_y + 1):
            self.ghost_y += 1

        # Ensure ghost piece snaps to grid
        self.ghost_y = int(self.ghost_y)

    def valid_position(self, shape, x, y):
        # Ensure x and y are integers for grid alignment
        x = round(x)
        y = round(y)

        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    if (y + i >= GRID_HEIGHT or
                            x + j < 0 or
                            x + j >= GRID_WIDTH or
                            self.grid[y + i][x + j]):
                        return False
        return True

    def merge_piece(self):
        self.current_piece.trigger_landing_effect()
        drop_sound.play()
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[self.current_piece.y + y][self.current_piece.x + x] = self.current_piece.shape_idx + 1
        self.score += self.soft_drop_points
        self.soft_drop_points = 0

    def check_t_spin(self, mini=False):
        if self.current_piece.shape_idx != 2:  # Not a T-piece
            return False

        x, y = self.current_piece.x, self.current_piece.y
        corners = []

        # Define corner positions based on rotation
        if self.current_piece.rotation == 0:  # Default orientation
            corners = [(x, y), (x + 2, y), (x, y + 2), (x + 2, y + 2)]
        elif self.current_piece.rotation == 1:  # 90 degrees
            corners = [(x, y), (x + 2, y), (x + 2, y + 2), (x, y + 2)]
        elif self.current_piece.rotation == 2:  # 180 degrees
            corners = [(x, y + 2), (x + 2, y + 2), (x, y), (x + 2, y)]
        elif self.current_piece.rotation == 3:  # 270 degrees
            corners = [(x + 2, y), (x + 2, y + 2), (x, y + 2), (x, y)]

        # Count filled corners
        filled = 0
        for cx, cy in corners:
            if not (0 <= cx < GRID_WIDTH and 0 <= cy < GRID_HEIGHT) or self.grid[cy][cx]:
                filled += 1

        # T-spin detection rules
        if mini:
            # Mini T-spin requires 2 filled corners and last move was rotation
            return filled >= 2 and self.last_rotation
        else:
            # Regular T-spin requires 3+ filled corners and last move was rotation
            return filled >= 3 and self.last_rotation

    def clear_lines(self):
        self.lines_to_clear = [i for i in range(len(self.grid)) if all(self.grid[i])]
        if self.lines_to_clear:
            self.clear_animation_timer = time.time()
            clear_sound.play()  # clear sound effects
            self.flash_alpha = 0
            self.flash_increasing = True

            # Check for T-spin before clearing
            is_tspin = self.check_t_spin()
            lines_cleared = len(self.lines_to_clear)

            # Base scoring
            if lines_cleared == 1:
                self.score += 100 * self.level
                self.floating_texts.append(FloatingText("SINGLE",
                                                        self.offset_x + GRID_WIDTH * BLOCK_SIZE // 2,
                                                        self.offset_y + GRID_HEIGHT * BLOCK_SIZE // 2,
                                                        GREEN))
            elif lines_cleared == 2:
                self.score += 300 * self.level

                self.floating_texts.append(FloatingText("DOUBLE",
                                                        self.offset_x + GRID_WIDTH * BLOCK_SIZE // 2,
                                                        self.offset_y + GRID_HEIGHT * BLOCK_SIZE // 2,
                                                        GREEN))
            elif lines_cleared == 3:
                self.score += 500 * self.level
                self.floating_texts.append(FloatingText("TRIPLE",
                                                        self.offset_x + GRID_WIDTH * BLOCK_SIZE // 2,
                                                        self.offset_y + GRID_HEIGHT * BLOCK_SIZE // 2,
                                                        YELLOW))
            elif lines_cleared == 4:
                self.score += 800 * self.level

                self.floating_texts.append(FloatingText("MONSTER STACK",
                                                        self.offset_x + GRID_WIDTH * BLOCK_SIZE // 2,
                                                        self.offset_y + GRID_HEIGHT * BLOCK_SIZE // 2,
                                                        RED))

            # Combo scoring
            if self.combo_count > 0:
                self.score += 50 * self.combo_count * self.level
                # BEGIN: Additions
                if self.combo_count > 1:
                    self.floating_texts.append(FloatingText(f"COMBO x{self.combo_count}",
                                                            self.offset_x + GRID_WIDTH * BLOCK_SIZE // 2,
                                                            self.offset_y + GRID_HEIGHT * BLOCK_SIZE // 2 + 30,
                                                            ORANGE))
                # END: Additions

            self.combo_count += 1
            # BEGIN: Additions
            # Create particles for line clear
            for line in self.lines_to_clear:
                for x in range(GRID_WIDTH):
                    for _ in range(5):  # 5 particles per block
                        self.particles.append(Particle(
                            self.offset_x + x * BLOCK_SIZE + BLOCK_SIZE // 2,
                            self.offset_y + line * BLOCK_SIZE + BLOCK_SIZE // 2
                        ))
            # END: Additions
        else:
            self.combo_count = 0  # Reset combo if no lines cleared

    def process_line_clear(self):
        if self.lines_to_clear:
            elapsed = time.time() - self.clear_animation_timer
            if elapsed > 0.5:
                for i in self.lines_to_clear:
                    del self.grid[i]
                    self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
                lines_cleared = len(self.lines_to_clear)
                self.lines += lines_cleared
                self.level = self.lines // 10 + 1
                self.fall_speed = max(0.05, 0.4 - (self.level * 0.3))  # Blocks fall faster as level increases
                self.lines_to_clear = []
                self.flash_alpha = 0

    def update(self):
        self.calculate_ghost_position()
        self.process_line_clear()

        # Check for win condition
        if self.score >= 1000:
            return "win"

        # Update fall speed based on level - smoother progression
        self.fall_speed = max(0.05, 0.4 - (self.level * 0.01))

        # Update movement speed to match fall speed
        self.update_movement_speed()

        if self.lines_to_clear:
            return True

        current_time = time.time()

        # Handle movement with improved delay system
        keys = pygame.key.get_pressed()

        # Check if movement keys are pressed
        left_pressed = keys[pygame.K_LEFT] or keys[pygame.K_a]
        right_pressed = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        down_pressed = keys[pygame.K_DOWN] or keys[pygame.K_s]

        # Handle movement with improved control
        if left_pressed or right_pressed or down_pressed:
            if current_time - self.last_move_time > self.move_delay:
                if left_pressed:
                    self.move(-1)
                if right_pressed:
                    self.move(1)
                if down_pressed:
                    if self.valid_position(self.current_piece.shape, self.current_piece.x, self.current_piece.y + 1):
                        self.current_piece.y += 1
                        self.last_valid_y = self.current_piece.y
                        self.soft_drop_points += 1
                        self.lock_timer = 0
                        self.last_move = "down"
                self.last_move_time = current_time
        else:
            # Reset move timer when no keys are pressed
            self.last_move_time = 0
            self.move_cooldown = 0

        # Handle piece falling with improved accuracy
        if current_time - self.last_time > self.fall_speed:
            if self.valid_position(self.current_piece.shape, self.current_piece.x, self.current_piece.y + 1):
                self.current_piece.y += 1
                self.lock_timer = 0
                self.last_was_tspin = False
            else:
                self.lock_timer += current_time - self.last_time
                # Dynamic lock delay based on recent moves
                current_lock_delay = self.lock_delay
                if self.last_move in ["left", "right", "down"]:
                    current_lock_delay += self.lock_delay_extension
                current_lock_delay = min(current_lock_delay, self.max_lock_delay)

                if self.lock_timer > current_lock_delay:
                    self.merge_piece()
                    self.clear_lines()
                    self.current_piece = self.next_pieces.pop(0)
                    self.next_pieces.append(Block())
                    self.can_hold = True
                    if not self.valid_position(self.current_piece.shape, self.current_piece.x, self.current_piece.y):
                        return False
            self.last_time = current_time

        # BEGIN: Additions
        # Update floating texts
        for text in self.floating_texts[:]:
            text.update()
            if text.alpha <= 0:
                self.floating_texts.remove(text)

        # Update particles
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)

        # Update score pulse animation
        if self.score_growing:
            self.score_pulse += 0.015
            if self.score_pulse >= 1.2:
                self.score_growing = False
        else:
            self.score_pulse -= 0.015
            if self.score_pulse <= 1.0:
                self.score_growing = True

        # Update level pulse animation
        if self.level_growing:
            self.level_pulse += 0.01
            if self.level_pulse >= 1.1:
                self.level_growing = False
        else:
            self.level_pulse -= 0.01
            if self.level_pulse <= 1.0:
                self.level_growing = True

        self.frame_count += 1
        # END: Additions

        return True

    def move(self, dx):
        current_time = time.time()

        # Check if enough time has passed since last move
        if current_time - self.move_cooldown < self.move_cooldown_time:
            return False

        # Store current position before move
        old_x = self.current_piece.x

        # Try the move
        if self.valid_position(self.current_piece.shape, self.current_piece.x + dx, self.current_piece.y):
            self.current_piece.x += dx
            self.last_valid_x = self.current_piece.x
            self.calculate_ghost_position()
            self.last_was_tspin = False
            self.last_move = "left" if dx < 0 else "right"
            self.move_cooldown = current_time
            return True
        return False

    def rotate(self):
        rotated = self.current_piece.rotate()
        current_rot = self.current_piece.rotation
        next_rot = (current_rot + 1) % 4
        shape_idx = self.current_piece.shape_idx

        # Wall kick tests for each rotation state
        wall_kicks = {
            # I-piece has special wall kicks
            0: {  # 0>>1 (clockwise) and 0>>3 (counter-clockwise)
                1: [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],
                3: [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)]
            },
            1: {  # R>>2 and R>>0
                2: [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)],
                0: [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)]
            },
            2: {  # 2>>3 and 2>>1
                3: [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],
                1: [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)]
            },
            3: {  # L>>0 and L>>2
                0: [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)],
                2: [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)]
            }
        }

        # For non-I pieces, use standard wall kicks
        if shape_idx != 0:  # Not I-piece
            wall_kicks = {
                0: {  # 0>>1 and 0>>3
                    1: [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
                    3: [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)]
                },
                1: {  # R>>2 and R>>0
                    2: [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
                    0: [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)]
                },
                2: {  # 2>>3 and 2>>1
                    3: [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
                    1: [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)]
                },
                3: {  # L>>0 and L>>2
                    0: [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
                    2: [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)]
                }
            }

        # Special case: O-piece doesn't rotate
        if shape_idx == 1:  # O-piece
            return False

        # Try each kick offset
        for offset_x, offset_y in wall_kicks[current_rot].get(next_rot, [(0, 0)]):
            new_x = self.current_piece.x + offset_x
            new_y = self.current_piece.y + offset_y

            # Additional check for right wall
            max_x = new_x + len(rotated[0])
            if max_x > GRID_WIDTH:
                offset_x -= (max_x - GRID_WIDTH)
                new_x = self.current_piece.x + offset_x

            if self.valid_position(rotated, new_x, new_y):
                self.current_piece.shape = rotated
                self.current_piece.x = new_x
                self.current_piece.y = new_y
                self.current_piece.rotation = next_rot
                self.calculate_ghost_position()
                self.last_rotation = True
                self.last_move = "rotate"

                # Check for T-spin conditions
                if shape_idx == 2:  # T-piece
                    self.last_was_tspin = self.check_t_spin()
                else:
                    self.last_was_tspin = False
                return True

        # If rotation failed, check for mini T-spin
        if shape_idx == 2:
            self.last_was_tspin = self.check_t_spin(mini=True)
        else:
            self.last_was_tspin = False

        return False

    def drop(self):
        lines_dropped = 0
        while self.valid_position(self.current_piece.shape, self.current_piece.x, self.current_piece.y + 1):
            self.current_piece.y += 1
            lines_dropped += 1
            self.soft_drop_points += 1  # Count as soft drop for scoring

        self.score += lines_dropped * 2  # Bonus points for hard drop
        self.merge_piece()
        self.clear_lines()
        self.current_piece = self.next_pieces.pop(0)
        self.next_pieces.append(Block())
        self.can_hold = True
        return self.valid_position(self.current_piece.shape, self.current_piece.x, self.current_piece.y)

    def hold(self):
        if self.can_hold:
            if self.hold_piece is None:
                self.hold_piece = Block()
                self.hold_piece.shape_idx = self.current_piece.shape_idx
                self.hold_piece.shape = SHAPES[self.current_piece.shape_idx]
                self.hold_piece.color = COLORS[self.current_piece.shape_idx]
                self.current_piece = self.next_pieces.pop(0)
                self.next_pieces.append(Block())
            else:
                self.current_piece.shape_idx, self.hold_piece.shape_idx = self.hold_piece.shape_idx, self.current_piece.shape_idx
                self.current_piece.shape, self.hold_piece.shape = self.hold_piece.shape, self.current_piece.shape
                self.current_piece.color, self.hold_piece.color = self.hold_piece.color, self.current_piece.color
            self.current_piece.x = GRID_WIDTH // 2 - len(self.current_piece.shape[0]) // 2
            self.current_piece.y = 0
            self.can_hold = False
            self.last_was_tspin = False  # Reset T-spin flag on hold

    def draw_grid(self, surface, offset_x, offset_y):
        text_map = {
            0: "PLAN",  # I-block
            1: "SYNC",  # O-block
            2: "LOOP",  # T-block
            3: "CODE",  # L-block
            4: "DOCS",  # J-block
            5: "ART",  # S-block
            6: "BUGS"  # Z-block
        }

        # Custom font for labels inside locked blocks
        block_font = pygame.font.Font("pixel_font.otf", int(BLOCK_SIZE * 0.45))

        # No background or border drawing here - handled by draw method for the combined box

        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                cell_value = self.grid[y][x]
                # Calculate position relative to the game grid offset (which is relative to the screen)
                rect = pygame.Rect(offset_x + x * BLOCK_SIZE,
                                   offset_y + y * BLOCK_SIZE,
                                   BLOCK_SIZE, BLOCK_SIZE)

                if cell_value:
                    color = COLORS[cell_value - 1]
                    # Draw the block using the existing modern block style
                    draw_modern_block(surface, color, rect, "", style="pixel")

                    # Draw label (keep existing label logic)
                    label = text_map.get(cell_value - 1, "")
                    if label:
                        text = block_font.render(label, True, BLACK)
                        tx = rect.left + (BLOCK_SIZE - text.get_width()) // 2
                        ty = rect.top + (BLOCK_SIZE - text.get_height()) // 2
                        surface.blit(text, (tx, ty))
                else:
                    # Empty cell - draw pure black grid lines
                    # Draw grid lines within the grid area with increased thickness
                    pygame.draw.line(surface, GRID_LINE_COLOR, (rect.left, rect.top), (rect.right, rect.top), 2)
                    pygame.draw.line(surface, GRID_LINE_COLOR, (rect.left, rect.top), (rect.left, rect.bottom), 2)
                    # Only draw rightmost vertical line if it's the last column in the grid
                    if x == GRID_WIDTH - 1:
                        pygame.draw.line(surface, GRID_LINE_COLOR, (rect.right, rect.top), (rect.right, rect.bottom), 2)
                    # Only draw bottom horizontal line if it's the last row in the grid
                    if y == GRID_HEIGHT - 1:
                        pygame.draw.line(surface, GRID_LINE_COLOR, (rect.left, rect.bottom), (rect.right, rect.bottom), 2)

    def draw_info(self, surface, info_x, info_y):
        # No background or border drawing here - handled by draw method for the combined box

        # Calculate the inner usable width for sections, accounting for info panel border thickness and section padding
        # Use INFO_PANEL_WIDTH here as it's the defined width for the info area within the combined box
        inner_panel_width = INFO_PANEL_WIDTH - 2 * BORDER_THICKNESS
        section_inner_width = inner_panel_width - 2 * SECTION_PADDING

        # Vertical positioning variables, relative to the top of the info panel area (info_y)
        # Start below the top border thickness and section margin of the *combined* box, relative to info_y
        current_y_offset = BORDER_THICKNESS + SECTION_MARGIN
        section_spacing = 20 # Adjusted spacing for slimmer panel

        # --- Hold Piece Section ---
        hold_label = font.render("HOLD", True, LABEL_COLOR)
        # Draw label relative to info_x and current_y_offset within the info panel area
        surface.blit(hold_label, (info_x + SECTION_PADDING, info_y + current_y_offset))

        hold_box_top_offset = current_y_offset + hold_label.get_height() + 8  # Adjusted spacing for slimmer panel
        # Position the hold box relative to info_x and info_y, using section_inner_width
        hold_box_rect = pygame.Rect(info_x + SECTION_PADDING, info_y + hold_box_top_offset,
                                    section_inner_width, HOLD_NEXT_BOX_HEIGHT + 5)  # Adjusted height for slimmer panel
        pygame.draw.rect(surface, DARK_GRAY, hold_box_rect, border_radius=5)
        pygame.draw.rect(surface, SECTION_BORDER_COLOR, hold_box_rect, SECTION_BORDER_THICKNESS, border_radius=5)

        if self.hold_piece:
            # Center the hold piece in its box (positions are relative to the screen, calculated from hold_box_rect)
            hold_piece_width = len(self.hold_piece.shape[0]) * MINI_BLOCK_SIZE
            hold_piece_height = len(self.hold_piece.shape) * MINI_BLOCK_SIZE
            hold_piece_x = hold_box_rect.centerx - hold_piece_width // 2
            hold_piece_y = hold_box_rect.centery - hold_piece_height // 2

            for y, row in enumerate(self.hold_piece.shape):
                for x, cell in enumerate(row):
                    if cell:
                        # Draw mini block relative to its calculated position
                        self.draw_mini_block_with_text(
                            surface, self.hold_piece.color,
                            hold_piece_x + x * MINI_BLOCK_SIZE,
                            hold_piece_y + y * MINI_BLOCK_SIZE,
                            MINI_BLOCK_SIZE, ""
                        )

        current_y_offset = hold_box_top_offset + (HOLD_NEXT_BOX_HEIGHT + 5) + section_spacing # Update offset for next section with adjusted height

        # --- Next Pieces Section ---
        next_label = font.render("NEXT", True, LABEL_COLOR)
        # Draw label relative to info_x and current_y_offset within the info panel area
        surface.blit(next_label, (info_x + SECTION_PADDING, info_y + current_y_offset))

        # Calculate required height for the next box to fit 3 pieces vertically without overlap, with specific padding and gap
        next_box_vertical_padding = 12  # Adjusted padding for slimmer panel
        gap_between_pieces = 15  # Adjusted gap for slimmer panel
        space_for_one_tallest_piece = MINI_BLOCK_SIZE * 4
        num_next_pieces_to_show = 3

        # Height of each piece slot (tallest piece and gap)
        next_piece_slot_total_height = space_for_one_tallest_piece + gap_between_pieces

        # Total height needed for 3 slots and top/bottom padding
        next_box_height = (next_piece_slot_total_height * num_next_pieces_to_show) + next_box_vertical_padding * 2

        next_box_top_offset = current_y_offset + next_label.get_height() + 8  # Adjusted spacing for slimmer panel
        # Position the next box relative to info_x and info_y, using section_inner_width
        next_box_rect = pygame.Rect(info_x + SECTION_PADDING, info_y + next_box_top_offset,
                                    section_inner_width, next_box_height)
        pygame.draw.rect(surface, DARK_GRAY, next_box_rect, border_radius=5)
        pygame.draw.rect(surface, SECTION_BORDER_COLOR, next_box_rect, SECTION_BORDER_THICKNESS, border_radius=5)

        # Draw next pieces inside the box (positions are relative to the screen, calculated from next_box_rect)
        next_piece_start_y = next_box_rect.top + next_box_vertical_padding

        for i, piece in enumerate(self.next_pieces[:num_next_pieces_to_show]):
            piece_width = len(piece.shape[0]) * MINI_BLOCK_SIZE
            piece_height = len(piece.shape) * MINI_BLOCK_SIZE
            piece_x = next_box_rect.centerx - piece_width // 2
            piece_y = next_piece_start_y + (next_piece_slot_total_height * i) + (space_for_one_tallest_piece - piece_height) // 2

            for y, row in enumerate(piece.shape):
                for x, cell in enumerate(row):
                    if cell:
                        # Draw mini block relative to its calculated position
                        self.draw_mini_block_with_text(
                            surface, piece.color,
                            piece_x + x * MINI_BLOCK_SIZE,
                            piece_y + y * MINI_BLOCK_SIZE,
                            MINI_BLOCK_SIZE, ""
                        )

        # No stats section here - stats are now displayed on the left side of the screen

    def draw_flashing_lines(self, surface, offset_x, offset_y):
        if self.lines_to_clear:
            # Flash animation
            if self.flash_increasing:
                self.flash_alpha += 10
                if self.flash_alpha >= 200:
                    self.flash_increasing = False
            else:
                self.flash_alpha -= 10
                if self.flash_alpha <= 0:
                    self.flash_increasing = True

            # Draw flashing lines
            for line in self.lines_to_clear:
                s = pygame.Surface((GRID_WIDTH * BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
                s.fill((255, 255, 255, self.flash_alpha))
                surface.blit(s, (offset_x, offset_y + line * BLOCK_SIZE))

    def draw_game_stats(self, surface):
        # Create a semi-transparent overlay for the stats on the left side of the screen
        stats_width = 150  # Increased width for more space
        stats_height = 190  # Reduced height since we're removing combo
        stats_x = 8  # Slightly increased distance from edge
        stats_y = (SCREEN_HEIGHT - stats_height) // 2

        stats_overlay = pygame.Surface((stats_width, stats_height), pygame.SRCALPHA)
        stats_overlay.fill((30, 30, 0, 180))  # Semi-transparent black background
        surface.blit(stats_overlay, (stats_x, stats_y))

        # Draw border around the stats panel
        pygame.draw.rect(surface, (100, 100, 100, 200), (stats_x, stats_y, stats_width, stats_height), 2, border_radius=5)

        # Vertical spacing between stats
        padding_top = 30  # Increased top padding for better spacing
        line_height = 70  # Increased line height for better separation
        value_offset = 35  # Increased space between label and value to prevent overlap

        # Draw score
        score_label = font.render("SCORE", True, BRIGHT_WHITE)
        score_value = font.render(f"{self.score}", True, BRIGHT_WHITE)
        # Center the label horizontally
        surface.blit(score_label, (stats_x + (stats_width - score_label.get_width()) // 2, stats_y + padding_top))
        # Center the value horizontally
        surface.blit(score_value, (stats_x + (stats_width - score_value.get_width()) // 2, stats_y + padding_top + value_offset))

        # Draw level
        level_label = font.render("LEVEL", True, BRIGHT_WHITE)
        level_value = font.render(f"{self.level}", True, BRIGHT_WHITE)
        # Center the label horizontally
        surface.blit(level_label, (stats_x + (stats_width - level_label.get_width()) // 2, stats_y + padding_top + line_height))
        # Center the value horizontally
        surface.blit(level_value, (stats_x + (stats_width - level_value.get_width()) // 2, stats_y + padding_top + line_height + value_offset))

    def draw_mini_block_with_text(self, surface, color, x, y, size, text):
        rect = pygame.Rect(x, y, size, size)

        # Create surface for the mini block
        block_surf = pygame.Surface((size, size), pygame.SRCALPHA)

        # Define pixel size for mini blocks
        pixel_size = 2

        # Calculate colors for pixel art effect
        light_color = tuple(min(255, c + 80) for c in color)
        dark_color = tuple(max(0, c - 80) for c in color)

        # Fill the main block area
        pygame.draw.rect(block_surf, color, (pixel_size, pixel_size,
                                             size - 2 * pixel_size, size - 2 * pixel_size))

        # Draw pixel art edges
        # Top light edge
        pygame.draw.rect(block_surf, light_color, (0, 0, size - pixel_size, pixel_size))
        pygame.draw.rect(block_surf, light_color, (0, 0, pixel_size, size - pixel_size))

        # Bottom dark edge
        pygame.draw.rect(block_surf, dark_color, (pixel_size, size - pixel_size,
                                                  size - pixel_size, pixel_size))
        pygame.draw.rect(block_surf, dark_color, (size - pixel_size, pixel_size,
                                                  pixel_size, size - pixel_size))

        # Add corner pixels
        pygame.draw.rect(block_surf, color, (0, 0, pixel_size, pixel_size))
        pygame.draw.rect(block_surf, color, (size - pixel_size, 0, pixel_size, pixel_size))
        pygame.draw.rect(block_surf, color, (0, size - pixel_size, pixel_size, pixel_size))
        pygame.draw.rect(block_surf, dark_color, (size - pixel_size, size - pixel_size,
                                                  pixel_size, pixel_size))

        # Apply the block to the surface
        surface.blit(block_surf, (x, y))

        # Add text with improved visibility
        if text:
            mini_font = pygame.font.Font("pixel_font.otf", int(size * 0.4))  # Slightly smaller text

            # Create text with outline for better visibility
            text_surf = mini_font.render(text, True, WHITE)  # White text
            text_rect = text_surf.get_rect(center=(x + size // 2, y + size // 2))

            # Draw dark outline
            outline_size = 1  # Smaller outline for mini blocks
            for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:  # Diagonal outlines
                surface.blit(text_surf, (text_rect.x + dx * outline_size,
                                         text_rect.y + dy * outline_size))
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:  # Cross outlines
                surface.blit(text_surf, (text_rect.x + dx * outline_size,
                                         text_rect.y + dy * outline_size))

            # Draw the main text
            text_surf = mini_font.render(text, True, BLACK)  # Black main text
            surface.blit(text_surf, text_rect)

    def draw(self, surface):
        video_frame = get_next_video_game()
        screen.blit(video_frame, (0, 0))

        # Calculate dimensions for the combined game and info box content area
        gap_between_grid_and_info = 10 # Matches value in __init__
        combined_content_width = GRID_WIDTH * BLOCK_SIZE + gap_between_grid_and_info + INFO_PANEL_WIDTH
        combined_content_height = GRID_HEIGHT * BLOCK_SIZE

        # Calculate total size including border
        total_box_width = combined_content_width + 2 * BORDER_THICKNESS
        total_box_height = combined_content_height + 2 * BORDER_THICKNESS

        # Calculate the top-left corner of the combined box on the screen
        combined_box_x = (SCREEN_WIDTH - total_box_width) // 2
        combined_box_y = (SCREEN_HEIGHT - total_box_height) // 2

        # Draw the background for the combined box
        combined_rect = pygame.Rect(combined_box_x, combined_box_y, total_box_width, total_box_height)
        pygame.draw.rect(surface, GRID_BACKGROUND_COLOR, combined_rect)

        # Draw the outer border for the combined box
        pygame.draw.rect(surface, BORDER_COLOR, combined_rect, BORDER_THICKNESS, border_radius=BORDER_RADIUS)

        # Draw the game grid content
        # The grid's top-left is offset from the combined box's top-left by the border thickness
        grid_draw_x = combined_box_x + BORDER_THICKNESS
        grid_draw_y = combined_box_y + BORDER_THICKNESS
        # Pass these drawing coordinates to draw_grid (will need to modify draw_grid signature)
        self.draw_grid(surface, grid_draw_x, grid_draw_y)

        # Draw the info panel content
        # The info panel's top-left is offset from the combined box's top-left
        # by the border thickness + grid width + gap
        info_panel_draw_x = combined_box_x + BORDER_THICKNESS + GRID_WIDTH * BLOCK_SIZE + gap_between_grid_and_info
        info_panel_draw_y = combined_box_y + BORDER_THICKNESS
        # Pass these drawing coordinates to draw_info
        self.draw_info(surface, info_panel_draw_x, info_panel_draw_y)

        # Drawing pieces and effects should now use the grid_draw_x and grid_draw_y as their offset
        ghost = Block()
        ghost.shape = self.current_piece.shape
        ghost.x = self.current_piece.x
        ghost.y = self.ghost_y
        ghost.color = self.current_piece.color
        # Draw ghost piece relative to the grid drawing offset
        draw_glowing_ghost(surface, ghost, grid_draw_x, grid_draw_y)

        # Draw current piece relative to the grid drawing offset
        self.current_piece.draw(surface, grid_draw_x, grid_draw_y)
        self.current_piece.draw_landing_effect(surface, grid_draw_x, grid_draw_y)

        # Draw flashing lines relative to the grid drawing offset
        self.draw_flashing_lines(surface, grid_draw_x, grid_draw_y) # Will need to modify draw_flashing_lines signature

        for text in self.floating_texts:
            # Floating texts should be centered in the grid area, which is handled in the FloatingText draw method
            # No change needed here as FloatingText already uses absolute coordinates for centering in the grid area
            text.draw(surface)

        # Draw particles relative to the grid area, which is handled in the Particle draw method
        # No change needed here as Particle drawing seems relative to the particle's position which is in grid coordinates
        for particle in self.particles:
            particle.draw(surface)

        # Draw score, level, and combo in a more visible format at the top of the screen
        self.draw_game_stats(surface)


def draw_menu(selected_option):
    # Animated background
    video_frame = get_next_video_frame()
    screen.blit(video_frame, (0, 0))

    # Title with pulse animation
    title_text = big_font.render("TASKTRIS", True, GREEN)
    pulse = 1.0 + 0.05 * math.sin(pygame.time.get_ticks() / 200)
    scaled_title = pygame.transform.scale_by(title_text, pulse)
    screen.blit(scaled_title, (SCREEN_WIDTH // 2 - scaled_title.get_width() // 2, 100))

    # Menu options with selection animation
    options = ["Start Game", "Settings", "About"]
    for i, option in enumerate(options):
        y_offset = 0
        if i == selected_option:
            y_offset = 5 * math.sin(pygame.time.get_ticks() / 200)

        y_pos = 250 + i * 80
        color = BRIGHT_WHITE if i == selected_option else GRAY
        option_text = font.render(option, True, color)
        text_rect = option_text.get_rect(center=(SCREEN_WIDTH // 2, y_pos + y_offset))
        screen.blit(option_text, text_rect)

        if i == selected_option:
            indicator_size = 10 + 3 * math.sin(pygame.time.get_ticks() / 150)
            pygame.draw.polygon(screen, GREEN, [
                (text_rect.left - 30, text_rect.centery),
                (text_rect.left - 30 - indicator_size, text_rect.centery - indicator_size),
                (text_rect.left - 30 - indicator_size, text_rect.centery + indicator_size)
            ])
            pygame.draw.polygon(screen, GREEN, [
                (text_rect.right + 30, text_rect.centery),
                (text_rect.right + 30 + indicator_size, text_rect.centery - indicator_size),
                (text_rect.right + 30 + indicator_size, text_rect.centery + indicator_size)
            ])

    version_text = small_font.render("Use the UP and DOWN arrow or W/S keys to navigate. Press ENTER to select.", True, WHITE)
    screen.blit(version_text, (20, SCREEN_HEIGHT - 30))

    pygame.display.flip()


def draw_pause_menu(selected_option):
    # Semi-transparent overlay (same as before)
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    # Pulsing title (now positioned like main menu)
    title_text = big_font.render("PAUSED", True, WHITE)
    pulse = 1.0 + 0.05 * math.sin(pygame.time.get_ticks() / 200)
    scaled_title = pygame.transform.scale_by(title_text, pulse)
    screen.blit(scaled_title, (SCREEN_WIDTH // 2 - scaled_title.get_width() // 2, 100))  # Same Y position as main menu

    # Menu options with same layout as main menu
    options = ["Resume", "Restart", "Settings", "Main Menu"]

    for i, option in enumerate(options):
        y_offset = 0
        if i == selected_option:
            y_offset = 5 * math.sin(pygame.time.get_ticks() / 200)  # Same floating effect as main menu

        y_pos = 250 + i * 80  # Same spacing as main menu (250 start, 80 px between)
        color = BRIGHT_WHITE if i == selected_option else GRAY  # Same colors

        option_text = font.render(option, True, color)
        text_rect = option_text.get_rect(center=(SCREEN_WIDTH // 2, y_pos + y_offset))
        screen.blit(option_text, text_rect)

        # Same selection indicators as main menu
        if i == selected_option:
            indicator_size = 10 + 3 * math.sin(pygame.time.get_ticks() / 150)
            pygame.draw.polygon(screen, GREEN, [
                (text_rect.left - 30, text_rect.centery),
                (text_rect.left - 30 - indicator_size, text_rect.centery - indicator_size),
                (text_rect.left - 30 - indicator_size, text_rect.centery + indicator_size)
            ])
            pygame.draw.polygon(screen, GREEN, [
                (text_rect.right + 30, text_rect.centery),
                (text_rect.right + 30 + indicator_size, text_rect.centery - indicator_size),
                (text_rect.right + 30 + indicator_size, text_rect.centery + indicator_size)
            ])

    # Same bottom text position as main menu
    version_text = small_font.render("Use the UP and DOWN arrow or W/S keys to navigate. Press ENTER to select.", True, WHITE)
    screen.blit(version_text, (20, SCREEN_HEIGHT - 30))

    pygame.display.flip()


def draw_game_over_menu(selected_option, score):
    # Animated Background
    video_frame = get_next_video_game_over()
    screen.blit(video_frame, (0, 0))

    # Pulsing title
    title_text = big_font.render("GAME OVER", True, NEON_RED)
    pulse = 1.0 + 0.05 * math.sin(pygame.time.get_ticks() / 200)
    scaled_title = pygame.transform.scale_by(title_text, pulse)
    screen.blit(scaled_title, (SCREEN_WIDTH // 2 - scaled_title.get_width() // 2, 100))

    # Score display with animation
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 180))

    # Animated menu options
    options = ["Play Again", "Main Menu"]
    for i, option in enumerate(options):
        y_offset = 0
        if i == selected_option:
            y_offset = 5 * math.sin(pygame.time.get_ticks() / 200)

        y_pos = 250 + i * 80
        color = WHITE if i == selected_option else GRAY
        option_text = font.render(option, True, color)
        text_rect = option_text.get_rect(center=(SCREEN_WIDTH // 2, y_pos + y_offset))
        screen.blit(option_text, text_rect)

        if i == selected_option:
            indicator_size = 10 + 3 * math.sin(pygame.time.get_ticks() / 150)
            pygame.draw.polygon(screen, NEON_RED, [
                (text_rect.left - 30, text_rect.centery),
                (text_rect.left - 30 - indicator_size, text_rect.centery - indicator_size),
                (text_rect.left - 30 - indicator_size, text_rect.centery + indicator_size)
            ])
            pygame.draw.polygon(screen, NEON_RED, [
                (text_rect.right + 30, text_rect.centery),
                (text_rect.right + 30 + indicator_size, text_rect.centery - indicator_size),
                (text_rect.right + 30 + indicator_size, text_rect.centery + indicator_size)
            ])

    pygame.display.flip()


# Confetti particle class for win screen
class ConfettiParticle:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(-50, SCREEN_HEIGHT // 2)
        self.size = random.randint(4, 10)
        self.color = random.choice([
            (50, 255, 150), (0, 255, 0), (0, 200, 255), (255, 230, 0), (255, 100, 0), (255, 50, 50), (255, 255, 255)
        ])
        self.speed_x = random.uniform(-1.5, 1.5)
        self.speed_y = random.uniform(2, 5)
        self.angle = random.uniform(0, 2 * math.pi)
        self.angular_speed = random.uniform(-0.1, 0.1)

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.angle += self.angular_speed
        if self.y > SCREEN_HEIGHT:
            self.y = random.randint(-50, 0)
            self.x = random.randint(0, SCREEN_WIDTH)

    def draw(self, surface):
        points = []
        for i in range(4):
            angle = self.angle + i * math.pi / 2
            px = self.x + self.size * math.cos(angle)
            py = self.y + self.size * math.sin(angle)
            points.append((px, py))
        pygame.draw.polygon(surface, self.color, points)


# Win screen state variables
win_confetti = [ConfettiParticle() for _ in range(80)]
win_start_time = None


def draw_win_screen():
    global win_confetti, win_start_time
    screen.fill((8, 16, 8))  # Very dark green/black

    # Draw confetti
    for particle in win_confetti:
        particle.update()
        particle.draw(screen)

    win_text = win_font.render("YOU WIN", True, GOLD)
    glow_surface = pygame.Surface((win_text.get_width() + 40, win_text.get_height() + 40), pygame.SRCALPHA)
    for i in range(1, 4):  # Fewer layers
        alpha = max(10, 40 - i * 10)  # Lower alpha
        glow = win_font.render("YOU WIN", True, GOLD)
        glow_surface.blit(pygame.transform.scale(glow, (win_text.get_width() + i * 4, win_text.get_height() + i * 4)),
                          (20 - i * 2, 20 - i * 2))
    glow_surface.blit(win_text, (20, 20))
    screen.blit(glow_surface, (SCREEN_WIDTH // 2 - glow_surface.get_width() // 2, SCREEN_HEIGHT // 2 - 120))

    # After 8 seconds, show 'press anywhere to continue'
    if win_start_time is not None:
        elapsed = time.time() - win_start_time
        if elapsed > 8:
            blink = int(time.time() * 2) % 2 == 0
            if blink:
                continue_text = font.render("press anywhere to continue", True, WHITE)
                screen.blit(continue_text,
                            (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, SCREEN_HEIGHT // 2 + 40))

    pygame.display.flip()


def draw_about_screen():
    # Clear screen with black background
    screen.fill(BLACK)

    # Title
    title = big_font.render("ABOUT", True, GREEN)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

    # Controls information (text only)
    controls = [
        "A GAME CREATED BY:",
        "RALPH CEDRICK G. BAYANAY",
        "JEI GRAYWAYNE C. GARCE",
        "JAMES P. ALVAREZ"
    ]

    # Draw controls
    for i, control in enumerate(controls):
        control_text = font.render(control, True, WHITE)
        screen.blit(control_text, (SCREEN_WIDTH // 2 - control_text.get_width() // 2, 200 + i * 50))

    # Continue prompt
    continue_text = font.render("PRESS ANY KEY TO GO BACK TO MENU", True, WHITE)
    screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, SCREEN_HEIGHT - 100))

    pygame.display.flip()

    # Wait for any key press
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                waiting = False
        pygame.time.delay(50)


def Tasktris():
    global win_start_time, win_confetti
    clock = pygame.time.Clock()
    state = "menu"
    selected_option = 0
    game = None
    game_over_selected = 0
    win_selected = 0
    pause_selected = 0
    settings_selected = 0
    settings_from_pause = False
    music_position = 0
    game_over_time = 0
    global current_volume, volume_key_held, volume_key_timer

    current_volume = 12
    volume_key_held = False
    volume_key_timer = 0
    volume_key_delay = 0.3
    volume_key_repeat = 0.05

    while True:
        current_time = time.time()

        try:
            if state == "menu":
                draw_menu(selected_option)

            elif state == "play":
                screen.fill(BLACK)
                if game is None:
                    game = Game()
                update_result = game.update()
                if update_result == "win":
                    save_highscore(game.score)
                    state = "win"
                    win_selected = 0
                    pygame.mixer.music.stop()
                    win_sound.play()
                elif not update_result:
                    save_highscore(game.score)
                    state = "game_over_transition"
                    game_over_selected = 0
                    pygame.mixer.music.stop()
                    game_over_sound.play()
                    game_over_time = current_time
                else:
                    game.draw(screen)
                pygame.display.flip()

            elif state == "game_over_transition":
                elapsed = current_time - game_over_time
                sound_length = game_over_sound.get_length()

                screen.fill(BLACK)
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                screen.blit(overlay, (0, 0))

                pulse = 1.0 + 0.1 * math.sin(pygame.time.get_ticks() / 200)
                title = big_font.render("GAME OVER", True, RED)
                scaled_title = pygame.transform.scale_by(title, pulse)
                screen.blit(scaled_title, (SCREEN_WIDTH // 2 - scaled_title.get_width() // 2, 200))

                progress_width = 400 * min(1.0, elapsed / sound_length)
                pygame.draw.rect(screen, GRAY, (SCREEN_WIDTH // 2 - 200, 300, 400, 20), 2)
                pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH // 2 - 200, 300, progress_width, 20))

                if elapsed >= sound_length:
                    continue_text = font.render("Press any key to continue...", True, WHITE)
                    screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, 350))

                pygame.display.flip()

                if elapsed >= sound_length:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            return
                        elif event.type == pygame.KEYDOWN:
                            change_music(GAME_OVER_MUSIC, position=0.0)
                            state = "game_over"

            elif state == "pause":
                draw_pause_menu(pause_selected)

            elif state == "game_over":
                draw_game_over_menu(game_over_selected, game.score if game else 0)

            elif state == "settings":
                draw_settings_menu(settings_selected, settings_from_pause)

            elif state == "win":
                if win_start_time is None:
                    win_start_time = time.time()
                draw_win_screen()
                elapsed = time.time() - win_start_time
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                        if elapsed > 8:
                            # Reset win state variables for next win
                            win_start_time = None
                            win_confetti = [ConfettiParticle() for _ in range(80)]
                            game = None
                            state = "menu"
                            selected_option = 0
                            # Start menu music immediately when returning to menu
                            pygame.mixer.music.stop()  # Stop any playing music
                            change_music(MENU_MUSIC, position=0.0)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

                elif event.type == pygame.KEYDOWN:
                    if state == "menu":
                        if event.key in (pygame.K_UP, pygame.K_w):
                            selected_option = (selected_option - 1) % 3
                            menu_select_sound.play()
                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            selected_option = (selected_option + 1) % 3
                            menu_select_sound.play()
                        elif event.key == pygame.K_RETURN:
                            if selected_option == 0:
                                show_controls_screen(screen)
                                game = Game()
                                state = "play"
                                change_music(GAME_MUSIC, position=0.0)
                            elif selected_option == 1:  # Settings
                                settings_from_pause = False
                                settings_selected = 0
                                state = "settings"
                            elif selected_option == 2:  # About
                                draw_about_screen()
                    elif state == "play":
                        if event.key in (pygame.K_UP, pygame.K_w):
                            game.rotate()
                        elif event.key == pygame.K_SPACE:
                            game.drop()
                        elif event.key == pygame.K_LSHIFT:
                            game.hold()
                        elif event.key == pygame.K_ESCAPE:
                            state = "pause"
                            pause_selected = 0
                            pause_sound.play()
                            change_music(PAUSE_MUSIC)

                    elif state == "pause":
                        if event.key in (pygame.K_UP, pygame.K_w):
                            pause_selected = (pause_selected - 1) % 4
                            menu_select_sound.play()
                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            pause_selected = (pause_selected + 1) % 4
                            menu_select_sound.play()
                        elif event.key == pygame.K_RETURN:
                            if pause_selected == 0:
                                state = "play"
                                unpause_sound.play()
                                change_music(GAME_MUSIC)
                            elif pause_selected == 1:
                                game = Game()
                                state = "play"
                                change_music(GAME_MUSIC)
                            elif pause_selected == 2:  # Settings
                                settings_from_pause = True
                                settings_selected = 0
                                state = "settings"
                            elif pause_selected == 3:
                                state = "menu"
                                selected_option = 0
                                change_music(MENU_MUSIC, position=0.0)
                        elif event.key == pygame.K_ESCAPE:
                            state = "play"
                            unpause_sound.play()
                            change_music(GAME_MUSIC)

                    elif state == "game_over":
                        if event.key in (pygame.K_UP, pygame.K_w):
                            game_over_selected = (game_over_selected - 1) % 2
                            menu_select_sound.play()
                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            game_over_selected = (game_over_selected + 1) % 2
                            menu_select_sound.play()
                        elif event.key == pygame.K_RETURN:
                            if game_over_selected == 0:
                                game = Game()
                                state = "play"
                                change_music(GAME_MUSIC, position=0.0)
                            elif game_over_selected == 1:
                                state = "menu"
                                selected_option = 0
                                change_music(MENU_MUSIC, position=0.0)
                    elif state == "settings":
                        if event.key in (pygame.K_UP, pygame.K_w):
                            settings_selected = (settings_selected - 1) % 3
                            menu_select_sound.play()
                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            settings_selected = (settings_selected + 1) % 3
                            menu_select_sound.play()
                        elif event.key == pygame.K_RETURN:
                            if settings_selected == 0:  # Volume adjustment
                                pass  # Handled by key hold
                            elif settings_selected == 1:  # View Controls
                                show_controls_screen_settings(screen)
                            elif settings_selected == 2:  # Back
                                state = "pause" if settings_from_pause else "menu"
                        elif event.key in (pygame.K_LEFT, pygame.K_RIGHT) and settings_selected == 0:
                            volume_key_held = True
                            volume_key_timer = current_time + volume_key_delay
                            if event.key == pygame.K_LEFT:
                                current_volume = max(0, current_volume - 1)
                            else:
                                current_volume = min(VOLUME_LEVELS, current_volume + 1)
                            pygame.mixer.music.set_volume(current_volume / VOLUME_LEVELS)
                        elif event.key == pygame.K_ESCAPE:
                            state = "pause" if settings_from_pause else "menu"

                elif event.type == pygame.KEYUP:
                    if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        volume_key_held = False

            # Handle continuous volume adjustment when key is held
            if volume_key_held and current_time > volume_key_timer:
                keys = pygame.key.get_pressed()
                if (state == "menu" and selected_option == 1) or \
                        (state == "pause" and pause_selected == 2) or \
                        (state == "settings" and settings_selected == 0):
                    if keys[pygame.K_LEFT]:
                        current_volume = max(0, current_volume - 1)
                        pygame.mixer.music.set_volume(current_volume / VOLUME_LEVELS)
                        volume_key_timer = current_time + volume_key_repeat
                    elif keys[pygame.K_RIGHT]:
                        current_volume = min(VOLUME_LEVELS, current_volume + 1)
                        pygame.mixer.music.set_volume(current_volume / VOLUME_LEVELS)
                        volume_key_timer = current_time + volume_key_repeat

        except Exception as e:
            print(f"Error occurred: {e}")
            pygame.quit()
            exit()

        clock.tick(60)


if __name__ == "__main__":
    Tasktris()
