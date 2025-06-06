import pygame
import sys
import os
import random
import math
# Import the introduction module
from INTRODUCTION import introduction_main

# Initialize pygame
pygame.init()

# Display constants
WIDTH, HEIGHT = 1280, 720
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Deadline Chronicles")

# Set window icon
try:
    icon = pygame.image.load("Images\\DEADLINE_CHRONICLES.png")
    pygame.display.set_icon(icon)
except pygame.error:
    print("Warning: Could not load icon image")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
BEIGE = (245, 215, 160)  # Color for pixel text
BUTTON_RED = (180, 60, 40)  # Main button color
BUTTON_RED_DARK = (140, 30, 20)  # Dark red for shadows/borders
BUTTON_RED_LIGHT = (220, 80, 60)  # Light red for highlights
DARK_BLUE = (30, 30, 80)  # Game background color

# Pixel Fonts
# Define font paths
FONT_DIR = os.path.join(os.path.dirname(__file__), "Assets", "font", "PixelFonts")
FONT_REGULAR = os.path.join(FONT_DIR, "slkscr.ttf")
FONT_BOLD = os.path.join(FONT_DIR, "slkscrb.ttf")
FONT_EXTENDED = os.path.join(FONT_DIR, "slkscre.ttf")
FONT_EXTENDED_BOLD = os.path.join(FONT_DIR, "slkscreb.ttf")

# Load pixel fonts
try:
    font_small = pygame.font.Font(FONT_REGULAR, 24)
    font_medium = pygame.font.Font(FONT_REGULAR, 48)
    font_large = pygame.font.Font(FONT_REGULAR, 72)

    # Additional font variants
    font_small_bold = pygame.font.Font(FONT_BOLD, 24)
    font_medium_bold = pygame.font.Font(FONT_BOLD, 48)
    font_large_bold = pygame.font.Font(FONT_BOLD, 72)

    font_small_extended = pygame.font.Font(FONT_EXTENDED, 24)
    font_medium_extended = pygame.font.Font(FONT_EXTENDED, 48)
    font_large_extended = pygame.font.Font(FONT_EXTENDED, 72)

    font_small_extended_bold = pygame.font.Font(FONT_EXTENDED_BOLD, 24)
    font_medium_extended_bold = pygame.font.Font(FONT_EXTENDED_BOLD, 48)
    font_large_extended_bold = pygame.font.Font(FONT_EXTENDED_BOLD, 72)

    # Flag to indicate if pixel fonts loaded successfully
    pixel_fonts_loaded = True
except pygame.error:
    print("Warning: Could not load pixel fonts, falling back to system fonts")
    font_small = pygame.font.SysFont("Arial", 24)
    font_medium = pygame.font.SysFont("Arial", 48)
    font_large = pygame.font.SysFont("Arial", 72)
    pixel_fonts_loaded = False

# Load logo image
try:
    logo_img = pygame.image.load('Images\\DEADLINE_CHRONICLES.png')
    # Scale the logo if needed (adjust the size as appropriate for your screen)
    logo_img = pygame.transform.scale(logo_img, (580, 300))
except pygame.error:
    print("Warning: Could not load logo image 'Images\\DEADLINE_CHRONICLES.png'")
    logo_img = None

# --- Background Panning Variables ---
menu_bg_img = None
original_menu_bg_img = None  # Store the original loaded image
bg_pan_offset_y = 0  # Current vertical offset for panning
bg_pan_speed = 0.3  # How many pixels to move per frame
bg_pan_direction = 1  # 1 for down, -1 for up
can_bg_pan = False  # Flag to check if background can actually pan

# Load menu background image
try:
    original_menu_bg_img = pygame.image.load('Images\\Menu_Background\\ComLab2_Temp1.png').convert_alpha()

    # Fixed scaling approach
    new_width = WIDTH
    new_height = int(HEIGHT * 1.5)  # Make it 50% taller for panning

    menu_bg_img = pygame.transform.scale(original_menu_bg_img, (new_width, new_height))

    # Enable panning only if the scaled image is taller than the screen
    can_bg_pan = new_height > HEIGHT
    if can_bg_pan:
        print(f"Background scaled to: {new_width}x{new_height}. Panning enabled.")
    else:
        print(f"Background scaled to: {WIDTH}x{HEIGHT}. Panning disabled.")

except pygame.error:
    print("Warning: Could not load background image 'Images\\Menu_Background\\ComLab2_Temp1.png'")
    menu_bg_img = None
    can_bg_pan = False  # No image, no panning


class PixelButton:
    def __init__(self, x, y, width, height, text, image_path=None, animation_base_path=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.is_hovered = False
        self.is_clicked = False
        self.pixel_size = 5  # Size of each "pixel" in our button
        self.shadow_offset = 4  # Pixel offset for the 3D effect
        self.image_path = image_path
        self.button_image = None

        # Animation properties
        self.animation_base_path = animation_base_path
        self.idle_frames = []
        self.hover_frames = []
        self.click_frames = []
        self.current_frame_index = 0
        self.animation_speed = 0.2  # Lower is faster
        self.animation_timer = 0
        self.current_state = "idle"  # Can be "idle", "hover", or "click"

        # Load animations if base path is provided
        if animation_base_path:
            self.load_animations()
        # Load single button image if provided (fallback)
        elif image_path:
            try:
                self.button_image = pygame.image.load(image_path)
                # Scale the image to fit the button size
                self.button_image = pygame.transform.scale(self.button_image, (width, height))
            except pygame.error:
                print(f"Warning: Could not load button image '{image_path}'")
                self.button_image = None

        # Pre-render our text (fallback if no image)
        if not self.button_image and not animation_base_path:
            # Use pixel fonts if available, otherwise system fonts
            if pixel_fonts_loaded:
                font = font_small
            else:
                font = pygame.font.SysFont("Arial", 24)
            self.text_surface = font.render(text, True, BEIGE)
        else:
            self.text_surface = None

    def load_animations(self):
        # Load idle animations
        idle_path = os.path.join(self.animation_base_path, "Idle")
        hover_path = os.path.join(self.animation_base_path, "Hover")
        click_path = os.path.join(self.animation_base_path, "Click")

        # Check if it's a Start button or Exit button to determine naming pattern
        if "Start" in self.animation_base_path:
            # Start button pattern
            for i in range(1, 5):  # 4 frames for idle and hover
                try:
                    idle_img = pygame.image.load(os.path.join(idle_path, f"MainStartButtonTrueIdle{i}.png"))
                    # Scale to self.rect dimensions which are set in init
                    idle_img = pygame.transform.scale(idle_img, (self.rect.width, self.rect.height))
                    self.idle_frames.append(idle_img)

                    hover_img = pygame.image.load(os.path.join(hover_path, f"MainStartButtonTrueHover{i}.png"))
                    hover_img = pygame.transform.scale(hover_img, (self.rect.width, self.rect.height))
                    self.hover_frames.append(hover_img)
                except pygame.error as e:
                    print(f"Warning: Could not load animation frame: {e}")

            # 4 frames for click (not 5)
            for i in range(1, 5):
                try:
                    click_img = pygame.image.load(os.path.join(click_path, f"MainStartButtonTrueClick{i}.png"))
                    click_img = pygame.transform.scale(click_img, (self.rect.width, self.rect.height))
                    self.click_frames.append(click_img)
                except pygame.error as e:
                    print(f"Warning: Could not load animation frame: {e}")
        else:
            # Exit button pattern - has many more frames
            # Load idle frames (up to 77)
            for i in range(1, 77):
                try:
                    idle_img = pygame.image.load(os.path.join(idle_path, f"ExitPngIdle{i}.png"))
                    idle_img = pygame.transform.scale(idle_img, (self.rect.width, self.rect.height))
                    self.idle_frames.append(idle_img)
                except pygame.error:
                    # Stop if file doesn't exist
                    break

            # Load hover frames
            i = 1
            for i in range(1, 77):
                try:
                    hover_img = pygame.image.load(os.path.join(hover_path, f"ExitPngHover{i}.png"))
                    hover_img = pygame.transform.scale(hover_img, (self.rect.width, self.rect.height))
                    self.hover_frames.append(hover_img)
                    i += 1
                except pygame.error:
                    # Stop if file doesn't exist
                    break

            # Load click frames (up to 77)
            for i in range(1, 77):
                try:
                    click_img = pygame.image.load(os.path.join(click_path, f"ExitPngClick{i}.png"))
                    click_img = pygame.transform.scale(click_img, (self.rect.width, self.rect.height))
                    self.click_frames.append(click_img)
                except pygame.error:
                    # Stop if file doesn't exist
                    break

        # If we couldn't load any frames, print a warning
        if not self.idle_frames and not self.hover_frames and not self.click_frames:
            print(f"Warning: Could not load any animation frames from {self.animation_base_path}")
            # Fall back to static image if available
            if self.image_path:
                try:
                    self.button_image = pygame.image.load(self.image_path)
                    self.button_image = pygame.transform.scale(self.button_image, (self.rect.width, self.rect.height))
                except pygame.error:
                    print(f"Warning: Could not load fallback button image '{self.image_path}'")
                    self.button_image = None

    def update_animation(self, dt=1 / 60):
        """Update the animation frame based on the current state"""
        # Increment the animation timer
        self.animation_timer += dt

        # Check if it's time to advance to the next frame
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0

            # Get the appropriate frames list based on current state
            frames = []
            if self.current_state == "idle" and self.idle_frames:
                frames = self.idle_frames
            elif self.current_state == "hover" and self.hover_frames:
                frames = self.hover_frames
            elif self.current_state == "click" and self.click_frames:
                frames = self.click_frames

            # If we have frames to animate, advance to the next frame
            if frames:
                self.current_frame_index = (self.current_frame_index + 1) % len(frames)

    def draw(self, surface):
        # If we have animations, use them
        if self.animation_base_path:
            # Update the animation state based on hover/click status
            if self.is_clicked:
                self.current_state = "click"
            elif self.is_hovered:
                self.current_state = "hover"
            else:
                self.current_state = "idle"

            # Get the current frame to display
            current_frame = None
            if self.current_state == "idle" and self.idle_frames:
                current_frame = self.idle_frames[self.current_frame_index % len(self.idle_frames)]
            elif self.current_state == "hover" and self.hover_frames:
                current_frame = self.hover_frames[self.current_frame_index % len(self.hover_frames)]
            elif self.current_state == "click" and self.click_frames:
                current_frame = self.click_frames[self.current_frame_index % len(self.click_frames)]

            # If we have a frame to display, blit it to the surface
            if current_frame:
                image_rect = current_frame.get_rect(center=self.rect.center)
                surface.blit(current_frame, image_rect)
                return

        # If we have a static button image (fallback), use it
        if self.button_image:
            # Add a subtle hover effect by slightly adjusting the position
            offset = 2 if self.is_hovered else 0
            image_rect = self.button_image.get_rect(center=(self.rect.centerx + offset, self.rect.centery + offset))
            surface.blit(self.button_image, image_rect)
            return

        # Original pixel art button drawing code (fallback)
        # Draw the main button with a 3D effect
        # Draw shadow/border first (darker red)
        shadow_rect = pygame.Rect(
            self.rect.x + self.shadow_offset,
            self.rect.y + self.shadow_offset,
            self.rect.width,
            self.rect.height
        )
        pygame.draw.rect(surface, BUTTON_RED_DARK, shadow_rect)

        # Draw main button
        pygame.draw.rect(surface, BUTTON_RED, self.rect)

        # Add pixelated border
        border_color = WHITE if self.is_hovered else BUTTON_RED_DARK
        # Top border
        pygame.draw.rect(surface, BUTTON_RED_LIGHT, (self.rect.x, self.rect.y, self.rect.width, self.pixel_size))
        # Left border
        pygame.draw.rect(surface, BUTTON_RED_LIGHT, (self.rect.x, self.rect.y, self.pixel_size, self.rect.height))
        # Bottom border
        pygame.draw.rect(surface, BUTTON_RED_DARK, (self.rect.x, self.rect.y + self.rect.height - self.pixel_size,
                                                    self.rect.width, self.pixel_size))
        # Right border
        pygame.draw.rect(surface, BUTTON_RED_DARK, (self.rect.x + self.rect.width - self.pixel_size, self.rect.y,
                                                    self.pixel_size, self.rect.height))

        # Position the text in the center of the button
        if self.text_surface:
            text_rect = self.text_surface.get_rect(center=self.rect.center)
            surface.blit(self.text_surface, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        # Reset click state if mouse moves away from button
        if not self.is_hovered:
            self.is_clicked = False
        return self.is_hovered

    def handle_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            self.is_clicked = True
            return True
        # Reset click state when mouse button is released
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_clicked = False
        return False


def draw_menu():
    # Update background panning offset
    global bg_pan_offset_y, bg_pan_direction

    if menu_bg_img is not None and can_bg_pan:
        bg_pan_offset_y += bg_pan_speed * bg_pan_direction

        # Reverse direction if hitting boundaries
        # Top boundary is 0. Bottom boundary is (image height - screen height).
        if bg_pan_direction == 1 and bg_pan_offset_y >= (menu_bg_img.get_height() - HEIGHT):
            bg_pan_direction = -1
        elif bg_pan_direction == -1 and bg_pan_offset_y <= 0:
            bg_pan_direction = 1

        # Display background image with current offset
        # The blit function draws the image. The second argument is the destination rectangle.
        # We specify the top-left corner of the portion of the image we want to draw.
        # The third argument is the source rectangle (x, y, width, height) from the image.
        SCREEN.blit(menu_bg_img, (0, 0), (0, int(bg_pan_offset_y), WIDTH, HEIGHT))
    elif menu_bg_img is not None:
        # If panning is not possible (image not tall enough), just blit the scaled image
        SCREEN.blit(menu_bg_img, (0, 0))
    else:
        # Fallback to gradient if image isn't available
        for y in range(HEIGHT):
            # Create a gradient from dark blue to light blue
            color_value = int(y / HEIGHT * 155) + 100
            pygame.draw.line(SCREEN, (0, 0, color_value), (0, y), (WIDTH, y))

    # Display logo
    if logo_img is not None:
        logo_rect = logo_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
        SCREEN.blit(logo_img, logo_rect)
    else:
        # Fallback to text if logo image isn't available
        title_text = font_large.render("Deadline Chronicles", True, WHITE)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
        SCREEN.blit(title_text, title_rect)

    # Draw buttons
    start_button.draw(SCREEN)
    exit_button.draw(SCREEN)


def draw_game():
    # Display background image (this could be a different background for the game)
    # For now, it reuses the menu background, but you might want to change this.
    if menu_bg_img is not None:
        # For game screen, let's just display the static background for simplicity
        # Or you could implement panning for game background too, if desired.
        SCREEN.blit(menu_bg_img, (0, 0))
    else:
        # Fallback to black screen if image isn't available
        SCREEN.fill(BLACK)

    # Draw back to menu button
    back_button.draw(SCREEN)


def story_screen():
    """Display the story introduction screen with text on black background and typing animation"""
    clock = pygame.time.Clock()
    running = True

    # Use pre-loaded pixel fonts or create specific sizes if needed
    if pixel_fonts_loaded:
        # Create a specific size for the story text if needed
        try:
            story_font = pygame.font.Font(FONT_REGULAR, 28)
            continue_font = pygame.font.Font(FONT_REGULAR, 20)
        except pygame.error:
            print("Warning: Could not load pixel font for story screen, falling back to system font")
            story_font = pygame.font.SysFont("Arial", 28)
            continue_font = pygame.font.SysFont("Arial", 20)
    else:
        # Fallback to system fonts if pixel fonts weren't loaded
        story_font = pygame.font.SysFont("Arial", 28)
        continue_font = pygame.font.SysFont("Arial", 20)

    # Story text
    story_text = "There was a student who was given a task by his professor to do a project, but he ended up in another dimension the \"DEV REALM\". Let's follow the student's journey"

    # Split text into multiple lines for better readability
    words = story_text.split()
    lines = []
    current_line = []

    # Create lines with maximum width
    for word in words:
        test_line = ' '.join(current_line + [word])
        # If adding this word makes the line too long, start a new line
        if story_font.size(test_line)[0] > WIDTH - 100:
            lines.append(' '.join(current_line))
            current_line = [word]
        else:
            current_line.append(word)

    # Add the last line
    if current_line:
        lines.append(' '.join(current_line))

    # Animation variables
    typing_speed = 0.05  # seconds per character
    typing_timer = 0
    displayed_chars = [0] * len(lines)  # Number of characters to display for each line
    animation_complete = False

    # Continue text that tells user to press any key
    continue_text = continue_font.render("Press any key to continue...", True, WHITE)
    show_continue = False  # Only show after animation completes

    while running:
        dt = clock.tick(60) / 1000  # Delta time in seconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Any key press will exit the story screen if animation is complete
            # or speed up the animation if it's still in progress
            if event.type == pygame.KEYDOWN:
                if animation_complete:
                    # Instead of returning, directly call introduction_main()
                    # This ensures the story screen text is removed before showing the introduction
                    introduction_main()
                    return
                else:
                    # Complete the animation immediately
                    for i in range(len(lines)):
                        displayed_chars[i] = len(lines[i])
                    animation_complete = True
                    show_continue = True

        # Update typing animation
        if not animation_complete:
            typing_timer += dt
            if typing_timer >= typing_speed:
                typing_timer = 0

                # Find the current line being typed
                current_line_index = 0
                while current_line_index < len(lines) and displayed_chars[current_line_index] >= len(
                        lines[current_line_index]):
                    current_line_index += 1

                # If we have more lines to type
                if current_line_index < len(lines):
                    displayed_chars[current_line_index] += 1

                    # Check if we've completed this line
                    if displayed_chars[current_line_index] >= len(lines[current_line_index]):
                        # If we've completed all lines, mark animation as complete
                        if current_line_index == len(lines) - 1:
                            animation_complete = True
                            show_continue = True

        # Fill screen with black background
        SCREEN.fill(BLACK)

        # Calculate total height of all text for positioning
        line_spacing = 10  # Space between lines
        line_heights = [story_font.size(line[:chars])[1] for line, chars in zip(lines, displayed_chars)]
        total_height = sum(line_heights) + line_spacing * (len(lines) - 1)

        # Calculate starting y position to center text vertically
        start_y = (HEIGHT - total_height) // 2

        # Draw each line of text with typing effect
        current_y = start_y
        for i, line in enumerate(lines):
            # Only render the characters that should be visible
            visible_text = line[:displayed_chars[i]]
            if visible_text:  # Only render if there's text to show
                text_surface = story_font.render(visible_text, True, WHITE)
                text_rect = text_surface.get_rect(center=(WIDTH // 2, current_y))
                SCREEN.blit(text_surface, text_rect)
            current_y += story_font.size(line)[1] + line_spacing

        # Draw continue text at the bottom (only after animation is complete)
        if show_continue:
            continue_rect = continue_text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
            SCREEN.blit(continue_text, continue_rect)

        # Update display
        pygame.display.flip()


def game_loop():
    """Main game loop - this is where your actual game logic would go"""
    clock = pygame.time.Clock()
    running = True

    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Handle keyboard input
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return  # Return to main menu

                # Add your game controls here
                if event.key == pygame.K_w:
                    print("Moving up")
                elif event.key == pygame.K_s:
                    print("Moving down")
                elif event.key == pygame.K_a:
                    print("Moving left")
                elif event.key == pygame.K_d:
                    print("Moving right")
                elif event.key == pygame.K_SPACE:
                    print("Action!")

            # Handle back button click
            if back_button.handle_click(event):
                return  # Return to main menu

        # Check hover states
        back_button.check_hover(mouse_pos)

        # Draw game screen
        draw_game()

        # Update display
        pygame.display.flip()
        clock.tick(60)


def shutdown_animation():
    """Display a shutting down animation with flickering black and white background and shaking text"""
    clock = pygame.time.Clock()
    running = True

    # Animation parameters
    animation_duration = 2.0  # Total animation duration in seconds
    current_time = 0

    # Prepare "SHUTTING DOWN" text
    if pixel_fonts_loaded:
        shutdown_font = pygame.font.Font(FONT_REGULAR, 60)
    else:
        shutdown_font = pygame.font.SysFont("Arial", 60)

    # Fade parameters
    text_alpha = 0  # Start with transparent text
    fade_alpha = 0  # For fading to black

    # Flickering parameters
    flicker_speed = 6  # Higher values = faster flickering
    flicker_intensity = 0.3  # How strong the flickering effect is (0.0 to 1.0)

    # Shaking parameters
    shake_intensity = 3  # Maximum pixel offset for shaking

    while running and current_time < animation_duration:
        dt = clock.tick(60) / 1000  # Delta time in seconds
        current_time += dt

        # Calculate animation progress (0.0 to 1.0)
        progress = current_time / animation_duration

        # Update text alpha (fade in)
        if progress < 0.3:
            # Fade in text during first 30%
            text_alpha = int(255 * (progress / 0.3))
        else:
            text_alpha = 255

        # Update fade to black
        if progress > 0.7:
            # Fade to black during last 30%
            fade_progress = (progress - 0.7) / 0.3
            fade_alpha = int(255 * fade_progress)

        # Determine background color based on flickering effect
        # Only flicker if we're not in the fade-to-black phase
        if progress <= 0.7:
            # Create a flickering effect between black and white
            flicker_value = math.sin(progress * flicker_speed * math.pi * 2)
            flicker_factor = (flicker_value + 1) / 2  # Convert from -1..1 to 0..1

            # Apply intensity to make it more or less pronounced
            flicker_factor = flicker_factor * flicker_intensity

            # Calculate color value (0 = black, 255 = white)
            color_value = int(255 * flicker_factor)
            background_color = (color_value, color_value, color_value)

            # Fill screen with the calculated color
            SCREEN.fill(background_color)
        else:
            # During fade-to-black phase, keep background black
            SCREEN.fill(BLACK)

        # Draw "SHUTTING DOWN" text with a pulsating effect
        pulse_factor = 1.0 + 0.05 * math.sin(progress * 15)  # Subtle pulsating

        # Create pulsating text
        if pixel_fonts_loaded:
            pulse_size = int(60 * pulse_factor)
            pulse_font = pygame.font.Font(FONT_BOLD, pulse_size)
        else:
            pulse_size = int(60 * pulse_factor)
            pulse_font = pygame.font.SysFont("Arial", pulse_size)

        pulse_text = pulse_font.render("SHUTTING DOWN", True, WHITE if progress <= 0.7 else WHITE)
        # Set alpha for text fade-in
        pulse_text.set_alpha(text_alpha)

        # Apply shaking effect to text position
        shake_offset_x = random.randint(-shake_intensity, shake_intensity)
        shake_offset_y = random.randint(-shake_intensity, shake_intensity)

        # Get text rectangle and apply shake offset
        pulse_rect = pulse_text.get_rect(center=(WIDTH // 2 + shake_offset_x, HEIGHT // 2 + shake_offset_y))
        SCREEN.blit(pulse_text, pulse_rect)

        # Apply fade to black overlay
        if fade_alpha > 0:
            fade_surface = pygame.Surface((WIDTH, HEIGHT))
            fade_surface.fill(BLACK)
            fade_surface.set_alpha(fade_alpha)
            SCREEN.blit(fade_surface, (0, 0))

        # Update display
        pygame.display.flip()

        # Check for events (allow user to skip animation)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                running = False

    # Ensure we end with a black screen
    SCREEN.fill(BLACK)
    pygame.display.flip()

    # Small delay to show the black screen
    pygame.time.delay(300)


def main_menu():
    clock = pygame.time.Clock()
    running = True
    dt = 1 / 60  # Delta time for animation updates

    # Variables to track button click animations
    start_clicked_time = 0
    exit_clicked_time = 0
    click_animation_duration = 0.3  # Duration in seconds to show click animation

    while running:
        mouse_pos = pygame.mouse.get_pos()

        # Check events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Button click handling
            if start_button.handle_click(event) and start_clicked_time == 0:
                print("Start button clicked!")
                start_clicked_time = click_animation_duration  # Start the timer

            if exit_button.handle_click(event) and exit_clicked_time == 0:
                print("Exit button clicked!")
                exit_clicked_time = click_animation_duration  # Start the timer

        # Check hover states
        start_button.check_hover(mouse_pos)
        exit_button.check_hover(mouse_pos)

        # Update button animations
        start_button.update_animation(dt)
        exit_button.update_animation(dt)

        # Handle click animation timers
        if start_clicked_time > 0:
            start_clicked_time -= dt
            if start_clicked_time <= 0:
                # Animation finished, execute action
                start_clicked_time = 0
                # Show story screen first (which will transition to introduction screen)
                story_screen()
                # Finally transition to game window
                game_loop()

        if exit_clicked_time > 0:
            exit_clicked_time -= dt
            if exit_clicked_time <= 0:
                # Animation finished, execute action
                exit_clicked_time = 0
                # Play shutdown animation before exiting
                shutdown_animation()
                pygame.quit()
                sys.exit()

        # Draw menu
        draw_menu()

        # Update display
        pygame.display.flip()
        dt = clock.tick(60) / 1000  # Convert to seconds for animation timing


# Define button dimensions
start_button_width = 200
start_button_height = 80
exit_button_width = 200
exit_button_height = 80

# Define button animation paths
start_animation_path = os.path.join("Images", "StartButtonPNG")
exit_animation_path = os.path.join("Images", "ExitButtonPng")

# Create buttons with animations
start_button = PixelButton(
    WIDTH // 2 - start_button_width // 2, HEIGHT // 2 + 50,  # position
    start_button_width, start_button_height,  # size
    "START",
    "Images\\START_BUTTON.png",  # Fallback image
    start_animation_path  # Animation base path
)

exit_button = PixelButton(
    WIDTH // 2 - exit_button_width // 2, HEIGHT // 2 + 150,  # position
    exit_button_width, exit_button_height,  # size
    "EXIT",
    "Images\\EXIT_BUTTON.png",  # Fallback image
    exit_animation_path  # Animation base path
)

# Create back button for game screen (for game screen) - no image, uses original style
back_button = PixelButton(
    WIDTH // 2 - exit_button_width // 2, HEIGHT - 150,
    exit_button_width, exit_button_height, "BACK TO MENU"
)

if __name__ == "__main__":
    main_menu()
