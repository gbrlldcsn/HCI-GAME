import pygame
from pygame.locals import *
import random
import os
import sys

pygame.init()
clock = pygame.time.Clock()
fps = 60

# Screen setup
screen_width = 1280
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Cramming Collapse')

# Font and colors
white = (255, 255, 255)
gray = (150, 150, 150)  # Color for hover effects
yellow = (255, 255, 0)  # Color for highlighted buttons
blue = (100, 150, 255)  # Color for loading bar

font_path = os.path.join(os.path.dirname(__file__), 'Assets', 'Fonts', 'Terraria.ttf')
font = pygame.font.Font(font_path, 40)
small_font = pygame.font.Font(font_path, 24)  # Smaller Terraria font for instructions

# Game variables
ground_scroll = 0
bg_scroll = 0  # New background scroll variable
scroll_speed = 4
bg_scroll_speed = 1  # Slower scroll speed for background
flying = False
game_over = False
paused = False  # Pause variable
pipe_gap = 150
pipe_frequency = 1500
last_pipe = pygame.time.get_ticks() - pipe_frequency
pause_time_offset = 0  # Track time spent paused
pause_start_time = 0  # Global variable for pause timing
score = 0
best_score = 0
volume = 0.3

# Menu navigation variables
menu_selection = 0  # 0=Start, 1=Settings, 2=Exit
settings_selection = 0  # 0=Volume+, 1=Volume-, 2=Back
pause_selection = 0  # 0=Continue, 1=Restart, 2=Main Menu
game_over_selection = 0  # 0=Play Again, 1=Menu

# Game over delay variables
game_over_time = 0  # Time when game over occurred
game_over_delay = 3000  # Delay in milliseconds (3 seconds)
show_game_over_screen = False  # Whether to show the game over menu

# Countdown variables
countdown_start_time = 0
countdown_duration = 3
countdown_active = False
show_fly_hint = True
last_countdown_value = -1

# Loading screen variables
loading_progress = 0
loading_speed = 2  # Progress per frame
loading_complete = False
loading_messages = [
    "Loading assets...",
    "Preparing backgrounds...",
    "Loading bird sprites...",
    "Setting up pipes...",
    "Loading audio...",
    "Initializing game...",
    "Almost ready...",
    "Ready to fly!"
]
current_loading_message = 0
loading_message_timer = 0
loading_message_interval = 20  # Frames between message changes

# Game state
game_state = "loading"  # Start with loading screen
victory = False  # Track if player has won

# Background animation variables
bg_animation_timer = 0
bg_animation_speed = 10  # Frames to wait before switching (lower = faster animation)
bg_frame_index = 0

# Load day and night backgrounds with animation support
bg_images = []
bg_day_frames = []  # Store animated frames for day background
bg_night_frames = []  # Store animated frames for night background (if any)

# Try to load animated day background frames
try:
    # Try to load multiple day background frames (daybg1.png, daybg2.png, daybg3.png, etc.)
    day_frame_count = 0
    for i in range(1, 10):  # Try up to 9 frames
        try:
            frame_path = f'Assets/Background/daybg{i}.png'
            if os.path.exists(frame_path):
                bg_frame = pygame.image.load(frame_path).convert()
                bg_frame = pygame.transform.scale(bg_frame, (screen_width, screen_height))
                bg_day_frames.append(bg_frame)
                day_frame_count += 1
            else:
                break  # Stop when we can't find more frames
        except:
            break

    # If no animated frames found, try the original daybg4.png
    if day_frame_count == 0:
        try:
            bg_day = pygame.image.load('Assets/Background/daybg4.png').convert()
            bg_day = pygame.transform.scale(bg_day, (screen_width, screen_height))
            bg_day_frames.append(bg_day)
        except:
            # Create fallback day background
            bg_day = pygame.Surface((screen_width, screen_height))
            bg_day.fill((135, 206, 235))  # Sky blue
            bg_day_frames.append(bg_day)

    print(f"Loaded {len(bg_day_frames)} day background frames")

except:
    # Fallback to a simple colored background if image loading fails
    bg_day = pygame.Surface((screen_width, screen_height))
    bg_day.fill((135, 206, 235))  # Sky blue
    bg_day_frames.append(bg_day)

# Try to load night background (static for now, but can be extended for animation)
try:
    nightbg_path = 'Assets/Background/nightb.png'
    if os.path.exists(nightbg_path):
        bg_night = pygame.image.load(nightbg_path).convert()
        bg_night = pygame.transform.scale(bg_night, (screen_width, screen_height))
        bg_night_frames.append(bg_night)
    else:
        # Create a darkened version of the first day frame for night
        bg_night = bg_day_frames[0].copy()
        night_overlay = pygame.Surface((screen_width, screen_height))
        night_overlay.fill((20, 20, 60))  # Dark blue tint
        night_overlay.set_alpha(120)
        bg_night.blit(night_overlay, (0, 0))
        bg_night_frames.append(bg_night)
except:
    # Fallback to a darkened day background if image loading fails
    bg_night = bg_day_frames[0].copy()
    night_overlay = pygame.Surface((screen_width, screen_height))
    night_overlay.fill((20, 20, 60))
    night_overlay.set_alpha(120)
    bg_night.blit(night_overlay, (0, 0))
    bg_night_frames.append(bg_night)

# Combine all background sets
bg_images = [bg_day_frames, bg_night_frames]  # Each element is a list of frames

current_bg_index = 0
bg_width = screen_width

# Load other images
# --- DAY/NIGHT GROUND ---
ground_img_day = pygame.image.load('Assets/Ground/dirtblockground.png').convert_alpha()
ground_img_night = pygame.image.load('Assets/Ground/dirtblockgroundnight.png').convert_alpha() if os.path.exists('Assets/Ground/dirtblockgroundnight.png') else ground_img_day.copy()
ground_img_day = pygame.transform.scale(ground_img_day, (ground_img_day.get_width(), 148))
ground_img_night = pygame.transform.scale(ground_img_night, (ground_img_night.get_width(), 148))
ground_width = ground_img_day.get_width()
ground_y = screen_height - ground_img_day.get_height()

# --- DAY/NIGHT PIPES ---
pipe_img_day_raw = pygame.image.load('Assets/Pipes/pipe_books.png').convert_alpha()
pipe_img_night_raw = pygame.image.load('Assets/Pipes/pipe_books_night.png').convert_alpha() if os.path.exists('Assets/Pipes/pipe_books_night.png') else pipe_img_day_raw.copy()
pipe_img_day = pygame.transform.scale(pipe_img_day_raw, (120, 600))
pipe_img_night = pygame.transform.scale(pipe_img_night_raw, (120, 600))

# --- DAY/NIGHT BIRD FRAMES ---
bird_day_frames = []
bird_night_frames = []
for num in range(1, 8):
    # Day
    img_day = pygame.image.load(f'Assets/Bird/bird{num}.png').convert_alpha()
    img_day = pygame.transform.scale(img_day, (45, 37))
    bird_day_frames.append(img_day)
    # Night
    night_path = f'Assets/Bird/bird_night{num}.png'
    if os.path.exists(night_path):
        img_night = pygame.image.load(night_path).convert_alpha()
        img_night = pygame.transform.scale(img_night, (45, 37))
    else:
        img_night = img_day.copy()
    bird_night_frames.append(img_night)

# --- CLOUDS ---
clouds_day_img = pygame.image.load('Assets/Background/CloudsDay.png').convert_alpha() if os.path.exists('Assets/Background/CloudsDay.png') else None
clouds_night_img = pygame.image.load('Assets/Background/CloudNight.png').convert_alpha() if os.path.exists('Assets/Background/CloudNight.png') else None
if clouds_day_img:
    print('Loaded CloudsDay.png')
else:
    print('Warning: CloudsDay.png not found!')
if clouds_night_img:
    print('Loaded CloudNight.png')
else:
    print('Warning: CloudNight.png not found!')
clouds_scroll = 0
clouds_scroll_speed = 0.8  # Slower than bg_scroll_speed
clouds_width = clouds_day_img.get_width() if clouds_day_img else screen_width

# To play music
pygame.mixer.music.load('Assets/Audio/Pixelland.mp3')
pygame.mixer.music.set_volume(volume)
pygame.mixer.music.play(-1)
flap_sound = pygame.mixer.Sound('Assets/Audio/flap.mp3')
flap_sound.set_volume(0.5)

# Add a new game state for the user manual
user_manual_prev_state = None  # Track where the manual was opened from

# Function to update loading screen
def update_loading():
    global loading_progress, current_loading_message, loading_message_timer, loading_complete, game_state

    # Update loading progress
    if loading_progress < 100:
        loading_progress += loading_speed
        if loading_progress > 100:
            loading_progress = 100

    # Update loading message
    loading_message_timer += 1
    if loading_message_timer >= loading_message_interval:
        loading_message_timer = 0
        current_loading_message = (current_loading_message + 1) % len(loading_messages)

    # Check if loading is complete
    if loading_progress >= 100 and not loading_complete:
        loading_complete = True

def draw_user_manual():
    screen.fill((30, 30, 60))
    draw_text("How to Play", font, yellow, screen_width // 2 - 120, 100)
    y = 220
    lines = [
        "- Press SPACE to flap and keep the bird in the air.",
        "- Avoid hitting the pipes and the ground.",
        "- Press ESC to pause the game.",
        "- Use arrow keys or mouse to navigate menus.",
        "- Try to get the highest score!"
    ]
    for line in lines:
        draw_text(line, small_font, white, screen_width // 2 - 320, y)
        y += 60
    draw_text("Press ESC or Enter to go back", small_font, white, screen_width // 2 - 180, y + 60)

# Function to draw loading screen
def draw_loading_screen():
    # Fill screen with dark background
    screen.fill((20, 20, 40))

    # Draw title
    draw_text("The Cramming Collapse", font, white, screen_width // 2.2 - 120, 200)

    # Draw loading message
    message = loading_messages[current_loading_message]
    text_width = small_font.size(message)[0]
    draw_text(message, small_font, white, screen_width // 2 - text_width // 2, 300)

    # Draw loading bar background
    bar_width = 400
    bar_height = 30
    bar_x = screen_width // 2 - bar_width // 2
    bar_y = 380

    pygame.draw.rect(screen, gray, (bar_x, bar_y, bar_width, bar_height))
    pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height), 3)

    # Draw loading bar fill
    fill_width = int((loading_progress / 100) * bar_width)
    if fill_width > 0:
        pygame.draw.rect(screen, blue, (bar_x, bar_y, fill_width, bar_height))

    # Draw loading percentage
    percentage_text = f"{int(loading_progress)}%"
    text_width = small_font.size(percentage_text)[0]
    draw_text(percentage_text, small_font, white, screen_width // 2 - text_width // 2, 430)

    # Draw continue prompt when loading is complete
    if loading_complete:
        prompt_text = "Press any key to continue..."
        text_width = small_font.size(prompt_text)[0]
        # Add blinking effect
        if (pygame.time.get_ticks() // 500) % 2:  # Blink every 500ms
            draw_text(prompt_text, small_font, yellow, screen_width // 2 - text_width // 2, 500)


# Function to get current background frame based on score
def get_current_background():
    # Change background set every 10 points
    bg_set_index = (score // 5) % len(bg_images)
    bg_frame_set = bg_images[bg_set_index]

    # Get the current frame from the selected background set
    frame_index = bg_frame_index % len(bg_frame_set)
    return bg_frame_set[frame_index]


# Function to update background animation
def update_background_animation():
    global bg_animation_timer, bg_frame_index

    # Only animate if not paused and during gameplay
    if not paused and game_state == "play":
        bg_animation_timer += 1

        if bg_animation_timer >= bg_animation_speed:
            bg_animation_timer = 0
            # Get current background set to determine frame count
            bg_set_index = (score // 10) % len(bg_images)
            bg_frame_set = bg_images[bg_set_index]
            bg_frame_index = (bg_frame_index + 1) % len(bg_frame_set)


# Function to draw scrolling background
def draw_background():
    # Only draw the main background now
    current_bg = get_current_background()
    screen.blit(current_bg, (bg_scroll, 0))
    screen.blit(current_bg, (bg_scroll + bg_width, 0))


# Rename draw_clouds_foreground to draw_clouds_layer
def draw_clouds_layer():
    global clouds_scroll
    if is_night():
        clouds_img = clouds_night_img
    else:
        clouds_img = clouds_day_img
    if clouds_img:
        for i in range((screen_width // clouds_width) + 2):
            screen.blit(clouds_img, (i * clouds_width + int(clouds_scroll), 0))
    else:
        # Draw a simple placeholder cloud layer for debugging
        for i in range((screen_width // 300) + 2):
            pygame.draw.ellipse(screen, (255,255,255,128), (i*300 + int(clouds_scroll), 80, 200, 60))
    # Update cloud scroll (always scroll, even if paused)
    clouds_scroll -= clouds_scroll_speed
    if abs(clouds_scroll) > clouds_width:
        clouds_scroll = 0


# Enhanced draw text function with color selection and hover detection
def draw_text(text, font, color, x, y, is_selected=False):
    if is_selected:
        color = yellow
    img = font.render(text, True, color)
    screen.blit(img, (x, y))
    return img.get_rect(topleft=(x, y))


# Function to check if mouse is hovering over a button
def is_mouse_over_button(button_rect):
    mouse_pos = pygame.mouse.get_pos()
    return button_rect.collidepoint(mouse_pos)


def reset_game():
    global last_pipe, countdown_active, countdown_start_time, show_fly_hint, last_countdown_value, bg_scroll, paused, pause_time_offset, game_over_time, show_game_over_screen, bg_animation_timer, bg_frame_index, victory, victory_time
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = screen_height // 2
    flappy.vel = 0
    last_pipe = pygame.time.get_ticks() - pipe_frequency
    countdown_active = True
    countdown_start_time = pygame.time.get_ticks()
    show_fly_hint = True
    last_countdown_value = -1
    bg_scroll = 0  # Reset background scroll
    paused = False  # Reset pause state
    pause_time_offset = 0  # Reset pause time tracking
    game_over_time = 0  # Reset game over timing
    show_game_over_screen = False  # Reset game over screen flag
    bg_animation_timer = 0  # Reset background animation
    bg_frame_index = 0  # Reset to first frame
    victory = False  # Reset victory state
    victory_time = None
    # Ensure music continues playing at proper volume after reset
    pygame.mixer.music.set_volume(volume)
    return 0


# Toggle pause function
def toggle_pause():
    global paused, last_pipe, countdown_start_time, pause_time_offset, pause_start_time
    paused = not paused

    if paused:
        # When pausing, record the current time and lower music volume
        pause_start_time = pygame.time.get_ticks()
        pygame.mixer.music.set_volume(volume * 0.3)  # Lower volume to 30% of original
    else:
        # When unpausing, calculate how long we were paused and adjust timers
        pause_end_time = pygame.time.get_ticks()
        pause_duration = pause_end_time - pause_start_time
        pause_time_offset += pause_duration

        # Adjust the pipe timer and countdown timer
        last_pipe += pause_duration
        if countdown_active:
            countdown_start_time += pause_duration

        pygame.mixer.music.set_volume(volume)  # Restore original volume


# Helper function to determine if it's night
def is_night():
    # The background set alternates every 5 points (see get_current_background)
    # bg_set_index = (score // 5) % len(bg_images)
    # If bg_set_index == 1, it's night
    bg_set_index = (score // 5) % len(bg_images)
    return bg_set_index == 1


# Bird class
class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.index = 0
        self.counter = 0
        self.update_images()
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        self.vel = 0
        self.flap = False

    def update_images(self):
        # Choose day or night frames
        if is_night():
            self.images = bird_night_frames
        else:
            self.images = bird_day_frames

    def update(self):
        if paused:  # Don't update if paused
            return

        # Update images if day/night changed
        self.update_images()

        if flying or game_over:
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.top <= 0:
                self.vel = max(self.vel, 0)
            if self.rect.bottom < ground_y:
                self.rect.y += int(self.vel)

        if not game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] and not self.flap:
                self.flap = True
                self.vel = -10
                flap_sound.play()
            if not keys[pygame.K_SPACE]:
                self.flap = False

            self.counter += 1
            if self.counter > 5:
                self.counter = 0
                self.index = (self.index + 1) % len(self.images)

            self.image = self.images[self.index]
            self.image = pygame.transform.rotate(self.image, self.vel * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)

        self.mask = pygame.mask.from_surface(self.image)


# Pipe class
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        super().__init__()
        # Use correct pipe image for day/night
        self.last_night_state = is_night()
        self.position = position
        self.update_image()
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect = self.image.get_rect(midbottom=(x, y - pipe_gap // 2))
        else:
            self.rect = self.image.get_rect(midtop=(x, y + pipe_gap // 2))
        self.mask = pygame.mask.from_surface(self.image)
        self.passed = False

    def update_image(self):
        if is_night():
            self.image = pipe_img_night.copy()
        else:
            self.image = pipe_img_day.copy()
        # Flip if needed
        if self.position == 1:
            self.image = pygame.transform.flip(self.image, False, True)

    def update(self):
        # Check if day/night state has changed
        current_night = is_night()
        if current_night != self.last_night_state:
            # Update image and mask
            old_rect = self.rect
            self.update_image()
            self.rect = self.image.get_rect()
            self.rect.x = old_rect.x
            self.rect.y = old_rect.y
            self.mask = pygame.mask.from_surface(self.image)
            self.last_night_state = current_night
        if not game_over and not paused:  # Don't update if paused
            self.rect.x -= scroll_speed
            if self.rect.right < 0:
                self.kill()


# Sprite groups
bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()
flappy = Bird(100, screen_height // 2)
bird_group.add(flappy)

# Main loop
run = True
while run:
    clock.tick(fps)

    if game_state == "loading":
        update_loading()
        draw_loading_screen()

        # Handle events during loading
        for event in pygame.event.get():
            if event.type == QUIT:
                run = False
            elif event.type == KEYDOWN or event.type == MOUSEBUTTONDOWN:
                if loading_complete:
                    game_state = "menu"
                    menu_selection = 0

    elif game_state == "menu":
        # Update background animation
        update_background_animation()

        # Draw scrolling background
        draw_background()

        # Update background scroll for menu (always scroll in menu)
        bg_scroll -= bg_scroll_speed
        if abs(bg_scroll) > bg_width:
            bg_scroll = 0

        ground_scroll -= scroll_speed
        if abs(ground_scroll) > ground_width:
            ground_scroll = 0

        draw_text("The Cramming Collapse", font, white, screen_width // 2.3 - 120, 100)

        # Menu buttons
        start_btn = draw_text("Start", font, white, screen_width // 2 - 60, 250, menu_selection == 0)
        settings_btn = draw_text("Settings", font, white, screen_width // 2 - 90, 350, menu_selection == 1)
        manual_btn = draw_text("User Manual", font, yellow if menu_selection == 2 else white, screen_width // 2 - 120, 420, menu_selection == 2)
        exit_btn = draw_text("Exit", font, white, screen_width // 2 - 50, 500, menu_selection == 3)
        draw_text("Use Arrow Keys + Enter or Mouse to navigate", small_font, white, 20, screen_height - 60)
        draw_text("Press ESC to exit", small_font, white, 20, screen_height - 30)
        # Mouse hover
        if is_mouse_over_button(start_btn):
            menu_selection = 0
        elif is_mouse_over_button(settings_btn):
            menu_selection = 1
        elif is_mouse_over_button(manual_btn):
            menu_selection = 2
        elif is_mouse_over_button(exit_btn):
            menu_selection = 3
        for i in range((screen_width // ground_width) + 2):
            screen.blit(ground_img_night if is_night() else ground_img_day, (i * ground_width + ground_scroll, ground_y))
        for event in pygame.event.get():
            if event.type == QUIT:
                run = False
            if event.type == KEYDOWN:
                if event.key == K_UP:
                    menu_selection = (menu_selection - 1) % 4
                elif event.key == K_DOWN:
                    menu_selection = (menu_selection + 1) % 4
                elif event.key == K_RETURN:
                    if menu_selection == 0:  # Start
                        game_state = "play"
                        score = reset_game()
                        flying = False
                        game_over = False
                    elif menu_selection == 1:  # Settings
                        game_state = "settings"
                        settings_selection = 0
                    elif menu_selection == 2:  # User Manual
                        user_manual_prev_state = "menu"
                        game_state = "user_manual"
                    elif menu_selection == 3:  # Exit
                        run = False
                elif event.key == K_ESCAPE:
                    run = False
            if event.type == MOUSEBUTTONDOWN:
                if start_btn.collidepoint(event.pos):
                    game_state = "play"
                    score = reset_game()
                    flying = False
                    game_over = False
                elif settings_btn.collidepoint(event.pos):
                    game_state = "settings"
                    settings_selection = 0
                elif manual_btn.collidepoint(event.pos):
                    user_manual_prev_state = "menu"
                    game_state = "user_manual"
                elif exit_btn.collidepoint(event.pos):
                    run = False

    elif game_state == "settings":
        # Update background animation
        update_background_animation()

        # Draw scrolling background
        draw_background()

        # Update background scroll for settings (always scroll in settings)
        bg_scroll -= bg_scroll_speed
        if abs(bg_scroll) > bg_width:
            bg_scroll = 0

        ground_scroll -= scroll_speed
        if abs(ground_scroll) > ground_width:
            ground_scroll = 0

        draw_text("Settings", font, white, screen_width // 2 - 100, 100)
        volume_label = draw_text(f"Volume: {int(volume * 100)}%", font, white, screen_width // 2 - 120, 200)

        # Settings menu with selection highlighting
        volume_up_btn = draw_text("Volume +", font, white, screen_width // 2 - 150, 270, settings_selection == 0)
        volume_down_btn = draw_text("Volume -", font, white, screen_width // 2 - 150, 330, settings_selection == 1)
        back_btn = draw_text("Back", font, white, screen_width // 2 - 60, 400, settings_selection == 2)

        # Instructions
        draw_text("Use Arrow Keys + Enter or Mouse to navigate", small_font, white, 20, screen_height - 60)
        draw_text("Press ESC to go back", small_font, white, 20, screen_height - 30)

        # Update settings selection based on mouse hover
        if is_mouse_over_button(volume_up_btn):
            settings_selection = 0
        elif is_mouse_over_button(volume_down_btn):
            settings_selection = 1
        elif is_mouse_over_button(back_btn):
            settings_selection = 2

        for i in range((screen_width // ground_width) + 2):
            screen.blit(ground_img_night if is_night() else ground_img_day, (i * ground_width + ground_scroll, ground_y))

        for event in pygame.event.get():
            if event.type == QUIT:
                run = False
            if event.type == KEYDOWN:
                if event.key == K_UP:
                    settings_selection = (settings_selection - 1) % 3
                elif event.key == K_DOWN:
                    settings_selection = (settings_selection + 1) % 3
                elif event.key == K_RETURN:
                    if settings_selection == 0:  # Volume +
                        volume = min(1.0, volume + 0.1)
                        pygame.mixer.music.set_volume(volume)
                    elif settings_selection == 1:  # Volume -
                        volume = max(0.0, volume - 0.1)
                        pygame.mixer.music.set_volume(volume)
                    elif settings_selection == 2:  # Back
                        game_state = "menu"
                        menu_selection = 0
                elif event.key == K_ESCAPE:
                    game_state = "menu"
                    menu_selection = 0
            if event.type == MOUSEBUTTONDOWN:
                if back_btn.collidepoint(event.pos):
                    game_state = "menu"
                    menu_selection = 0
                elif volume_up_btn.collidepoint(event.pos):
                    volume = min(1.0, volume + 0.1)
                    pygame.mixer.music.set_volume(volume)
                elif volume_down_btn.collidepoint(event.pos):
                    volume = max(0.0, volume - 0.1)
                    pygame.mixer.music.set_volume(volume)

    elif game_state == "play":
        # Update background animation
        update_background_animation()

        # Draw scrolling background
        draw_background()
        draw_clouds_layer()

        # Update background scroll for gameplay (only if not paused)
        if not game_over and flying and not paused:
            bg_scroll -= bg_scroll_speed
            if abs(bg_scroll) > bg_width:
                bg_scroll = 0

        if not game_over and not paused:
            ground_scroll -= scroll_speed
            if abs(ground_scroll) > ground_width:
                ground_scroll = 0

        if countdown_active and not paused:
            time_now = pygame.time.get_ticks()
            elapsed = (time_now - countdown_start_time) // 1000
            remaining = countdown_duration - elapsed

            if remaining != last_countdown_value:
                last_countdown_value = remaining

            if remaining > 0:
                countdown_text = str(remaining)
            elif remaining == 0:
                countdown_text = "Go!"
            else:
                countdown_active = False
                show_fly_hint = False
                flying = True

            if countdown_active:
                draw_text(countdown_text, font, white, screen_width // 2 - 40, screen_height // 2 - 80)
                if show_fly_hint:
                    draw_text("Get ready!", font, white, screen_width // 2 - 120, screen_height // 2)
                    draw_text("Press space to start now!", font, white, screen_width // 2.4 - 120, screen_height // 1.5)
        else:
            bird_group.draw(screen)
            bird_group.update()
            pipe_group.update()

            # Only update game logic if not paused
            if not paused:
                for pipe in pipe_group:  # score logic
                    if pipe.position == 1 and not pipe.passed:
                        if flappy.rect.left > pipe.rect.right:
                            pipe.passed = True
                            score += 1
                            if score == 40 and game_state != "victory_screen":
                                victory = True
                                game_state = "victory_screen"
                                victory_time = None
                # Restore original collision and ground logic, but skip if in victory_screen
                if not game_over and game_state != "victory_screen":
                    for pipe in pipe_group:
                        if pygame.sprite.collide_mask(flappy, pipe):
                            game_over = True
                            game_over_time = pygame.time.get_ticks()
                    if flappy.rect.bottom >= ground_y:
                        game_over = True
                        game_over_time = pygame.time.get_ticks()
                        flying = False
                # Restore original pipe spawning logic
                if not game_over and flying and not victory:
                    time_now = pygame.time.get_ticks()
                    if time_now - last_pipe > pipe_frequency:
                        pipe_height = random.randint(-100, 100)
                        btm_pipe = Pipe(screen_width, screen_height // 2 + pipe_height, -1)
                        top_pipe = Pipe(screen_width, screen_height // 2 + pipe_height, 1)
                        pipe_group.add(btm_pipe)
                        pipe_group.add(top_pipe)
                        last_pipe = time_now

            # Display score
            draw_text(str(score), font, white, screen_width // 2, 20)

            # Display pause menu and instructions
            if paused:
                # Semi-transparent overlay
                pause_overlay = pygame.Surface((screen_width, screen_height))
                pause_overlay.set_alpha(128)
                pause_overlay.fill((0, 0, 0))
                screen.blit(pause_overlay, (0, 0))

                # Pause Menu with selection highlighting
                y_base = screen_height // 2 - 120
                continue_btn = draw_text("Continue", font, yellow if pause_selection == 0 else white, screen_width // 2 - 90, y_base, pause_selection == 0)
                restart_btn = draw_text("Restart", font, yellow if pause_selection == 1 else white, screen_width // 2 - 80, y_base + 70, pause_selection == 1)
                manual_btn = draw_text("How to Play", font, yellow if pause_selection == 2 else white, screen_width // 2 - 110, y_base + 140, pause_selection == 2)
                main_menu_btn = draw_text("Main Menu", font, yellow if pause_selection == 3 else white, screen_width // 2 - 110, y_base + 210, pause_selection == 3)
                draw_text("Use Arrow Keys + Enter or Mouse", small_font, white, screen_width // 2 - 120, y_base + 290)
                # Mouse hover
                if is_mouse_over_button(continue_btn):
                    pause_selection = 0
                elif is_mouse_over_button(restart_btn):
                    pause_selection = 1
                elif is_mouse_over_button(manual_btn):
                    pause_selection = 2
                elif is_mouse_over_button(main_menu_btn):
                    pause_selection = 3
                for event in pygame.event.get():
                    if event.type == QUIT:
                        run = False
                    if event.type == KEYDOWN:
                        if event.key == K_UP:
                            pause_selection = (pause_selection - 1) % 4
                        elif event.key == K_DOWN:
                            pause_selection = (pause_selection + 1) % 4
                        elif event.key == K_RETURN:
                            if pause_selection == 0:  # Continue
                                toggle_pause()
                                pause_selection = 0
                            elif pause_selection == 1:  # Restart
                                pygame.mixer.music.set_volume(volume)
                                score = reset_game()
                                flying = False
                                game_over = False
                                pause_selection = 0
                            elif pause_selection == 2:  # How to Play
                                user_manual_prev_state = "pause"
                                game_state = "user_manual"
                            elif pause_selection == 3:  # Main Menu
                                game_state = "menu"
                                paused = False
                                pygame.mixer.music.set_volume(volume)
                                menu_selection = 0
                                pause_selection = 0
                        elif event.key == K_ESCAPE:  # ESC to continue/unpause
                            toggle_pause()
                            pause_selection = 0
                    if event.type == MOUSEBUTTONDOWN:
                        if continue_btn.collidepoint(event.pos):
                            toggle_pause()  # Continue game
                            pause_selection = 0
                        elif restart_btn.collidepoint(event.pos):
                            pygame.mixer.music.set_volume(volume)
                            score = reset_game()
                            flying = False
                            game_over = False
                            pause_selection = 0
                        elif manual_btn.collidepoint(event.pos):
                            user_manual_prev_state = "pause"
                            game_state = "user_manual"
                        elif main_menu_btn.collidepoint(event.pos):
                            game_state = "menu"
                            paused = False
                            pygame.mixer.music.set_volume(volume)
                            menu_selection = 0
                            pause_selection = 0
            else:
                # Show ESC instruction during gameplay
                if flying and not countdown_active and not victory:
                    draw_text("ESC - Menu", small_font, white, 20, 20)

        # Draw pipes
        pipe_group.draw(screen)

        # Draw ground last so it is in the very front
        for i in range((screen_width // ground_width) + 2):
            screen.blit(ground_img_night if is_night() else ground_img_day, (i * ground_width + ground_scroll, ground_y))

        if game_state == "victory_screen":
            # Show victory message and exit immediately after drawing
            draw_text("Victory!", font, yellow, screen_width // 2 - 120, screen_height // 2 - 120)
            draw_text(f"Score: {score}", font, white, screen_width // 2 - 100, screen_height // 2 - 40)
            draw_text(f"Best: {best_score}", font, white, screen_width // 2 - 100, screen_height // 2 + 20)
            congrats_text = "Congratulations! You can now proceed to level 2"
            text_width = small_font.size(congrats_text)[0]
            draw_text(congrats_text, small_font, white, screen_width // 2 - text_width // 2, screen_height // 2 + 80)
            pygame.display.update()
            pygame.time.wait(2000)  # Optional: show for half a second so user sees it
            pygame.quit()
            sys.exit()

        elif game_over:
            # Check if enough time has passed to show game over screen
            if not show_game_over_screen:
                time_since_game_over = pygame.time.get_ticks() - game_over_time
                if time_since_game_over >= game_over_delay:
                    show_game_over_screen = True
                    if score > best_score:
                        best_score = score
                else:
                    # During delay, just show "Game Over" text
                    draw_text("Game Over", font, white, screen_width // 2 - 140, screen_height // 2 - 60)

            if show_game_over_screen:
                draw_text("Game Over", font, white, screen_width // 2 - 140, screen_height // 2 - 120)
                draw_text(f"Score: {score}", font, white, screen_width // 2 - 100, screen_height // 2 - 40)
                draw_text(f"Best: {best_score}", font, white, screen_width // 2 - 100, screen_height // 2 + 20)

                # Game over menu with selection highlighting
                play_again_btn = draw_text("Play Again", font, white, screen_width // 2 - 120, screen_height // 2 + 100,
                                           game_over_selection == 0)
                menu_btn = draw_text("Menu", font, white, screen_width // 2 - 70, screen_height // 2 + 180,
                                     game_over_selection == 1)

                # Instructions
                draw_text("Use Arrow Keys + Enter, Space, or Mouse", small_font, white, screen_width // 2 - 150,
                          screen_height // 2 + 240)

                # Update game over selection based on mouse hover
                if is_mouse_over_button(play_again_btn):
                    game_over_selection = 0
                elif is_mouse_over_button(menu_btn):
                    game_over_selection = 1

                for event in pygame.event.get():
                    if event.type == QUIT:
                        run = False
                    if event.type == KEYDOWN:
                        if event.key == K_UP:
                            game_over_selection = (game_over_selection - 1) % 2
                        elif event.key == K_DOWN:
                            game_over_selection = (game_over_selection + 1) % 2
                        elif event.key == K_RETURN:
                            if game_over_selection == 0:  # Play Again
                                score = reset_game()
                                flying = False
                                game_over = False
                                game_over_selection = 0
                            elif game_over_selection == 1:  # Menu
                                game_state = "menu"
                                menu_selection = 0
                                game_over_selection = 0
                        elif event.key == K_SPACE:
                            score = reset_game()
                            flying = False
                            game_over = False
                            game_over_selection = 0
                        elif event.key == K_ESCAPE:
                            game_state = "menu"
                            menu_selection = 0
                            game_over_selection = 0
                    if event.type == MOUSEBUTTONDOWN:
                        if play_again_btn.collidepoint(event.pos):
                            score = reset_game()
                            flying = False
                            game_over = False
                            game_over_selection = 0
                        elif menu_btn.collidepoint(event.pos):
                            game_state = "menu"
                            menu_selection = 0
                            game_over_selection = 0
            else:
                # During delay period, consume events but don't act on them
                for event in pygame.event.get():
                    if event.type == QUIT:
                        run = False
        else:
            # Only handle events if not paused (pause menu handles its own events)
            if not paused:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        run = False
                    if event.type == KEYDOWN:
                        if event.key == K_SPACE:
                            if countdown_active:
                                flying = True
                                countdown_active = False
                                show_fly_hint = False
                            elif not flying:
                                flying = True
                        elif event.key == K_ESCAPE:  # ESC key to pause
                            if flying and not countdown_active and not game_over:
                                toggle_pause()

    elif game_state == "user_manual":
        draw_user_manual()
        for event in pygame.event.get():
            if event.type == QUIT:
                run = False
            if event.type == KEYDOWN:
                if event.key in (K_ESCAPE, K_RETURN):
                    if user_manual_prev_state == "menu":
                        game_state = "menu"
                    elif user_manual_prev_state == "pause":
                        game_state = "play"
                        paused = True
            if event.type == MOUSEBUTTONDOWN:
                # Also allow click anywhere to go back
                if user_manual_prev_state == "menu":
                    game_state = "menu"
                elif user_manual_prev_state == "pause":
                    game_state = "play"
                    paused = True

    pygame.display.update()

pygame.quit()

