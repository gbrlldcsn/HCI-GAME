import pygame
import sys
import os

# Initialize pygame
pygame.init()

# Display constants
WIDTH, HEIGHT = 1280, 720
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")

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
font_medium = pygame.font.SysFont("Arial", 48)
font_large = pygame.font.SysFont("Arial", 72)
font_small = pygame.font.SysFont("Arial", 24)

# Load logo for display in menu
try:
    logo = pygame.image.load("Images/DEADLINE_CHRONICLES.png")
    # Scale the logo to an appropriate size for display
    logo = pygame.transform.scale(logo, (500, 500))
except pygame.error:
    print("Warning: Could not load logo image for display")
    logo = None


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
        self.animation_speed = 8  # frames per animation frame (slower = more frames between changes)
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
                self.button_image = pygame.image.load(image_path)
                # Scale the image to fit the button size
                self.button_image = pygame.transform.scale(self.button_image, (width, height))
            except pygame.error:
                print(f"Warning: Could not load button image '{image_path}'")
                self.button_image = None

        # Load animation frames
        for i, frame_path in enumerate(self.animation_frames):
            try:
                frame_img = pygame.image.load(frame_path)
                frame_img = pygame.transform.scale(frame_img, (width, height))
                self.animation_frames[i] = frame_img
            except pygame.error:
                print(f"Warning: Could not load animation frame '{frame_path}'")
                self.animation_frames[i] = None

        # Load idle animation frames
        for i, frame_path in enumerate(self.idle_animation_frames):
            try:
                frame_img = pygame.image.load(frame_path)
                frame_img = pygame.transform.scale(frame_img, (width, height))
                self.idle_animation_frames[i] = frame_img
            except pygame.error:
                print(f"Warning: Could not load idle animation frame '{frame_path}'")
                self.idle_animation_frames[i] = None

        # Load hover animation frames
        for i, frame_path in enumerate(self.hover_animation_frames):
            try:
                frame_img = pygame.image.load(frame_path)
                frame_img = pygame.transform.scale(frame_img, (width, height))
                self.hover_animation_frames[i] = frame_img
            except pygame.error:
                print(f"Warning: Could not load hover animation frame '{frame_path}'")
                self.hover_animation_frames[i] = None

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
        # This is a simplified pixel font renderer
        # In a full implementation, you'd have a proper pixel font system
        letter_spacing = 10
        letter_height = 30
        letter_width = 20

        # Create a surface for the entire text
        text_width = len(text) * (letter_width + letter_spacing)
        text_surface = pygame.Surface((text_width, letter_height), pygame.SRCALPHA)

        # Draw each letter (very simplified)
        x_pos = 0
        for char in text:
            if char == 'S':
                self.draw_pixel_S(text_surface, x_pos, 0)
            elif char == 'T':
                self.draw_pixel_T(text_surface, x_pos, 0)
            elif char == 'A':
                self.draw_pixel_A(text_surface, x_pos, 0)
            elif char == 'R':
                self.draw_pixel_R(text_surface, x_pos, 0)
            elif char == 'E':
                self.draw_pixel_E(text_surface, x_pos, 0)
            elif char == 'X':
                self.draw_pixel_X(text_surface, x_pos, 0)
            elif char == 'I':
                self.draw_pixel_I(text_surface, x_pos, 0)
            elif char == 'C':
                self.draw_pixel_C(text_surface, x_pos, 0)
            elif char == 'K':
                self.draw_pixel_K(text_surface, x_pos, 0)
            elif char == 'M':
                self.draw_pixel_M(text_surface, x_pos, 0)
            elif char == 'U':
                self.draw_pixel_U(text_surface, x_pos, 0)
            elif char == 'N':
                self.draw_pixel_N(text_surface, x_pos, 0)

            x_pos += letter_width + letter_spacing

        return text_surface

    # Functions to draw pixel letters (keeping all the original letter drawing functions)
    def draw_pixel_S(self, surface, x, y):
        pixels = [
            (1, 0), (2, 0), (3, 0),
            (0, 1),
            (1, 2), (2, 2),
            (3, 3),
            (0, 4), (1, 4), (2, 4)
        ]
        for px, py in pixels:
            pygame.draw.rect(surface, BEIGE, (x + px * 4, y + py * 6, 4, 6))

    def draw_pixel_T(self, surface, x, y):
        pixels = [
            (0, 0), (1, 0), (2, 0), (3, 0), (4, 0),
            (2, 1), (2, 2), (2, 3), (2, 4)
        ]
        for px, py in pixels:
            pygame.draw.rect(surface, BEIGE, (x + px * 4, y + py * 6, 4, 6))

    def draw_pixel_A(self, surface, x, y):
        pixels = [
            (1, 0), (2, 0),
            (0, 1), (3, 1),
            (0, 2), (1, 2), (2, 2), (3, 2),
            (0, 3), (3, 3),
            (0, 4), (3, 4)
        ]
        for px, py in pixels:
            pygame.draw.rect(surface, BEIGE, (x + px * 4, y + py * 6, 4, 6))

    def draw_pixel_R(self, surface, x, y):
        pixels = [
            (0, 0), (1, 0), (2, 0),
            (0, 1), (3, 1),
            (0, 2), (1, 2), (2, 2),
            (0, 3), (2, 3),
            (0, 4), (3, 4)
        ]
        for px, py in pixels:
            pygame.draw.rect(surface, BEIGE, (x + px * 4, y + py * 6, 4, 6))

    def draw_pixel_E(self, surface, x, y):
        pixels = [
            (0, 0), (1, 0), (2, 0), (3, 0),
            (0, 1),
            (0, 2), (1, 2), (2, 2),
            (0, 3),
            (0, 4), (1, 4), (2, 4), (3, 4)
        ]
        for px, py in pixels:
            pygame.draw.rect(surface, BEIGE, (x + px * 4, y + py * 6, 4, 6))

    def draw_pixel_X(self, surface, x, y):
        pixels = [
            (0, 0), (3, 0),
            (1, 1), (2, 1),
            (1, 2),
            (1, 3), (2, 3),
            (0, 4), (3, 4)
        ]
        for px, py in pixels:
            pygame.draw.rect(surface, BEIGE, (x + px * 4, y + py * 6, 4, 6))

    def draw_pixel_I(self, surface, x, y):
        pixels = [
            (0, 0), (1, 0), (2, 0),
            (1, 1), (1, 2), (1, 3),
            (0, 4), (1, 4), (2, 4)
        ]
        for px, py in pixels:
            pygame.draw.rect(surface, BEIGE, (x + px * 4, y + py * 6, 4, 6))

    def draw_pixel_C(self, surface, x, y):
        pixels = [
            (1, 0), (2, 0), (3, 0),
            (0, 1),
            (0, 2),
            (0, 3),
            (1, 4), (2, 4), (3, 4)
        ]
        for px, py in pixels:
            pygame.draw.rect(surface, BEIGE, (x + px * 4, y + py * 6, 4, 6))

    def draw_pixel_K(self, surface, x, y):
        pixels = [
            (0, 0), (3, 0),
            (0, 1), (2, 1),
            (0, 2), (1, 2),
            (0, 3), (2, 3),
            (0, 4), (3, 4)
        ]
        for px, py in pixels:
            pygame.draw.rect(surface, BEIGE, (x + px * 4, y + py * 6, 4, 6))

    def draw_pixel_M(self, surface, x, y):
        pixels = [
            (0, 0), (1, 0), (2, 0), (3, 0), (4, 0),
            (0, 1), (2, 1), (4, 1),
            (0, 2), (4, 2),
            (0, 3), (4, 3),
            (0, 4), (4, 4)
        ]
        for px, py in pixels:
            pygame.draw.rect(surface, BEIGE, (x + px * 4, y + py * 6, 4, 6))

    def draw_pixel_U(self, surface, x, y):
        pixels = [
            (0, 0), (3, 0),
            (0, 1), (3, 1),
            (0, 2), (3, 2),
            (0, 3), (3, 3),
            (1, 4), (2, 4)
        ]
        for px, py in pixels:
            pygame.draw.rect(surface, BEIGE, (x + px * 4, y + py * 6, 4, 6))

    def draw_pixel_N(self, surface, x, y):
        pixels = [
            (0, 0), (3, 0),
            (0, 1), (1, 1), (3, 1),
            (0, 2), (2, 2), (3, 2),
            (0, 3), (3, 3),
            (0, 4), (3, 4)
        ]
        for px, py in pixels:
            pygame.draw.rect(surface, BEIGE, (x + px * 4, y + py * 6, 4, 6))

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
    # Background with gradient
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


def on_start_animation_complete():
    """Called when the start button animation completes"""
    print("Start button animation completed! Starting game...")
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


# Updated animation frames - using your new start button images
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
start_button = PixelButton(WIDTH // 2 - button_width // 2, HEIGHT // 2 + 100,
                           button_width, button_height, "START",
                           "Images/StartButtonPNG/Idle/IdleStartButtonPNG1.png", 
                           start_animation_frames, idle_animation_frames, hover_animation_frames)

# Exit button with image (using existing EXIT button image)
exit_button = PixelButton(WIDTH // 2 - button_width // 2, HEIGHT // 2 + 100 + button_height + 20,
                          button_width, button_height, "EXIT", "Images/EXIT_BUTTON.png")

# Back to menu button (for game screen) - no image, uses original style
back_button = PixelButton(WIDTH // 2 - button_width // 2, HEIGHT - 150,
                          button_width, button_height, "BACK TO MENU")

# Run the menu
if __name__ == "__main__":
    main_menu()
