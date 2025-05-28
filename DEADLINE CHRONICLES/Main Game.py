import pygame
import sys
import os

# Initialize pygame
pygame.init()

# Display constants
WIDTH, HEIGHT = 1280, 720
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DEALINE CHRONICLES")

# Set window icon (keep this functionality but don't display logo in menu)
try:
    icon = pygame.image.load("Images/DEADLINE_CHRONICLES.png")
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

# Font
# Load custom fonts from Fonts folder
try:
    font_medium = pygame.font.Font("Fonts/slkscr.ttf", 24)
    font_large = pygame.font.Font("Fonts/slkscr.ttf", 36)
    font_small = pygame.font.Font("Fonts/slkscr.ttf", 16)
    # Also load bold and extended variants for potential use
    font_medium_bold = pygame.font.Font("Fonts/slkscrb.ttf", 24)
    font_medium_extended = pygame.font.Font("Fonts/slkscre.ttf", 24)
    font_medium_extended_bold = pygame.font.Font("Fonts/slkscreb.ttf", 24)
except pygame.error:
    print("Warning: Could not load custom fonts, falling back to system fonts")
    font_medium = pygame.font.SysFont("Arial", 48)
    font_large = pygame.font.SysFont("Arial", 72)
    font_small = pygame.font.SysFont("Arial", 24)

# Font is loaded from TTF files above

# Load logo for display in menu
try:
    logo = pygame.image.load("Images/DEADLINE_CHRONICLES.png")
    # Scale the logo to an appropriate size for display
    logo = pygame.transform.scale(logo, (700, 500))
except pygame.error:
    print("Warning: Could not load logo image for display")
    logo = None

# Load menu background
try:
    menu_bg = pygame.image.load("Images/Menu_Background/ComLab2_Temp.png")
    # Scale the background to fill the window in landscape orientation
    menu_bg = pygame.transform.scale(menu_bg, (WIDTH, HEIGHT))
except pygame.error:
    print("Warning: Could not load menu background image")
    menu_bg = None


class PixelButton:
    def __init__(self, x, y, width, height, text, image_path=None, animation_frames=None, idle_animation_frames=None, hover_animation_frames=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.is_hovered = False
        self.pixel_size = 5  # Size of each "pixel" in our button
        self.shadow_offset = 4  # Pixel offset for the 3D effect
        self.image_path = image_path
        self.button_image = None

        # Animation properties
        self.animation_frames = animation_frames or []
        self.current_frame = 0
        self.is_animating = False
        self.animation_speed = 8  # Adjusted speed for new click animation (lower = faster)
        self.animation_counter = 0
        self.animation_complete_callback = None

        # Idle animation properties
        self.idle_animation_frames = idle_animation_frames or []
        self.idle_current_frame = 0
        self.idle_animation_speed = 12  # Slower than click animation
        self.idle_animation_counter = 0
        self.is_idle_animating = True  # Start idle animation by default

        # Hover animation properties
        self.hover_animation_frames = hover_animation_frames or []
        self.hover_current_frame = 0
        self.hover_animation_speed = 10  # Medium speed between click and idle
        self.hover_animation_counter = 0
        self.is_hover_animating = False  # Start hover animation when hovered

        # Load button image if provided
        if image_path:
            try:
                # Force reload by creating a new Surface
                self.button_image = pygame.image.load(image_path).convert_alpha()
                # Scale the image to fit the button size
                self.button_image = pygame.transform.scale(self.button_image, (width, height))
            except pygame.error:
                print(f"Warning: Could not load button image '{image_path}'")
                self.button_image = None

        # Load animation frames
        animation_frames_copy = self.animation_frames.copy()  # Create a copy to avoid modifying the original array
        self.animation_frames = []  # Clear the array
        for frame_path in animation_frames_copy:
            try:
                # Force reload by creating a new Surface
                frame_img = pygame.image.load(frame_path).convert_alpha()
                frame_img = pygame.transform.scale(frame_img, (width, height))
                self.animation_frames.append(frame_img)
            except pygame.error:
                print(f"Warning: Could not load animation frame '{frame_path}'")
                self.animation_frames.append(None)

        # Load idle animation frames
        idle_animation_frames_copy = self.idle_animation_frames.copy()  # Create a copy to avoid modifying the original array
        self.idle_animation_frames = []  # Clear the array
        for frame_path in idle_animation_frames_copy:
            try:
                # Force reload by creating a new Surface
                frame_img = pygame.image.load(frame_path).convert_alpha()
                frame_img = pygame.transform.scale(frame_img, (width, height))
                self.idle_animation_frames.append(frame_img)
            except pygame.error:
                print(f"Warning: Could not load idle animation frame '{frame_path}'")
                self.idle_animation_frames.append(None)

        # Load hover animation frames
        hover_animation_frames_copy = self.hover_animation_frames.copy()  # Create a copy to avoid modifying the original array
        self.hover_animation_frames = []  # Clear the array
        for frame_path in hover_animation_frames_copy:
            try:
                # Force reload by creating a new Surface
                frame_img = pygame.image.load(frame_path).convert_alpha()
                frame_img = pygame.transform.scale(frame_img, (width, height))
                self.hover_animation_frames.append(frame_img)
            except pygame.error:
                print(f"Warning: Could not load hover animation frame '{frame_path}'")
                self.hover_animation_frames.append(None)

        # Pre-render our pixel font text (fallback if no image)
        if not self.button_image and not self.animation_frames:
            self.text_surface = self.create_pixel_text(text)
        else:
            self.text_surface = None

    def start_click_animation(self, callback=None):
        """Start the click animation"""
        if self.animation_frames:
            self.is_animating = True
            self.current_frame = 0
            self.animation_counter = 0
            self.animation_complete_callback = callback

    def update_animation(self):
        """Update click animation frame"""
        if not self.is_animating:
            return False

        self.animation_counter += 1

        if self.animation_counter >= self.animation_speed:
            self.animation_counter = 0
            self.current_frame += 1

            if self.current_frame >= len(self.animation_frames):
                # Animation complete
                self.is_animating = False
                self.current_frame = 0

                # Call callback if provided
                if self.animation_complete_callback:
                    self.animation_complete_callback()
                    self.animation_complete_callback = None

                return True  # Animation finished

        return False  # Animation still running

    def update_idle_animation(self):
        """Update idle animation frame"""
        if not self.is_idle_animating or not self.idle_animation_frames:
            return False

        # Don't update idle animation if click animation is running or hover animation is active
        if self.is_animating or (self.is_hover_animating and self.is_hovered):
            return False

        self.idle_animation_counter += 1

        if self.idle_animation_counter >= self.idle_animation_speed:
            self.idle_animation_counter = 0
            self.idle_current_frame += 1

            if self.idle_current_frame >= len(self.idle_animation_frames):
                # Loop the idle animation
                self.idle_current_frame = 0

        return True  # Idle animation updated

    def update_hover_animation(self):
        """Update hover animation frame"""
        if not self.is_hover_animating or not self.hover_animation_frames or not self.is_hovered:
            return False

        # Don't update hover animation if click animation is running
        if self.is_animating:
            return False

        self.hover_animation_counter += 1

        if self.hover_animation_counter >= self.hover_animation_speed:
            self.hover_animation_counter = 0
            self.hover_current_frame += 1

            if self.hover_current_frame >= len(self.hover_animation_frames):
                # Loop the hover animation
                self.hover_current_frame = 0

        return True  # Hover animation updated

    def create_pixel_text(self, text):
        """Create a surface with text rendered using the loaded font"""
        # Use the medium font for button text
        try:
            # Try to use the loaded font
            text_surface = font_medium.render(text, True, BEIGE)
        except:
            # Fallback to system font if there's an issue
            fallback_font = pygame.font.SysFont("Arial", 24)
            text_surface = fallback_font.render(text, True, BEIGE)

        return text_surface

    def draw(self, surface):
        # Update animations
        self.update_animation()
        self.update_hover_animation()
        self.update_idle_animation()

        # If we're animating and have animation frames, use the current animation frame
        if self.is_animating and self.animation_frames and self.current_frame < len(self.animation_frames):
            current_image = self.animation_frames[self.current_frame]
            if current_image:
                # Add a subtle hover effect by slightly adjusting the position
                offset = 2 if self.is_hovered else 0
                image_rect = current_image.get_rect(center=(self.rect.centerx + offset, self.rect.centery + offset))
                surface.blit(current_image, image_rect)
                return

        # If we're hovering and have hover animation frames, use the current hover frame
        if self.is_hover_animating and self.is_hovered and self.hover_animation_frames and self.hover_current_frame < len(self.hover_animation_frames):
            current_hover_image = self.hover_animation_frames[self.hover_current_frame]
            if current_hover_image:
                # Add a subtle hover effect by slightly adjusting the position
                offset = 2  # Always apply offset for hover animation
                image_rect = current_hover_image.get_rect(center=(self.rect.centerx + offset, self.rect.centery + offset))
                surface.blit(current_hover_image, image_rect)
                return

        # If we have idle animation frames and idle animation is active, use the current idle frame
        if self.is_idle_animating and self.idle_animation_frames and self.idle_current_frame < len(self.idle_animation_frames):
            current_idle_image = self.idle_animation_frames[self.idle_current_frame]
            if current_idle_image:
                # Add a subtle hover effect by slightly adjusting the position
                offset = 2 if self.is_hovered else 0
                image_rect = current_idle_image.get_rect(center=(self.rect.centerx + offset, self.rect.centery + offset))
                surface.blit(current_idle_image, image_rect)
                return

        # If we have a button image (and not animating), use it as fallback
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
        was_hovered = self.is_hovered
        self.is_hovered = self.rect.collidepoint(pos)

        # Toggle hover animation based on hover state
        if self.is_hovered and not was_hovered:
            # Mouse just entered the button
            self.is_hover_animating = True
            self.hover_current_frame = 0
        elif not self.is_hovered and was_hovered:
            # Mouse just left the button
            self.is_hover_animating = False

        return self.is_hovered

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            return True
        return False


def draw_menu():
    # Display background image if available
    if menu_bg is not None:
        SCREEN.blit(menu_bg, (0, 0))
    else:
        # Fallback to gradient if background image is not available
        for y in range(HEIGHT):
            # Create a gradient from dark blue to light blue
            color_value = int(y / HEIGHT * 155) + 100
            pygame.draw.line(SCREEN, (0, 0, color_value), (0, y), (WIDTH, y))

    # Display logo if available
    if logo is not None:
        logo_rect = logo.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 150))
        SCREEN.blit(logo, logo_rect)

    # Draw buttons
    start_button.draw(SCREEN)
    exit_button.draw(SCREEN)


def draw_game():
    # Simple black screen
    SCREEN.fill(BLACK)

    # Draw back to menu button
    back_button.draw(SCREEN)


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
            if back_button.is_clicked(event):
                return  # Return to main menu

        # Check hover states
        back_button.check_hover(mouse_pos)

        # Draw game screen
        SCREEN.fill(BLACK)  # Clear the screen once per frame
        back_button.draw(SCREEN)  # Draw the back button directly

        # Update display
        pygame.display.flip()
        clock.tick(60)


def show_intro_message():
    """Shows the intro message with typing animation effect using custom fonts"""
    message = "There was a student who was given a task by his professor to do a project, but he ended up in another dimension. Let's follow this student's journey"

    clock = pygame.time.Clock()
    running = True
    displayed_chars = 0
    typing_speed = 1  # Characters per frame
    typing_complete = False


    # Use the custom font for the message
    message_font = font_medium
    continue_font = font_small

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Skip animation if any key is pressed
            if event.type == pygame.KEYDOWN:
                if typing_complete:
                    return  # Proceed to game
                else:
                    displayed_chars = len(message)  # Show full message

        # Clear screen with black background
        SCREEN.fill(BLACK)

        # Update typing animation
        if displayed_chars < len(message):
            displayed_chars += typing_speed
            if displayed_chars >= len(message):
                typing_complete = True
                displayed_chars = len(message)

        # Render the message
        current_text = message[:displayed_chars]

        # Split text into multiple lines if needed
        max_width = WIDTH - 100  # Width for text wrapping
        lines = []
        words = current_text.split(' ')
        current_line = words[0] if words else ""

        for word in words[1:]:
            test_line = current_line + " " + word
            # Create a temporary text surface to check width
            test_surface = message_font.render(test_line, True, WHITE)
            if test_surface.get_width() <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word

        lines.append(current_line)

        # Draw text lines
        line_height = message_font.get_linesize() + 5  # Add a little extra spacing between lines
        y_pos = HEIGHT // 2 - (len(lines) * line_height) // 2

        for line in lines:
            # Create text surface for each line
            text_surface = message_font.render(line, True, WHITE)
            text_rect = text_surface.get_rect(center=(WIDTH // 2, y_pos))
            SCREEN.blit(text_surface, text_rect)
            y_pos += line_height

        # Show "Press any key to continue" when typing is complete
        if typing_complete:
            continue_text = continue_font.render("Press any key to continue", True, WHITE)
            continue_rect = continue_text.get_rect(center=(WIDTH // 2, HEIGHT - 100))
            SCREEN.blit(continue_text, continue_rect)

        pygame.display.flip()
        clock.tick(60)

def on_start_animation_complete():
    """Called when the start button animation completes"""
    print("Start button animation completed! Showing intro message...")
    show_intro_message()
    print("Intro message complete! Starting game...")
    game_loop()


def main_menu():
    clock = pygame.time.Clock()
    running = True

    while running:
        mouse_pos = pygame.mouse.get_pos()

        # Check events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Button click handling
            if start_button.is_clicked(event):
                print("Start button clicked!")
                # Start the click animation instead of immediately transitioning
                start_button.start_click_animation(on_start_animation_complete)

            if exit_button.is_clicked(event):
                print("Exit button clicked!")
                pygame.quit()
                sys.exit()

        # Check hover states
        start_button.check_hover(mouse_pos)
        exit_button.check_hover(mouse_pos)

        # Draw menu
        draw_menu()

        # Update display
        pygame.display.flip()
        clock.tick(60)


# Updated animation frames - using the latest click button images
start_animation_frames = [
    "Images/StartButtonPNG/Click/ClickStartButtonPNG1.png",  # Frame 1
    "Images/StartButtonPNG/Click/ClickStartButtonPNG2.png",  # Frame 2
    "Images/StartButtonPNG/Click/ClickStartButtonPNG3.png",  # Frame 3
    "Images/StartButtonPNG/Click/ClickStartButtonPNG4.png",  # Frame 4
    "Images/StartButtonPNG/Click/ClickStartButtonPNG5.png"  # Frame 5
]

# Idle animation frames
idle_animation_frames = [
    "Images/StartButtonPNG/Idle/IdleStartButtonPNG1.png",  # Frame 1
    "Images/StartButtonPNG/Idle/IdleStartButtonPNG2.png",  # Frame 2
    "Images/StartButtonPNG/Idle/IdleStartButtonPNG3.png",  # Frame 3
    "Images/StartButtonPNG/Idle/IdleStartButtonPNG4.png"   # Frame 4
]

# Hover animation frames
hover_animation_frames = [
    "Images/StartButtonPNG/Hover/HoverStartButtonPNG1.png",  # Frame 1
    "Images/StartButtonPNG/Hover/HoverStartButtonPNG2.png",  # Frame 2
    "Images/StartButtonPNG/Hover/HoverStartButtonPNG3.png",  # Frame 3
    "Images/StartButtonPNG/Hover/HoverStartButtonPNG4.png"   # Frame 4
]

# Create buttons with pixel art style
button_width = 400
button_height = 120

# Start button with idle image, click animation frames, idle animation frames, and hover animation frames
start_button = PixelButton(WIDTH // 2 - button_width // 2, HEIGHT // 2 + 60,
                           button_width, button_height, "START",
                           "Images/StartButtonPNG/Idle/IdleStartButtonPNG1.png",
                           start_animation_frames, idle_animation_frames, hover_animation_frames)

# Exit button with image (using existing EXIT button image)
exit_button = PixelButton(WIDTH // 2 - button_width // 2, HEIGHT // 2 + 60 + button_height + 20,
                          button_width, button_height, "EXIT", "Images/EXIT_BUTTON.png")

# Back to menu button (for game screen) - no image, uses original style
back_button = PixelButton(WIDTH // 2 - button_width // 2, HEIGHT - 150,
                          button_width, button_height, "BACK TO MENU")

# Run the menu
if __name__ == "__main__":
    main_menu()
